# export_doctors.py 修改说明

## 修改目标

将导出功能从只导出"在职"医生修改为导出"所有医生"（包括在职和离职）。

## 修改内容

### 1. 查询逻辑修改

**修改前**:
```python
# 获取所有在职医生
doctors = Doctor.query.filter_by(status='在职').order_by(Doctor.sequence).all()
```

**修改后**:
```python
# 获取所有医生（包括在职和离职）
doctors = Doctor.query.order_by(Doctor.sequence).all()
```

### 2. 统计信息增强

**新增功能**:
```python
# 统计在职和离职医生数量
active_count = len([d for d in doctors if d.status == '在职'])
inactive_count = len(doctors) - active_count
print(f"   - 在职医生: {active_count} 名")
print(f"   - 离职医生: {inactive_count} 名")
```

### 3. 用户关联逻辑优化

**修改前**:
```python
# 如果有关联的用户，也导出用户信息
if hasattr(doctor, 'associated_user') and doctor.associated_user:
```

**修改后**:
```python
# 如果有关联的用户且医生在职，也导出用户信息
if hasattr(doctor, 'associated_user') and doctor.associated_user and doctor.status == '在职':
```

### 4. 用户创建逻辑修改

**修改前**:
```python
# 查找对应的医生
doctor = Doctor.query.filter_by(name=user_data['doctor_name']).first()
```

**修改后**:
```python
# 查找对应的医生（必须是在职状态）
doctor = Doctor.query.filter_by(name=user_data['doctor_name'], status='在职').first()
```

### 5. 显示信息增强

**修改前**:
```python
print(f"   {i}. {doctor.name} - {doctor.title} - {specialties}{user_info}")
```

**修改后**:
```python
status_badge = "" if doctor.status == '在职' else ""
print(f"   {i}. {doctor.name} - {doctor.title} - {doctor.gender} - {doctor.status} - {specialties}{user_info} {status_badge}")
```

## 输出示例

修改后的导出输出示例：

```
👨‍⚕️ 导出医生数据...
   找到 7 名医生（包括在职和离职）
   - 在职医生: 5 名
   - 离职医生: 2 名
    导出完成！文件保存为: doctors_init_data.py
   📊 导出了 7 名医生数据
   👤 包含 3 个关联用户账户

📋 导出的医生列表:
   1. 张三 - 主任医师 - 女 - 在职 - 妇科、产科 (用户: zhangsan) 
   2. 李四 - 副主任医师 - 男 - 在职 - 儿科 (用户: lisi) 
   3. 王五 - 主治医师 - 女 - 在职 - 门诊、筛查 (用户: wangwu) 
   4. 赵六 - 住院医师 - 男 - 离职 - 急诊 
   5. 孙七 - 主任医师 - 女 - 在职 - 产科 
   6. 周八 - 主治医师 - 男 - 离职 - 妇科、筛查 
   7. 郑十 - 住院医师 - 女 - 在职 - 急诊、门诊 
```

## 生成的初始化代码特点

### 1. 包含所有医生状态
- 在职医生：保留所有信息，可正常使用
- 离职医生：保留历史数据，但状态为"离职"

### 2. 用户账户只关联在职医生
- 离职医生的用户账户不会被重新创建
- 避免离职医生重新获得系统访问权限

### 3. 状态注释
每个医生数据都有状态注释：
```python
{
    "name": "张三",
    "gender": "女",
    "title": "主任医师",
    "status": "在职",
    # ... 其他字段
},  # 当前状态: 在职
```

## 使用注意事项

1. **数据完整性**: 导出的数据包含完整的医生历史记录
2. **用户安全**: 只有在职医生的账户会被重新创建
3. **状态管理**: 离职医生的状态会被保留，便于数据分析
4. **恢复功能**: 可以完整恢复系统中的所有医生数据

## 测试建议

1. **验证导出**: 运行 `python export_doctors.py` 查看输出
2. **检查用户**: 确认只有在职医生有用户账户
3. **测试恢复**: 使用生成的数据测试数据库恢复功能
4. **状态确认**: 验证医生状态是否正确保留

## 优势

1. **数据完整性**: 不会丢失任何医生的历史数据
2. **安全性**: 自动过滤离职医生的用户账户
3. **可追溯性**: 保留医生的完整工作历史
4. **灵活性**: 支持医生状态的灵活管理

---

此修改确保了医生数据的完整导出，同时保持了系统的安全性和数据管理的灵活性。