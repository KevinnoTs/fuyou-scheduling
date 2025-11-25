#!/usr/bin/env python3
"""
服务器环境诊断脚本
用于检查部署环境和问题诊断
"""

import sys
import os

def check_python_environment():
    """检查Python环境"""
    print("🐍 Python环境检查:")
    print(f"   Python版本: {sys.version}")
    print(f"   Python路径: {sys.executable}")
    print(f"   当前目录: {os.getcwd()}")

    try:
        import flask
        print(f"   ✅ Flask版本: {flask.__version__}")
    except ImportError:
        print("   ❌ Flask未安装")
        return False

    return True

def check_project_files():
    """检查项目文件"""
    print("\n📁 项目文件检查:")

    required_files = [
        'app/__init__.py',
        'app/models.py',
        'app/routes.py',
        'run.py',
        'requirements.txt'
    ]

    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - 缺失")
            return False

    return True

def check_imports():
    """检查模块导入"""
    print("\n📦 模块导入检查:")

    try:
        print("   测试导入app模块...")
        from app import create_app
        print("   ✅ app.create_app 导入成功")

        print("   测试创建应用...")
        app = create_app()
        print("   ✅ Flask应用创建成功")

        print("   测试应用上下文...")
        with app.app_context():
            print("   ✅ 应用上下文创建成功")

            from app.extensions import db
            print("   ✅ 数据库扩展导入成功")

            db.create_all()
            print("   ✅ 数据库表创建成功")

            return True

    except Exception as e:
        print(f"   ❌ 导入错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database():
    """检查数据库"""
    print("\n💾 数据库检查:")

    try:
        from app import create_app
        app = create_app()

        with app.app_context():
            from app.models import User, Doctor, Holiday
            from app.extensions import db

            # 检查表是否存在
            tables = db.engine.table_names()
            print(f"   数据库表: {tables}")

            # 检查数据
            user_count = User.query.count()
            doctor_count = Doctor.query.count()
            holiday_count = Holiday.query.count()

            print(f"   用户数量: {user_count}")
            print(f"   医生数量: {doctor_count}")
            print(f"   节假日数量: {holiday_count}")

            return True

    except Exception as e:
        print(f"   ❌ 数据库检查错误: {e}")
        return False

def main():
    print("🔍 Fuyou Scheduling 服务器环境诊断")
    print("=" * 50)

    # 检查Python环境
    if not check_python_environment():
        print("\n❌ Python环境检查失败，请先安装必要依赖")
        return

    # 检查项目文件
    if not check_project_files():
        print("\n❌ 项目文件检查失败，请确保在正确的项目目录")
        return

    # 检查模块导入
    if not check_imports():
        print("\n❌ 模块导入检查失败，请检查代码")
        return

    # 检查数据库
    if check_database():
        print("\n✅ 所有检查通过！")

        # 如果没有数据，提示初始化
        from app import create_app
        app = create_app()
        with app.app_context():
            from app.models import User
            if User.query.count() == 0:
                print("\n💡 数据库为空，需要初始化数据")
                print("   请运行: from app import init_data; init_data.init_all_data()")
            else:
                print("\n✅ 数据库已有数据，可以正常使用")
    else:
        print("\n❌ 数据库检查失败")

if __name__ == '__main__':
    main()