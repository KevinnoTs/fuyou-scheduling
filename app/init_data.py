from datetime import time
from app.models import Specialty, ShiftType, User
from app.extensions import db

def init_specialties():
    """初始化擅长方向数据"""
    required_specialties = [
        {
            'name': '妇科',
            'description': '擅长妇科诊疗工作',
            'color': '#e91e63'  # 粉色
        },
        {
            'name': '产科',
            'description': '擅长产科诊疗工作',
            'color': '#9c27b0'  # 紫色
        },
        {
            'name': '儿科',
            'description': '擅长儿科诊疗工作',
            'color': '#2196f3'  # 蓝色
        },
        {
            'name': '筛查',
            'description': '擅长筛查工作，优先安排筛查任务',
            'color': '#ff9800'  # 橙色
        }
    ]

    existing_specialties = [spec.name for spec in Specialty.query.all()]
    new_count = 0

    for spec_data in required_specialties:
        if spec_data['name'] not in existing_specialties:
            spec = Specialty(**spec_data)
            db.session.add(spec)
            new_count += 1

    db.session.commit()
    print(f"擅长方向数据完成，新增 {new_count} 项")

def init_shift_types():
    """初始化班次类型数据"""
    required_shift_types = [
        {
            'name': '白班',
            'start_time': time(8, 0),
            'end_time': time(17, 30),  # 以夏季时间为标准
            'duration_hours': 7.5,     # 夏季7.5小时，冬季7小时
            'work_score': 1.0,         # 基础工作量分值
            'description': '早8点-中午12点，下午时间段\n5月-10月: 下午2点半-5点半 (7.5小时)\n10月-次年5月: 下午2点-5点 (7小时)'
        },
        {
            'name': '中班',
            'start_time': time(8, 0),
            'end_time': time(14, 30),  # 以夏季时间为标准
            'duration_hours': 6.0,     # 夏季6小时，冬季5.5小时
            'work_score': 0.8,         # 相对白班工作量较低
            'description': '早8点-中午11点半，下午时间段\n5月-10月: 中午12点-2点半 (6小时)\n10月-次年5月: 中午12点-2点 (5.5小时)'
        },
        {
            'name': '值班',
            'start_time': time(8, 0),
            'end_time': time(23, 59),  # 以夏季时间为标准
            'duration_hours': 13.5,    # 夏季13.5小时，冬季13小时
            'work_score': 1.8,         # 工作量较高
            'description': '早8点-中午12点，下午时间段+夜间\n5月-10月: 下午2点半-23:59 (13.5小时)\n10月-次年5月: 下午2点-23:00 (13小时)'
        },
        {
            'name': '夜班',
            'start_time': time(16, 0),
            'end_time': time(23, 59),
            'duration_hours': 8.0,
            'work_score': 1.2,         # 夜班工作量相对较高
            'description': '下午4点-午夜 (8小时)'
        },
        {
            'name': '下夜',
            'start_time': time(0, 0),
            'end_time': time(8, 0),
            'duration_hours': 8.0,
            'work_score': 1.2,         # 夜班工作量相对较高
            'description': '当天0点-早晨8点 (8小时)'
        },
        {
            'name': '休息',
            'start_time': time(0, 0),
            'end_time': time(0, 0),
            'duration_hours': 0.0,
            'work_score': 0.0,
            'description': '正常休息日'
        },
        {
            'name': '探亲假',
            'start_time': time(0, 0),
            'end_time': time(0, 0),
            'duration_hours': 0.0,
            'work_score': 0.0,
            'description': '探亲假休息'
        },
        {
            'name': '公休',
            'start_time': time(0, 0),
            'end_time': time(0, 0),
            'duration_hours': 0.0,
            'work_score': 0.0,
            'description': '年假休息 (对应医生表中的年假天数)'
        }
    ]

    existing_shift_types = [shift.name for shift in ShiftType.query.all()]
    new_count = 0

    for shift_data in required_shift_types:
        if shift_data['name'] not in existing_shift_types:
            shift = ShiftType(**shift_data)
            db.session.add(shift)
            new_count += 1

    db.session.commit()
    print(f"班次类型数据完成，新增 {new_count} 项")

def init_admin_user():
    """初始化管理员用户"""
    try:
        # 检查是否已有管理员用户
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            print("管理员用户已存在，跳过初始化")
            return

        # 创建默认管理员用户
        admin = User(
            username='admin',
            full_name='系统管理员',
            is_admin=True,
            is_active=True
        )
        admin.set_password('admin123')  # 默认密码

        db.session.add(admin)
        db.session.commit()
        print("默认管理员用户创建成功!")
        print("  用户名: admin")
        print("  密码: admin123")
        print("WARNING: 请在生产环境中修改默认密码!")

    except Exception as e:
        print(f"管理员用户初始化失败: {e}")
        db.session.rollback()

def init_all_data():
    """初始化所有基础数据"""
    try:
        # 初始化管理员用户
        init_admin_user()

        # 检查是否已有数据
        if Specialty.query.first():
            print("擅长方向数据已存在，跳过初始化")
        else:
            init_specialties()

        if ShiftType.query.first():
            print("班次类型数据已存在，跳过初始化")
        else:
            init_shift_types()

        # 初始化医生和用户数据
        from scripts.data.database_init_data import init_doctors, init_users
        init_doctors()
        init_users()

        # 初始化节假日数据
        from scripts.data.holidays_init_data import check_holidays_data
        check_holidays_data()

        print("基础数据初始化完成!")

    except Exception as e:
        print(f"数据初始化失败: {e}")
        db.session.rollback()

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        init_all_data()