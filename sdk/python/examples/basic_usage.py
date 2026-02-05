#!/usr/bin/env python3
"""
AION Story Engine SDK 示例

展示如何使用 Python SDK 进行常见操作

运行:
    python examples/basic_usage.py
"""

import os
import time
from aion_sdk import AionClient


def main():
    # 配置
    API_KEY = os.getenv("AION_API_KEY", "test_api_key")
    BASE_URL = os.getenv("AION_API_URL", "http://localhost:8000/api/v1")

    print("🌌 AION Story Engine SDK 示例")
    print("=" * 70)
    print(f"API 地址: {BASE_URL}")
    print(f"API Key: {API_KEY[:10]}...")
    print("=" * 70)

    # 创建客户端
    try:
        client = AionClient(api_key=API_KEY, base_url=BASE_URL)
        print("\n✅ 客户端创建成功")
    except Exception as e:
        print(f"\n❌ 创建客户端失败: {e}")
        print("请确保 API 服务器正在运行")
        return

    # 示例 1: 健康检查
    print("\n" + "=" * 70)
    print("示例 1: 健康检查")
    print("=" * 70)

    try:
        health = client.health_check()
        print(f"✅ 服务状态: {health['status']}")
        print(f"   版本: {health['version']}")
        print(f"   服务: {health['service']}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")

    # 示例 2: 创建故事会话
    print("\n" + "=" * 70)
    print("示例 2: 创建故事会话")
    print("=" * 70)

    try:
        session = client.create_session(
            name="实验室火灾场景",
            owner_id="alice"
        )
        print(f"✅ 会话创建成功!")
        print(f"   ID: {session.session_id}")
        print(f"   名称: {session.name}")
        print(f"   状态: {session.status}")

        # 保存会话 ID 供后续使用
        session_id = session.session_id

    except Exception as e:
        print(f"❌ 创建会话失败: {e}")
        session_id = None

    # 示例 3: 列出现有会话
    print("\n" + "=" * 70)
    print("示例 3: 列出现有会话")
    print("=" * 70)

    try:
        sessions = client.list_sessions(limit=5)
        print(f"✅ 找到 {len(sessions)} 个会话:")
        for i, s in enumerate(sessions, 1):
            status_icon = "🟢" if s.status == "active" else "🟡"
            print(f"   {i}. {status_icon} {s.name} ({s.session_id})")
    except Exception as e:
        print(f"❌ 列出会话失败: {e}")

    # 示例 4: 获取特定会话
    if session_id:
        print("\n" + "=" * 70)
        print(f"示例 4: 获取会话 {session_id}")
        print("=" * 70)

        try:
            session = client.get_session(session_id)
            print(f"✅ 会话信息:")
            print(f"   名称: {session.name}")
            print(f"   状态: {session.status}")
            print(f"   消息: {session.message}")
        except Exception as e:
            print(f"❌ 获取会话失败: {e}")

    # 示例 5: 浏览创作资产
    print("\n" + "=" * 70)
    print("示例 5: 浏览创作资产")
    print("=" * 70)

    try:
        assets = client.list_assets(limit=5)
        print(f"✅ 找到 {len(assets)} 个资产:")
        for i, a in enumerate(assets, 1):
            price = "免费" if a.price == 0 else f"${a.price:.2f}"
            rating = f"⭐{a.rating:.1f}" if a.rating else "无评分"
            print(f"   {i}. {a.name}")
            print(f"      类型: {a.type} | 价格: {price} | 评分: {rating}")
    except Exception as e:
        print(f"❌ 列出资产失败: {e}")

    # 示例 6: 创建多元宇宙
    print("\n" + "=" * 70)
    print("示例 6: 创建多元宇宙")
    print("=" * 70)

    try:
        universe = client.create_universe(
            name="科幻冒险宇宙",
            creator_id="alice",
            description="一个充满星际冒险和未知文明的科幻宇宙",
            physics_rules={
                "gravity": 9.8,
                "faster_than_light": True,
                "quantum_mechanics": "advanced"
            },
            theme="sci-fi",
            tags=["space", "adventure", "aliens", "technology"],
            is_public=True
        )
        print(f"✅ 宇宙创建成功!")
        print(f"   ID: {universe.universe_id}")
        print(f"   名称: {universe.name}")
        print(f"   主题: {universe.theme}")
        print(f"   标签: {', '.join(universe.tags)}")
        print(f"   公开: {'是' if universe.is_public else '否'}")

        universe_id = universe.universe_id

    except Exception as e:
        print(f"❌ 创建宇宙失败: {e}")
        universe_id = None

    # 示例 7: 列出多元宇宙
    print("\n" + "=" * 70)
    print("示例 7: 列出多元宇宙")
    print("=" * 70)

    try:
        universes = client.list_universes(limit=5)
        print(f"✅ 找到 {len(universes)} 个宇宙:")
        for i, u in enumerate(universes, 1):
            visibility = "🌍" if u.is_public else "🔒"
            theme_colors = {
                "fantasy": "🧙",
                "sci-fi": "🚀",
                "horror": "👻",
                "modern": "🏙️"
            }
            theme_icon = theme_colors.get(u.theme, "📦")
            print(f"   {i}. {visibility} {theme_icon} {u.name}")
            print(f"      主题: {u.theme} | 创建者: {u.creator_id}")
            print(f"      标签: {', '.join(u.tags[:3])}")
    except Exception as e:
        print(f"❌ 列出宇宙失败: {e}")

    # 示例 8: 查看市场统计
    print("\n" + "=" * 70)
    print("示例 8: 查看创作者市场统计")
    print("=" * 70)

    try:
        stats = client.get_marketplace_stats()
        print(f"✅ 市场统计数据:")
        print(f"   总资产数: {stats['total_listings']:,}")
        print(f"   总交易数: {stats['total_transactions']:,}")
        print(f"   总收入: ${stats['total_revenue']:,.2f}")
    except Exception as e:
        print(f"❌ 获取市场统计失败: {e}")

    # 示例 9: 列出治理提案
    print("\n" + "=" * 70)
    print("示例 9: 列出治理提案")
    print("=" * 70)

    try:
        proposals = client.list_proposals(limit=3)
        print(f"✅ 找到 {len(proposals)} 个提案:")
        for i, p in enumerate(proposals, 1):
            status_icons = {
                "active": "🟢",
                "passed": "✅",
                "rejected": "❌",
                "expired": "⏰"
            }
            status_icon = status_icons.get(p.status, "❓")
            print(f"   {i}. {status_icon} {p.title}")
            print(f"      类型: {p.proposal_type}")
            print(f"      状态: {p.status}")
            print(f"      创建者: {p.proposer_id}")
            print(f"      投票: ✅{p.votes_for} / ❌{p.votes_against} / 🤐{p.votes_abstain}")
    except Exception as e:
        print(f"❌ 列出提案失败: {e}")

    # 总结
    print("\n" + "=" * 70)
    print("🎉 示例运行完成!")
    print("=" * 70)
    print("\n下一步:")
    print("1. 查看 API 文档: http://localhost:8000/docs")
    print("2. 阅读 SDK 文档: docs/sdk/python/README.md")
    print("3. 尝试其他示例: examples/ 目录")


if __name__ == "__main__":
    main()
