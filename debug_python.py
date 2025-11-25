import sys
import os

print("=== Python 环境诊断 ===")
print(f"Python 版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")

print("\n=== 路径信息 ===")
current_file = os.path.abspath(__file__)
print(f"当前文件: {current_file}")

# 测试不同的路径计算方法
method1 = os.path.dirname(os.path.dirname(current_file))
print(f"方法1 (两层上级): {method1}")

method2 = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
print(f"方法2 (三层上级): {method2}")

# 找到 app 目录
app_dir = None
for root, dirs, files in os.walk(os.getcwd()):
    if 'app' in dirs:
        app_dir = os.path.join(root, 'app')
        break

print(f"找到的 app 目录: {app_dir}")

if app_dir:
    sys.path.insert(0, os.getcwd())
    print(f"已添加到 sys.path: {os.getcwd()}")

print("\n=== sys.path 内容 ===")
for i, path in enumerate(sys.path[:5]):
    print(f"{i}: {path}")

print("\n=== 测试导入 ===")
try:
    import app
    print("✅ 成功导入 app 模块")
except ImportError as e:
    print(f"❌ 导入 app 模块失败: {e}")

try:
    from app import create_app
    print("✅ 成功导入 create_app")
except ImportError as e:
    print(f"❌ 导入 create_app 失败: {e}")

# 检查 __init__.py 文件
print("\n=== 检查 __init__.py 文件 ===")
init_file = os.path.join(os.getcwd(), 'app', '__init__.py')
print(f"app/__init__.py 存在: {os.path.exists(init_file)}")

if os.path.exists(init_file):
    print("app/__init__.py 文件大小:", os.path.getsize(init_file))
else:
    print("app/__init__.py 文件不存在!")