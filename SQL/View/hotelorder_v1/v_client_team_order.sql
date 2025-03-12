CREATE VIEW v_client_team_order AS
SELECT
    ho.order_id,
    c.cname AS client_name,
    t.tname AS team_name,
    ho.ordertype,
    ho.start_time,
    ho.end_time,
    ho.money AS total_amount,
    ho.order_status,
    p.total_paid,
    CASE
        WHEN p.total_paid >= ho.money THEN 'Fully Paid'
        WHEN p.total_paid IS NULL OR p.total_paid = 0 THEN 'Unpaid'
        ELSE 'Partially Paid'
    END AS payment_status
FROM hotelorder_v1 ho
LEFT JOIN client c ON ho.ordertype = '个人' AND ho.id = c.cid
LEFT JOIN team t ON ho.ordertype = '团队' AND ho.id = t.tid
LEFT JOIN (
    SELECT order_id, SUM(pay_amount) AS total_paid
    FROM payment
    WHERE payment_status = 'paid'
    GROUP BY order_id
) p ON ho.order_id = p.order_id;
