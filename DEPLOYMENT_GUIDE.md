# Ubuntu服务器部署指南 - 从零开始

## 第一阶段：系统基础设置

### 1. 更新系统包
```bash
# 更新包列表
sudo apt update

# 升级已安装的包
sudo apt upgrade -y

# 安装常用工具
sudo apt install -y curl wget vim git unzip htop
```

### 2. 安装Git
```bash
# 安装Git
sudo apt install -y git

# 验证Git安装
git --version

# 配置Git用户信息（替换为您的信息）
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. 创建项目目录
```bash
# 创建项目主目录
sudo mkdir -p /var/www
sudo chown $USER:$USER /var/www

# 创建项目目录
mkdir -p /var/www/fuyou_scheduling
cd /var/www/fuyou_scheduling
```

## 第二阶段：获取项目代码

### 选项A：如果您使用GitHub/GitLab等远程仓库

```bash
# 克隆您的仓库（替换为您的实际仓库地址）
git clone https://github.com/yourusername/fuyou-scheduling.git .

# 或者如果是私有仓库
git clone https://yourusername:yourtoken@github.com/yourusername/fuyou-scheduling.git .
```

### 选项B：如果您没有远程仓库，手动上传

```bash
# 在本地打包项目
cd /d/Python/claude/fuyou_scheduling
tar -czf fuyou_scheduling.tar.gz --exclude='.git' --exclude='__pycache__' --exclude='instance' --exclude='*.pyc' .

# 上传到服务器（使用scp）
scp fuyou_scheduling.tar.gz user@server:/var/www/fuyou_scheduling/

# 在服务器上解压
cd /var/www/fuyou_scheduling
tar -xzf fuyou_scheduling.tar.gz
rm fuyou_scheduling.tar.gz
```

## 第三阶段：安装Python环境

### 1. 安装Python和pip
```bash
# Ubuntu 20.04+ 通常自带Python 3.8+
sudo apt install -y python3 python3-pip python3-venv

# 验证安装
python3 --version
pip3 --version
```

### 2. 创建虚拟环境
```bash
# 创建虚拟环境
cd /var/www/fuyou_scheduling
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 验证虚拟环境（应该看到 (venv) 前缀）
which python  # 应该指向 /var/www/fuyou_scheduling/venv/bin/python
```

## 第四阶段：安装项目依赖

### 1. 安装系统依赖
```bash
# 安装必要的系统包
sudo apt install -y python3-dev build-essential libssl-dev libffi-dev

# 安装SQLite开发包（如果需要）
sudo apt install -y sqlite3 libsqlite3-dev
```

### 2. 升级pip并安装项目依赖
```bash
# 激活虚拟环境（如果还没激活）
source /var/www/fuyou_scheduling/venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装项目依赖（如果有requirements.txt）
pip install -r requirements.txt

# 如果没有requirements.txt，手动安装Flask等
pip install flask flask-sqlalchemy flask-login flask-wtf werkzeug python-dotenv
```

### 3. 创建requirements.txt（推荐）
```bash
# 在项目根目录创建requirements.txt
cat > requirements.txt << EOF
Flask==2.3.2
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.2
Flask-WTF==1.1.1
Werkzeug==2.3.6
python-dotenv==1.0.0
Jinja2==3.1.2
itsdangerous==2.1.2
MarkupSafe==2.1.2
gunicorn==20.1.0
EOF

# 安装依赖
pip install -r requirements.txt
```

## 第五阶段：配置应用

### 1. 创建必要的目录
```bash
# 创建instance目录（用于数据库）
mkdir -p instance
mkdir -p static/uploads/avatars

# 设置权限
chmod 755 instance static/uploads static/uploads/avatars
```

### 2. 创建环境配置文件
```bash
# 创建.env文件
cat > .env << EOF
FLASK_ENV=production
FLASK_APP=run.py
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///instance/fuyou.db
EOF

# 设置文件权限
chmod 600 .env
```

### 3. 测试应用启动
```bash
# 激活虚拟环境
source /var/www/fuyou_scheduling/venv/bin/activate

# 初始化数据库
python -c "
from app import create_app
app = create_app()
with app.app_context():
    from app import init_data
    init_data.init_all_data()
    print('数据库初始化完成！')
"

# 测试Flask应用
python -c "
from app import create_app
app = create_app()
print('Flask应用创建成功！')
print('应用配置：')
print(f'  数据库: {app.config[\"SQLALCHEMY_DATABASE_URI\"]}')
print(f'  密钥: {app.config[\"SECRET_KEY\"][:10]}...')
"
```

## 第六阶段：配置Web服务器

### 选项A：使用Gunicorn + Nginx（推荐）

#### 1. 安装和配置Gunicorn
```bash
# 安装Gunicorn
pip install gunicorn

# 创建Gunicorn配置文件
cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
daemon = False
user = "www-data"
group = "www-data"
tmp_upload_dir = None
logfile = "/var/log/gunicorn/fuyou_scheduling.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
EOF

# 创建日志目录
sudo mkdir -p /var/log/gunicorn
sudo chown www-data:www-data /var/log/gunicorn
```

#### 2. 安装和配置Nginx
```bash
# 安装Nginx
sudo apt install -y nginx

