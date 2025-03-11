import unittest
from unittest.mock import MagicMock, patch
import pymysql
# from Main import Room  # 假设 Room 类已实现 checkoutDB 方法
from Main import Staff, get_staff


class TestCheckoutDB(unittest.TestCase):

    def setUp(self):
        """初始化数据库连接 & Room 实例"""
        self.mock_db = pymysql.connect(host='localhost', user='root', password='Tsuki', db='dbdesign')

        """Mock 全局 staff 变量"""
        global staff  # 确保 staff 在测试期间是全局可访问的
        staff = MagicMock(spec=Staff)  # 创建 staff 的 Mock 对象
        staff.sid = "11"  # 模拟员工 ID
        staff.sname = "张经理"
        staff.srole = "2"  # 例如管理员
        staff.susername = "zhangjl"

        # Patch `get_staff()` 方法，确保调用时返回 Mock staff
        self.staff_patch = patch("Main.get_staff", return_value=staff)
        self.staff_patch.start()  # 启用 patch

        from Main import Room  # 这里 Room 需要在 staff 被 patch 之后导入
        self.room = Room()  # 现在 Room 类实例的 staff 变量已 Mock，不会触发 NameError
        # self.room = Room()
        self.room.db = self.mock_db
        self.room.cursor = self.mock_db.cursor(pymysql.cursors.DictCursor)

    def test_personal_checkout_success(self):
        """测试个人用户正常退房"""
        with patch.object(self.room.cursor, "execute") as mock_execute, \
                patch.object(self.room.cursor, "fetchone", return_value={
                    'rid': '201', 'cid': '130898199212233434', 'start_time': '2023-03-01',
                    'end_time': '2023-03-04', 'total_price': '624'
                }):
            result = self.room.checkoutDB("个人", "130898199212233434", "201", "WeChat", "无特殊要求")
            self.assertTrue(result)
            mock_execute.assert_any_call("DELETE FROM checkin_client WHERE rid=%s AND cid=%s",
                                         ('201', '130898199212233434'))

    def test_team_checkout_success(self):
        """测试团队正常退房"""
        with patch.object(self.room.cursor, "execute") as mock_execute, \
                patch.object(self.room.cursor, "fetchone", return_value={
                    'rid': '307', 'tid': '1', 'start_time': '2023-03-01',
                    'end_time': '2023-03-04', 'total_price': '5000'
                }):
            result = self.room.checkoutDB("团队", "1", "307", "Bank Transfer", "会议完成")
            self.assertTrue(result)
            mock_execute.assert_any_call("DELETE FROM checkin_team WHERE rid=%s AND tid=%s", ('307', '1'))

    def test_personal_checkout_no_stay(self):
        """测试个人退房（无入住记录）"""
        with patch.object(self.room.cursor, "fetchone", return_value=None):
            result = self.room.checkoutDB("个人", "999999999999999999", "202", "WeChat", "误操作")
            self.assertFalse(result)

    def test_team_checkout_no_stay(self):
        """测试团队退房（无入住记录）"""
        with patch.object(self.room.cursor, "fetchone", return_value=None):
            result = self.room.checkoutDB("团队", "999", "507", "Bank Transfer", "误操作")
            self.assertFalse(result)

    def test_multiple_rooms_team_checkout(self):
        """测试多房间团队退房"""
        with patch.object(self.room.cursor, "execute") as mock_execute, \
                patch.object(self.room.cursor, "fetchone", side_effect=[
                    {'rid': '307', 'tid': '1', 'start_time': '2023-03-01', 'end_time': '2023-03-04',
                     'total_price': '5000'},
                    {'rid': '308', 'tid': '1', 'start_time': '2023-03-01', 'end_time': '2023-03-04',
                     'total_price': '7200'}
                ]):
            result = self.room.checkoutDB("团队", "1", "307, 308", "Alipay", "完成所有会议")
            self.assertTrue(result)
            mock_execute.assert_any_call("DELETE FROM checkin_team WHERE rid=%s AND tid=%s", ('307', '1'))
            mock_execute.assert_any_call("DELETE FROM checkin_team WHERE rid=%s AND tid=%s", ('308', '1'))

    def test_database_error(self):
        """测试数据库异常回滚"""
        with patch.object(self.room.db, "commit", side_effect=Exception("Database Error")):
            result = self.room.checkoutDB("个人", "130898199212233434", "201", "WeChat", "事务测试")
            self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
