import unittest
import pymysql
import datetime
from Main import Chart  # 假设 `Chart` 类在 chart.py 文件中
from service.config import MYSQL_CONFIG  # 确保配置文件中包含数据库连接信息


class TestChart(unittest.TestCase):
    """测试 Chart 类的方法"""

    @classmethod
    def setUpClass(cls):
        """在测试开始前，初始化数据库连接和 Chart 实例"""
        MYSQL_CONFIG["cursorclass"] = pymysql.cursors.DictCursor
        cls.chart = Chart(MYSQL_CONFIG)

    def test_getRevenue(self):
        """测试 getRevenue() 是否返回正确的营业额"""
        dates, revenues = self.chart.getRevenue()

        self.assertEqual(len(dates), 7, "应返回最近 7 天的数据")
        self.assertEqual(len(revenues), 7, "营业额列表长度应与日期相同")

        for revenue in revenues:
            self.assertIsInstance(revenue, (int, float), "营业额应为数字类型")

    def test_getOccupy(self):
        """测试 getOccupy() 是否返回正确的入住率"""
        dates, occupancy_rates = self.chart.getOccupy()

        self.assertEqual(len(dates), 7, "应返回最近 7 天的数据")
        self.assertEqual(len(occupancy_rates), 7, "入住率列表长度应与日期相同")

        for rate in occupancy_rates:
            self.assertIsInstance(rate, float, "入住率应为浮点数")
            self.assertGreaterEqual(rate, 0.0, "入住率应 >= 0")
            self.assertLessEqual(rate, 1.0, "入住率应 <= 1")

    def test_getClientStatics(self):
        """测试 getClientStatics() 是否正确统计个人和团队订单数量"""
        client_team_stats = self.chart.getClientStatics()

        self.assertEqual(len(client_team_stats), 2, "应返回两个值（个人订单数, 团队订单数）")
        self.assertIsInstance(client_team_stats[0], int, "个人订单数应为整数")
        self.assertIsInstance(client_team_stats[1], int, "团队订单数应为整数")

    def test_getStaffStatics(self):
        """测试 getStaffStatics() 是否正确统计员工订单处理量"""
        staff_ids, order_counts = self.chart.getStaffStatics()

        self.assertEqual(len(staff_ids), len(order_counts), "员工 ID 列表与订单处理量列表长度应相同")

        for staff_id in staff_ids:
            self.assertIsInstance(staff_id, str, "员工 ID 应为字符串")

        for count in order_counts:
            self.assertIsInstance(count, int, "订单处理数应为整数")

    @classmethod
    def tearDownClass(cls):
        """测试结束后关闭数据库连接"""
        cls.chart.db.close()


if __name__ == '__main__':
    unittest.main()
