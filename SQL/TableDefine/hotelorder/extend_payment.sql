CREATE TABLE `payment` (
    `payment_id` INT AUTO_INCREMENT PRIMARY KEY,  -- 唯一支付记录ID
    `order_id` INT NOT NULL,                      -- 关联 hotelorder_v1 的订单ID
    `pay_amount` DECIMAL(10,2) NOT NULL,          -- 付款金额
    `pay_method` ENUM('WeChat', 'Alipay', 'Credit Card', 'Cash', 'Bank Transfer') NOT NULL,  -- 支付方式
    `payment_status` ENUM('pending', 'paid', 'failed', 'refunded') NOT NULL DEFAULT 'pending',  -- 支付状态
    `transaction_id` VARCHAR(255) NULL DEFAULT NULL,  -- 第三方支付流水号（如微信、支付宝）
    `pay_time` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,  -- 支付时间
    `remark` VARCHAR(255) NULL DEFAULT NULL,  -- 备注（如退款原因）
    CONSTRAINT `fk_payment_order` FOREIGN KEY (`order_id`) REFERENCES `hotelorder_v1`(`order_id`) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX `idx_payment_order` (`order_id`),  -- 提高查询效率
    INDEX `idx_payment_status` (`payment_status`)  -- 便于按状态查询
);
