from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Pydantic Models
class SessionCreateRequest(BaseModel):
    name: str = Field(..., description="Name of the story session")
    owner_id: Optional[str] = Field(None, description="ID of the session owner")


class SessionResponse(BaseModel):
    session_id: str
    name: str
    status: str
    message: Optional[str] = None


class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]
    total: int


class AssetResponse(BaseModel):
    id: str
    name: str
    type: str
    price: float
    creator: Optional[str] = None
    rating: Optional[float] = None
    downloads: Optional[int] = None


class AssetListResponse(BaseModel):
    assets: List[AssetResponse]
    total: int


class MarketplaceStatsResponse(BaseModel):
    total_listings: int
    total_transactions: int
    total_revenue: float


class UniverseCreateRequest(BaseModel):
    name: str
    creator_id: str
    description: str
    physics_rules: Dict[str, Any]
    theme: str
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = True


class UniverseResponse(BaseModel):
    universe_id: str
    name: str
    creator_id: str
    description: str
    physics_rules: Dict[str, Any]
    theme: str
    tags: List[str]
    created_at: str
    is_public: bool


class ProposalCreateRequest(BaseModel):
    title: str
    description: str
    proposal_type: str
    voting_period_days: Optional[int] = None


class ProposalResponse(BaseModel):
    proposal_id: str
    title: str
    description: str
    proposal_type: str
    proposer_id: str
    created_at: str
    voting_period_days: int
    status: str
    votes_for: int
    votes_against: int
    votes_abstain: int


# FastAPI Application
app = FastAPI(
    title="AION Story Engine API",
    description="""
    🌌 AION Story Engine - 想象力的基础设施

    AION Story Engine 是一个基于世界模型的多层叙事系统，结合了 Medici Synapse 跨域创新引擎和创作者数字孪生系统。

    ## 功能特性

    ### 核心系统
    - **故事会话管理** - 创建、编辑、管理交互式故事
    - **资产系统** - 管理和分享创作资产
    - **协作功能** - 多人实时协作创作
    - **多元宇宙** - 创建和连接多个故事世界
    - **DAO 治理** - 去中心化治理和投票系统

    ### 高级功能
    - **节点树系统** - 分支和合并故事线
    - **物理引擎** - 真实的世界模拟
    - **认知引擎** - AI 驱动的 NPC 行为
    - **叙事引擎** - 自动生成故事内容
    - **数字孪生** - 个性化创作助手

    ## 认证

    API 使用 API Key 进行认证。在请求头中添加：
    ```
    X-API-Key: your_api_key_here
    ```

    ## 速率限制

    - 免费版：100 请求/分钟
    - 专业版：1000 请求/分钟
    - 企业版：无限制

    ## 支持

    - 📧 邮箱：support@aion-story.com
    - 💬 Discord：https://discord.gg/aion-story
    - 📖 文档：https://docs.aion-story.com
    """,
    version="6.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Sessions",
            "description": "故事会话管理",
        },
        {
            "name": "Assets",
            "description": "资产系统",
        },
        {
            "name": "Marketplace",
            "description": "创作者市场",
        },
        {
            "name": "Universes",
            "description": "多元宇宙",
        },
        {
            "name": "Governance",
            "description": "DAO 治理",
        },
        {
            "name": "Collaboration",
            "description": "协作功能",
        },
    ],
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Key Authentication (simplified)
@app.middleware("http")
async def api_key_auth(request, call_next):
    # Skip auth for docs and health check
    if request.url.path in ["/docs", "/redoc", "/openapi.json", "/health"]:
        response = await call_next(request)
        return response

    # Check API key (in production, use proper JWT or OAuth)
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "API key missing. Include X-API-Key header."},
        )

    # In production, validate the API key against a database
    # For now, just pass through
    response = await call_next(request)
    return response


