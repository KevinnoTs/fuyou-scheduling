#!/usr/bin/env python3
"""
医生数据初始化脚本
自动生成于: 2025-11-21 19:22:58
"""

from datetime import datetime
from app.models import Doctor, User
from app.extensions import db

def init_doctors():
    """初始化医生数据"""

    # 医生数据列表
    doctors_data = [
        {
        "name": "冉佩入",
        "gender": "女",
        "title": "医师",
        "status": "在职",
        "specialties": "[\"妇科\", \"产科\", \"儿科\"]",
        "annual_leave_days": 15,
        "used_leave_days": 15,
        "avatar": null,
        "sequence": 10
},  # 当前状态: 在职
        {
        "name": "李世珍",
        "gender": "女",
        "title": "医师",
        "status": "在职",
        "specialties": "[\"妇科\", \"产科\", \"儿科\", \"筛查\"]",
        "annual_leave_days": 10,
        "used_leave_days": 10,
        "avatar": null,
        "sequence": 20
},  # 当前状态: 在职
        {
        "name": "李文娟",
        "gender": "女",
        "title": "主任医师",
        "status": "在职",
        "specialties": "[\"妇科\", \"产科\", \"儿科\"]",
        "annual_leave_days": 10,
        "used_leave_days": 0,
        "avatar": null,
        "sequence": 30
},  # 当前状态: 在职
        {
        "name": "吴春梅",
        "gender": "女",
        "title": "医师",
        "status": "在职",
        "specialties": "[\"妇科\", \"产科\", \"儿科\"]",
        "annual_leave_days": 15,
        "used_leave_days": 15,
        "avatar": null,
        "sequence": 40
},  # 当前状态: 在职
        {
        "name": "曾慧尹",
        "gender": "女",
        "title": "医师",
        "status": "在职",
        "specialties": "[\"妇科\", \"产科\", \"儿科\", \"筛查\"]",
        "annual_leave_days": 10,
        "used_leave_days": 10,
        "avatar": null,
        "sequence": 50
},  # 当前状态: 在职
        {
        "name": "汪金美",
        "gender": "女",
        "title": "医师",
        "status": "在职",
        "specialties": "[\"妇科\", \"产科\", \"儿科\"]",
        "annual_leave_days": 5,
        "used_leave_days": 5,
        "avatar": null,
        "sequence": 60
},  # 当前状态: 在职
        {
        "name": "孙楠",
        "gender": "男",
        "title": "医师",
        "status": "离职",
        "specialties": "[\"妇科\", \"产科\", \"筛查\"]",
        "annual_leave_days": 15,
        "used_leave_days": 0,
        "avatar": null,
        "sequence": 70
},  # 当前状态: 离职
    ]

    # 检查现有医生
    existing_doctors = [doc.name for doc in Doctor.query.all()]
    new_count = 0

    for i, doctor_data in enumerate(doctors_data):
        if doctor_data['name'] not in existing_doctors:
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
            )
            db.session.add(doctor)
            new_count += 1

    db.session.commit()
    print(f"医生数据初始化完成，新增 {new_count} 名医生")

    # 创建关联用户
    create_associated_users()

def create_associated_users():
    """为医生创建关联的用户账户"""

    # 用户数据 (username: password)
    users_data = {
    }

    for username, user_data in users_data.items():
        # 检查用户是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"用户 {username} 已存在，跳过创建")
            continue

        # 查找对应的医生（必须是在职状态）
        doctor = Doctor.query.filter_by(name=user_data['doctor_name'], status='在职').first()
        if not doctor:
            print(f"找不到在职医生 {user_data['doctor_name']}，跳过用户创建")
            continue

        # 创建用户
        user = User(
            username=user_data['username'],
            full_name=user_data['full_name'],
            is_admin=user_data['is_admin'],
            is_super_admin=user_data['is_super_admin'],
            associated_doctor_id=doctor.id
        )
        user.set_password(user_data['password'])
        db.session.add(user)

    db.session.commit()
    print(f"用户账户创建完成")