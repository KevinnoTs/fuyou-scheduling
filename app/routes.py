from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app.models import Doctor, Specialty, User
from app.extensions import db
from app.utils import save_avatar, delete_avatar, admin_required, editor_required, super_admin_required
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """首页 - 默认显示当月排班"""
    return redirect(url_for('schedules.index'))

# ========== 医生管理相关路由 ==========

@main.route('/doctors')
def doctors():
    """医生列表页面"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    query = Doctor.query
    if search:
        query = query.filter(Doctor.name.like(f'%{search}%'))

    doctors = query.order_by(Doctor.sequence.asc(), Doctor.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )

    return render_template('doctors/index.html',
                         doctors=doctors,
                         search=search)

@main.route('/doctors/add', methods=['GET', 'POST'])
@admin_required
def add_doctor():
    """添加医生页面"""
    specialties = Specialty.query.all()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        gender = request.form.get('gender')
        title = request.form.get('title', '打字员')
        status = request.form.get('status', '在职')
        specialties_list = request.form.getlist('specialties')  # 获取多选的擅长方向
        annual_leave_days = request.form.get('annual_leave_days', 0, type=int)
        used_leave_days = request.form.get('used_leave_days', 0, type=int)
        sequence = request.form.get('sequence', 999, type=int)  # 默认序号999，显示在最后

        # 表单验证
        error = None
        if not name:
            error = '请输入医生姓名'
        elif not gender:
            error = '请选择性别'
        elif not title:
            error = '请选择职称'
        elif not status:
            error = '请选择在职状态'
        elif not specialties_list:
            error = '请至少选择一个擅长方向'
        elif annual_leave_days < 0:
            error = '年假天数不能为负数'

        if error:
            flash(error, 'error')
            return render_template('doctors/add.html',
                                 specialties=specialties,
                                 name=name,
                                 gender=gender,
                                 annual_leave_days=annual_leave_days)

        # 处理头像上传
        avatar = None
        cropped_avatar_data = request.form.get('croppedAvatar')

        # 优先处理裁剪后的图片（base64数据）
        if cropped_avatar_data:
            try:
                import base64
                from io import BytesIO
                from PIL import Image
                import os
                import uuid

                # 解析base64数据
                if 'base64,' in cropped_avatar_data:
                    base64_string = cropped_avatar_data.split('base64,')[1]
                else:
                    base64_string = cropped_avatar_data

                # 解码base64数据
                image_data = base64.b64decode(base64_string)

                # 使用PIL处理图片
                img = Image.open(BytesIO(image_data))

                # 生成唯一的文件名
                filename = f"avatar_temp_{uuid.uuid4().hex[:8]}.jpg"

                # 确保上传目录存在
                upload_folder = current_app.config['UPLOAD_FOLDER']
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                # 保存图片
                filepath = os.path.join(upload_folder, filename)
                img.save(filepath, 'JPEG', quality=90, optimize=True)

                avatar = filename

            except Exception as e:
                flash(f'头像裁剪处理失败：{str(e)}', 'error')

        # 如果没有裁剪数据，处理传统文件上传
        elif 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '':
                avatar = save_avatar(file, current_app.config['UPLOAD_FOLDER'])
                if not avatar:
                    flash('头像上传失败，请检查文件格式和大小', 'warning')

        # 创建医生记录
        doctor = Doctor(
            name=name,
            gender=gender,
            title=title,
            status=status,
            specialties=None,  # 稍后设置
            annual_leave_days=annual_leave_days,
            used_leave_days=used_leave_days,
            sequence=sequence,  # 设置序号
            avatar=avatar
        )

        # 设置擅长方向列表
        doctor.set_specialties_list(specialties_list)

        try:
            db.session.add(doctor)
            db.session.commit()
            flash(f'医生 {name} 添加成功！', 'success')
            return redirect(url_for('main.doctors'))
        except Exception as e:
            db.session.rollback()
            # 如果创建记录失败，删除已上传的头像
            if avatar:
                delete_avatar(avatar, current_app.config['UPLOAD_FOLDER'])
            flash(f'添加失败：{str(e)}', 'error')

    return render_template('doctors/add.html', specialties=specialties)

@main.route('/doctors/<int:doctor_id>/edit', methods=['GET', 'POST'])
@editor_required
def edit_doctor(doctor_id):
    """编辑医生页面"""
    doctor = Doctor.query.get_or_404(doctor_id)
    specialties = Specialty.query.all()

    if request.method == 'POST':
        # 检查用户权限
        can_edit_all = current_user.can_edit_doctor_info(doctor_id)
        can_edit_avatar_only = current_user.can_edit_doctor_avatar(doctor_id) and not can_edit_all

        name = request.form.get('name', '').strip()
        gender = request.form.get('gender')
        title = request.form.get('title')
        status = request.form.get('status')
        specialties_list = request.form.getlist('specialties')
        annual_leave_days = request.form.get('annual_leave_days', 0, type=int)
        used_leave_days = request.form.get('used_leave_days', 0, type=int)
        sequence = request.form.get('sequence', 999, type=int)

        # 如果只能编辑头像，验证其他字段是否被修改
        if can_edit_avatar_only:
            if (name != doctor.name or
                gender != doctor.gender or
                title != doctor.title or
                status != doctor.status or
                set(specialties_list) != set(doctor.get_specialties_list()) or
                annual_leave_days != doctor.annual_leave_days):
                flash('关联用户只能修改头像，不能修改医生基本信息', 'error')
                return render_template('doctors/edit.html',
                                     doctor=doctor,
                                     specialties=specialties,
                                     can_edit_avatar_only=True)

        # 表单验证（只有能编辑全部信息的用户才需要验证）
        error = None
        if can_edit_all:
            if not name:
                error = '请输入医生姓名'
            elif not gender:
                error = '请选择性别'
            elif not title:
                error = '请选择职称'
            elif not status:
                error = '请选择在职状态'
            elif not specialties_list:
                error = '请至少选择一个擅长方向'
            elif annual_leave_days < 0:
                error = '年假天数不能为负数'

        if error:
            flash(error, 'error')
            return render_template('doctors/edit.html',
                                 doctor=doctor,
                                 specialties=specialties,
                                 can_edit_avatar_only=can_edit_avatar_only)

        # 处理头像更新
        new_avatar = None
        cropped_avatar_data = request.form.get('croppedAvatar')

        # 优先处理裁剪后的图片（base64数据）
        if cropped_avatar_data:
            try:
                import base64
                from io import BytesIO
                from PIL import Image
                import os
                import uuid

                # 解析base64数据
                if 'base64,' in cropped_avatar_data:
                    base64_string = cropped_avatar_data.split('base64,')[1]
                else:
                    base64_string = cropped_avatar_data

                # 解码base64数据
                image_data = base64.b64decode(base64_string)

                # 使用PIL处理图片
                img = Image.open(BytesIO(image_data))

                # 生成唯一的文件名
                filename = f"avatar_{doctor.id}_{uuid.uuid4().hex[:8]}.jpg"

                # 确保上传目录存在
                upload_folder = current_app.config['UPLOAD_FOLDER']
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                # 保存图片
                filepath = os.path.join(upload_folder, filename)
                img.save(filepath, 'JPEG', quality=90, optimize=True)

                new_avatar = filename

            except Exception as e:
                flash(f'头像裁剪处理失败：{str(e)}', 'error')

        # 如果没有裁剪数据，处理传统文件上传
        elif 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '':
                new_avatar = save_avatar(file, current_app.config['UPLOAD_FOLDER'])
                if not new_avatar:
                    flash('头像上传失败，请检查文件格式和大小', 'warning')

        # 更新医生信息（只有有权限的用户才能修改）
        old_avatar = doctor.avatar
        if can_edit_all:
            doctor.name = name
            doctor.gender = gender
            doctor.title = title
            doctor.status = status
            doctor.annual_leave_days = annual_leave_days
            doctor.used_leave_days = used_leave_days
            # 更新擅长方向
            doctor.set_specialties_list(specialties_list)

        # 超级管理员可以修改序号
        if current_user.is_super_admin:
            doctor.sequence = sequence

        if new_avatar:
            doctor.avatar = new_avatar

        try:
            db.session.commit()

            # 如果更新了头像，删除旧头像
            if new_avatar and old_avatar:
                delete_avatar(old_avatar, current_app.config['UPLOAD_FOLDER'])

            flash(f'医生 {name} 更新成功！', 'success')
            return redirect(url_for('main.doctors'))
        except Exception as e:
            db.session.rollback()
            # 如果更新失败，删除新上传的头像
            if new_avatar:
                delete_avatar(new_avatar, current_app.config['UPLOAD_FOLDER'])
            flash(f'更新失败：{str(e)}', 'error')

    # 检查用户权限
    can_edit_all = current_user.can_edit_doctor_info(doctor_id)
    can_edit_avatar_only = current_user.can_edit_doctor_avatar(doctor_id) and not can_edit_all

    return render_template('doctors/edit.html',
                         doctor=doctor,
                         specialties=specialties,
                         can_edit_all=can_edit_all,
                         can_edit_avatar_only=can_edit_avatar_only)

@main.route('/doctors/<int:doctor_id>/delete', methods=['POST'])
@super_admin_required
def delete_doctor(doctor_id):
    """删除医生"""
    doctor = Doctor.query.get_or_404(doctor_id)

    try:
        # 删除头像文件
        if doctor.avatar:
            delete_avatar(doctor.avatar, current_app.config['UPLOAD_FOLDER'])

        db.session.delete(doctor)
        db.session.commit()

        flash(f'医生 {doctor.name} 删除成功！', 'success')
        return redirect(url_for('main.doctors'))
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'error')
        return redirect(url_for('main.doctors'))

@main.route('/doctors/<int:doctor_id>')
def view_doctor(doctor_id):
    """查看医生详情"""
    doctor = Doctor.query.get_or_404(doctor_id)

    # 获取统计信息
    from datetime import date
    today = date.today()
    current_year = today.year
    current_month = today.month

    stats = {
        'monthly_schedules': doctor.get_monthly_schedules_count(current_year, current_month),
        'monthly_hours': doctor.get_monthly_work_hours(current_year, current_month),
        'monthly_score': doctor.get_monthly_work_score(current_year, current_month),
        'yearly_score': doctor.get_yearly_work_score(current_year),
        'current_year': current_year,
        'current_month': current_month
    }

    return render_template('doctors/view.html', doctor=doctor, stats=stats)


# ========== 用户-医生关联功能 ==========

@main.route('/users/<int:user_id>/associate_doctor', methods=['GET', 'POST'])
@admin_required
def associate_doctor(user_id):
    """关联用户与医生"""
    user = User.query.get_or_404(user_id)

    # 权限检查：普通管理员不能关联超级管理员，但超级管理员可以关联其他超级管理员（不能关联自己）
    if not current_user.is_super_admin and user.is_super_admin:
        flash('普通管理员不能关联超级管理员账户', 'error')
        return redirect(url_for('main.users'))

    doctors = Doctor.query.all()

    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        action = request.form.get('action')  # 'associate' or 'dissociate'

        try:
            if action == 'associate' and doctor_id:
                # 关联用户与医生
                user.associate_with_doctor(int(doctor_id))
                flash(f'已将用户 {user.username} 与医生关联', 'success')
            elif action == 'dissociate':
                # 取消关联
                user.dissociate_doctor()
                flash(f'已取消用户 {user.username} 的医生关联', 'success')
            else:
                flash('操作无效', 'error')

        except Exception as e:
            flash(f'操作失败：{str(e)}', 'error')

        return redirect(url_for('main.users'))

    return render_template('users/associate_doctor.html',
                         user=user,
                         doctors=doctors)

# ========== 调试路由 ==========

@main.route('/debug_simple')
def debug_simple():
    """简单的调试路由"""
    return "调试路由正常工作！"

@main.route('/debug_db_status')
def debug_db_status():
    """数据库状态调试"""
    try:
        from app.models import User
        users = User.query.all()
        user_info = []
        for user in users:
            user_info.append(f"{user.username}: is_admin={user.is_admin}, is_super_admin={user.is_super_admin}")

        return "<h1>数据库用户状态</h1><pre>" + "\n".join(user_info) + "</pre>"
    except Exception as e:
        return f"错误: {str(e)}"

# ========== 用户管理相关路由 ==========

@main.route('/users')
@admin_required
def users():
    """用户管理页面"""
    print("DEBUG: Accessing user management page")
    print(f"   Current user: {current_user.username}")

    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    query = User.query

    # 打印所有用户的权限状态（仅第一页）
    if page == 1:
        all_users = query.all()
        print("   Current user permissions in database:")
        for user in all_users[:10]:  # 只显示前10个
            role = "Regular User"
            if user.is_super_admin:
                role = "Super Administrator"
            elif user.is_admin:
                role = "Administrator"
            print(f"     {user.username:<15} - {role} (is_admin={user.is_admin}, is_super_admin={user.is_super_admin})")
    if search:
        query = query.filter(
            User.username.like(f'%{search}%') |
            User.full_name.like(f'%{search}%')
        )

    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )

    return render_template('users/index.html', users=users, search=search)

@main.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """编辑用户"""
    user = User.query.get_or_404(user_id)

    # 权限检查：所有用户都可以编辑自己，管理员可以编辑普通用户，超级管理员可以编辑所有用户
    if not current_user.is_super_admin and user.id != current_user.id and not current_user.is_admin:
        flash('您没有权限编辑其他用户', 'error')
        return redirect(url_for('auth.profile'))

    if not current_user.is_super_admin and not current_user.is_admin and user.id != current_user.id:
        flash('普通用户只能编辑自己的信息', 'error')
        return redirect(url_for('auth.profile'))

    if not current_user.is_super_admin and current_user.is_admin and user.id != current_user.id and (user.is_admin or user.is_super_admin):
        flash('普通管理员只能编辑自己和普通用户', 'error')
        return redirect(url_for('main.users'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        is_admin = 'is_admin' in request.form
        is_active = 'is_active' in request.form

        # 密码管理（超级管理员可以修改任何人密码，管理员只能修改自己密码）
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # 表单验证
        error = None

        # 密码验证权限检查
        can_modify_password = False
        if current_user.is_super_admin:
            # 超级管理员可以修改任何人的密码
            can_modify_password = True
        elif current_user.is_admin and not current_user.is_super_admin:
            # 普通管理员只能修改自己密码
            if user.id == current_user.id:
                can_modify_password = True
        elif not current_user.is_admin:
            # 普通用户只能修改自己密码
            if user.id == current_user.id:
                can_modify_password = True

        # 密码格式验证
        if can_modify_password and new_password:
            if len(new_password) < 6:
                error = '密码长度至少6位'
            elif new_password != confirm_password:
                error = '两次输入的密码不一致'

        if error:
            flash(error, 'error')
            return render_template('users/edit.html', user=user)

        # 防止用户禁用自己
        if user.id == current_user.id and not is_active:
            flash('不能禁用自己的账户', 'error')
            return render_template('users/edit.html', user=user)

        # 防止用户取消自己的管理员权限
        if user.id == current_user.id and (current_user.is_admin or current_user.is_super_admin) and not is_admin:
            admin_count = User.query.filter_by(is_admin=True).count()
            if admin_count <= 1:
                flash('不能取消自己的管理员权限（至少需要保留一个管理员）', 'error')
                return render_template('users/edit.html', user=user)

        try:
            user.full_name = full_name

            # 密码修改
            if can_modify_password and new_password:
                user.set_password(new_password)
                if user.id == current_user.id:
                    flash(f'密码修改成功！', 'success')
                else:
                    flash(f'已强制修改用户 {user.username} 的密码！', 'warning')

            # 只有超级管理员可以修改用户权限
            if current_user.is_super_admin:
                user.is_super_admin = request.form.get('is_super_admin') == 'on'
                user.is_admin = is_admin
            else:
                # 普通管理员不能修改用户的管理员状态
                pass

            user.is_active = is_active

            db.session.commit()

            # 如果没有修改密码，显示普通成功信息
            if not (can_modify_password and new_password):
                if user.id == current_user.id:
                    flash('个人资料更新成功！', 'success')
                else:
                    flash(f'用户 {user.username} 更新成功！', 'success')

            # 根据操作类型决定重定向目标
            if user.id == current_user.id:
                return redirect(url_for('auth.profile'))
            else:
                return redirect(url_for('main.users'))

        except Exception as e:
            db.session.rollback()
            flash(f'更新失败：{str(e)}', 'error')

    # 根据操作类型决定渲染模板
    if user.id == current_user.id:
        return render_template('users/edit.html', user=user, editing_self=True)
    else:
        return render_template('users/edit.html', user=user)

@main.route('/users/<int:user_id>/toggle_admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    """切换用户管理员状态"""
    print(f"DEBUG: toggle_admin called")
    print(f"   user_id: {user_id}")
    print(f"   current_user: {current_user.username} (is_admin={current_user.is_admin}, is_super_admin={current_user.is_super_admin})")

    user = User.query.get_or_404(user_id)
    print(f"   target_user: {user.username} (is_admin={user.is_admin}, is_super_admin={user.is_super_admin})")

    # 防止用户修改自己的管理员状态
    if user.id == current_user.id:
        flash('不能修改自己的管理员权限', 'error')
        return redirect(url_for('main.users'))

    # 权限检查逻辑
    if user.is_admin:
        print("   User is already admin, executing cancel admin logic")
        # 取消管理员权限的情况
        if not current_user.is_super_admin:
            print("   Regular admin cannot cancel other admin's permissions")
            # 普通管理员不能取消其他管理员的权限
            flash('普通管理员不能修改其他管理员的权限', 'error')
            return redirect(url_for('main.users'))

        # 超级管理员取消管理员权限时检查是否是最后一个管理员
        admin_count = User.query.filter_by(is_admin=True).count()
        print(f"   Current admin count: {admin_count}")
        if admin_count <= 1:
            print("   Cannot cancel the last admin")
            flash('不能取消最后一个管理员的管理员权限', 'error')
            return redirect(url_for('main.users'))

    else:
        print("   User is regular user, executing set admin logic")

    # 对于普通用户，管理员和超级管理员都可以设为管理员（继续执行）

    try:
        print(f"   Starting permission toggle: {user.username} is_admin={user.is_admin}")
        user.is_admin = not user.is_admin
        print(f"   Permission toggle completed: {user.username} is_admin={user.is_admin}")

        # 提交数据库更改
        db.session.commit()
        print(f"   Database commit successful")

        status = "管理员" if user.is_admin else "普通用户"
        flash(f'已将 {user.username} 设置为{status}', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'操作失败：{str(e)}', 'error')
        print(f"   Database commit failed: {e}")

    return redirect(url_for('main.users'))

@main.route('/users/<int:user_id>/toggle_super_admin', methods=['POST'])
@super_admin_required
def toggle_super_admin(user_id):
    """切换用户超级管理员状态"""
    user = User.query.get_or_404(user_id)

    # 防止用户修改自己的超级管理员状态
    if user.id == current_user.id:
        flash('不能修改自己的超级管理员权限', 'error')
        return redirect(url_for('main.users'))

    # 防止取消最后一个超级管理员
    if user.is_super_admin:
        super_admin_count = User.query.filter_by(is_super_admin=True).count()
        if super_admin_count <= 1:
            flash('不能取消最后一个超级管理员', 'error')
            return redirect(url_for('main.users'))

    try:
        # 保存原始管理员状态
        original_is_admin = user.is_admin

        if not user.is_super_admin:
            # 设置为超级管理员时，自动设为管理员
            user.is_super_admin = True
            user.is_admin = True
            action = "超级管理员"
        else:
            # 取消超级管理员权限时，保留管理员权限
            user.is_super_admin = False
            # 保持原有的管理员权限不变
            action = "超级管理员权限"

        db.session.commit()

        if not user.is_super_admin:
            if user.is_admin:
                status = "管理员"
            else:
                status = "普通用户"
        else:
            status = "超级管理员"

        flash(f'已将 {user.username} 设置为{status}', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'操作失败：{str(e)}', 'error')

    return redirect(url_for('main.users'))

@main.route('/users/<int:user_id>/toggle_status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """切换用户状态（启用/禁用）"""
    user = User.query.get_or_404(user_id)

    # 防止用户禁用自己
    if user.id == current_user.id:
        flash('不能禁用自己的账户', 'error')
        return redirect(url_for('main.users'))

    # 普通管理员不能禁用其他管理员（包括超级管理员）
    if not current_user.is_super_admin and (user.is_admin or user.is_super_admin):
        flash('普通管理员不能禁用管理员账户', 'error')
        return redirect(url_for('main.users'))

    try:
        user.is_active = not user.is_active
        db.session.commit()

        status = "启用" if user.is_active else "禁用"
        flash(f'已{status}用户 {user.username}', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'操作失败：{str(e)}', 'error')

    return redirect(url_for('main.users'))