# Health Check
@app.get("/health", tags=["System"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "version": "6.0.0",
        "service": "AION Story Engine API",
    }


# Session Endpoints
@app.get(
    "/api/v1/sessions/{session_id}",
    response_model=SessionResponse,
    tags=["Sessions"],
    summary="获取会话",
    description="根据会话 ID 获取故事会话的详细信息",
)
async def get_session(session_id: str):
    """获取指定的故事会话"""
    try:
        # In a real implementation, fetch from database
        return SessionResponse(
            session_id=session_id,
            name="Lab Fire Scenario",
            status="active",
            message="Session retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")


@app.post(
    "/api/v1/sessions",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Sessions"],
    summary="创建会话",
    description="创建一个新的故事会话",
)
async def create_session(request: SessionCreateRequest):
    """创建新的故事会话"""
    try:
        # In a real implementation, save to database
        session_id = f"session-{hash(request.name) % 10000}"
        return SessionResponse(
            session_id=session_id,
            name=request.name,
            status="created",
            message="Session created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@app.get(
    "/api/v1/sessions",
    response_model=SessionListResponse,
    tags=["Sessions"],
    summary="获取会话列表",
    description="获取当前用户的所有故事会话",
)
async def list_sessions(skip: int = 0, limit: int = 100):
    """列出用户的故事会话"""
    # In a real implementation, fetch from database with pagination
    sessions = [
        SessionResponse(
            session_id=f"session-{i}",
            name=f"Story {i}",
            status="active" if i % 2 == 0 else "completed",
            message="Retrieved successfully"
        )
        for i in range(skip, min(skip + limit, 10))
    ]

    return SessionListResponse(
        sessions=sessions,
        total=10
    )


# Asset Endpoints
@app.get(
    "/api/v1/assets",
    response_model=AssetListResponse,
    tags=["Assets"],
    summary="获取资产列表",
    description="获取可用的创作资产列表",
)
async def list_assets(skip: int = 0, limit: int = 100, asset_type: Optional[str] = None):
    """列出所有可用的资产"""
    # Mock data
    all_assets = [
        AssetResponse(
            id="asset-1",
            name="Fire Physics Rule",
            type="world_rule",
            price=0.0,
            creator="alice",
            rating=5.0,
            downloads=1247,
        ),
        AssetResponse(
            id="asset-2",
            name="Medieval Magic System",
            type="asset_pack",
            price=9.99,
            creator="FantasyWizard",
            rating=4.8,
            downloads=892,
        ),
        AssetResponse(
            id="asset-3",
            name="Cyberpunk NPC Template",
            type="npc_template",
            price=5.0,
            creator="CyberCreator",
            rating=4.6,
            downloads=567,
        ),
    ]

    # Apply filters
    filtered_assets = all_assets
    if asset_type:
        filtered_assets = [a for a in filtered_assets if a.type == asset_type]

    return AssetListResponse(
        assets=filtered_assets[skip:skip + limit],
        total=len(filtered_assets)
    )


# Marketplace Endpoints
@app.get(
    "/api/v1/marketplace/stats",
    response_model=MarketplaceStatsResponse,
    tags=["Marketplace"],
    summary="获取市场统计",
    description="获取创作者市场的统计数据",
)
async def get_marketplace_stats():
    """获取市场统计数据"""
    return MarketplaceStatsResponse(
        total_listings=150,
        total_transactions=1200,
        total_revenue=45000.0,
    )


@app.get(
    "/api/v1/marketplace/assets",
    response_model=AssetListResponse,
    tags=["Marketplace"],
    summary="获取市场资产",
    description="获取市场中所有可购买的资产",
)
async def list_marketplace_assets(skip: int = 0, limit: int = 100):
    """列出市场中的所有资产"""
    # Mock data for marketplace
    assets = [
        AssetResponse(
            id=f"market-asset-{i}",
            name=f"Asset {i}",
            type="pattern",
            price=float(i) * 0.99,
            creator=f"creator_{i % 5}",
            rating=4.0 + (i % 10) * 0.1,
            downloads=i * 10,
        )
        for i in range(1, 21)
    ]

    return AssetListResponse(
        assets=assets[skip:skip + limit],
        total=len(assets)
    )


# Universe Endpoints
@app.get(
    "/api/v1/universes",
    response_model=List[UniverseResponse],
    tags=["Universes"],
    summary="获取宇宙列表",
    description="获取所有可用的多元宇宙",
)
async def list_universes(skip: int = 0, limit: int = 100):
    """列出所有多元宇宙"""
    universes = [
        UniverseResponse(
            universe_id=f"universe-{i}",
            name=f"Universe {i}",
            creator_id=f"creator_{i % 10}",
            description=f"Description for universe {i}",
            physics_rules={"gravity": 9.8, "thermodynamics": True},
            theme="fantasy" if i % 2 == 0 else "sci-fi",
            tags=["magic", "dragons"] if i % 2 == 0 else ["spaceships", "robots"],
            created_at="2025-02-05T00:00:00Z",
            is_public=True,
        )
        for i in range(1, 11)
    ]

    return universes[skip:skip + limit]


@app.post(
    "/api/v1/universes",
    response_model=UniverseResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Universes"],
    summary="创建宇宙",
    description="创建一个新的多元宇宙",
)
async def create_universe(request: UniverseCreateRequest):
    """创建新的多元宇宙"""
    universe_id = f"universe-{hash(request.name) % 10000}"
    return UniverseResponse(
        universe_id=universe_id,
        name=request.name,
        creator_id=request.creator_id,
        description=request.description,
        physics_rules=request.physics_rules,
        theme=request.theme,
        tags=request.tags or [],
        created_at="2025-02-05T00:00:00Z",
        is_public=request.is_public or True,
    )


# Governance Endpoints
@app.get(
    "/api/v1/governance/proposals",
    response_model=List[ProposalResponse],
    tags=["Governance"],
    summary="获取提案列表",
    description="获取所有治理提案",
)
async def list_proposals(skip: int = 0, limit: int = 100, status: Optional[str] = None):
    """列出所有治理提案"""
    proposals = [
        ProposalResponse(
            proposal_id=f"proposal-{i}",
            title=f"Proposal {i}",
            description=f"Description for proposal {i}",
            proposal_type="feature_request",
            proposer_id=f"user_{i % 5}",
            created_at="2025-02-05T00:00:00Z",
            voting_period_days=7,
            status="active" if i % 3 == 0 else "passed",
            votes_for=i * 100,
            votes_against=i * 20,
            votes_abstain=i * 10,
        )
        for i in range(1, 11)
    ]

    if status:
        proposals = [p for p in proposals if p.status == status]

    return proposals[skip:skip + limit]


# Root Endpoint
@app.get("/")
async def root():
    """API 根端点"""
    return {
        "message": "Welcome to AION Story Engine API",
        "version": "6.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


if __name__ == "__main__":
    uvicorn.run(
        "api_fastapi:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
