#!/usr/bin/env python3
"""
年度重置脚本
每年1月1号将所有医生的已休天数重置为0
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Doctor
from app.extensions import db

def reset_annual_leave():
    """重置所有医生的已休天数为0"""
    app = create_app()
    with app.app_context():
        try:
            print(" 开始年度重置...")

            # 检查当前日期是否为1月1号
            today = datetime.now()
            if today.month != 1 or today.day != 1:
                print(f"⚠️  当前日期 {today.strftime('%Y-%m-%d')} 不是1月1号")
                print("💡 如果确实需要重置，请使用 --force 参数")
                return

            # 获取所有医生
            doctors = Doctor.query.all()
            reset_count = 0

            print(f" 找到 {len(doctors)} 名医生")

            for doctor in doctors:
                if doctor.used_leave_days > 0:
                    print(f" 重置医生 {doctor.name} 的已休天数: {doctor.used_leave_days} → 0")
                    doctor.used_leave_days = 0
                    reset_count += 1
                else:
                    print(f" 医生 {doctor.name} 已休天数已为0，无需重置")

            # 提交更改
            db.session.commit()

            print(f"\n 年度重置完成！")
            print(f" 统计信息:")
            print(f"   - 总医生数: {len(doctors)}")
            print(f"   - 重置医生数: {reset_count}")
            print(f"   - 无需重置: {len(doctors) - reset_count}")

        except Exception as e:
            print(f" 年度重置失败: {str(e)}")
            db.session.rollback()
            raise

def reset_annual_leave_force():
    """强制重置所有医生的已休天数为0（不检查日期）"""
    app = create_app()
    with app.app_context():
        try:
            print(" 强制年度重置...")

            # 获取所有医生
            doctors = Doctor.query.all()
            reset_count = 0

            print(f" 找到 {len(doctors)} 名医生")

            for doctor in doctors:
                if doctor.used_leave_days > 0:
                    print(f" 重置医生 {doctor.name} 的已休天数: {doctor.used_leave_days} → 0")
                    doctor.used_leave_days = 0
                    reset_count += 1
                else:
                    print(f" 医生 {doctor.name} 已休天数已为0，无需重置")

            # 提交更改
            db.session.commit()

            print(f"\n 强制年度重置完成！")
            print(f" 统计信息:")
            print(f"   - 总医生数: {len(doctors)}")
            print(f"   - 重置医生数: {reset_count}")
            print(f"   - 无需重置: {len(doctors) - reset_count}")

        except Exception as e:
            print(f" 强制年度重置失败: {str(e)}")
            db.session.rollback()
            raise

def show_current_status():
    """显示当前医生的年假状态"""
    app = create_app()
    with app.app_context():
        try:
            print(" 当前医生年假状态:")
            print("=" * 60)

            doctors = Doctor.query.order_by(Doctor.sequence).all()
            total_doctors = len(doctors)
            doctors_with_used_leave = len([d for d in doctors if d.used_leave_days > 0])
            total_used_days = sum(d.used_leave_days for d in doctors)

            print(f"总医生数: {total_doctors}")
            print(f"有已休天数的医生: {doctors_with_used_leave}")
            print(f"总已休天数: {total_used_days}")
            print()

            print("详细列表:")
            print("-" * 60)
            print(f"{'序号':<4} {'姓名':<10} {'年假天数':<8} {'已休天数':<8} {'剩余天数':<8}")
            print("-" * 60)

            for doctor in doctors:
                remaining = doctor.annual_leave_days - doctor.used_leave_days
                print(f"{doctor.sequence:<4} {doctor.name:<10} {doctor.annual_leave_days:<8} {doctor.used_leave_days:<8} {remaining:<8}")

        except Exception as e:
            print(f" 查询失败: {str(e)}")

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == '--force':
            reset_annual_leave_force()
        elif sys.argv[1] == '--status':
            show_current_status()
        else:
            print("用法:")
            print("  python reset_annual_leave.py           # 仅在1月1号执行重置")
            print("  python reset_annual_leave.py --force   # 强制执行重置")
            print("  python reset_annual_leave.py --status  # 查看当前状态")
    else:
        reset_annual_leave()