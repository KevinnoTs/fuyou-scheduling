#!/usr/bin/env python3
"""
导出当前数据库数据为初始化脚本
支持导出医生表和用户表的数据
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import Doctor, User

def export_data_to_init():
    """导出医生和用户数据为初始化代码"""
    app = create_app()

    with app.app_context():
        print(" 导出数据库数据...")
        print("=" * 50)

        # 导出医生数据
        doctors_data = export_doctors()

        # 导出用户数据
        users_data = export_users()

        # 生成完整的初始化文件
        generate_init_file(doctors_data, users_data)

def export_doctors():
    """导出医生数据"""
    print(" 导出医生数据...")

    # 获取所有医生（包括在职和离职）
    doctors = Doctor.query.order_by(Doctor.sequence).all()

    if not doctors:
        print("   ⚠️  没有找到医生数据")
        return []

    print(f"   找到 {len(doctors)} 名医生（包括在职和离职）")

    # 统计在职和离职医生数量
    active_count = len([d for d in doctors if d.status == '在职'])
    inactive_count = len(doctors) - active_count
    print(f"   - 在职医生: {active_count} 名")
    print(f"   - 离职医生: {inactive_count} 名")

    # 生成医生数据
    doctors_data = []
    for i, doctor in enumerate(doctors):
        # 处理擅长方向
        specialties_list = doctor.get_specialties_list()
        specialties_json = json.dumps(specialties_list, ensure_ascii=False)

        # 生成医生数据
        doctor_data = {
            'name': doctor.name,
            'gender': doctor.gender,
            'title': doctor.title,
            'status': doctor.status,
            'specialties': specialties_json,
            'annual_leave_days': doctor.annual_leave_days if doctor.annual_leave_days is not None else 0,
            'used_leave_days': doctor.used_leave_days if doctor.used_leave_days is not None else 0,
            'avatar': doctor.avatar if doctor.avatar else None,
            'sequence': doctor.sequence if doctor.sequence is not None else (i + 1)
        }

        doctors_data.append(doctor_data)

    return doctors_data

def export_users():
    """导出用户数据"""
    print("\n 导出用户数据...")

    # 获取所有用户
    users = User.query.order_by(User.id).all()

    if not users:
        print("   ⚠️  没有找到用户数据")
        return []

    print(f"   找到 {len(users)} 个用户账户")

    # 统计用户类型
    super_admin_count = len([u for u in users if u.is_super_admin])
    admin_count = len([u for u in users if u.is_admin and not u.is_super_admin])
    regular_count = len([u for u in users if not u.is_admin and not u.is_super_admin])

    print(f"   - 超级管理员: {super_admin_count} 个")
    print(f"   - 普通管理员: {admin_count} 个")
    print(f"   - 普通用户: {regular_count} 个")

    # 生成用户数据
    users_data = []
    for user in users:
        user_data = {
            'username': user.username,
            'password_hash': user.password_hash,  # 保留密码哈希用于初始化
            'full_name': user.full_name,
            'is_admin': user.is_admin,
            'is_super_admin': user.is_super_admin,
            'is_active': user.is_active,
            'associated_doctor_id': user.associated_doctor_id
        }

        # 添加关联医生信息
        if user.associated_doctor:
            user_data['associated_doctor_name'] = user.associated_doctor.name
            user_data['associated_doctor_status'] = user.associated_doctor.status

        users_data.append(user_data)

    return users_data

def generate_init_file(doctors_data, users_data):
    """生成完整的初始化文件"""

    print("\n📝 生成初始化代码...")

    # 生成医生初始化代码
    doctors_init_code = generate_doctors_init_code(doctors_data)

    # 生成用户初始化代码
    users_init_code = generate_users_init_code(users_data)

    # 合并为完整的初始化文件
    full_init_code = generate_full_init_file(doctors_init_code, users_init_code)

    # 写入文件
    output_file = 'database_init_data.py'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_init_code)

    # 修复 JavaScript 值为 Python 值
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    # 替换 null 为 None
    content = content.replace('"avatar": null,', '"avatar": None,')
    # 替换 true/false 为 True/False
    content = content.replace('"is_admin": true,', '"is_admin": True,')
    content = content.replace('"is_admin": false,', '"is_admin": False,')
    content = content.replace('"is_super_admin": true,', '"is_super_admin": True,')
    content = content.replace('"is_super_admin": false,', '"is_super_admin": False,')
    content = content.replace('"is_active": true', '"is_active": True')
    content = content.replace('"is_active": false', '"is_active": False')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"    初始化文件已生成: {output_file}")
    print(f"    包含 {len(doctors_data)} 名医生和 {len(users_data)} 个用户数据")

    # 显示导出的统计信息
    print("\n📋 导出统计:")

    if doctors_data:
        print(f"   医生数据:")
        active_doctors = [d for d in doctors_data if d['status'] == '在职']
        print(f"     - 总计: {len(doctors_data)} 名")
        print(f"     - 在职: {len(active_doctors)} 名")
        print(f"     - 离职: {len(doctors_data) - len(active_doctors)} 名")

    if users_data:
        print(f"   用户数据:")
        print(f"     - 总计: {len(users_data)} 个")
        admin_users = [u for u in users_data if u['is_admin'] or u['is_super_admin']]
        print(f"     - 管理员: {len(admin_users)} 个")

        associated_users = [u for u in users_data if u['associated_doctor_id']]
        print(f"     - 关联医生: {len(associated_users)} 个")

def generate_doctors_init_code(doctors_data):
    """生成医生初始化代码"""

    init_code = []
    init_code.append('def init_doctors():')
    init_code.append('    """初始化医生数据"""')
    init_code.append('')
    init_code.append('    # 医生数据列表')
    init_code.append('    doctors_data = [')

    for doctor in doctors_data:
        init_code.append(f'        {json.dumps(doctor, ensure_ascii=False, indent=8)},  # 当前状态: {doctor["status"]}')

    init_code.append('    ]')
    init_code.append('')
    init_code.append('    # 检查现有医生')
    init_code.append('    existing_doctors = [doc.name for doc in Doctor.query.all()]')
    init_code.append('    new_count = 0')
    init_code.append('')
    init_code.append('    for doctor_data in doctors_data:')
    init_code.append('        if doctor_data["name"] not in existing_doctors:')
    init_code.append('            doctor = Doctor(')
    init_code.append('                name=doctor_data["name"],')
    init_code.append('                gender=doctor_data["gender"],')
    init_code.append('                title=doctor_data["title"],')
    init_code.append('                status=doctor_data["status"],')
    init_code.append('                specialties=doctor_data["specialties"],')
    init_code.append('                annual_leave_days=doctor_data["annual_leave_days"],')
    init_code.append('                used_leave_days=doctor_data["used_leave_days"],')
    init_code.append('                avatar=doctor_data["avatar"],')
    init_code.append('                sequence=doctor_data["sequence"]')
    init_code.append('            )')
    init_code.append('            db.session.add(doctor)')
    init_code.append('            new_count += 1')
    init_code.append('')
    init_code.append('    db.session.commit()')
    init_code.append('    print(f"医生数据初始化完成，新增 {new_count} 名医生")')
    init_code.append('')

    return '\n'.join(init_code)

def generate_users_init_code(users_data):
    """生成用户初始化代码"""

    init_code = []
    init_code.append('def init_users():')
    init_code.append('    """初始化用户数据"""')
    init_code.append('')
    init_code.append('    # 用户数据列表')
    init_code.append('    users_data = [')

    for user in users_data:
        user_display = {
            'username': user['username'],
            'password_hash': user['password_hash'],
            'full_name': user['full_name'],
            'is_admin': user['is_admin'],
            'is_super_admin': user['is_super_admin'],
            'is_active': user['is_active']
        }

        # 添加关联医生信息作为注释
        comment = ''
        if user.get('associated_doctor_name'):
            comment = f'  # 关联医生: {user["associated_doctor_name"]} ({user["associated_doctor_status"]})'

        user_json = json.dumps(user_display, ensure_ascii=False, indent=8)
        # 确保逗号在注释之前
        if comment:
            init_code.append(f'        {user_json},{comment}')
        else:
            init_code.append(f'        {user_json},')

    init_code.append('    ]')
    init_code.append('')
    init_code.append('    # 检查现有用户')
    init_code.append('    existing_users = [user.username for user in User.query.all()]')
    init_code.append('    new_count = 0')
    init_code.append('')
    init_code.append('    for user_data in users_data:')
    init_code.append('        if user_data["username"] not in existing_users:')
    init_code.append('            user = User(')
    init_code.append('                username=user_data["username"],')
    init_code.append('                password_hash=user_data["password_hash"],')
    init_code.append('                full_name=user_data["full_name"],')
    init_code.append('                is_admin=user_data["is_admin"],')
    init_code.append('                is_super_admin=user_data["is_super_admin"],')
    init_code.append('                is_active=user_data["is_active"]')
    init_code.append('            )')

    # 处理医生关联
    init_code.append('            ')
    init_code.append('            # 查找关联的医生（必须是在职状态）')
    init_code.append('            if user_data.get("associated_doctor_name"):')
    init_code.append('                doctor = Doctor.query.filter_by(name=user_data["associated_doctor_name"], status="在职").first()')
    init_code.append('                if doctor:')
    init_code.append('                    user.associated_doctor_id = doctor.id')
    init_code.append('')
    init_code.append('            db.session.add(user)')
    init_code.append('            new_count += 1')
    init_code.append('')
    init_code.append('    db.session.commit()')
    init_code.append('    print(f"用户数据初始化完成，新增 {new_count} 个用户")')
    init_code.append('')

    return '\n'.join(init_code)

def generate_full_init_file(doctors_init_code, users_init_code):
    """生成完整的初始化文件"""

    file_content = f'''#!/usr/bin/env python3
"""
数据库初始化脚本
自动生成于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

包含医生表和用户表的完整数据
"""

import json
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Doctor, User
from app.extensions import db

{doctors_init_code}

{users_init_code}

def init_all_data():
    """初始化所有数据"""
    app = create_app()
    with app.app_context():
        try:
            print("🗄️ 开始数据库初始化...")

            # 初始化医生数据
            init_doctors()

            # 初始化用户数据
            init_users()

            print(" 数据库初始化完成！")

        except Exception as e:
            print(f" 数据库初始化失败: {{str(e)}}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    init_all_data()
'''

    return file_content

if __name__ == '__main__':
    print("🏥 妇幼排班管理系统 - 数据导出工具")
    print("=" * 50)

    try:
        export_data_to_init()
        print("\n" + "=" * 50)
        print(" 数据导出成功！")
        print("\n📝 使用说明:")
        print("1. 将生成的 database_init_data.py 移动到 app/ 目录下")
        print("2. 在应用初始化时调用 init_all_data() 函数")
        print("3. 或者手动运行 python app/database_init_data.py")
        print("=" * 50)
    except Exception as e:
        print(f"\n 导出失败: {str(e)}")
        import traceback
        traceback.print_exc()