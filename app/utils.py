import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
from functools import wraps
import time
from flask import abort, flash, redirect, url_for, request
from flask_login import current_user

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
AVATAR_SIZE = (150, 150)  # 头像尺寸

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_avatar(file, upload_folder):
    """保存头像文件，返回文件名

    Args:
        file: 上传的文件对象
        upload_folder: 上传目录路径

    Returns:
        str: 保存的文件名，如果失败返回None
    """
    if file and file.filename and allowed_file(file.filename):
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE:
            return None

        # 生成安全的文件名
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()

        # 使用时间戳和UUID生成唯一文件名
        timestamp = str(int(time.time()))
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{unique_id}.{file_extension}"

        # 确保上传目录存在
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, filename)

        try:
            # 保存原始文件
            file.save(file_path)

            # 如果是图片，压缩并调整尺寸
            if file_extension.lower() in ['jpg', 'jpeg', 'png', 'bmp']:
                try:
                    with Image.open(file_path) as img:
                        # 转换为RGB模式（处理RGBA等模式）
                        if img.mode in ('RGBA', 'LA', 'P'):
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'P':
                                img = img.convert('RGBA')
                            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                            img = background

                        # 调整尺寸并保持宽高比
                        img.thumbnail(AVATAR_SIZE, Image.Resampling.LANCZOS)

                        # 保存压缩后的图片
                        if file_extension.lower() == 'png':
                            img.save(file_path, 'PNG', optimize=True)
                        else:
                            img.save(file_path, 'JPEG', quality=85, optimize=True)

                except Exception as e:
                    print(f"图片处理失败: {e}")
                    # 如果图片处理失败，保留原始文件

            return filename

        except Exception as e:
            print(f"文件保存失败: {e}")
            return None

    return None

def delete_avatar(filename, upload_folder):
    """删除头像文件

    Args:
        filename: 要删除的文件名
        upload_folder: 上传目录路径

    Returns:
        bool: 删除是否成功
    """
    if filename:
        file_path = os.path.join(upload_folder, filename)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            print(f"删除文件失败: {e}")
    return False

# =================== 权限控制装饰器 ===================

def super_admin_required(f):
    """超级管理员权限装饰器

    只有超级管理员才能访问的页面使用此装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查用户是否已登录
        if not current_user.is_authenticated:
            flash('请先登录', 'info')
            return redirect(url_for('auth.login', next=request.url))

        # 检查用户是否为超级管理员
        if not current_user.is_super_admin:
            flash('需要超级管理员权限才能访问此功能', 'error')
            return redirect(url_for('main.doctors'))

        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理员权限装饰器（包括超级管理员）

    管理员和超级管理员才能访问的页面使用此装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查用户是否已登录
        if not current_user.is_authenticated:
            flash('请先登录', 'info')
            return redirect(url_for('auth.login', next=request.url))

        # 检查用户是否为管理员或超级管理员
        if not (current_user.is_admin or current_user.is_super_admin):
            flash('需要管理员权限才能访问此功能', 'error')
            return redirect(url_for('main.doctors'))

        return f(*args, **kwargs)
    return decorated_function

def editor_required(f):
    """编辑权限装饰器（管理员、超级管理员或有权限的用户）

    可以编辑用户（包括关联医生的用户）可以访问的页面使用此装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查用户是否已登录
        if not current_user.is_authenticated:
            flash('请先登录以使用此功能', 'info')
            return redirect(url_for('auth.login', next=request.url))

        return f(*args, **kwargs)
    return decorated_function

def get_user_permissions():
    """获取当前用户的权限信息

    Returns:
        dict: 用户权限信息
    """
    if not current_user.is_authenticated:
        return {
            'can_view': True,
            'can_add': False,
            'can_edit': False,
            'can_delete': False,
            'can_manage_users': False,
            'is_admin': False,
            'is_super_admin': False
        }

    if current_user.is_super_admin:
        return {
            'can_view': True,
            'can_add': True,
            'can_edit': True,
            'can_delete': True,
            'can_manage_users': True,
            'can_promote_admin': True,
            'is_admin': True,
            'is_super_admin': True
        }

    if current_user.is_admin:
        return {
            'can_view': True,
            'can_add': True,
            'can_edit': True,
            'can_delete': True,
            'can_manage_users': False,
            'can_promote_admin': False,
            'is_admin': True,
            'is_super_admin': False
        }

    # 普通登录用户
    return {
        'can_view': True,
        'can_add': False,
        'can_edit': False,
        'can_delete': False,
        'can_manage_users': False,
        'can_promote_admin': False,
        'is_admin': False,
        'is_super_admin': False
    }