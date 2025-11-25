#!/bin/bash
# Fuyou Scheduling 环境安装脚本
# 使用方法: chmod +x INSTALL_ENVIRONMENT.sh && ./INSTALL_ENVIRONMENT.sh

set -e

echo "🚀 开始安装Fuyou排班系统所需环境..."

# 更新系统
echo "📦 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 安装基础工具
echo "🔧 安装基础工具..."
sudo apt install -y curl wget vim git unzip htop tree
sudo apt install -y build-essential pkg-config
sudo apt install -y net-tools lsof  # 包含netstat

# 安装Python环境
echo "🐍 安装Python环境..."
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y sqlite3 libsqlite3-dev

# 安装Web服务器
echo "🌐 安装Web服务器..."
sudo apt install -y nginx

# 安装图像处理库
echo "🖼️ 安装图像处理库..."
sudo apt install -y libjpeg-dev libpng-dev libfreetype6-dev

# 安装SSL和安全
echo "🔒 安装SSL和安全工具..."
sudo apt install -y libssl-dev libffi-dev
sudo apt install -y ufw

# 验证安装
echo "✅ 验证安装..."
echo "Python版本: $(python3 --version)"
echo "Nginx版本: $(nginx -v 2>&1)"
echo "Git版本: $(git --version)"
echo "SQLite版本: $(sqlite3 --version)"

echo ""
echo "🎉 基础环境安装完成！"
echo ""
echo "📋 下一步操作："
echo "1. 获取项目代码: git clone <repository-url>"
echo "2. 创建虚拟环境: python3 -m venv venv"
echo "3. 激活虚拟环境: source venv/bin/activate"
echo "4. 安装Python依赖: pip install -r requirements.txt"
echo "5. 配置和启动应用"
echo ""
echo "📚 Python包安装参考："
echo "pip install flask flask-sqlalchemy flask-login flask-wtf"
echo "pip install gunicorn python-dotenv"
echo "pip install Pillow"