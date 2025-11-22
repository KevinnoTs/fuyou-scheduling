from datetime import datetime, date
from calendar import monthrange
import sqlalchemy as sa
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# 从extensions导入db实例
from app.extensions import db

class User(UserMixin, db.Model):
    """用户表"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # 是否为管理员
    is_super_admin = db.Column(db.Boolean, default=False)  # 是否为超级管理员
    full_name = db.Column(db.String(50))  # 全名
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    # 关联的医生ID（一个用户只能关联一个医生）
    associated_doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=True)

    # 关联关系
    associated_doctor = db.relationship('Doctor', foreign_keys=[associated_doctor_id], backref='associated_user')

    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def get_role_name(self):
        """获取用户角色名称"""
        if self.is_super_admin:
            return "超级管理员"
        elif self.is_admin:
            return "管理员"
        elif self.is_authenticated:
            return "普通用户"
        else:
            return "未登录"

    def can_edit_doctor_info(self, doctor_id=None):
        """检查是否可以编辑医生信息（除头像外的基本信息）"""
        # 超级管理员可以编辑所有医生信息
        if self.is_super_admin:
            return True

        # 管理员可以编辑所有医生信息
        if self.is_admin:
            return True

        # 关联医生不能编辑基本信息（只能编辑头像）
        return False

    def can_edit_doctor_avatar(self, doctor_id):
        """检查是否可以编辑医生头像"""
        # 超级管理员和普通管理员可以编辑任何医生头像
        if self.is_super_admin or self.is_admin:
            return True

        # 关联医生可以编辑自己的头像
        if self.associated_doctor_id and self.associated_doctor_id == doctor_id:
            return True

        return False

    def can_delete_doctor(self):
        """检查是否可以删除医生"""
        # 只有超级管理员可以删除医生
        return self.is_super_admin

    def can_view_leave_info(self, doctor_id):
        """检查是否可以查看年假信息"""
        # 管理员和超级管理员可以查看所有医生的年假信息
        if self.is_admin or self.is_super_admin:
            return True

        # 关联医生可以查看自己的年假信息
        if self.associated_doctor_id and self.associated_doctor_id == doctor_id:
            return True

        return False

    def can_manage_users(self):
        """检查是否可以管理用户"""
        return self.is_super_admin

    def can_promote_admin(self):
        """检查是否可以提升管理员权限"""
        return self.is_super_admin

    def can_edit_user(self, target_user_id):
        """检查是否可以编辑特定用户"""
        # 超级管理员可以编辑所有用户
        if self.is_super_admin:
            return True

        # 普通管理员不能编辑其他管理员
        if self.is_admin:
            return False

        return False

    def associate_with_doctor(self, doctor_id):
        """关联医生"""
        self.associated_doctor_id = doctor_id
        db.session.commit()

    def dissociate_doctor(self):
        """取消关联医生"""
        self.associated_doctor_id = None
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'

class Doctor(db.Model):
    """医生表"""
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(2), nullable=False)     # 性别: 男/女
    title = db.Column(db.String(20), default='打字员')     # 职称: 主任医师/副主任医师/打字员
    status = db.Column(db.String(10), default='在职')      # 在职状态: 在职/离职
    specialties = db.Column(db.Text)                     # 擅长方向，JSON格式存储多个方向
    annual_leave_days = db.Column(db.Integer, default=0)  # 每年年假天数
    used_leave_days = db.Column(db.Integer, default=0)   # 本年已休息天数
    sequence = db.Column(db.Integer, default=999)       # 排序序号（仅超级管理员可编辑）
    avatar = db.Column(db.String(255))                   # 头像文件路径
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联排班记录
    schedules = db.relationship('Schedule', backref='doctor', lazy=True)

    def get_avatar_url(self):
        """获取头像URL"""
        if self.avatar:
            # 如果用户上传了自定义头像
            return f'/static/uploads/avatars/{self.avatar}'
        else:
            # 根据性别返回默认头像
            if self.gender == '女':
                return '/static/images/default_female_avatar.jpg'
            else:
                return '/static/images/default_male_avatar.jpg'

    def get_specialties_list(self):
        """获取擅长方向列表"""
        import json
        if not self.specialties:
            return []
        try:
            return json.loads(self.specialties)
        except:
            return []

    def set_specialties_list(self, specialties_list):
        """设置擅长方向列表"""
        import json
        self.specialties = json.dumps(specialties_list)

    def get_specialties_display(self):
        """获取擅长方向的显示文本"""
        specialties = self.get_specialties_list()
        return ', '.join(specialties) if specialties else '未设置'

    def has_specialty(self, specialty_name):
        """检查是否有某个擅长方向"""
        return specialty_name in self.get_specialties_list()

    def get_monthly_schedules_count(self, year=None, month=None):
        """获取指定月份的排班天数"""
        if year is None:
            year = date.today().year
        if month is None:
            month = date.today().month

        # 计算该月的第一天和最后一天
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])

        count = db.session.query(sa.func.count(Schedule.id)).filter(
            Schedule.doctor_id == self.id,
            Schedule.date >= first_day,
            Schedule.date <= last_day,
            Schedule.status == '正常'
        ).scalar()

        return count or 0

    def get_monthly_work_hours(self, year=None, month=None):
        """获取指定月份的总工时"""
        if year is None:
            year = date.today().year
        if month is None:
            month = date.today().month

        # 首先尝试从工时统计表获取
        hours = db.session.query(sa.func.sum(WorkHours.total_hours)).filter(
            WorkHours.doctor_id == self.id,
            WorkHours.year == year,
            WorkHours.month == month
        ).scalar()

        if hours:
            return float(hours)

        # 如果工时统计表没有数据，从排班表计算
        # 使用JOIN通过班次名称关联ShiftType
        total_hours = db.session.query(sa.func.sum(ShiftType.duration_hours)).join(
            Schedule, ShiftType.name == Schedule.shift
        ).filter(
            Schedule.doctor_id == self.id,
            Schedule.status == 'assigned'  # 使用正确的状态值：assigned
        ).filter(
            sa.extract('year', Schedule.date) == year,
            sa.extract('month', Schedule.date) == month
        ).scalar() or 0

        return float(total_hours)

    def get_monthly_work_score(self, year=None, month=None):
        """获取指定月份的总工分"""
        if year is None:
            year = date.today().year
        if month is None:
            month = date.today().month

        # 首先尝试从工分统计表获取
        score = db.session.query(sa.func.sum(WorkScore.score)).filter(
            WorkScore.doctor_id == self.id,
            WorkScore.year == year,
            WorkScore.month == month
        ).scalar()

        if score:
            return float(score)

        # 如果工分统计表没有数据，从排班表计算
        total_score = db.session.query(sa.func.sum(ShiftType.work_score)).join(
            Schedule, ShiftType.name == Schedule.shift
        ).filter(
            Schedule.doctor_id == self.id,
            Schedule.status == 'assigned'  # 使用正确的状态值：assigned
        ).filter(
            sa.extract('year', Schedule.date) == year,
            sa.extract('month', Schedule.date) == month
        ).scalar() or 0

        return float(total_score)

    def get_yearly_work_score(self, year=None):
        """获取指定年度的总工分"""
        if year is None:
            year = date.today().year

        # 首先尝试从工分统计表获取
        score = db.session.query(sa.func.sum(WorkScore.score)).filter(
            WorkScore.doctor_id == self.id,
            WorkScore.year == year
        ).scalar()

        if score:
            return float(score)

        # 如果工分统计表没有数据，从排班表计算
        total_score = db.session.query(sa.func.sum(ShiftType.work_score)).join(
            Schedule, ShiftType.name == Schedule.shift
        ).filter(
            Schedule.doctor_id == self.id,
            Schedule.status == 'assigned'  # 使用正确的状态值：assigned
        ).filter(
            sa.extract('year', Schedule.date) == year
        ).scalar() or 0

        return float(total_score)

    def __repr__(self):
        return f'<Doctor {self.name}>'

class Specialty(db.Model):
    """擅长方向表"""
    __tablename__ = 'specialties'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#007bff')  # 显示颜色
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Specialty {self.name}>'

class ShiftType(db.Model):
    """班次类型表"""
    __tablename__ = 'shift_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    duration_hours = db.Column(db.Numeric(4, 2), nullable=False)
    work_score = db.Column(db.Numeric(4, 1), nullable=False)  # 工作量分值
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ShiftType {self.name}>'

class Schedule(db.Model):
    """排班表"""
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=True)  # 可以为空，表示未分配
    date = db.Column(db.Date, nullable=False)
    weekday = db.Column(db.String(10), nullable=False)  # 星期一、星期二等
    shift = db.Column(db.String(20), nullable=False)  # 白班、夜班等
    time_range = db.Column(db.String(20), nullable=False)  # 08:00-16:00等
    department = db.Column(db.String(50), nullable=False)  # 门诊、急诊等
    status = db.Column(db.String(20), default='unassigned')  # unassigned, assigned
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        doctor_name = self.doctor.name if self.doctor else '未分配'
        return f'<Schedule {doctor_name} - {self.date} - {self.shift}>'

    def get_status_display(self):
        """获取状态的显示文本"""
        status_map = {
            'unassigned': '待分配',
            'assigned': '已分配',
            'cancelled': '已取消',
            'leave': '请假'
        }
        return status_map.get(self.status, self.status)

class WorkHours(db.Model):
    """工时统计表"""
    __tablename__ = 'work_hours'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    total_hours = db.Column(db.Numeric(4, 2), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<WorkHours {self.doctor.name} - {self.date} - {self.total_hours}h>'

class WorkScore(db.Model):
    """工作量分值表"""
    __tablename__ = 'work_scores'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    score = db.Column(db.Numeric(4, 1), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<WorkScore {self.doctor.name} - {self.date} - {self.score}分>'

class Holiday(db.Model):
    """节假日表"""
    __tablename__ = 'holidays'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(20), nullable=False, default='custom')  # holiday, workday, custom
    is_system = db.Column(db.Boolean, default=False)  # 是否为系统预设
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Holiday {self.date} - {self.name} - {self.type}>'