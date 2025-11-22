# Scripts 目录说明

本目录包含了妇幼排班管理系统的所有脚本工具，按功能分类组织。

## 📁 目录结构

```
scripts/
├── data/                    # 数据相关脚本
│   ├── holidays_init_data.py    # 节假日数据初始化
│   ├── doctors_init_data.py     # 医生数据初始化
│   ├── users_init_data.py       # 用户数据初始化
│   └── export_data.py           # 数据导出工具（分别导出三个文件）
├── maintenance/            # 维护相关脚本
│   ├── reset_database.py       # 数据库重置工具
│   └── reset_annual_leave.py   # 年假重置工具
├── utils/                  # 工具类脚本
│   ├── check_syntax.py         # 语法检查工具
│   └── download_fonts.py       # 字体下载工具
└── README.md               # 本说明文件
```

## 🚀 使用方法

### 数据初始化脚本

#### 1. 医生和用户数据初始化
```bash
python scripts/data/doctors_init_data.py
```
- **用途：** 初始化医生数据和对应的用户账户
- **包含：** 冉佩入、李世珍、李文娟等真实医生数据
- **时机：** 数据库为空或需要重新导入医生数据时

#### 2. 节假日数据初始化
```bash
python scripts/data/holidays_init_data.py
```
- **用途：** 初始化2025年和2026年节假日数据
- **包含：** 法定节假日和调休安排
- **时机：** 数据库为空或需要更新节假日数据时

#### 3. 数据导出工具
```bash
python scripts/data/export_data.py
```
- **用途：** 导出当前数据库中的医生和用户数据
- **输出：** 生成可用于恢复的初始化脚本
- **时机：** 备份数据或迁移数据时

### 维护脚本

#### 1. 数据库重置
```bash
python scripts/maintenance/reset_database.py
```
- **用途：** 完全重置数据库到初始状态
- **包含：** 清空所有数据，重新初始化基础数据
- **时机：** 开发测试或数据损坏时
- **注意：** 会删除所有数据，请谨慎使用！

#### 2. 年假重置
```bash
python scripts/maintenance/reset_annual_leave.py
```
- **用途：** 重置所有医生的年假使用记录
- **时机：** 新年开始时（1月1日）
- **效果：** 将已使用年假天数重置为0

### 工具脚本

#### 1. 语法检查工具
```bash
python scripts/utils/check_syntax.py
```
- **用途：** 检查Python文件的语法错误
- **时机：** 开发过程中检查代码语法

#### 2. 字体下载工具
```bash
python scripts/utils/download_fonts.py
```
- **用途：** 下载霞鹜新晰黑字体文件
- **时机：** 首次部署或字体文件丢失时

## 📋 完整的数据恢复流程

如果需要完全恢复系统到初始状态：

```bash
# 1. 重置数据库（清除所有数据）
python scripts/maintenance/reset_database.py

# 2. 导入真实医生数据
python scripts/data/doctors_init_data.py

# 3. 导入用户数据（依赖医生数据）
python scripts/data/users_init_data.py

# 4. 初始化节假日数据（可选，通常自动完成）
python scripts/data/holidays_init_data.py
```

## ⚠️ 注意事项

1. **数据安全：** `reset_database.py` 会删除所有数据，请先备份重要数据
2. **执行顺序：** 建议按照上述顺序执行脚本，避免数据冲突
3. **路径依赖：** 所有脚本都设计为从项目根目录执行
4. **权限要求：** 确保对 `instance/` 目录有读写权限

## 🔄 常见使用场景

### 开发环境搭建
```bash
# 快速初始化开发环境
python scripts/maintenance/reset_database.py
python scripts/data/doctors_init_data.py
```

### 数据备份
```bash
# 导出当前数据作为备份
python scripts/data/export_data.py
```

### 年度维护
```bash
# 新年重置年假（每年1月1日执行）
python scripts/maintenance/reset_annual_leave.py
```

## 📞 支持

如果遇到问题，请检查：
1. Python环境是否正确配置
2. 是否在项目根目录执行脚本
3. 数据库文件权限是否正确
4. 相关依赖包是否已安装

---
*最后更新时间：2025-11-23*