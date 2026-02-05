"""
FastAPI Web Interface - Web API 主程序
提供RESTful API和WebSocket实时更新
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import asyncio
from contextlib import asynccontextmanager

# 导入后端模块
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from collaboration.manager import get_collaboration_manager
from sync.engine import get_sync_engine
from economy.marketplace import get_marketplace


# 请求/响应模型
class UserCreate(BaseModel):
    """用户创建"""
    name: str
    email: str
    avatar_url: Optional[str] = None


class SessionCreate(BaseModel):
    """会话创建"""
    story_id: str
    user_id: str
    name: str
    email: str


class SessionJoin(BaseModel):
    """加入会话"""
    user_id: str
    name: str
    email: str
    role: str = "viewer"  # owner, editor, commenter, viewer


class ChangeSubmit(BaseModel):
    """提交变更"""
    session_id: str
    user_id: str
    node_id: str
    change_type: str  # create, update, delete
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None


class ConflictResolve(BaseModel):
    """解决冲突"""
    session_id: str
    conflict_id: str
    resolution: str
    strategy: str = "last_write_wins"


class AssetPublish(BaseModel):
    """发布资产"""
    creator_id: str
    asset_type: str
    name: str
    description: str
    price: float
    license_type: str = "personal"
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class AssetSearch(BaseModel):
    """搜索资产"""
    query: str = ""
    asset_type: str = ""
    tags: Optional[List[str]] = None
    min_price: float = 0
    max_price: float = float('inf')
    min_rating: float = 0
    sort_by: str = "relevance"
    limit: int = 20


class ReviewCreate(BaseModel):
    """创建评价"""
    asset_id: str
    user_id: str
    rating: int
    title: str
    content: str
    verified_purchase: bool = False


# WebSocket连接管理器
class ConnectionManager:
    """WebSocket连接管理"""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str, user_id: str):
        """连接"""
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        self.user_connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket, session_id: str, user_id: str):
        """断开连接"""
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
        if user_id in self.user_connections:
            del self.user_connections[user_id]

    async def broadcast_to_session(self, session_id: str, message: Dict[str, Any]):
        """向会话广播消息"""
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """向用户发送消息"""
        if user_id in self.user_connections:
            try:
                await self.user_connections[user_id].send_json(message)
            except:
                pass


manager = ConnectionManager()


# 应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    # 启动时初始化
    print("Starting AION Story Engine API...")
    yield
    # 关闭时清理
    print("Shutting down AION Story Engine API...")


# 创建FastAPI应用
app = FastAPI(
    title="AION Story Engine API",
    description="AI-powered collaborative storytelling platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 健康检查
@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "AION Story Engine API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# ============ 协作相关端点 ============

@app.post("/api/collaboration/sessions")
async def create_session(session_data: SessionCreate):
    """创建协作会话"""
    collab_manager = get_collaboration_manager()

    from collaboration.manager import User
    user = User(
        id=session_data.user_id,
        name=session_data.name,
        email=session_data.email
    )

    session = collab_manager.create_session(session_data.story_id, user)

    return {
        "session_id": session.id,
        "story_id": session.story_id,
        "created_at": session.created_at.isoformat(),
        "collaborators": len(session.collaborators)
    }


@app.post("/api/collaboration/sessions/{session_id}/join")
async def join_session(session_id: str, join_data: SessionJoin):
    """加入协作会话"""
    collab_manager = get_collaboration_manager()

    from collaboration.manager import User, UserRole
    user = User(
        id=join_data.user_id,
        name=join_data.name,
        email=join_data.email
    )

    role = UserRole(join_data.role)
    success = collab_manager.join_session(session_id, user, role)

    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"success": True, "message": "Joined session successfully"}


@app.get("/api/collaboration/sessions/{session_id}/users")
async def get_active_users(session_id: str):
    """获取活跃用户"""
    collab_manager = get_collaboration_manager()
    users = collab_manager.get_active_users(session_id)

    return {
        "session_id": session_id,
        "active_users": users,
        "count": len(users)
    }


@app.post("/api/collaboration/changes")
async def submit_change(change_data: ChangeSubmit):
    """提交变更"""
    collab_manager = get_collaboration_manager()

    from collaboration.manager import Change
    change = Change(
        user_id=change_data.user_id,
        node_id=change_data.node_id,
        change_type=change_data.change_type,
        old_value=change_data.old_value,
        new_value=change_data.new_value,
        metadata=change_data.metadata or {}
    )

    success = collab_manager.submit_change(change_data.session_id, change)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to submit change")

    # 广播变更
    await manager.broadcast_to_session(change_data.session_id, {
        "type": "change",
        "data": change.to_dict()
    })

    return {"success": True, "change_id": change.id}


@app.get("/api/collaboration/sessions/{session_id}/changes")
async def get_session_changes(session_id: str, since: Optional[str] = None):
    """获取会话变更"""
    collab_manager = get_collaboration_manager()

    since_dt = datetime.fromisoformat(since) if since else None
    changes = collab_manager.get_session_changes(session_id, since_dt)

    return {
        "session_id": session_id,
        "changes": changes,
        "count": len(changes)
    }


@app.get("/api/collaboration/sessions/{session_id}/conflicts")
async def get_session_conflicts(session_id: str):
    """获取会话冲突"""
    collab_manager = get_collaboration_manager()
    conflicts = collab_manager.get_session_conflicts(session_id)

    return {
        "session_id": session_id,
        "conflicts": conflicts,
        "count": len(conflicts)
    }


@app.post("/api/collaboration/conflicts/resolve")
async def resolve_conflict(resolve_data: ConflictResolve):
    """解决冲突"""
    collab_manager = get_collaboration_manager()
    success = collab_manager.resolve_conflict(
        resolve_data.session_id,
        resolve_data.conflict_id,
        resolve_data.resolution,
        resolve_data.strategy
    )

    if not success:
        raise HTTPException(status_code=400, detail="Failed to resolve conflict")

    return {"success": True, "message": "Conflict resolved"}


# ============ 同步相关端点 ============

@app.post("/api/sync/pull")
async def pull_changes():
    """拉取变更"""
    sync_engine = get_sync_engine("workspace", "https://github.com/user/repo.git")
    result = sync_engine.sync()

    return {
        "success": result.success,
        "changes_synced": result.changes_synced,
        "conflicts_detected": result.conflicts_detected,
        "sync_time": result.sync_time.total_seconds(),
        "error_message": result.error_message
    }


@app.post("/api/sync/push")
async def push_changes():
    """推送变更"""
    sync_engine = get_sync_engine("workspace", "https://github.com/user/repo.git")
    result = sync_engine.sync()

    return {
        "success": result.success,
        "changes_synced": result.changes_synced,
        "sync_time": result.sync_time.total_seconds(),
        "error_message": result.error_message
    }


@app.get("/api/sync/status")
async def get_sync_status():
    """获取同步状态"""
    sync_engine = get_sync_engine("workspace", "https://github.com/user/repo.git")
    status = sync_engine.get_status()

    return status


# ============ 市场相关端点 ============

@app.post("/api/marketplace/assets")
async def publish_asset(asset_data: AssetPublish):
    """发布资产"""
    marketplace = get_marketplace()

    from economy.marketplace import LicenseType
    license_type = LicenseType(asset_data.license_type)

    asset = marketplace.publish_asset(
        creator_id=asset_data.creator_id,
        asset_type=asset_data.asset_type,
        name=asset_data.name,
        description=asset_data.description,
        price=asset_data.price,
        license_type=license_type,
        tags=asset_data.tags,
        metadata=asset_data.metadata
    )

    if not asset:
        raise HTTPException(status_code=400, detail="Failed to publish asset")

    return {
        "asset_id": asset.id,
        "status": asset.status.value,
        "created_at": asset.created_at.isoformat()
    }


@app.post("/api/marketplace/assets/search")
async def search_assets(search_params: AssetSearch):
    """搜索资产"""
    marketplace = get_marketplace()

    assets = marketplace.search_assets(
        query=search_params.query,
        asset_type=search_params.asset_type,
        tags=search_params.tags,
        min_price=search_params.min_price,
        max_price=search_params.max_price,
        min_rating=search_params.min_rating,
        sort_by=search_params.sort_by,
        limit=search_params.limit
    )

    return {
        "assets": [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "price": a.price,
                "rating": a.rating,
                "purchase_count": a.purchase_count,
                "tags": a.tags,
                "license_type": a.license_type.value
            }
            for a in assets
        ],
        "count": len(assets)
    }


@app.get("/api/marketplace/assets/trending")
async def get_trending_assets(limit: int = 10):
    """获取热门资产"""
    marketplace = get_marketplace()
    assets = marketplace.get_trending_assets(limit)

    return {
        "assets": [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "price": a.price,
                "rating": a.rating,
                "purchase_count": a.purchase_count
            }
            for a in assets
        ]
    }


@app.post("/api/marketplace/assets/{asset_id}/purchase")
async def purchase_asset(asset_id: str, user_id: str = Header(..., alias="X-User-ID")):
    """购买资产"""
    marketplace = get_marketplace()
    transaction = marketplace.purchase_asset(asset_id, user_id)

    if not transaction:
        raise HTTPException(status_code=400, detail="Failed to purchase asset")

    return {
        "transaction_id": transaction.id,
        "status": transaction.status,
        "amount": transaction.amount
    }


@app.post("/api/marketplace/reviews")
async def create_review(review_data: ReviewCreate):
    """创建评价"""
    marketplace = get_marketplace()
    review = marketplace.add_review(
        asset_id=review_data.asset_id,
        user_id=review_data.user_id,
        rating=review_data.rating,
        title=review_data.title,
        content=review_data.content,
        verified_purchase=review_data.verified_purchase
    )

    if not review:
        raise HTTPException(status_code=400, detail="Failed to create review")

    return {
        "review_id": review.id,
        "rating": review.rating,
        "created_at": review.created_at.isoformat()
    }


@app.get("/api/marketplace/assets/{asset_id}/reviews")
async def get_asset_reviews(asset_id: str, limit: int = 10):
    """获取资产评价"""
    marketplace = get_marketplace()
    reviews = marketplace.get_asset_reviews(asset_id, limit)

    return {
        "reviews": [
            {
                "id": r.id,
                "rating": r.rating,
                "title": r.title,
                "content": r.content,
                "helpful_count": r.helpful_count,
                "verified_purchase": r.verified_purchase,
                "created_at": r.created_at.isoformat()
            }
            for r in reviews
        ]
    }


@app.get("/api/marketplace/creators/{creator_id}/stats")
async def get_creator_stats(creator_id: str):
    """获取创作者统计"""
    marketplace = get_marketplace()
    profile = marketplace.get_creator_profile(creator_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Creator not found")

    revenue = marketplace.calculate_revenue(
        creator_id,
        datetime.now() - timedelta(days=30),
        datetime.now()
    )

    return {
        "creator_id": creator_id,
        "display_name": profile.display_name,
        "total_sales": profile.total_sales,
        "total_revenue": profile.total_revenue,
        "rating": profile.rating,
        "review_count": profile.review_count,
        "follower_count": profile.follower_count,
        "last_30_days_revenue": revenue
    }


@app.get("/api/marketplace/statistics")
async def get_marketplace_statistics():
    """获取市场统计"""
    marketplace = get_marketplace()
    stats = marketplace.get_statistics()

    return stats


# ============ WebSocket端点 ============

@app.websocket("/ws/collaboration/{session_id}")
async def websocket_collaboration(websocket: WebSocket, session_id: str, user_id: str):
    """协作WebSocket"""
    await manager.connect(websocket, session_id, user_id)

    try:
        while True:
            # 接收消息
            data = await websocket.receive_json()

            # 处理不同类型的消息
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif data.get("type") == "change":
                # 广播变更
                await manager.broadcast_to_session(session_id, data)
            elif data.get("type") == "cursor":
                # 广播光标位置
                await manager.broadcast_to_session(session_id, {
                    "type": "cursor_update",
                    "user_id": user_id,
                    "position": data.get("position")
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id, user_id)
        # 通知其他用户
        await manager.broadcast_to_session(session_id, {
            "type": "user_left",
            "user_id": user_id
        })


# ============ 错误处理 ============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "detail": str(exc)
            }
        }
    )


# 运行服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
