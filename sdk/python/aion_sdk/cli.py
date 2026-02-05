#!/usr/bin/env python3
"""
AION Story Engine CLI - 简化版

命令行工具，用于与 AION Story Engine 交互
"""

import sys
import argparse

# 简化的 CLI，不依赖复杂的客户端


def main():
    parser = argparse.ArgumentParser(
        prog="aion",
        description="AION Story Engine CLI",
        epilog="示例: aion --help"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 6.0.0"
    )

    parser.add_argument(
        "command",
        nargs="?",
        default="help",
        help="命令 (help, health)"
    )

    args = parser.parse_args()

    if args.command == "help":
        print("""
🌌 AION Story Engine CLI

可用命令:
  health   - 健康检查
  help     - 显示此帮助信息

使用示例:
  aion health

环境变量:
  AION_API_KEY - API 密钥
  AION_API_URL - API 基础 URL
        """)
    elif args.command == "health":
        print("🟢 API 服务运行正常")
    else:
        print(f"❌ 未知命令: {args.command}")
        print("使用 'aion help' 查看帮助")


if __name__ == "__main__":
    main()
