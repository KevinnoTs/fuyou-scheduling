#!/usr/bin/env python3
"""
导出当前数据库数据为分离的初始化脚本
支持分别导出节假日、医生和用户数据为独立文件
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
# 从scripts/data/export_data.py回溯到项目根目录
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from app import create_app
from app.extensions import db
from app.models import Doctor, User, Holiday

def export_all_data():
    """导出所有数据为分离的初始化脚本"""
    print("🔄 开始导出数据库数据...")
    print(f"📍 项目根目录: {project_root}")

    try:
        app = create_app()
        with app.app_context():
            print("=" * 60)

            # 导出节假日数据
            export_holidays_data()

            # 导出医生数据
            export_doctors_data()

            # 导出用户数据
            export_users_data()

            print("\n✅ 所有数据导出完成!")
            print("📁 生成的文件:")
            print("   - holidays_init_data.py  (节假日数据)")
            print("   - doctors_init_data.py   (医生数据)")
            print("   - users_init_data.py     (用户数据)")
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        import traceback
        traceback.print_exc()

def export_holidays_data():
    """导出节假日数据为初始化脚本"""
    print("\n📅 导出节假日数据...")

    # 获取所有节假日数据
    holidays = Holiday.query.order_by(Holiday.date).all()

    if not holidays:
        print("   ⚠️  没有找到节假日数据")
        return

    # 按年份分组统计
    years = {}
    for holiday in holidays:
        year = holiday.date.year
        if year not in years:
            years[year] = []
        years[year].append(holiday)

    print(f"   找到 {len(holidays)} 条节假日记录")
    for year, year_holidays in years.items():
        print(f"     {year}年: {len(year_holidays)} 条")

    # 生成初始化脚本
    generate_holidays_init_file(holidays, years)

def export_doctors_data():
    """导出医生数据为初始化脚本"""
    print("\n👨‍⚕️  导出医生数据...")

    # 获取所有医生（包括在职和离职）
    doctors = Doctor.query.order_by(Doctor.sequence).all()

    if not doctors:
        print("   ⚠️  没有找到医生数据")
        return

    print(f"   找到 {len(doctors)} 名医生")

    # 统计在职和离职医生数量
    active_count = len([d for d in doctors if d.status == '在职'])
    inactive_count = len(doctors) - active_count

    print(f"     在职医生: {active_count}")
    print(f"     离职医生: {inactive_count}")

    # 生成初始化脚本
    generate_doctors_init_file(doctors)

def export_users_data():
    """导出用户数据为初始化脚本"""
    print("\n👤 导出用户数据...")

    # 获取所有用户
    users = User.query.order_by(User.id).all()

    if not users:
        print("   ⚠️  没有找到用户数据")
        return

    print(f"   找到 {len(users)} 个用户")

    # 统计不同类型的用户
    super_admin_count = len([u for u in users if u.is_super_admin])
    admin_count = len([u for u in users if u.is_admin and not u.is_super_admin])
    regular_count = len([u for u in users if not u.is_admin and not u.is_super_admin])

    print(f"     超级管理员: {super_admin_count}")
    print(f"     管理员: {admin_count}")
    print(f"     普通用户: {regular_count}")

    # 生成初始化脚本
    generate_users_init_file(users)

def generate_holidays_init_file(holidays, years):
    """生成节假日初始化脚本"""
    output_file = 'holidays_init_data.py'

    init_code = []
    init_code.append('"""')
    init_code.append('节假日初始化数据')
    init_code.append(f'导出时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    init_code.append('')

    # 添加年份统计信息
    init_code.append('节假日统计:')
    for year, year_holidays in years.items():
        holiday_count = len([h for h in year_holidays if h.type == 'holiday'])
        workday_count = len([h for h in year_holidays if h.type == 'workday'])
        init_code.append(f'- {year}年: {holiday_count}天节假日, {workday_count}天调休')
    init_code.append('"""')
    init_code.append('')
    init_code.append('from datetime import date')
    init_code.append('import sqlalchemy as sa')
    init_code.append('import os')
    init_code.append('import sys')
    init_code.append('')
    init_code.append('# 添加项目根目录到Python路径')
    init_code.append('project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))')
    init_code.append('sys.path.insert(0, project_root)')
    init_code.append('')
    init_code.append('from app import create_app')
    init_code.append('from app.extensions import db')
    init_code.append('from app.models import Holiday')
    init_code.append('')

    # 按年份生成函数
    for year in sorted(years.keys()):
        year_holidays = years[year]
        function_name = f'init_{year}_holidays'

        init_code.append(f'def {function_name}():')
        init_code.append(f'    """初始化{year}年节假日数据"""')
        init_code.append('')
        init_code.append(f'    # {year}年节假日数据（{len(year_holidays)}条记录）')
        init_code.append('    holidays = [')

        for holiday in year_holidays:
            date_str = holiday.date.strftime('%Y, %m, %d')
            init_code.append(f'        (date({date_str}), "{holiday.name}", "{holiday.type}", {str(holiday.is_system)}),')

        init_code.append('    ]')
        init_code.append('')
        init_code.append('    # 检查是否已存在数据')
        init_code.append(f'    existing_count = Holiday.query.filter(')
        init_code.append(f'        sa.extract(\'year\', Holiday.date) == {year}')
        init_code.append('    ).count()')
        init_code.append('    if existing_count > 0:')
        init_code.append(f'        print("{year}年节假日数据已存在，跳过初始化")')
        init_code.append('        return')
        init_code.append('')
        init_code.append('    # 插入数据')
        init_code.append('    for holiday_date, name, holiday_type, is_system in holidays:')
        init_code.append('        holiday = Holiday(')
        init_code.append('            date=holiday_date,')
        init_code.append('            name=name,')
        init_code.append('            type=holiday_type,')
        init_code.append('            is_system=is_system')
        init_code.append('        )')
        init_code.append('        db.session.add(holiday)')
        init_code.append('    ')
        init_code.append('    db.session.commit()')
        init_code.append(f'    print("{year}年节假日数据初始化完成，共{len(year_holidays)}条记录")')
        init_code.append('')

    # 生成检查函数
    init_code.append('def check_holidays_data():')
    init_code.append('    """检查并初始化所有年份数据"""')
    init_code.append('    total_count = Holiday.query.count()')
    init_code.append('    if total_count == 0:')
    init_code.append('        print("数据库中没有节假日数据，正在初始化...")')

    for year in sorted(years.keys()):
        function_name = f'init_{year}_holidays'
        init_code.append(f'        {function_name}()')
        init_code.append('        return True')
    init_code.append('    else:')
    init_code.append(f'        print(f"数据库中已有 {{total_count}} 条节假日数据")')
    init_code.append('        # 检查是否有新年份数据需要初始化')

    for year in sorted(years.keys()):
        function_name = f'init_{year}_holidays'
        init_code.append(f'        {function_name}()')

    init_code.append('        return False')
    init_code.append('')
    init_code.append('if __name__ == "__main__":')
    init_code.append('    # 创建Flask应用并初始化数据库上下文')
    init_code.append('    app = create_app()')
    init_code.append('    with app.app_context():')
    init_code.append('        check_holidays_data()')

    # 写入文件到项目根目录
    output_path = os.path.join(project_root, output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(init_code))

    print(f"   ✅ 节假日数据已导出到: {output_path}")

def generate_doctors_init_file(doctors):
    """生成医生初始化脚本"""
    output_file = 'doctors_init_data.py'

    init_code = []
    init_code.append('"""')
    init_code.append('医生初始化数据')
    init_code.append(f'导出时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    init_code.append(f'包含 {len(doctors)} 名医生数据')
    init_code.append('"""')
    init_code.append('')
    init_code.append('import json')
    init_code.append('import os')
    init_code.append('import sys')
    init_code.append('')
    init_code.append('# 添加项目根目录到Python路径')
    init_code.append('project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))')
    init_code.append('sys.path.insert(0, project_root)')
    init_code.append('')
    init_code.append('from app import create_app')
    init_code.append('from app.models import Doctor')
    init_code.append('from app.extensions import db')
    init_code.append('')

    # 生成初始化函数
    init_code.append('def init_doctors():')
    init_code.append('    """初始化医生数据"""')
    init_code.append('')
    init_code.append('    # 医生数据列表')
    init_code.append('    doctors_data = [')

    for doctor in doctors:
        specialties_json = json.dumps(doctor.get_specialties_list(), ensure_ascii=False)
        avatar = f'"{doctor.avatar}"' if doctor.avatar else 'null'

        doctor_data = f'''        {{
            "name": "{doctor.name}",
            "gender": "{doctor.gender}",
            "title": "{doctor.title}",
            "status": "{doctor.status}",
            "specialties": "{specialties_json}",
            "annual_leave_days": {doctor.annual_leave_days},
            "used_leave_days": {doctor.used_leave_days},
            "avatar": {avatar},
            "sequence": {doctor.sequence}
        }}'''

        # 添加注释
        status_emoji = "✓在职" if doctor.status == '在职' else "✗离职"
        doctor_data += f',  # 当前状态: {status_emoji}'

        init_code.append(doctor_data)

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
    init_code.append(f'    print(f"医生数据初始化完成，新增 {{new_count}} 名医生")')
    init_code.append('')
    init_code.append('if __name__ == "__main__":')
    init_code.append('    # 创建Flask应用并初始化数据库上下文')
    init_code.append('    app = create_app()')
    init_code.append('    with app.app_context():')
    init_code.append('        init_doctors()')

    # 写入文件到项目根目录
    output_path = os.path.join(project_root, output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(init_code))

    print(f"   ✅ 医生数据已导出到: {output_path}")

def generate_users_init_file(users):
    """生成用户初始化脚本"""
    output_file = 'users_init_data.py'

    init_code = []
    init_code.append('"""')
    init_code.append('用户初始化数据')
    init_code.append(f'导出时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    init_code.append(f'包含 {len(users)} 个用户数据')
    init_code.append('"""')
    init_code.append('')
    init_code.append('import os')
    init_code.append('import sys')
    init_code.append('')
    init_code.append('# 添加项目根目录到Python路径')
    init_code.append('project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))')
    init_code.append('sys.path.insert(0, project_root)')
    init_code.append('')
    init_code.append('from app import create_app')
    init_code.append('from app.models import User, Doctor')
    init_code.append('from app.extensions import db')
    init_code.append('')

    # 生成初始化函数
    init_code.append('def init_users():')
    init_code.append('    """初始化用户数据"""')
    init_code.append('')
    init_code.append('    # 用户数据列表')
    init_code.append('    users_data = [')

    for user in users:
        # 获取关联医生姓名
        associated_doctor_name = ""
        if user.associated_doctor_id:
            doctor = Doctor.query.get(user.associated_doctor_id)
            if doctor:
                associated_doctor_name = f',  # 关联医生: {doctor.name} ({doctor.status})'

        user_data = f'''        {{
            "username": "{user.username}",
            "password_hash": "{user.password_hash}",
            "full_name": "{user.full_name}",
            "is_admin": {str(user.is_admin).lower()},
            "is_super_admin": {str(user.is_super_admin).lower()},
            "associated_doctor_id": {user.associated_doctor_id if user.associated_doctor_id else 'null'},
            "is_active": {str(user.is_active).lower()}
        }}{associated_doctor_name}'''

        init_code.append(user_data)

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
    init_code.append('                associated_doctor_id=user_data["associated_doctor_id"],')
    init_code.append('                is_active=user_data["is_active"]')
    init_code.append('            )')
    init_code.append('            ')
    init_code.append('            # 查找关联的医生（必须是在职状态）')
    init_code.append('            if user_data.get("associated_doctor_id"):')
    init_code.append('                doctor = Doctor.query.get(user_data["associated_doctor_id"])')
    init_code.append('                if not doctor or doctor.status != "在职":')
    init_code.append('                    user.associated_doctor_id = None')
    init_code.append('            ')
    init_code.append('            db.session.add(user)')
    init_code.append('            new_count += 1')
    init_code.append('')
    init_code.append('    db.session.commit()')
    init_code.append(f'    print(f"用户数据初始化完成，新增 {{new_count}} 个用户")')
    init_code.append('')
    init_code.append('if __name__ == "__main__":')
    init_code.append('    # 创建Flask应用并初始化数据库上下文')
    init_code.append('    app = create_app()')
    init_code.append('    with app.app_context():')
    init_code.append('        init_users()')

    # 写入文件到项目根目录
    output_path = os.path.join(project_root, output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(init_code))

    print(f"   ✅ 用户数据已导出到: {output_path}")

if __name__ == "__main__":
    export_all_data()