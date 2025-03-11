INSERT INTO `hotelorder_v1` (`id`, `ordertype`, `start_time`, `end_time`, `rid`, `pay_type`, `pay_status`, `money`, `order_status`, `remark`, `order_time`, `register_sid`) VALUES
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