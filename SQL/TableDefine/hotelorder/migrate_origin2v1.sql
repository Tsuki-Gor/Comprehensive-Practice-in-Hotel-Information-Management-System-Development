INSERT INTO hotelorder_v1
    (id, ordertype, start_time, end_time, rid, pay_type, pay_status, money, order_status, remark, order_time, register_sid)
SELECT id, ordertype, start_time, end_time, rid, pay_type,
       'paid' AS pay_status,  -- 设定默认值，假设历史订单都已支付
       CAST(money AS DECIMAL(10,2)),
       'completed' AS order_status, -- 设定默认值，假设历史订单都已完成
       remark, order_time, register_sid
FROM hotelorder;