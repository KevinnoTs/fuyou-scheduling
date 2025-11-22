from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.extensions import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    # 如果用户已经登录，重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('main.doctors'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False

        # 表单验证
        error = None
        if not username:
            error = '请输入用户名'
        elif not password:
            error = '请输入密码'

        if error:
            flash(error, 'error')
            return render_template('auth/login.html')

        # 查找用户
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if user.is_active:
                login_user(user, remember=remember)
                user.update_last_login()

                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)

                flash(f'欢迎回来，{user.full_name or user.username}！', 'success')
                return redirect(url_for('main.doctors'))
            else:
                flash('您的账户已被禁用，请联系管理员', 'error')
        else:
            flash('用户名或密码错误', 'error')

    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    # 如果用户已经登录，重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('main.doctors'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()

        # 表单验证
        error = None
        if not username:
            error = '请输入用户名'
        elif not password:
            error = '请输入密码'
        elif len(password) < 6:
            error = '密码长度至少为6位'
        elif password != confirm_password:
            error = '两次输入的密码不一致'

        if error:
            flash(error, 'error')
            return render_template('auth/register.html',
                                 username=username,
                                 full_name=full_name)

        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'error')
            return render_template('auth/register.html',
                                 username=username,
                                 full_name=full_name)

        # 创建新用户
        try:
            user = User(
                username=username,
                full_name=full_name
            )
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            flash(f'注册成功！欢迎加入，{full_name or username}！', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash(f'注册失败：{str(e)}', 'error')

    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    flash('您已成功退出登录', 'success')
    return redirect(url_for('main.doctors'))

@auth.route('/profile')
@login_required
def profile():
    """用户资料"""
    return render_template('auth/profile.html')