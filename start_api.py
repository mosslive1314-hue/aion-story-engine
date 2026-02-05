#!/usr/bin/env python3
"""
AION Story Engine API 服务器启动脚本

用法:
    python start_api.py [--port PORT] [--host HOST] [--reload]

示例:
    python start_api.py --port 8000 --host 0.0.0.0
    python start_api.py --reload  # 开发模式，自动重载
"""

import argparse
import sys
import uvicorn

# 添加项目根目录到 Python 路径
sys.path.insert(0, '/c/Users/maiyi/Desktop/story')

from aion_engine.api.fastapi_app import app


def main():
    parser = argparse.ArgumentParser(
        description="AION Story Engine API 服务器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --port 8000 --host 0.0.0.0
  %(prog)s --reload  # 开发模式
        """
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="服务器端口 (默认: 8000)"
    )

    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="服务器主机 (默认: 127.0.0.1)"
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="启用自动重载 (开发模式)"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="日志级别 (默认: info)"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🌌 AION Story Engine API Server")
    print("=" * 60)
    print(f"🚀 服务器启动中...")
    print(f"📡 地址: http://{args.host}:{args.port}")
    print(f"📚 API 文档: http://{args.host}:{args.port}/docs")
    print(f"📖 ReDoc: http://{args.host}:{args.port}/redoc")
    print(f"❤️  健康检查: http://{args.host}:{args.port}/health")
    print("=" * 60)
    print()

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    main()
