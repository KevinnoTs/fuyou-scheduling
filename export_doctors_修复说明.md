# export_doctors.py 修复说明

## 问题描述

运行 `python export_doctors.py` 时出现错误：
```
AttributeError: 'Doctor' object has no attribute 'notes'
```

## 问题原因

代码尝试访问 `Doctor` 模型的 `notes` 字段，但实际的数据模型中并没有这个字段。

## 修复内容

### 1. 修复 export_doctors.py

**文件**: `export_doctors.py:57`

**修复前**:
```python
'notes': doctor.notes
```

**修复后**:
```python
'notes': None  # Doctor模型中没有notes字段
```

**文件**: `export_doctors.py:97`

**修复前**:
```python
init_code.append('                notes=doctor_data.get(\'notes\')')
```

**修复后**:
```python
# init_code.append('                notes=doctor_data.get(\'notes\')')  # Doctor模型中没有notes字段
```

### 2. 修复 doctors_init_data.py

移除了所有医生数据中的 `notes` 字段：

**修复前**:
```python
{
    "name": "张三",
    "gender": "女",
    "title": "主任医师",
    "status": "在职",
    "specialties": "[\"妇科\", \"产科\"]",
    "annual_leave_days": 15,
    "used_leave_days": 0,
    "avatar": null,
    "sequence": 1,
    "notes": "资深妇科专家"
}
```

**修复后**:
```python
{
    "name": "张三",
    "gender": "女",
    "title": "主任医师",
    "status": "在职",
    "specialties": "[\"妇科\", \"产科\"]",
    "annual_leave_days": 15,
    "used_leave_days": 0,
    "avatar": null,
    "sequence": 1
    # "notes": "资深妇科专家"  # Doctor模型中没有notes字段
}
```

**修复前**:
```python
doctor = Doctor(
    name=doctor_data['name'],
    gender=doctor_data['gender'],
    title=doctor_data['title'],
    status=doctor_data['status'],
    specialties=doctor_data['specialties'],
    annual_leave_days=doctor_data['annual_leave_days'],
    used_leave_days=doctor_data['used_leave_days'],
    avatar=doctor_data['avatar'],
    sequence=doctor_data['sequence'],
    notes=doctor_data.get('notes')
)
```

**修复后**:
```python
doctor = Doctor(
    name=doctor_data['name'],
    gender=doctor_data['gender'],
    title=doctor_data['title'],
    status=doctor_data['status'],
    specialties=doctor_data['specialties'],
    annual_leave_days=doctor_data['annual_leave_days'],
    used_leave_days=doctor_data['used_leave_days'],
    avatar=doctor_data['avatar'],
    sequence=doctor_data['sequence']
    # notes=doctor_data.get('notes')  # Doctor模型中没有notes字段
)
```

## Doctor 模型实际字段

根据 `app/models.py` 中的定义，`Doctor` 模型包含以下字段：

```python
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(2), nullable=False)      # 性别: 男/女
    title = db.Column(db.String(20), default='打字员')     # 职称
    status = db.Column(db.String(10), default='在职')      # 在职状态: 在职/离职
    specialties = db.Column(db.Text)                      # 擅长方向，JSON格式
    annual_leave_days = db.Column(db.Integer, default=0)  # 年假天数
    used_leave_days = db.Column(db.Integer, default=0)   # 已用年假
    sequence = db.Column(db.Integer, default=999)        # 排序序号
    avatar = db.Column(db.String(255))                   # 头像文件路径
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

## 测试验证

创建了测试脚本 `test_export_fix.py` 来验证修复是否成功：

```bash
python test_export_fix.py
```

## 使用说明

修复后，可以正常运行导出功能：

```bash
python export_doctors.py
```

这将会：
1. 读取数据库中的所有在职医生
2. 生成 `doctors_init_data.py` 文件
3. 包含医生的完整信息和关联用户
4. 不再包含 `notes` 字段

## 注意事项

1. **向后兼容**: 如果之前的医生初始化数据包含 `notes` 字段，新的初始化代码会忽略这个字段
2. **数据完整性**: 移除 `notes` 字段不会影响其他功能
3. **扩展性**: 如果将来需要添加 `notes` 字段，需要同时修改数据模型和导出代码

## 相关文件

- `export_doctors.py` - 已修复的导出脚本
- `app/doctors_init_data.py` - 已修复的初始化数据
- `test_export_fix.py` - 测试脚本
- `app/models.py` - 数据模型定义