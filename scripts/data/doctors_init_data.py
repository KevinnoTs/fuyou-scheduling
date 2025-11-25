"""
医生初始化数据
导出时间: 2025-11-23 02:58:02
包含 7 名医生数据

数据格式说明:
- specialties: JSON数组格式，自动避免引号嵌套问题
- avatar: 字符串或None值
- 状态注释: 显示医生当前在职状态
"""

import json
import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from app import create_app
from app.models import Doctor
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
            "specialties": ["妇科", "产科", "儿科"],
            "annual_leave_days": 15,
            "used_leave_days": 15,
            "avatar": "avatar_1_5b880dd0.jpg",
            "sequence": 10
        },  # 当前状态: ✓在职
        {
            "name": "李世珍",
            "gender": "女",
            "title": "医师",
            "status": "在职",
            "specialties": ["妇科", "产科", "儿科", "筛查"],
            "annual_leave_days": 10,
            "used_leave_days": 10,
            "avatar": "avatar_2_894bc1ac.jpg",
            "sequence": 20
        },  # 当前状态: ✓在职
        {
            "name": "李文娟",
            "gender": "女",
            "title": "主任医师",
            "status": "在职",
            "specialties": ["妇科", "产科", "儿科"],
            "annual_leave_days": 10,
            "used_leave_days": 10,
            "avatar": "avatar_3_ced0f306.jpg",
            "sequence": 30
        },  # 当前状态: ✓在职
        {
            "name": "吴春梅",
            "gender": "女",
            "title": "医师",
            "status": "在职",
            "specialties": ["妇科", "产科", "儿科"],
            "annual_leave_days": 15,
            "used_leave_days": 15,
            "avatar": None,
            "sequence": 40
        },  # 当前状态: ✓在职
        {
            "name": "曾慧尹",
            "gender": "女",
            "title": "医师",
            "status": "在职",
            "specialties": ["妇科", "产科", "儿科", "筛查"],
            "annual_leave_days": 10,
            "used_leave_days": 10,
            "avatar": "avatar_5_f061f3a7.jpg",
            "sequence": 50
        },  # 当前状态: ✓在职
        {
            "name": "汪金美",
            "gender": "女",
            "title": "医师",
            "status": "在职",
            "specialties": ["妇科", "产科", "儿科"],
            "annual_leave_days": 5,
            "used_leave_days": 5,
            "avatar": "avatar_6_ec197002.jpg",
            "sequence": 60
        },  # 当前状态: ✓在职
        {
            "name": "孙楠",
            "gender": "男",
            "title": "医师",
            "status": "离职",
            "specialties": ["妇科", "产科", "筛查"],
            "annual_leave_days": 0,
            "used_leave_days": 0,
            "avatar": None,
            "sequence": 70
        },  # 当前状态: ✗离职
    ]

    # 检查现有医生
    existing_doctors = [doc.name for doc in Doctor.query.all()]
    new_count = 0

    for doctor_data in doctors_data:
        if doctor_data["name"] not in existing_doctors:
            doctor = Doctor(
                name=doctor_data["name"],
                gender=doctor_data["gender"],
                title=doctor_data["title"],
                status=doctor_data["status"],
                specialties=doctor_data["specialties"],
                annual_leave_days=doctor_data["annual_leave_days"],
                used_leave_days=doctor_data["used_leave_days"],
                avatar=doctor_data["avatar"],
                sequence=doctor_data["sequence"]
            )
            db.session.add(doctor)
            new_count += 1

    db.session.commit()
    print(f"医生数据初始化完成，新增 {new_count} 名医生")

if __name__ == "__main__":
    # 创建Flask应用并初始化数据库上下文
    app = create_app()
    with app.app_context():
        init_doctors()