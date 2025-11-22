# 妇幼排班管理系统

一个基于Flask的妇幼排班管理系统，支持医生信息管理、用户权限管理、排班安排和统计功能。

## 项目特色

### 🏥 医生管理
- 医生基本信息管理（姓名、性别、职称、在职状态）
- 多擅长方向选择（妇科、产科、儿科、筛查）
- 智能头像系统（支持自定义头像和性别默认头像）
- 医生关联用户系统

### 👥 用户权限管理
- **三级权限体系**：普通用户、管理员、超级管理员
- **细粒度权限控制**：
  - 管理员：可管理医生、排班、普通用户
  - 超级管理员：拥有所有权限，可管理管理员
  - 普通用户：只能查看信息，编辑个人资料

### 📅 排班功能
- 班次类型管理（白班、中班、值班、下夜班等）
- 工作量统计和工分计算
- 年假管理和统计

### 🔐 安全特性
- 用户登录/注册系统
- 密码加密存储
- 会话管理
- 操作权限验证

## 系统要求

- Python 3.8+
- 现代浏览器（Chrome、Firefox、Safari、Edge）

## 安装和运行

### 1. 确保Python已安装

首先检查Python是否已安装：
```bash
python --version
```
或者
```bash
python3 --version
```

如果没有安装Python，请从 https://www.python.org/downloads/ 下载安装。

### 2. 安装依赖

在项目目录中运行：
```bash
pip install -r requirements.txt
```
或者如果系统有多个Python版本：
```bash
python3 -m pip install -r requirements.txt
```

### 3. 运行系统

```bash
python run.py
```
或者
```bash
python3 run.py
```

### 4. 访问系统

打开浏览器访问：`http://localhost:5000`

## 常见问题

### 3. 数据库问题
如果遇到数据库问题，删除 instance/hospital.db 文件，重新启动应用会自动创建新的数据库。

## 项目结构

```
fuyou_scheduling/
├── app/                    # 应用核心代码
│   ├── __init__.py        # 应用初始化
│   ├── models.py          # 数据模型
│   ├── routes.py          # 主要路由
│   ├── auth_routes.py     # 认证路由
│   ├── extensions.py      # 扩展配置
│   ├── init_data.py       # 基础数据初始化
│   ├── templates/         # 模板文件
│   │   ├── layouts/      # 页面布局
│   │   ├── auth/         # 认证页面
│   │   ├── users/        # 用户管理
│   │   └── doctors/      # 医生管理
│   └── static/           # 静态文件
├── scripts/               # 脚本工具目录
│   ├── data/            # 数据相关脚本
│   │   ├── holidays_init_data.py  # 节假日初始化
│   │   ├── doctors_init_data.py   # 医生数据初始化
│   │   ├── users_init_data.py     # 用户数据初始化
│   │   └── export_data.py         # 数据导出（分别导出）
│   ├── maintenance/     # 维护脚本
│   │   ├── reset_database.py     # 数据库重置
│   │   └── reset_annual_leave.py # 年假重置
│   └── utils/           # 工具脚本
│       ├── check_syntax.py       # 语法检查
│       └── download_fonts.py     # 字体下载
├── instance/              # 数据库文件
├── logs/                 # 日志文件
├── run.py               # 启动文件
├── requirements.txt      # Python依赖
└── README.md            # 说明文档
```

### 脚本使用

项目包含完整的脚本工具集，用于数据管理和系统维护：

#### 数据管理
```bash
# 初始化节假日数据（优先级1）
python scripts/data/holidays_init_data.py

# 初始化医生数据（优先级2）
python scripts/data/doctors_init_data.py

# 初始化用户数据（优先级3，依赖医生数据）
python scripts/data/users_init_data.py

# 导出当前数据为分离的文件
python scripts/data/export_data.py
```

#### 系统维护
```bash
# 完全重置数据库
python scripts/maintenance/reset_database.py

# 重置年假（每年执行一次）
python scripts/maintenance/reset_annual_leave.py
```

详细说明请参考 [scripts/README.md](scripts/README.md)

## 默认账户

系统会自动创建一个默认管理员账户：
- 用户名：`admin`
- 密码：`admin123`

**重要**: 生产环境请立即修改默认密码！

## 主要功能

### 医生管理
- 添加/编辑/删除医生信息
- 设置医生擅长方向（可多选）
- 管理医生头像
- 查看医生统计数据

### 用户管理
- 用户注册/登录
- 权限管理
- 用户与医生关联

### 排班管理
- 班次类型配置
- 排班安排
- 工作量统计

### 年假管理
- 年假天数设置
- 已休年假统计
- 剩余年假计算

## 开发说明

### 数据库迁移
应用启动时会自动检测数据库结构并执行必要的迁移，包括：
- 添加新的表字段
- 设置默认值
- 数据完整性检查

### 权限系统
- 装饰器权限控制
- 前端权限验证
- API权限检查

## 技术架构

- **后端框架**: Flask + SQLAlchemy
- **前端框架**: Bootstrap 5 + Jinja2
- **数据库**: SQLite
- **认证**: Flask-Login
- **文件上传**: Pillow (头像处理)

## 开发说明

### 数据库迁移
应用启动时会自动检测数据库结构并执行必要的迁移，包括：
- 添加新的表字段
- 设置默认值
- 数据完整性检查

### 权限系统
- 装饰器权限控制
- 前端权限验证
- API权限检查

### 文件上传
- 头像上传处理
- 图片压缩和优化
- 文件类型和大小验证

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。