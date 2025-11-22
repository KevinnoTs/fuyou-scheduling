"""
2025年节假日初始化数据
用于数据库初始化时自动导入2025年的节假日数据

2025年节假日统计：
- 元旦假期：1天 (1月1日)
- 春节假期：8天 (1月28日-2月4日)
- 春节调休：2天 (1月26日、2月8日)
- 清明节假期：3天 (4月4日-4月6日)
- 劳动节假期：5天 (5月1日-5月5日)
- 劳动节调休：1天 (4月27日)
- 端午节假期：3天 (5月31日-6月2日)
- 国庆节假期：8天 (10月1日-10月8日)
- 国庆节调休：2天 (9月28日、10月11日)

总计：
- 节假日：28天
- 调休：5天

2026年节假日统计：
- 元旦假期：3天 (1月1日-1月3日)
- 元旦调休：1天 (1月4日)
- 春节假期：9天 (2月15日-2月23日)
- 春节调休：2天 (2月14日、2月28日)
- 清明节假期：3天 (4月4日-4月6日)
- 劳动节假期：5天 (5月1日-5月5日)
- 劳动节调休：1天 (5月9日)
- 端午节假期：3天 (6月19日-6月21日)
- 国庆节假期：3天 (9月25日-9月27日)
- 国庆节假期：7天 (10月1日-10月7日)
- 国庆节调休：2天 (9月20日、10月10日)

总计：
- 节假日：33天
- 调休：6天
"""

from datetime import date
import sqlalchemy as sa
from app.extensions import db
from app.models import Holiday

def init_2025_holidays():
    """初始化2025年节假日数据"""

    # 2025年节假日数据（33条记录）
    holidays_2025 = [
        # 元旦假期
        (date(2025, 1, 1), "元旦", "holiday", True),

        # 春节调休
        (date(2025, 1, 26), "春节调休", "workday", False),

        # 春节假期
        (date(2025, 1, 28), "春节", "holiday", True),
        (date(2025, 1, 29), "春节", "holiday", True),
        (date(2025, 1, 30), "春节", "holiday", True),
        (date(2025, 1, 31), "春节", "holiday", True),
        (date(2025, 2, 1), "春节", "holiday", True),
        (date(2025, 2, 2), "春节", "holiday", True),
        (date(2025, 2, 3), "春节", "holiday", True),
        (date(2025, 2, 4), "春节", "holiday", False),

        # 春节调休
        (date(2025, 2, 8), "春节调休", "workday", False),

        # 清明节假期
        (date(2025, 4, 4), "清明节", "holiday", False),
        (date(2025, 4, 5), "清明节", "holiday", True),
        (date(2025, 4, 6), "清明节", "holiday", True),

        # 劳动节调休
        (date(2025, 4, 27), "劳动节调休", "workday", False),

        # 劳动节假期
        (date(2025, 5, 1), "劳动节", "holiday", True),
        (date(2025, 5, 2), "劳动节", "holiday", True),
        (date(2025, 5, 3), "劳动节", "holiday", True),
        (date(2025, 5, 4), "劳动节", "holiday", False),
        (date(2025, 5, 5), "劳动节", "holiday", False),

        # 端午节假期
        (date(2025, 5, 31), "端午节", "holiday", True),
        (date(2025, 6, 1), "端午节", "holiday", True),
        (date(2025, 6, 2), "端午节", "holiday", True),

        # 国庆节调休
        (date(2025, 9, 28), "国庆节调休", "workday", False),

        # 国庆节假期
        (date(2025, 10, 1), "国庆节", "holiday", True),
        (date(2025, 10, 2), "国庆节", "holiday", True),
        (date(2025, 10, 3), "国庆节", "holiday", True),
        (date(2025, 10, 4), "国庆节", "holiday", True),
        (date(2025, 10, 5), "国庆节", "holiday", True),
        (date(2025, 10, 6), "国庆节", "holiday", True),
        (date(2025, 10, 7), "国庆节", "holiday", True),
        (date(2025, 10, 8), "国庆节", "holiday", False),

        # 国庆节调休
        (date(2025, 10, 11), "国庆节调休", "workday", False),
    ]

    print("正在初始化2025年节假日数据...")

    for holiday_date, name, holiday_type, is_system in holidays_2025:
        # 检查是否已存在
        existing = Holiday.query.filter_by(date=holiday_date).first()
        if not existing:
            holiday = Holiday(
                date=holiday_date,
                name=name,
                type=holiday_type,
                is_system=is_system
            )
            db.session.add(holiday)
            print(f"  - 添加节假日: {holiday_date} {name} ({holiday_type})")

    db.session.commit()
    print("2025年节假日数据初始化完成！")

