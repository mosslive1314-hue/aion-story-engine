#!/usr/bin/env python3
"""
AION Story Engine API 测试脚本

测试 API 的所有端点是否正常工作
"""

import requests
import json
import time

# API 配置
API_BASE = "http://localhost:8000/api/v1"
API_KEY = "test_api_key"
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}


def test_endpoint(name, method, url, **kwargs):
    """测试单个端点"""
    try:
        print(f"\n{'='*60}")
        print(f"测试: {name}")
        print(f"方法: {method.upper()} {url}")
        print(f"{'='*60}")

        response = requests.request(
            method=method,
            url=f"{API_BASE}{url}",
            headers=HEADERS,
            **kwargs
        )

        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")

        if response.status_code == 200:
            print("✅ 成功")
            if response.headers.get('content-type', '').startswith('application/json'):
                print(f"响应数据:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            else:
                print(f"响应内容: {response.text}")
            return True
        else:
            print("❌ 失败")
            print(f"错误信息: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - 请确保 API 服务器正在运行")
        print("运行: python start_api.py --reload")
        return False
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False


def main():
    print("🌌 AION Story Engine API 测试")
    print("=" * 60)

    results = []

    # 测试健康检查
    results.append(test_endpoint("健康检查", "GET", "/../health"))

    # 测试根端点
    results.append(test_endpoint("根端点", "GET", "/../"))

    # 测试会话管理
    results.append(test_endpoint(
        "创建会话",
        "POST",
        "/sessions",
        json={"name": "测试故事", "owner_id": "user123"}
    ))

    results.append(test_endpoint("列出会话", "GET", "/sessions?skip=0&limit=100"))

    results.append(test_endpoint(
        "获取会话",
        "GET",
        "/sessions/session-1234"
    ))

    # 测试资产管理
    results.append(test_endpoint("列示资产", "GET", "/assets?skip=0&limit=100"))

    # 测试市场
    results.append(test_endpoint("获取市场统计", "GET", "/marketplace/stats"))

    results.append(test_endpoint("获取市场资产", "GET", "/marketplace/assets"))

    # 测试多元宇宙
    results.append(test_endpoint(
        "创建宇宙",
        "POST",
        "/universes",
        json={
            "name": "测试宇宙",
            "creator_id": "user123",
            "description": "这是一个测试宇宙",
            "physics_rules": {"gravity": 9.8},
            "theme": "sci-fi",
            "tags": ["test", "space"],
            "is_public": True
        }
    ))

    results.append(test_endpoint("列示宇宙", "GET", "/universes?skip=0&limit=100"))

    # 测试治理
    results.append(test_endpoint("列示提案", "GET", "/governance/proposals"))

    # 统计结果
    print("\n" + "=" * 60)
    print("📊 测试结果统计")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0

    print(f"总测试数: {total}")
    print(f"通过数: {passed}")
    print(f"失败数: {total - passed}")
    print(f"成功率: {success_rate:.1f}%")

    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")

    print("=" * 60)


if __name__ == "__main__":
    main()
