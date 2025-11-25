"""
用户初始化数据
导出时间: 2025-11-23 02:58:02
包含 8 个用户数据

数据格式说明:
- password_hash: 哈希密码，保持原始格式
- associated_doctor_id: 关联医生ID或None
- 医生关联注释: 显示关联医生的姓名和状态
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
            "password_hash": "scrypt:32768:8:1$rJ4IlMlaOjBqrJMR$6b706f8d6d0996a423428b8f2e79e4ef016f9ff8111097d13c8d8b5173b1218dbf9dde8fc327ec5cdcdaa63dcc47251483516a57af211fefe84cf17459a050d2",
            "full_name": "系统管理员",
            "is_admin": true,
            "is_super_admin": true,
            "associated_doctor_id": None,
            "is_active": true
        },
        {
            "username": "kevinnots",
            "password_hash": "scrypt:32768:8:1$UNuBBQiQ5RCBqGf6$ded8cd6855190147ed3aa85f092908d0bb626615df58a04ba7f10aaabb693c97a57064bd2fd3ce5295232e370b743ece50ab6ded09b44fdcaf855739a10f207e",
            "full_name": "高启宸",
            "is_admin": true,
            "is_super_admin": true,
            "associated_doctor_id": None,
            "is_active": true
        },
        {
            "username": "liwenjuan",
            "password_hash": "scrypt:32768:8:1$Kl0MZOchxJ9kXjcq$eddbd0740d6b1b82882543a77ef022c3a37aa5d1f537f361518c6c9a5406797d475ef4f0bcac8bdcab8f36fef82973a4d030d7fa3ff7ac6237ac299bec47e8e3",
            "full_name": "李文娟",
            "is_admin": true,
            "is_super_admin": false,
            "associated_doctor_id": 3,
            "is_active": true
        },  # 关联医生: 李文娟 (在职)
        {
            "username": "ranpeiru",
            "password_hash": "scrypt:32768:8:1$Rs0dSkZmhyYJDnp8$54b9b3e1ed34a860c2d9821e4596de393202a73d3978df7c7cd2c68dd15c043824c8b616f4d566faf127751ff7b6d3c95c476054e6305db469b3bb1e0d1790c9",
            "full_name": "冉佩入",
            "is_admin": false,
            "is_super_admin": false,
            "associated_doctor_id": 1,
            "is_active": true
        },  # 关联医生: 冉佩入 (在职)
        {
            "username": "lishizhen",
            "password_hash": "scrypt:32768:8:1$Jakz38TtGISDyMQy$a00dc873f3899d9b999d9e1d57ba8c77aab936a4992b853d3841e899dd11c08352fc40f980b2ecb241b0cb2fb3940dc52bf9fc05f9b5911f275f02d93d9b89b6",
            "full_name": "李世珍",
            "is_admin": false,
            "is_super_admin": false,
            "associated_doctor_id": 2,
            "is_active": true
        },  # 关联医生: 李世珍 (在职)
        {
            "username": "wuchunmei",
            "password_hash": "scrypt:32768:8:1$DjPc8VKKc9jQbaO2$eb5f1b9024a0d34b5a43d96d82bfb4b742e022ca74e91c188feff3b980f86d63390f96bcacf7028ac7201efa0626fbc2f9117fc3d4583a9986647a05a4f771c2",
            "full_name": "吴春梅",
            "is_admin": false,
            "is_super_admin": false,
            "associated_doctor_id": 4,
            "is_active": true
        },  # 关联医生: 吴春梅 (在职)
        {
            "username": "zenghuiyin",
            "password_hash": "scrypt:32768:8:1$YEDWeREsW7LSgl8B$5ed018908318583694c09763c1e749547ebfe41387e637802f29856954ee252e4a1f29736ab5e52e48cf5dda026f8cd1a34b4e126d1adf210c962659dc7472bf",
            "full_name": "曾慧尹",
            "is_admin": false,
            "is_super_admin": false,
            "associated_doctor_id": 5,
            "is_active": true
        },  # 关联医生: 曾慧尹 (在职)
        {
            "username": "wangjinmei",
            "password_hash": "scrypt:32768:8:1$55Ji0Uopc1aOINii$6785d2c058b790b5bcf6faa5c52752c737ff9b60c4c758858590452b9bf8499dc7b3995b395f85704c4c732faa1937489dca3c94957f00c8428bd793de7c6505",
            "full_name": "汪金美",
            "is_admin": false,
            "is_super_admin": false,
            "associated_doctor_id": 6,
            "is_active": true
        },  # 关联医生: 汪金美 (在职)
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