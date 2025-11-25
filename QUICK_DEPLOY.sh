#!/bin/bash
# Fuyou Scheduling 快速部署脚本
# 使用方法：chmod +x QUICK_DEPLOY.sh && ./QUICK_DEPLOY.sh

set -e

echo "🚀 开始部署Fuyou排班系统..."

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then
    echo "请不要使用root用户运行此脚本"
    exit 1
fi

# 更新系统
echo "📦 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 安装基础软件
echo "🔧 安装基础软件..."
sudo apt install -y git python3 python3-pip python3-venv curl wget

# 配置Git
echo "📝 配置Git..."
read -p "请输入您的姓名: " name
read -p "请输入您的邮箱: " email
git config --global user.name "$name"
git config --global user.email "$email"

# 创建项目目录
echo "📁 创建项目目录..."
sudo mkdir -p /var/www
sudo chown $USER:$USER /var/www
cd /var/www

# 获取项目代码
echo "⬇️ 获取项目代码..."
echo "选择获取代码的方式："
echo "1. 从Git仓库克隆"
echo "2. 从本地文件上传"
read -p "请选择 (1/2): " choice

if [ "$choice" = "1" ]; then
    read -p "请输入Git仓库地址: " repo_url
    git clone "$repo_url" fuyou_scheduling
    cd fuyou_scheduling
else
    echo "请将项目文件压缩包上传到 /home/$USER/ 目录"
    echo "然后运行: tar -xzf fuyou_scheduling.tar.gz -C /var/www/"
    echo "并重命名为 fuyou_scheduling"
    exit 0
fi

# 创建虚拟环境
echo "🐍 创建Python虚拟环境..."
cd /var/www/fuyou_scheduling
python3 -m venv venv
source venv/bin/activate

# 安装依赖
echo "📚 安装项目依赖..."
pip install --upgrade pip
pip install flask flask-sqlalchemy flask-login flask-wtf werkzeug python-dotenv gunicorn

# 创建必要目录
echo "📂 创建必要目录..."
mkdir -p instance
mkdir -p static/uploads/avatars

# 创建环境文件
echo "⚙️ 创建环境配置..."
cat > .env << EOF
FLASK_ENV=production
FLASK_APP=run.py
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///instance/fuyou.db
EOF

chmod 600 .env

# 初始化数据库
echo "💾 初始化数据库..."
python -c "
from app import create_app
app = create_app()
with app.app_context():
    from app import init_data
    init_data.init_all_data()
    print('✅ 数据库初始化完成！')
"

# 测试应用
echo "🧪 测试应用..."
python -c "
from app import create_app
app = create_app()
print('✅ Flask应用创建成功！')
"

# 创建systemd服务
echo "🔧 创建系统服务..."
sudo cat > /etc/systemd/system/fuyou_scheduling.service << EOF
[Unit]
Description=Fuyou Scheduling System
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=/var/www/fuyou_scheduling
Environment=PATH=/var/www/fuyou_scheduling/venv/bin
ExecStart=/var/www/fuyou_scheduling/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
echo "🚀 启动服务..."
sudo systemctl daemon-reload
sudo systemctl start fuyou_scheduling
sudo systemctl enable fuyou_scheduling

# 检查服务状态
echo "📊 检查服务状态..."
sudo systemctl status fuyou_scheduling --no-pager

echo ""
echo "✅ 部署完成！"
echo "📝 重要信息："
echo "  项目路径: /var/www/fuyou_scheduling"
echo "  服务状态: sudo systemctl status fuyou_scheduling"
echo "  查看日志: sudo journalctl -u fuyou_scheduling -f"
echo "  重启服务: sudo systemctl restart fuyou_scheduling"
echo ""
echo "🌐 应用访问地址: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "📋 下一步："
echo "  1. 配置防火墙: sudo ufw allow 5000"
echo "  2. 考虑配置Nginx反向代理"
echo "  3. 设置SSL证书"