from flask import Flask, redirect, url_for
from os import path
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)

    
    # 配置
    app.config['SECRET_KEY'] = 'fuyou-scheduling-secret-key-2024'

    # 数据库配置 - 使用SQLite
    basedir = path.abspath(path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{path.join(basedir, "..", "instance", "fuyou.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 文件上传配置
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = path.join(basedir, "static", "uploads", "avatars")

    # 初始化数据库
    from app.extensions import db
    db.init_app(app)

    # 初始化登录管理器
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录以访问此页面'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    # 注册蓝图
    from app.routes import main
    app.register_blueprint(main, url_prefix='/')

    # 注册认证蓝图
    from app.auth_routes import auth
    app.register_blueprint(auth, url_prefix='/auth')

    
    # 注册节假日管理蓝图
    from app.holidays_routes import holidays_bp
    app.register_blueprint(holidays_bp, url_prefix='/')

    # 注册调试路由
    try:
        from flask import render_template_string
        from flask_login import login_required, current_user
        from app.models import User

        @app.route('/debug/users')
        @login_required
        def debug_users():
            """调试用户列表页面"""
            print("DEBUG: Accessing debug user list page")
            print(f"   Current user: {current_user.username}")

            users = User.query.all()
            users_info = []
            for user in users:
                users_info.append({
                    'id': user.id,
                    'username': user.username,
                    'is_admin': user.is_admin,
                    'is_super_admin': user.is_super_admin,
                    'can_be_promoted': not user.is_admin and not user.is_super_admin
                })
                print(f"   User {user.username}: is_admin={user.is_admin}, is_super_admin={user.is_super_admin}")

            return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>调试用户列表</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h1>调试用户列表</h1>
        <div class="alert alert-info">
            <strong>当前用户:</strong> {{ current_user.username }}
            {% if current_user.is_super_admin %}
                <span class="badge bg-danger">超级管理员</span>
            {% elif current_user.is_admin %}
                <span class="badge bg-warning">管理员</span>
            {% else %}
                <span class="badge bg-secondary">普通用户</span>
            {% endif %}
        </div>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>用户名</th>
                    <th>当前角色</th>
                    <th>数据库状态</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                {% for info in users_info %}
                <tr>
                    <td>{{ info.username }}</td>
                    <td>
                        {% if info.is_super_admin %}
                            <span class="badge bg-danger">超级管理员</span>
                        {% elif info.is_admin %}
                            <span class="badge bg-warning">管理员</span>
                        {% else %}
                            <span class="badge bg-secondary">普通用户</span>
                        {% endif %}
                    </td>
                    <td>
                        <small>
                            is_admin: {{ info.is_admin }}<br>
                            is_super_admin: {{ info.is_super_admin }}
                        </small>
                    </td>
                    <td>
                        {% if info.can_be_promoted and (current_user.is_admin or current_user.is_super_admin) %}
                        <form method="POST" action="/debug/toggle_admin/{{ info.id }}" style="display: inline;">
                            <button type="submit" class="btn btn-sm btn-success" onclick="return confirm('确定要将 {{ info.username }} 设为管理员吗？')">
                                设为管理员
                            </button>
                        </form>
                        {% else %}
                            <button class="btn btn-sm btn-secondary" disabled>不能操作</button>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <div class="mt-3">
            <a href="/users" class="btn btn-primary">返回用户管理</a>
            <a href="/debug_simple" class="btn btn-secondary">测试简单路由</a>
        </div>
    </div>
</body>
</html>
            ''', users_info=users_info)

        @app.route('/debug/toggle_admin/<int:user_id>', methods=['POST'])
        @login_required
        def debug_toggle_admin(user_id):
            """调试版本的切换管理员权限"""
            print(f"\\nDEBUG: debug_toggle_admin called - user_id: {user_id}")

            user = User.query.get_or_404(user_id)
            print(f"   Target user: {user.username}")
            print(f"   Before toggle: is_admin={user.is_admin}")

            if user.id == current_user.id:
                flash('不能修改自己的管理员权限', 'error')
                return redirect('/debug/users')

            if not (current_user.is_admin or current_user.is_super_admin):
                flash('没有管理权限', 'error')
                return redirect('/debug/users')

            try:
                user.is_admin = not user.is_admin
                from app.extensions import db
                db.session.commit()

                print(f"   Toggle successful: is_admin={user.is_admin}")
                status = "Admin" if user.is_admin else "Regular User"
                flash(f'Debug success! Set {user.username} as {status}', 'success')

            except Exception as e:
                from app.extensions import db
                db.session.rollback()
                print(f"   Error: {e}")
                flash(f'Operation failed: {str(e)}', 'error')

            return redirect('/debug/users')

        print("调试路由已成功注册")

    except Exception as e:
        print(f"调试路由注册失败: {e}")
        import traceback
        traceback.print_exc()

    # 创建数据库表
    with app.app_context():
        # 智能检测数据库结构并更新
        smart_database_update()

        # 输出当前医生表数据
        from app.models import Doctor
        doctors = Doctor.query.all()

        print("\n" + "="*50)
        print("Fuyou Scheduling System - Current Data Status")
        print("="*50)
        print(f"Total doctors: {len(doctors)}")

        if doctors:
            print("\nDoctor details:")
            for i, doctor in enumerate(doctors, 1):
                print(f"\n{i}. {doctor.name} ({doctor.gender})")
                print(f"   Specialties: {doctor.get_specialties_display()}")
                print(f"   Annual leave: {doctor.annual_leave_days - doctor.used_leave_days}/{doctor.annual_leave_days} days")
                print(f"   Avatar: {'Yes' if doctor.avatar else 'No'}")
        else:
            print("\nNo doctor data available")
        print("="*50 + "\n")

    return app

def smart_database_update():
    """智能检测并更新数据库结构"""
    import sqlalchemy as sa
    from app.models import User, Doctor, Specialty, ShiftType, Holiday
    from app.extensions import db

    try:
        # 检查表是否存在
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()

        print("Checking database structure...")
        print(f"   Existing tables: {existing_tables}")

        # 检查doctors表的字段
        if 'doctors' in existing_tables:
            columns = [column['name'] for column in inspector.get_columns('doctors')]
            print(f"   doctors table columns: {columns}")

            # 检查并添加缺失的字段
            need_column_update = False
            if 'title' not in columns:
                print("+ Need to add title field")
                need_column_update = True

            if 'status' not in columns:
                print("+ Need to add status field")
                need_column_update = True

            if 'sequence' not in columns:
                print("+ Need to add sequence field")
                need_column_update = True

            # 总是检查并更新现有记录的NULL值
            need_value_update = 'title' not in columns or 'status' not in columns

            if need_column_update or need_value_update:
                print("Updating doctors table fields...")
                # 使用SQLite的ALTER TABLE命令添加字段
                with db.engine.connect() as conn:
                    if 'title' not in columns:
                        conn.execute(db.text("ALTER TABLE doctors ADD COLUMN title VARCHAR(20) DEFAULT '打字员'"))
                        print("title field added")

                    if 'status' not in columns:
                        conn.execute(db.text("ALTER TABLE doctors ADD COLUMN status VARCHAR(10) DEFAULT '在职'"))
                        print("status field added")

                    if 'sequence' not in columns:
                        conn.execute(db.text("ALTER TABLE doctors ADD COLUMN sequence INTEGER DEFAULT 999"))
                        print("sequence field added")

                    # 总是更新现有记录的NULL值，确保数据完整性
                    result = conn.execute(db.text("""
                        UPDATE doctors
                        SET title = COALESCE(title, '打字员'),
                            status = COALESCE(status, '在职'),
                            sequence = COALESCE(sequence, 999)
                    """))
                    if result.rowcount > 0:
                        print(f"Updated {result.rowcount} doctor records with title, status and sequence")
                    else:
                        print("All doctor records already have title and status set")

                    conn.commit()

        # 检查schedules表的字段
        if 'schedules' in existing_tables:
            columns = [column['name'] for column in inspector.get_columns('schedules')]
            print(f"   schedules table columns: {columns}")

            # 检查是否需要重构schedules表（因为新的模型结构与旧版本差异很大）
            old_columns = ['specialty_id', 'shift_type_id']
            new_columns = ['weekday', 'shift', 'time_range', 'department']

            need_rebuild = any(col in columns for col in old_columns) or not all(col in columns for col in new_columns)

            if need_rebuild:
                print("Rebuilding schedules table for new scheduling system...")
                with db.engine.connect() as conn:
                    # 备份现有数据（如果有的话）
                    existing_schedules = conn.execute(db.text("SELECT COUNT(*) FROM schedules")).scalar()
                    print(f"   Existing schedule records: {existing_schedules}")

                    # 重建表结构
                    conn.execute(db.text("DROP TABLE IF EXISTS schedules"))
                    conn.execute(db.text("""
                        CREATE TABLE schedules (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            doctor_id INTEGER,
                            date DATE NOT NULL,
                            weekday VARCHAR(10) NOT NULL,
                            shift VARCHAR(20) NOT NULL,
                            time_range VARCHAR(20) NOT NULL,
                            department VARCHAR(50) NOT NULL,
                            status VARCHAR(20) DEFAULT 'unassigned',
                            notes TEXT,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    """))

                    # 创建索引
                    conn.execute(db.text("CREATE INDEX ix_schedules_date ON schedules (date)"))
                    conn.execute(db.text("CREATE INDEX ix_schedules_doctor_id ON schedules (doctor_id)"))

                    print("schedules table rebuilt with new format")
                    conn.commit()

        # 检查users表的字段
        if 'users' in existing_tables:
            columns = [column['name'] for column in inspector.get_columns('users')]
            print(f"   users table columns: {columns}")

            # 检查并添加缺失的字段
            need_column_update = False
            if 'is_super_admin' not in columns:
                print("+ Need to add is_super_admin field")
                need_column_update = True

            if 'associated_doctor_id' not in columns:
                print("+ Need to add associated_doctor_id field")
                need_column_update = True

            # 检查是否需要删除email字段
            if 'email' in columns:
                print("- Need to remove email field")
                need_column_update = True

            if need_column_update:
                print("Updating users table fields...")
                # 使用SQLite的ALTER TABLE命令添加字段
                with db.engine.connect() as conn:
                    if 'is_super_admin' not in columns:
                        conn.execute(db.text("ALTER TABLE users ADD COLUMN is_super_admin BOOLEAN DEFAULT 0"))
                        print("is_super_admin field added")

                    if 'associated_doctor_id' not in columns:
                        conn.execute(db.text("ALTER TABLE users ADD COLUMN associated_doctor_id INTEGER"))
                        print("associated_doctor_id field added")

                    # 删除email字段需要重建表（SQLite不支持直接删除列）
                    if 'email' in columns:
                        print("Rebuilding users table to remove email field...")
                        conn.execute(db.text("""
                            CREATE TABLE users_new (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username VARCHAR(80) NOT NULL UNIQUE,
                                password_hash VARCHAR(255) NOT NULL,
                                is_admin BOOLEAN DEFAULT 0,
                                is_super_admin BOOLEAN DEFAULT 0,
                                full_name VARCHAR(50),
                                created_at DATETIME,
                                last_login DATETIME,
                                is_active BOOLEAN DEFAULT 1,
                                associated_doctor_id INTEGER
                            )
                        """))

                        # 迁移数据（不包含email）
                        result = conn.execute(db.text("""
                            INSERT INTO users_new (
                                id, username, password_hash, is_admin, is_super_admin,
                                full_name, created_at, last_login, is_active, associated_doctor_id
                            )
                            SELECT
                                id, username, password_hash, is_admin, is_super_admin,
                                full_name, created_at, last_login, is_active, associated_doctor_id
                            FROM users
                        """))

                        migrated_rows = result.rowcount
                        print(f"Migrated {migrated_rows} user records")

                        # 替换表
                        conn.execute(db.text("DROP TABLE users"))
                        conn.execute(db.text("ALTER TABLE users_new RENAME TO users"))

                        # 重建索引
                        conn.execute(db.text("CREATE UNIQUE INDEX ix_users_username ON users (username)"))

                        print("email field removed")

                    conn.commit()

        # 创建所有表（如果不存在）
        db.create_all()
        print("Ensured all tables exist")

        # 检查新表是否被创建
        new_tables = []
        required_tables = ['users', 'doctors', 'specialties', 'shift_types', 'schedules', 'work_hours', 'work_scores', 'holidays']

        for table in required_tables:
            if table not in existing_tables:
                new_tables.append(table)

        # 如果有新表，初始化基础数据
        if new_tables:
            print(f"New tables detected: {new_tables}")
            # 初始化基础数据
            from app import init_data
            init_data.init_all_data()
            print("Basic data initialization completed")
        else:
            print("Database structure is up to date, keeping existing data")
            # 检查并补充基础数据（如果需要）
            from app import init_data
            init_data.init_all_data()
            print("Basic data check completed")

        # 检查并更新超级管理员
        from app.models import User
        admin_users = User.query.filter_by(is_admin=True).all()
        super_admin_users = User.query.filter_by(is_super_admin=True).all()

        if admin_users and not super_admin_users:
            # 如果有管理员但没有超级管理员，提升第一个管理员为超级管理员
            first_admin = admin_users[0]
            first_admin.is_super_admin = True
            db.session.commit()
            print(f"Promoted user {first_admin.username} to super administrator")
        elif admin_users and super_admin_users:
            print(f"Current super administrators: {[u.username for u in super_admin_users]}")

    except Exception as e:
        print(f"Database update failed: {e}")
        print("Attempting to recreate database...")
        # 如果智能更新失败，回退到重建数据库
        db.drop_all()
        db.create_all()
        from app import init_data
        init_data.init_all_data()
        print("Database has been recreated, original data cleared")