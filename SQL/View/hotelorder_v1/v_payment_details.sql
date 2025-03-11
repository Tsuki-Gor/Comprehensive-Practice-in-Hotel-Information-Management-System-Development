CREATE VIEW v_payment_details AS
SELECT
    p.payment_id,
    p.order_id,
    ho.id AS client_or_team_id,
    ho.ordertype,
    p.pay_amount,
    p.pay_method,
    p.payment_status,
    p.transaction_id,
    p.pay_time
FROM payment p
JOIN hotelorder_v1 ho ON p.order_id = ho.order_id;
