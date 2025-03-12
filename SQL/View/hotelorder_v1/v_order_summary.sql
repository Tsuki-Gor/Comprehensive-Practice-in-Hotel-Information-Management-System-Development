CREATE VIEW v_order_summary AS
SELECT
    ho.order_id,
    ho.id AS client_or_team_id,
    ho.ordertype,
    ho.start_time,
    ho.end_time,
    ho.rid,
    ho.money AS total_amount,
    ho.order_status,
    ho.pay_type,
    ho.pay_status,
    ho.register_sid,  -- ✅ 添加 register_sid
    p.total_paid,
    CASE
        WHEN p.total_paid >= ho.money THEN 'Fully Paid'
        WHEN p.total_paid IS NULL OR p.total_paid = 0 THEN 'Unpaid'
        ELSE 'Partially Paid'
    END AS payment_status,
    i.invoice_status,
    oh.last_status_change,
    oh.last_changed_by
FROM hotelorder_v1 ho
LEFT JOIN (
    SELECT
        order_id,
        SUM(pay_amount) AS total_paid
    FROM payment
    WHERE payment_status = 'paid'
    GROUP BY order_id
) p ON ho.order_id = p.order_id
LEFT JOIN (
    SELECT
        order_id,
        MAX(issue_time) AS last_invoice_time,
        MAX(invoice_status) AS invoice_status
    FROM invoice
    GROUP BY order_id
) i ON ho.order_id = i.order_id
LEFT JOIN (
    SELECT
        order_id,
        MAX(change_time) AS last_status_change,
        MAX(new_status) AS last_status,
        MAX(changed_by) AS last_changed_by
    FROM order_history
    GROUP BY order_id
) oh ON ho.order_id = oh.order_id;
