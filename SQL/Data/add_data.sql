INSERT INTO `booking_client` (`cid`, `rid`, `start_time`, `end_time`, `booking_time`, `remark`) VALUES
('130898199212233434', '201', CURDATE() - INTERVAL 10 DAY, CURDATE() - INTERVAL 7 DAY, NOW(), '商务出差'),
('131989238123991308', '203', CURDATE() - INTERVAL 8 DAY, CURDATE() - INTERVAL 5 DAY, NOW(), '旅游休闲');

INSERT INTO `booking_team` (`tid`, `rid`, `start_time`, `end_time`, `booking_time`, `remark`) VALUES
('1', '307', CURDATE() - INTERVAL 12 DAY, CURDATE() - INTERVAL 9 DAY, NOW(), '团队会议'),
('11', '308', CURDATE() - INTERVAL 11 DAY, CURDATE() - INTERVAL 7 DAY, NOW(), '学术交流');

INSERT INTO `checkin_client` (`rid`, `cid`, `start_time`, `end_time`, `total_price`, `check_in_sid`, `remark`) VALUES
('201', '130898199212233434', CURDATE() - INTERVAL 10 DAY, CURDATE() - INTERVAL 7 DAY, '624', '1', '无特殊要求'),
('203', '131989238123991308', CURDATE() - INTERVAL 8 DAY, CURDATE() - INTERVAL 5 DAY, '832', '10', '要求无烟房');

INSERT INTO `checkin_team` (`rid`, `tid`, `start_time`, `end_time`, `total_price`, `check_in_sid`, `remark`) VALUES
('307', '1', CURDATE() - INTERVAL 12 DAY, CURDATE() - INTERVAL 9 DAY, '5000', '2', '会议专用'),
('308', '11', CURDATE() - INTERVAL 11 DAY, CURDATE() - INTERVAL 7 DAY, '7200', '2', '学术交流团队入住');

INSERT INTO `hotelorder_v1` (`id`, `ordertype`, `start_time`, `end_time`, `rid`, `pay_type`, `pay_status`, `money`, `order_status`, `remark`, `order_time`, `register_sid`) VALUES
('130898199212233434', '个人', CURDATE() - INTERVAL 10 DAY, CURDATE() - INTERVAL 7 DAY, '201', 'WeChat', 'paid', 624.00, 'completed', '退房结算完成', NOW(), '1'),
('131989238123991308', '个人', CURDATE() - INTERVAL 8 DAY, CURDATE() - INTERVAL 5 DAY, '203', 'Credit Card', 'paid', 832.00, 'completed', '退房结算完成', NOW(), '10'),
('1', '团队', CURDATE() - INTERVAL 12 DAY, CURDATE() - INTERVAL 9 DAY, '307', 'Bank Transfer', 'paid', 5000.00, 'completed', '团队会议订单结算', NOW(), '2'),
('11', '团队', CURDATE() - INTERVAL 11 DAY, CURDATE() - INTERVAL 7 DAY, '308', 'Alipay', 'paid', 7200.00, 'completed', '学术交流订单结算', NOW(), '2'),
-- 个人订单
('320111198511113456', '个人', CURDATE() - INTERVAL 6 DAY, CURDATE() - INTERVAL 3 DAY, '201', 'WeChat', 'paid', 560.00, 'completed', '个人商务差旅结算', NOW(), '3'),
('320222199012314567', '个人', CURDATE() - INTERVAL 5 DAY, CURDATE() - INTERVAL 2 DAY, '202', 'Credit Card', 'paid', 720.00, 'completed', '休闲度假结算', NOW(), '4'),
('310123199506283678', '个人', CURDATE() - INTERVAL 4 DAY, CURDATE() - INTERVAL 1 DAY, '205', 'Alipay', 'paid', 980.00, 'completed', '短期出差订单结算', NOW(), '5'),
('350321198805194567', '个人', CURDATE() - INTERVAL 3 DAY, CURDATE(), '301', 'Cash', 'pending', 840.00, 'pending', '住客等待支付', NOW(), '6'),
('330987199812301234', '个人', CURDATE() - INTERVAL 2 DAY, CURDATE(), '402', 'WeChat', 'pending', 1120.00, 'pending', '客户已登记，尚未支付', NOW(), '7'),
-- 团队订单
('21', '团队', CURDATE() - INTERVAL 7 DAY, CURDATE() - INTERVAL 4 DAY, '507', 'Bank Transfer', 'paid', 8500.00, 'completed', '公司团建活动订单结算', NOW(), '8'),
('31', '团队', CURDATE() - INTERVAL 6 DAY, CURDATE() - INTERVAL 3 DAY, '508', 'Credit Card', 'paid', 9400.00, 'completed', '商务会议团队订单结算', NOW(), '8'),
('41', '团队', CURDATE() - INTERVAL 5 DAY, CURDATE() - INTERVAL 2 DAY, '410', 'Alipay', 'pending', 7600.00, 'pending', '学术会议订单，等待支付', NOW(), '7'),
('51', '团队', CURDATE() - INTERVAL 4 DAY, CURDATE() - INTERVAL 1 DAY, '406', 'Bank Transfer', 'paid', 10500.00, 'completed', '国际交流团队订单结算', NOW(), '6'),
('61', '团队', CURDATE() - INTERVAL 3 DAY, CURDATE(), '307', 'WeChat', 'pending', 6200.00, 'pending', '体育赛事团队入住订单，等待支付', NOW(), '5');


