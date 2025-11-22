"""
中国法定节假日处理工具
支持预定义节假日
"""
import json
from datetime import datetime, date, timedelta
from typing import Dict, Set, Optional

class ChinaHolidays:
    def __init__(self):
        self.holiday_cache = {}  # 缓存节假日数据

    def get_holidays(self, year: int) -> Dict[str, Dict[str, str]]:
        """
        获取指定年份的数据库节假日（生产环境专用）
        只返回数据库中保存的节假日，不包含系统预定义和API推断的节假日

        Returns:
            Dict[str, Dict[str, str]]: 日期字符串 -> 节假日信息字典
            例如: {"2025-01-01": {"name": "元旦", "type": "holiday"}, "2025-05-01": {"name": "劳动节", "type": "holiday"}}
        """
        if year in self.holiday_cache:
            return self.holiday_cache[year]

        # 生产环境：只从数据库获取节假日
        holidays = self._get_database_holidays(year)

        # 缓存结果
        self.holiday_cache[year] = holidays
        return holidays

    def get_all_holidays(self, year: int) -> Dict[str, Dict[str, str]]:
        """
        获取指定年份的所有节假日（包括数据库、预定义和API推断）
        供节假日管理页面使用，给用户参考以便添加或编辑

        Returns:
            Dict[str, Dict[str, str]]: 日期字符串 -> 节假日信息字典
        """
        # 1. 先获取预定义的固定节假日
        holidays = self._get_predefined_holidays(year)

        # 2. 尝试从API获取动态节假日（春节、清明等）
        api_holidays = self._get_api_holidays(year)
        if api_holidays:
            holidays.update(api_holidays)

        # 3. 从数据库获取用户自定义节假日（数据库优先级最高）
        db_holidays = self._get_database_holidays(year)
        if db_holidays:
            holidays.update(db_holidays)

        return holidays

    def _get_predefined_holidays(self, year: int) -> Dict[str, Dict[str, str]]:
        """获取预定义的固定节假日"""
        holidays = {
            # 元旦 (1月1日)
            f"{year}-01-01": {"name": "元旦", "type": "holiday", "is_system": True},

            # 劳动节 (5月1-3日)
            f"{year}-05-01": {"name": "劳动节", "type": "holiday", "is_system": True},
            f"{year}-05-02": {"name": "劳动节", "type": "holiday", "is_system": True},
            f"{year}-05-03": {"name": "劳动节", "type": "holiday", "is_system": True},

            # 国庆节 (10月1-7日)
            f"{year}-10-01": {"name": "国庆节", "type": "holiday", "is_system": True},
            f"{year}-10-02": {"name": "国庆节", "type": "holiday", "is_system": True},
            f"{year}-10-03": {"name": "国庆节", "type": "holiday", "is_system": True},
            f"{year}-10-04": {"name": "国庆节", "type": "holiday", "is_system": True},
            f"{year}-10-05": {"name": "国庆节", "type": "holiday", "is_system": True},
            f"{year}-10-06": {"name": "国庆节", "type": "holiday", "is_system": True},
            f"{year}-10-07": {"name": "国庆节", "type": "holiday", "is_system": True},
        }
        return holidays

    def _get_api_holidays(self, year: int) -> Optional[Dict[str, Dict[str, str]]]:
        """从API获取节假日数据"""
        try:
            # 使用免费的节假日API
            url = f"http://api.goseek.cn/Tools/holiday?date={year}-01-01"

            # 这个API需要逐日查询，我们使用更简单的方法
            # 使用聚合数据API或其他免费API
            return self._get_holiday_from_ripedb(year)

        except Exception as e:
            print(f"API查询节假日失败: {e}")
            return None

    def _get_database_holidays(self, year: int) -> Dict[str, Dict[str, str]]:
        """从数据库获取用户自定义节假日"""
        try:
            from app.models import Holiday
            import sqlalchemy as sa

            # 从数据库查询指定年份的节假日
            db_holidays = Holiday.query.filter(
                sa.extract('year', Holiday.date) == year
            ).all()

            holidays = {}
            for holiday in db_holidays:
                date_str = holiday.date.strftime('%Y-%m-%d')
                holidays[date_str] = {
                    'name': holiday.name,
                    'type': holiday.type,
                    'is_system': holiday.is_system
                }

            return holidays

        except Exception as e:
            print(f"从数据库获取节假日失败: {e}")
            return {}

    def _get_holiday_from_ripedb(self, year: int) -> Optional[Dict[str, Dict[str, str]]]:
        """从备用API获取节假日"""
        try:
            # 使用一个简单的API来查询
            # 注意：实际使用时可能需要API key或更复杂的处理
            # 这里提供基础的实现框架

            # 对于2025年的特殊节假日（可以在网上搜索后手动添加）
            if year == 2025:
                return {
                    # 春节 (2025年春节1月29日，假期通常1月28日-2月3日)
                    "2025-01-28": {"name": "春节", "type": "holiday", "is_system": True},
                    "2025-01-29": {"name": "春节", "type": "holiday", "is_system": True},
                    "2025-01-30": {"name": "春节", "type": "holiday", "is_system": True},
                    "2025-01-31": {"name": "春节", "type": "holiday", "is_system": True},
                    "2025-02-01": {"name": "春节", "type": "holiday", "is_system": True},
                    "2025-02-02": {"name": "春节", "type": "holiday", "is_system": True},
                    "2025-02-03": {"name": "春节", "type": "holiday", "is_system": True},

                    # 清明节 (2025年4月5日，通常4月5-7日)
                    "2025-04-05": {"name": "清明节", "type": "holiday", "is_system": True},
                    "2025-04-06": {"name": "清明节", "type": "holiday", "is_system": True},
                    "2025-04-07": {"name": "清明节", "type": "holiday", "is_system": True},

                    # 端午节 (2025年5月31日)
                    "2025-05-31": {"name": "端午节", "type": "holiday", "is_system": True},
                    "2025-06-01": {"name": "端午节", "type": "holiday", "is_system": True},
                    "2025-06-02": {"name": "端午节", "type": "holiday", "is_system": True},

                    # 中秋节 (2025年10月6日，与国庆重合)
                    "2025-10-06": {"name": "中秋节", "type": "holiday", "is_system": True},
                }

            return None

        except Exception as e:
            print(f"获取节假日数据失败: {e}")
            return None

    def is_holiday(self, date_str: str) -> bool:
        """检查指定日期是否为节假日"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year = date_obj.year
            holidays = self.get_holidays(year)
            return date_str in holidays
        except:
            return False

    def get_holiday_name(self, date_str: str) -> Optional[str]:
        """获取指定日期的节假日名称"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year = date_obj.year
            holidays = self.get_holidays(year)
            holiday_info = holidays.get(date_str)
            return holiday_info["name"] if holiday_info else None
        except:
            return None

    def add_custom_holiday(self, date_str: str, name: str, holiday_type: str = "custom", end_date_str: str = None):
        """添加自定义节假日"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year = date_obj.year

            if year not in self.holiday_cache:
                self.holiday_cache[year] = self._get_predefined_holidays(year)

            # 如果没有提供结束日期，则结束日期等于开始日期
            if not end_date_str:
                end_date_str = date_str

            end_date_obj = datetime.strptime(end_date_str, "%Y-%m-%d")

            # 验证结束日期不能早于开始日期
            if end_date_obj < date_obj:
                return False, "结束日期不能早于开始日期"

            # 生成日期范围
            current_date = date_obj
            added_count = 0

            while current_date <= end_date_obj:
                current_date_str = current_date.strftime("%Y-%m-%d")

                # 检查是否已存在
                if current_date_str in self.holiday_cache[year]:
                    current_date += timedelta(days=1)
                    continue  # 跳过已存在的日期

                self.holiday_cache[year][current_date_str] = {
                    "name": name,
                    "type": holiday_type,
                    "is_system": False
                }
                added_count += 1
                current_date += timedelta(days=1)

            return True, f"成功添加{added_count}天节假日"

        except Exception as e:
            print(f"添加自定义节假日失败: {e}")
            return False, f"添加失败: {str(e)}"

    def remove_custom_holiday(self, date_str: str):
        """删除自定义节假日"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year = date_obj.year

            # 确保该年份的缓存已加载
            if year not in self.holiday_cache:
                self.holiday_cache[year] = self._get_predefined_holidays(year)

            # 删除指定日期的节假日（如果存在）
            if date_str in self.holiday_cache[year]:
                del self.holiday_cache[year][date_str]
                return True
            return False

        except Exception as e:
            print(f"删除自定义节假日失败: {e}")
            return False

    def clear_cache(self, year: int = None):
        """
        清理指定年份的缓存，如果不指定年份则清理所有缓存

        Args:
            year (int, optional): 要清理的年份，如果不指定则清理所有年份
        """
        if year:
            if year in self.holiday_cache:
                del self.holiday_cache[year]
                print(f"已清理 {year} 年的节假日缓存")
        else:
            self.holiday_cache.clear()
            print("已清理所有年份的节假日缓存")

    def is_holiday(self, date_str: str) -> bool:
        """
        判断指定日期是否为放假日（基于数据库定义）
        生产环境：完全按照数据库中的节假日记录判断

        Args:
            date_str (str): 日期字符串，格式：YYYY-MM-DD

        Returns:
            bool: True表示放假日，False表示工作日
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year = date_obj.year
            weekday = date_obj.weekday()  # 0-6 (周一到周日)

            # 获取数据库中的节假日数据
            holidays = self.get_holidays(year)

            # 检查数据库中是否有该日期的记录
            if date_str in holidays:
                holiday_type = holidays[date_str].get('type')
                # 数据库中明确标记为调休工作日 → 工作日
                if holiday_type == 'workday':
                    return False
                # 数据库中明确标记为节假日 → 放假日
                elif holiday_type == 'holiday':
                    return True

            # 如果数据库中没有该日期的记录，按常规周末规则判断
            # 周一至周五：工作日；周六周日：放假日
            return weekday >= 5  # 5=周六, 6=周日

        except Exception as e:
            print(f"判断节假日失败: {e}")
            return False

    def is_workday(self, date_str: str) -> bool:
        """
        判断指定日期是否为工作日（周一到周五 + 调休）

        Args:
            date_str (str): 日期字符串，格式：YYYY-MM-DD

        Returns:
            bool: True表示工作日，False表示放假日
        """
        return not self.is_holiday(date_str)

# 创建全局实例
holiday_helper = ChinaHolidays()