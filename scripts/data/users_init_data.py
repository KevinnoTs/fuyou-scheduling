#!/usr/bin/env python3
"""
用户初始化数据
自动生成于: 2025-11-21 21:20:58

包含用户表的完整数据
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import create_app
from app.models import User, Doctor
from app.extensions import db

def init_users():
    """初始化用户数据"""

    # 用户数据列表
    users_data = [
        {
            "username": "admin",
            "password_hash": "pbkdf2:sha256:600000$VMOUGMX4hE7T2vUO$16d09442c3c75e4d6fc2b1b584e513bf2395c03792f9bcf5e9c7de64523c453d",
            "full_name": "系统管理员",
            "is_admin": True,
            "is_super_admin": True,
            "associated_doctor_id": None,
            "is_active": True
        },
        {
            "username": "zhangsan",
            "password_hash": "pbkdf2:sha256:600000$aE3bB0N2h4uM8hJp$f3e583e8f2a2b1e6ac73df7b8d5c2a92f317ad32fe9e8c79a6d97381b6a5896b",
            "full_name": "冉佩入",
            "is_admin": True,
            "is_super_admin": False,
            "associated_doctor_id": 1,  # 关联医生: 冉佩入 (在职)
            "is_active": True
        },
        {
            "username": "lisi",
            "password_hash": "pbkdf2:sha256:600000$dF4cC1O3j5vN9kKq$4f593f9g3b3c2f7bd84ge9c9e6d3b93g428be34gf0a9d8b7e7e08492c7a6a7c",
            "full_name": "李世珍",
            "is_admin": True,
            "is_super_admin": False,
            "associated_doctor_id": 2,  # 关联医生: 李世珍 (在职)
            "is_active": True
        },
        {
            "username": "wangwu",
            "password_hash": "pbkdf2:sha256:600000$eG5dD2P4k6wO0lLr$5f604g0h4c4d3g8ce95hf0d0e7f4c04h539cf45hg1b0e9c8f8f19503d8b8b8d",
            "full_name": "李文娟",
            "is_admin": False,
            "is_super_admin": False,
            "associated_doctor_id": 3,  # 关联医生: 李文娟 (在职)
            "is_active": True
        },
        {
            "username": "zhaoliu",
            "password_hash": "pbkdf2:sha256:600000$fH6eE3Q5l7xP1mMs$6f705h1i5d5e4h9df06g1e1f8g5d15h640dg56hi2c1f0d9g9g20614e9c9c9e",
            "full_name": "汪金美",
            "is_admin": False,
            "is_super_admin": False,
            "associated_doctor_id": 4,  # 关联医生: 汪金美 (在职)
            "is_active": True
        }
    ]

    # 检查现有用户
    existing_users = [user.username for user in User.query.all()]
    new_count = 0

    for user_data in users_data:
        if user_data["username"] not in existing_users:
            user = User(
                username=user_data["username"],
                password_hash=user_data["password_hash"],
                full_name=user_data["full_name"],
                is_admin=user_data["is_admin"],
                is_super_admin=user_data["is_super_admin"],
                associated_doctor_id=user_data["associated_doctor_id"],
                is_active=user_data["is_active"]
            )

            # 查找关联的医生（必须是在职状态）
            if user_data.get("associated_doctor_id"):
                doctor = Doctor.query.get(user_data["associated_doctor_id"])
                if not doctor or doctor.status != "在职":
                    user.associated_doctor_id = None

            db.session.add(user)
            new_count += 1

    db.session.commit()
    print(f"用户数据初始化完成，新增 {new_count} 个用户")


if __name__ == "__main__":
    # 创建Flask应用并初始化数据库上下文
    app = create_app()
    with app.app_context():
        init_users()