INSERT INTO `payment` (`order_id`, `pay_amount`, `pay_method`, `payment_status`, `transaction_id`, `pay_time`, `remark`) VALUES
(1, 624.00, 'WeChat', 'paid', 'WX1234567890', NOW(), '个人订单支付完成'),
(2, 832.00, 'Credit Card', 'paid', 'CC9876543210', NOW(), '个人订单支付完成'),
(3, 5000.00, 'Bank Transfer', 'paid', 'BANK567890123', NOW(), '团队订单支付完成'),
(4, 7200.00, 'Alipay', 'paid', 'ALI9876543210', NOW(), '团队订单支付完成');

INSERT INTO `invoice` (`order_id`, `invoice_title`, `invoice_type`, `invoice_amount`, `tax_number`, `invoice_status`, `issue_time`, `remark`) VALUES
(1, '张三', 'Electronic', 624.00, NULL, 'issued', NOW(), '客户申请电子发票'),
(2, '李四', 'Paper', 832.00, '91330106MA2C8XXXX', 'issued', NOW(), '公司报销'),
(3, '科技公司', 'Electronic', 5000.00, '91330106MA5XXXX', 'issued', NOW(), '会议订单开发票'),
(4, '学术交流团队', 'Paper', 7200.00, '91330106MA9XXXX', 'issued', NOW(), '团队开发票');

INSERT INTO `order_history` (`order_id`, `previous_status`, `new_status`, `change_time`, `changed_by`, `remark`) VALUES
(1, 'pending', 'paid', NOW() - INTERVAL 9 DAY, '1', '个人订单支付完成'),
(2, 'pending', 'paid', NOW() - INTERVAL 6 DAY, '10', '个人订单支付完成'),
(3, 'pending', 'paid', NOW() - INTERVAL 10 DAY, '2', '团队订单支付完成'),
(4, 'pending', 'paid', NOW() - INTERVAL 8 DAY, '2', '团队订单支付完成');

INSERT INTO `room` (`rid`, `rtype`, `rstorey`, `rprice`, `rdesc`, `rpic`) VALUES
('202', '标准间（单人）', '2', '208', '电视故障', 'D:/pictures/ss.jpg'),
('204', '标准间（单人）', '2', '208', '无', 'D:/pictures/ss.jpg'),
('507', '总统套房', '5', '1200', '带阳台，带独立浴缸', 'D:/pictures/hs.jpg'),
('508', '大床房', '5', '800', '适合商务人士', 'D:/pictures/bc.jpg');

INSERT INTO `staff` (`sid`, `sname`, `ssex`, `stime`, `susername`, `spassword`, `srole`, `sidcard`, `sphone`) VALUES
('11', '张经理', '男', '2018-05-20', 'zhangjl', 'abc123', '2', '310109198705283299', '13577778888');