def init_2026_holidays():
    """初始化2026年节假日数据"""

    # 2026年节假日数据（40条记录）
    holidays_2026 = [
        # 元旦假期
        (date(2026, 1, 1), "元旦", "holiday", True),
        (date(2026, 1, 2), "元旦", "holiday", True),
        (date(2026, 1, 3), "元旦", "holiday", True),

        # 元旦调休
        (date(2026, 1, 4), "元旦调休", "workday", False),

        # 春节调休
        (date(2026, 2, 14), "春节调休", "workday", False),

        # 春节假期
        (date(2026, 2, 15), "春节", "holiday", True),
        (date(2026, 2, 16), "春节", "holiday", True),
        (date(2026, 2, 17), "春节", "holiday", True),
        (date(2026, 2, 18), "春节", "holiday", True),
        (date(2026, 2, 19), "春节", "holiday", True),
        (date(2026, 2, 20), "春节", "holiday", True),
        (date(2026, 2, 21), "春节", "holiday", True),
        (date(2026, 2, 22), "春节", "holiday", True),
        (date(2026, 2, 23), "春节", "holiday", True),

        # 春节调休
        (date(2026, 2, 28), "春节调休", "workday", False),

        # 清明节假期
        (date(2026, 4, 4), "清明节", "holiday", True),
        (date(2026, 4, 5), "清明节", "holiday", True),
        (date(2026, 4, 6), "清明节", "holiday", True),

        # 劳动节假期
        (date(2026, 5, 1), "劳动节", "holiday", True),
        (date(2026, 5, 2), "劳动节", "holiday", True),
        (date(2026, 5, 3), "劳动节", "holiday", True),
        (date(2026, 5, 4), "劳动节", "holiday", True),
        (date(2026, 5, 5), "劳动节", "holiday", True),

        # 劳动节调休
        (date(2026, 5, 9), "劳动节调休", "workday", False),

        # 端午节假期
        (date(2026, 6, 19), "端午节", "holiday", True),
        (date(2026, 6, 20), "端午节", "holiday", True),
        (date(2026, 6, 21), "端午节", "holiday", True),

        # 国庆节调休
        (date(2026, 9, 20), "国庆节调休", "workday", False),

        # 国庆节假期
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

        # 国庆节调休
        (date(2026, 10, 10), "国庆节调休", "workday", False),
    ]

    print("正在初始化2026年节假日数据...")

    for holiday_date, name, holiday_type, is_system in holidays_2026:
        # 检查是否已存在
        existing = Holiday.query.filter_by(date=holiday_date).first()
        if not existing:
            holiday = Holiday(
                date=holiday_date,
                name=name,
                type=holiday_type,
                is_system=is_system
            )
            db.session.add(holiday)
            print(f"  - 添加节假日: {holiday_date} {name} ({holiday_type})")

    db.session.commit()
    print("2026年节假日数据初始化完成！")

def check_holidays_data():
    """检查节假日数据"""
    count = Holiday.query.count()
    if count == 0:
        print("数据库中没有节假日数据，正在初始化...")
        init_2025_holidays()
        init_2026_holidays()
        return True
    else:
        print(f"数据库中已有 {count} 条节假日数据")
        # 检查是否需要初始化2026年数据
        count_2026 = Holiday.query.filter(
            sa.extract('year', Holiday.date) == 2026
        ).count()
        if count_2026 == 0:
            print("数据库中没有2026年节假日数据，正在初始化...")
            init_2026_holidays()
            return True
        return False

if __name__ == "__main__":
    check_holidays_data()