# 创建Nginx站点配置
sudo cat > /etc/nginx/sites-available/fuyou_scheduling << EOF
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名或IP

    # 静态文件
    location /static {
        alias /var/www/fuyou_scheduling/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 上传文件
    location /static/uploads {
        alias /var/www/fuyou_scheduling/static/uploads;
        expires 1y;
        add_header Cache-Control "public";
    }

    # 主应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
EOF

# 启用站点
sudo ln -s /etc/nginx/sites-available/fuyou_scheduling /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # 删除默认站点

# 测试Nginx配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

#### 3. 创建systemd服务
```bash
# 创建systemd服务文件
sudo cat > /etc/systemd/system/fuyou_scheduling.service << EOF
[Unit]
Description=Fuyou Scheduling System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/fuyou_scheduling
Environment=PATH=/var/www/fuyou_scheduling/venv/bin
ExecStart=/var/www/fuyou_scheduling/venv/bin/gunicorn -c gunicorn.conf.py run:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 设置文件权限
sudo chown -R www-data:www-data /var/www/fuyou_scheduling

# 启动并启用服务
sudo systemctl daemon-reload
sudo systemctl start fuyou_scheduling
sudo systemctl enable fuyou_scheduling

# 检查服务状态
sudo systemctl status fuyou_scheduling
```

### 选项B：仅使用Flask开发服务器（测试用）

```bash
# 仅用于测试，不建议生产环境使用
cd /var/www/fuyou_scheduling
source venv/bin/activate

# 后台运行Flask应用
nohup python run.py > app.log 2>&1 &

# 或者使用screen/tmux
screen -S fuyou_app
source venv/bin/activate
python run.py
# 按 Ctrl+A 然后按 D 分离会话
```

## 第七阶段：防火墙和安全配置

### 1. 配置防火墙
```bash
# 安装ufw（如果没有）
sudo apt install -y ufw

# 配置防火墙规则
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp  # 如果使用HTTPS

# 启用防火墙
sudo ufw enable

# 检查状态
sudo ufw status
```

### 2. 安全配置
```bash
# 禁用root SSH登录（推荐）
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# 修改SSH端口（可选）
# sudo sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config

# 重启SSH服务
sudo systemctl restart ssh

# 创建备份用户
sudo adduser backup
sudo usermod -aG sudo backup
```

## 第八阶段：监控和维护

### 1. 创建维护脚本
```bash
# 创建备份脚本
sudo cat > /usr/local/bin/backup_fuyou.sh << EOF
#!/bin/bash
BACKUP_DIR="/var/backups/fuyou_scheduling"
DATE=\$(date +%Y%m%d_%H%M%S)

mkdir -p \$BACKUP_DIR

# 备份数据库
cp /var/www/fuyou_scheduling/instance/fuyou.db \$BACKUP_DIR/fuyou_\$DATE.db

# 备份上传文件
tar -czf \$BACKUP_DIR/uploads_\$DATE.tar.gz -C /var/www/fuyou_scheduling static/uploads/

# 删除7天前的备份
find \$BACKUP_DIR -name "*.db" -mtime +7 -delete
find \$BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "备份完成: \$DATE"
EOF

sudo chmod +x /usr/local/bin/backup_fuyou.sh

# 添加到cron（每天凌晨2点备份）
echo "0 2 * * * /usr/local/bin/backup_fuyou.sh" | sudo crontab -
```

### 2. 创建监控脚本
```bash
# 创建健康检查脚本
sudo cat > /usr/local/bin/check_fuyou.sh << EOF
#!/bin/bash
# 检查应用是否运行
if ! systemctl is-active --quiet fuyou_scheduling; then
    echo "Fuyou服务未运行，正在重启..."
    sudo systemctl restart fuyou_scheduling
    echo "服务已重启"
fi

# 检查端口是否监听
if ! netstat -tlnp | grep :8000 > /dev/null; then
    echo "端口8000未监听，正在重启服务..."
    sudo systemctl restart fuyou_scheduling
fi
EOF

sudo chmod +x /usr/local/bin/check_fuyou.sh

# 每5分钟检查一次
echo "*/5 * * * * /usr/local/bin/check_fuyou.sh" | sudo crontab -
```

## 第九阶段：SSL证书配置（可选但推荐）

### 1. 使用Let's Encrypt免费SSL
```bash
# 安装certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取SSL证书（替换为您的域名）
sudo certbot --nginx -d your-domain.com

# 自动续期
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

## 故障排除

### 常见问题

1. **权限问题**
   ```bash
   sudo chown -R www-data:www-data /var/www/fuyou_scheduling
   sudo chmod -R 755 /var/www/fuyou_scheduling
   ```

2. **端口占用**
   ```bash
   sudo netstat -tlnp | grep :8000
   sudo kill -9 <PID>
   ```

3. **服务状态检查**
   ```bash
   sudo systemctl status fuyou_scheduling
   sudo journalctl -u fuyou_scheduling -f
   ```

4. **日志查看**
   ```bash
   tail -f /var/log/gunicorn/fuyou_scheduling.log
   tail -f /var/log/nginx/error.log
   ```

完成！您的Fuyou排班系统现在应该在Ubuntu服务器上正常运行了。