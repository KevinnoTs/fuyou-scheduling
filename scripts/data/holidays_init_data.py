"""
节假日初始化数据
导出时间: 2025-11-23 02:58:02

数据格式说明:
- 日期格式: date(year, month, day) - 统一使用无前导零格式
- 示例: date(2025, 1, 1) 表示2025年1月1日
- 空格格式: 日期参数间保持一致的空格分隔

节假日统计:
- 2025年: 28天节假日, 5天调休
- 2026年: 33天节假日, 6天调休
"""

from datetime import date
import sqlalchemy as sa
import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from app import create_app
from app.extensions import db
from app.models import Holiday

def init_2025_holidays():
    """初始化2025年节假日数据"""

    # 2025年节假日数据（33条记录）
    holidays = [
        (date(2025, 1, 1), "元旦", "holiday", True),
        (date(2025, 1, 26), "春节调休", "workday", False),
        (date(2025, 1, 28), "春节", "holiday", True),
        (date(2025, 1, 29), "春节", "holiday", True),
        (date(2025, 1, 30), "春节", "holiday", True),
        (date(2025, 1, 31), "春节", "holiday", True),
        (date(2025, 2, 1), "春节", "holiday", True),
        (date(2025, 2, 2), "春节", "holiday", True),
        (date(2025, 2, 3), "春节", "holiday", True),
        (date(2025, 2, 4), "春节", "holiday", False),
        (date(2025, 2, 8), "春节调休", "workday", False),
        (date(2025, 4, 4), "清明节", "holiday", False),
        (date(2025, 4, 5), "清明节", "holiday", True),
        (date(2025, 4, 6), "清明节", "holiday", True),
        (date(2025, 4, 27), "劳动节调休", "workday", False),
        (date(2025, 5, 1), "劳动节", "holiday", True),
        (date(2025, 5, 2), "劳动节", "holiday", True),
        (date(2025, 5, 3), "劳动节", "holiday", True),
        (date(2025, 5, 4), "劳动节", "holiday", False),
        (date(2025, 5, 5), "劳动节", "holiday", False),
        (date(2025, 5, 31), "端午节", "holiday", True),
        (date(2025, 6, 1), "端午节", "holiday", True),
        (date(2025, 6, 2), "端午节", "holiday", True),
        (date(2025, 9, 28), "国庆节调休", "workday", False),
        (date(2025, 10, 1), "国庆节", "holiday", True),
        (date(2025, 10, 2), "国庆节", "holiday", True),
        (date(2025, 10, 3), "国庆节", "holiday", True),
        (date(2025, 10, 4), "国庆节", "holiday", True),
        (date(2025, 10, 5), "国庆节", "holiday", True),
        (date(2025, 10, 6), "国庆节", "holiday", True),
        (date(2025, 10, 7), "国庆节", "holiday", True),
        (date(2025, 10, 8), "国庆节", "holiday", False),
        (date(2025, 10, 11), "国庆节调休", "workday", False),
    ]

    # 检查是否已存在数据
    existing_count = Holiday.query.filter(
        sa.extract('year', Holiday.date) == 2025
    ).count()
    if existing_count > 0:
        print("2025年节假日数据已存在，跳过初始化")
        return

    # 插入数据
    for holiday_date, name, holiday_type, is_system in holidays:
        holiday = Holiday(
            date=holiday_date,
            name=name,
            type=holiday_type,
            is_system=is_system
        )
        db.session.add(holiday)
    
    db.session.commit()
    print("2025年节假日数据初始化完成，共33条记录")

def init_2026_holidays():
    """初始化2026年节假日数据"""

    # 2026年节假日数据（39条记录）
    holidays = [
        (date(2026, 1, 1), "元旦", "holiday", True),
        (date(2026, 1, 2), "元旦", "holiday", True),
        (date(2026, 1, 3), "元旦", "holiday", True),
        (date(2026, 1, 4), "元旦调休", "workday", False),
        (date(2026, 2, 14), "春节调休", "workday", False),
        (date(2026, 2, 15), "春节", "holiday", True),
        (date(2026, 2, 16), "春节", "holiday", True),
        (date(2026, 2, 17), "春节", "holiday", True),
        (date(2026, 2, 18), "春节", "holiday", True),
        (date(2026, 2, 19), "春节", "holiday", True),
        (date(2026, 2, 20), "春节", "holiday", True),
        (date(2026, 2, 21), "春节", "holiday", True),
        (date(2026, 2, 22), "春节", "holiday", True),
        (date(2026, 2, 23), "春节", "holiday", True),
        (date(2026, 2, 28), "春节调休", "workday", False),
        (date(2026, 4, 4), "清明节", "holiday", True),
        (date(2026, 4, 5), "清明节", "holiday", True),
        (date(2026, 4, 6), "清明节", "holiday", True),
        (date(2026, 5, 1), "劳动节", "holiday", True),
        (date(2026, 5, 2), "劳动节", "holiday", True),
        (date(2026, 5, 3), "劳动节", "holiday", True),
        (date(2026, 5, 4), "劳动节", "holiday", True),
        (date(2026, 5, 5), "劳动节", "holiday", True),
        (date(2026, 5, 9), "劳动节调休", "workday", False),
        (date(2026, 6, 19), "端午节", "holiday", True),
        (date(2026, 6, 20), "端午节", "holiday", True),
        (date(2026, 6, 21), "端午节", "holiday", True),
        (date(2026, 9, 20), "国庆节调休", "workday", False),
        (date(2026, 9, 25), "国庆节", "holiday", True),
        (date(2026, 9, 26), "国庆节", "holiday", True),
        (date(2026, 9, 27), "国庆节", "holiday", True),
        (date(2026, 10, 1), "国庆节", "holiday", True),
        (date(2026, 10, 2), "国庆节", "holiday", True),
        (date(2026, 10, 3), "国庆节", "holiday", True),
        (date(2026, 10, 4), "国庆节", "holiday", True),
        (date(2026, 10, 5), "国庆节", "holiday", True),
        (date(2026, 10, 6), "国庆节", "holiday", True),
        (date(2026, 10, 7), "国庆节", "holiday", True),
        (date(2026, 10, 10), "国庆节调休", "workday", False),
    ]

    # 检查是否已存在数据
    existing_count = Holiday.query.filter(
        sa.extract('year', Holiday.date) == 2026
    ).count()
    if existing_count > 0:
        print("2026年节假日数据已存在，跳过初始化")
        return

    # 插入数据
    for holiday_date, name, holiday_type, is_system in holidays:
        holiday = Holiday(
            date=holiday_date,
            name=name,
            type=holiday_type,
            is_system=is_system
        )
        db.session.add(holiday)
    
    db.session.commit()
    print("2026年节假日数据初始化完成，共39条记录")

def check_holidays_data():
    """检查并初始化所有年份数据"""
    total_count = Holiday.query.count()
    if total_count == 0:
        print("数据库中没有节假日数据，正在初始化...")
        init_2025_holidays()
        return True
        init_2026_holidays()
        return True
    else:
        print(f"数据库中已有 {total_count} 条节假日数据")
        # 检查是否有新年份数据需要初始化
        init_2025_holidays()
        init_2026_holidays()
        return False

if __name__ == "__main__":
    # 创建Flask应用并初始化数据库上下文
    app = create_app()
    with app.app_context():
        check_holidays_data()