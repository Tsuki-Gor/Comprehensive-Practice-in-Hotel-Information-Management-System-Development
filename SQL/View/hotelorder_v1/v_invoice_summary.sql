CREATE VIEW v_invoice_summary AS
SELECT
    i.invoice_id,
    i.order_id,
    ho.id AS client_or_team_id,
    ho.ordertype,
    i.invoice_title,
    i.invoice_type,
    i.invoice_amount,
    i.tax_number,
    i.invoice_status,
    i.issue_time
FROM invoice i
JOIN hotelorder_v1 ho ON i.order_id = ho.order_id;
