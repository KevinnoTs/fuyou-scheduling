from flask import Blueprint, render_template, request, jsonify, flash, current_app, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models import Holiday
from app.extensions import db
from app.holiday_utils.holidays import holiday_helper
from functools import wraps

# 创建节假日管理蓝图
holidays_bp = Blueprint('holidays', __name__)

# 管理员权限装饰器
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not (current_user.is_admin or current_user.is_super_admin):
            flash('需要管理员权限', 'error')
            return redirect(url_for('holidays.manage_holidays'))
        return f(*args, **kwargs)
    return decorated_function

@holidays_bp.route('/holidays')
@login_required
def manage_holidays():
    """节假日管理页面"""
    from app.models import Holiday
    import sqlalchemy as sa

    year = request.args.get('year', datetime.now().year, type=int)

    # 生成年份选项 - 限制最小年份为2025
    current_year = datetime.now().year
    min_year = max(2025, current_year)  # 确保最小年份为2025
    # 如果请求的年份小于2025，则使用2025
    if year < 2025:
        year = 2025
    years = list(range(min_year, year + 5))  # 从最小年份开始，往后5年

    # 从数据库获取已保存的节假日数据
    holidays_db = Holiday.query.filter(
        sa.extract('year', Holiday.date) == year
    ).order_by(Holiday.date).all()

    # 转换为模板需要的格式
    holidays = {}
    for holiday in holidays_db:
        date_str = holiday.date.strftime('%Y-%m-%d')
        holidays[date_str] = {
            'name': holiday.name,
            'type': holiday.type,
            'is_system': holiday.is_system,
            'source': 'database'
        }

    return render_template('holidays/holiday_management.html',
                         current_year=year,
                         years=years,
                         holidays=holidays)

@holidays_bp.route('/holidays/add', methods=['POST'])
@admin_required
def add_holiday():
    """添加节假日"""
    from app.models import Holiday
    from datetime import date
    from flask import redirect, url_for

    try:
        data = request.get_json()
        date_str = data.get('date')
        end_date_str = data.get('end_date')  # 获取结束日期
        name = data.get('name')
        holiday_type = data.get('type', 'custom')

        if not date_str or not name:
            return jsonify({'success': False, 'message': '日期和名称不能为空'})

        # 检查日期格式
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

            # 如果有结束日期，也检查格式
            if end_date_str:
                end_date_obj = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                # 验证结束日期不能早于开始日期
                if end_date_obj < date_obj:
                    return jsonify({'success': False, 'message': '结束日期不能早于开始日期'})

        except ValueError:
            return jsonify({'success': False, 'message': '日期格式错误，请使用YYYY-MM-DD格式'})

        # 如果没有结束日期，设置为开始日期
        if not end_date_str:
            end_date_str = date_str
            end_date_obj = date_obj

        # 检查范围内的每一天是否已存在节假日
        current_date = date_obj
        while current_date <= end_date_obj:
            current_date_str = current_date.strftime('%Y-%m-%d')
            existing_holiday = Holiday.query.filter_by(date=current_date).first()
            if existing_holiday:
                return jsonify({
                    'success': False,
                    'message': f'日期 {current_date_str} 已存在节假日：{existing_holiday.name}（{existing_holiday.type}），请勿重复添加'
                })
            current_date += timedelta(days=1)

        # 添加节假日到数据库（支持日期范围）
        current_date = date_obj
        added_count = 0
        while current_date <= end_date_obj:
            holiday = Holiday(
                date=current_date,
                name=name,
                type=holiday_type,
                is_system=False  # 用户添加的都不是系统预设
            )
            db.session.add(holiday)
            added_count += 1
            current_date += timedelta(days=1)

        db.session.commit()

        # 清理缓存，确保新添加的节假日能立即生效
        holiday_helper.clear_cache(date_obj.year)

        if added_count == 1:
            message = f'成功添加节假日：{name}（{date_str}）'
        else:
            message = f'成功添加节假日：{name}（{date_str} 至 {end_date_str}，共{added_count}天）'

        return jsonify({'success': True, 'message': message})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败：{str(e)}'})

@holidays_bp.route('/holidays/remove', methods=['POST'])
@admin_required
def remove_holiday():
    """删除节假日"""
    from app.models import Holiday
    from datetime import date

    try:
        data = request.get_json()
        date_str = data.get('date')

        if not date_str:
            return jsonify({'success': False, 'message': '日期不能为空'})

        # 检查日期格式
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({'success': False, 'message': '日期格式错误，请使用YYYY-MM-DD格式'})

        # 从数据库查找并删除节假日
        holiday = Holiday.query.filter_by(date=date_obj).first()
        if not holiday:
            return jsonify({'success': False, 'message': '该日期没有找到节假日记录'})

        # 删除节假日（允许删除系统预设节假日，因为农历日期可能不完全准确）
        db.session.delete(holiday)
        db.session.commit()

        # 清理缓存，确保删除后能立即生效
        holiday_helper.clear_cache(date_obj.year)

        # 根据是否为系统预设显示不同的提示信息
        if holiday.is_system:
            return jsonify({'success': True, 'message': f'成功删除系统预设节假日：{holiday.name}（{date_str}）'})
        else:
            return jsonify({'success': True, 'message': f'成功删除用户节假日：{holiday.name}（{date_str}）'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'})