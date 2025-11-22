#!/usr/bin/env python3
"""
医生数据初始化脚本
用于在数据库清空后快速恢复医生数据
"""

import json
from app.models import Doctor, User
from app.extensions import db

def init_doctors():
    """初始化医生数据"""

    # 医生数据列表
    doctors_data = [
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
        },
        {
            "name": "李四",
            "gender": "男",
            "title": "副主任医师",
            "status": "在职",
            "specialties": "[\"儿科\"]",
            "annual_leave_days": 15,
            "used_leave_days": 2,
            "avatar": null,
            "sequence": 2,
            # "notes": "儿科专家"  # Doctor模型中没有notes字段
        },
        {
            "name": "王五",
            "gender": "女",
            "title": "主治医师",
            "status": "在职",
            "specialties": "[\"门诊\", \"筛查\"]",
            "annual_leave_days": 15,
            "used_leave_days": 0,
            "avatar": null,
            "sequence": 3,
            # "notes": "门诊和筛查工作"  # Doctor模型中没有notes字段
        },
        {
            "name": "赵六",
            "gender": "男",
            "title": "住院医师",
            "status": "在职",
            "specialties": "[\"急诊\"]",
            "annual_leave_days": 15,
            "used_leave_days": 1,
            "avatar": null,
            "sequence": 4,
            # "notes": "急诊科医生"  # Doctor模型中没有notes字段
        },
        {
            "name": "孙七",
            "gender": "女",
            "title": "主任医师",
            "status": "在职",
            "specialties": "[\"产科\"]",
            "annual_leave_days": 20,
            "used_leave_days": 0,
            "avatar": null,
            "sequence": 5,
            # "notes": "产科主任"  # Doctor模型中没有notes字段
        },
        {
            "name": "周八",
            "gender": "男",
            "title": "主治医师",
            "status": "在职",
            "specialties": "[\"妇科\", \"筛查\"]",
            "annual_leave_days": 15,
            "used_leave_days": 3,
            "avatar": null,
            "sequence": 6,
            # "notes": "妇科和筛查工作"  # Doctor模型中没有notes字段
        },
        {
            "name": "吴九",
            "gender": "女",
            "title": "副主任医师",
            "status": "在职",
            "specialties": "[\"儿科\", \"门诊\"]",
            "annual_leave_days": 15,
            "used_leave_days": 0,
            "avatar": null,
            "sequence": 7,
            # "notes": "儿科和门诊工作"  # Doctor模型中没有notes字段
        },
        {
            "name": "郑十",
            "gender": "男",
            "title": "住院医师",
            "status": "在职",
            "specialties": "[\"急诊\", \"门诊\"]",
            "annual_leave_days": 15,
            "used_leave_days": 0,
            "avatar": null,
            "sequence": 8,
            # "notes": "急诊和门诊轮转"  # Doctor模型中没有notes字段
        }
    ]

    # 检查现有医生
    existing_doctors = [doc.name for doc in Doctor.query.all()]
    new_count = 0

    for doctor_data in doctors_data:
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
                # notes=doctor_data.get('notes')  # Doctor模型中没有notes字段
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
        'zhangsan': {
            'username': 'zhangsan',
            'password': 'zhangsan123',
            'full_name': '张三',
            'is_admin': True,
            'is_super_admin': False,
            'doctor_name': '张三'
        },
        'lisi': {
            'username': 'lisi',
            'password': 'lisi123',
            'full_name': '李四',
            'is_admin': True,
            'is_super_admin': False,
            'doctor_name': '李四'
        },
        'wangwu': {
            'username': 'wangwu',
            'password': 'wangwu123',
            'full_name': '王五',
            'is_admin': False,
            'is_super_admin': False,
            'doctor_name': '王五'
        },
        'admin': {
            'username': 'admin',
            'password': 'admin123',
            'full_name': '系统管理员',
            'is_admin': True,
            'is_super_admin': True,
            'doctor_name': None
        }
    }

    for username, user_data in users_data.items():
        # 检查用户是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"用户 {username} 已存在，跳过创建")
            continue

        # 查找对应的医生
        associated_doctor_id = None
        if user_data['doctor_name']:
            doctor = Doctor.query.filter_by(name=user_data['doctor_name']).first()
            if doctor:
                associated_doctor_id = doctor.id
            else:
                print(f"找不到医生 {user_data['doctor_name']}，跳过用户创建")
                continue

        # 创建用户
        user = User(
            username=user_data['username'],
            full_name=user_data['full_name'],
            is_admin=user_data['is_admin'],
            is_super_admin=user_data['is_super_admin'],
            associated_doctor_id=associated_doctor_id
        )
        user.set_password(user_data['password'])
        db.session.add(user)

    db.session.commit()
    print(f"用户账户创建完成")

def update_existing_doctors():
    """更新现有医生的数据（用于数据恢复）"""

    # 更新数据
    updates = [
        {
            'name': '张三',
            'specialties': ["妇科", "产科"],
            'annual_leave_days': 18,
            'sequence': 1
        },
        {
            'name': '李四',
            'specialties': ["儿科"],
            'annual_leave_days': 15,
            'sequence': 2
        },
        {
            'name': '王五',
            'specialties': ["门诊", "筛查"],
            'annual_leave_days': 15,
            'sequence': 3
        }
    ]

    updated_count = 0
    for update in updates:
        doctor = Doctor.query.filter_by(name=update['name']).first()
        if doctor:
            specialties_json = json.dumps(update['specialties'], ensure_ascii=False)
            doctor.specialties = specialties_json
            doctor.annual_leave_days = update['annual_leave_days']
            doctor.sequence = update['sequence']
            updated_count += 1

    db.session.commit()
    print(f"更新了 {updated_count} 名医生的数据")

# 备用函数：创建默认医生数据（如果没有现有数据）
def create_default_doctors():
    """创建默认医生数据（确保系统至少有基本数据）"""

    existing_count = Doctor.query.count()
    if existing_count > 0:
        print(f"数据库中已有 {existing_count} 名医生，跳过默认数据创建")
        return

    print("创建默认医生数据...")
    init_doctors()

if __name__ == '__main__':
    print("👨‍⚕️ 医生数据初始化")
    print("=" * 30)

    # 初始化医生数据
    init_doctors()

    print("\n 医生数据初始化完成！")
    print("\n📝 默认用户账户:")
    print("- admin/admin123 (超级管理员)")
    print("- zhangsan/zhangsan123 (张三，管理员)")
    print("- lisi/lisi123 (李四，管理员)")
    print("- wangwu/wangwu123 (王五，普通用户)")