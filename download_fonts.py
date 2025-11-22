#!/usr/bin/env python3
"""
霞鹜新晰黑字体下载脚本
用于快速下载字体文件到项目目录
"""

import os
import urllib.request
import sys
from pathlib import Path

def download_file(url, filename):
    """下载文件"""
    try:
        print(f"正在下载: {filename}")
        urllib.request.urlretrieve(url, filename)
        print(f" 下载完成: {filename}")
        return True
    except Exception as e:
        print(f" 下载失败 {filename}: {str(e)}")
        return False

def main():
    """主函数"""
    print("🏥 妇幼排班管理系统 - 字体下载工具")
    print("=" * 50)
    print("正在下载霞鹜新晰黑字体...")
    print()

    # 字体文件目录
    fonts_dir = Path("static/fonts")
    fonts_dir.mkdir(parents=True, exist_ok=True)

    # 字体文件下载链接
    fonts = [
        {
            "name": "LXGWWenKai-Regular.ttf",
            "url": "https://cdn.jsdelivr.net/gh/lxgw/LxgwNeoXiHei/dist/LXGWWenKai-Regular.ttf",
            "description": "霞鹜新晰黑常规字体"
        },
        {
            "name": "LXGWWenKai-Bold.ttf",
            "url": "https://cdn.jsdelivr.net/gh/lxgw/LxgwNeoXiHei/dist/LXGWWenKai-Bold.ttf",
            "description": "霞鹜新晰黑粗体字体"
        }
    ]

    # 检查字体文件是否已存在
    existing_fonts = []
    missing_fonts = []

    for font in fonts:
        font_path = fonts_dir / font["name"]
        if font_path.exists():
            existing_fonts.append(font["name"])
            print(f"⚠️  字体已存在: {font['name']}")
        else:
            missing_fonts.append(font)

    if existing_fonts and not missing_fonts:
        print()
        print(" 所有字体文件已存在，无需下载")
        return

    if existing_fonts:
        print()
        print("是否覆盖已存在的字体文件？")
        choice = input("覆盖下载？(y/N): ").strip().lower()
        if choice != 'y':
            print("跳过已存在的字体文件")
            # 只下载缺失的字体
            fonts = missing_fonts

    print()
    print("开始下载字体文件...")
    print()

    # 下载字体文件
    success_count = 0
    for font in fonts:
        font_path = fonts_dir / font["name"]
        print(f"📄 {font['description']}")

        if download_file(font["url"], font_path):
            success_count += 1
        print()

    # 检查下载结果
    print("=" * 50)
    if success_count == len(fonts):
        print(f"🎉 成功下载 {success_count} 个字体文件！")
        print()
        print("字体文件已保存到:")
        print(f"  - {fonts_dir}/LXGWWenKai-Regular.ttf")
        print(f"  - {fonts_dir}/LXGWWenKai-Bold.ttf")
        print()
        print("现在可以重启应用，字体将自动生效。")
    else:
        print(f"⚠️  下载完成，成功 {success_count}/{len(fonts)} 个文件")
        print()
        print("请检查网络连接或手动下载字体文件。")
        print("手动下载地址: https://github.com/lxgw/LxgwNeoXiHei")

def check_fonts_exist():
    """检查字体文件是否存在"""
    fonts_dir = Path("static/fonts")
    regular_font = fonts_dir / "LXGWWenKai-Regular.ttf"
    bold_font = fonts_dir / "LXGWWenKai-Bold.ttf"

    return regular_font.exists() and bold_font.exists()

if __name__ == "__main__":
    # 检查字体是否已存在
    if check_fonts_exist():
        print("🔍 检查到字体文件已存在")
        choice = input("是否重新下载？(y/N): ").strip().lower()
        if choice != 'y':
            print("字体文件已就绪，无需下载。")
            sys.exit(0)

    main()