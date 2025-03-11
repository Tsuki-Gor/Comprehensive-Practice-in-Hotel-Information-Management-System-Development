CREATE TABLE `invoice` (
    `invoice_id` INT AUTO_INCREMENT PRIMARY KEY,  -- 唯一发票ID
    `order_id` INT NOT NULL,                      -- 关联 hotelorder_v1 订单ID
    `invoice_title` VARCHAR(255) NOT NULL,        -- 发票抬头
    `invoice_type` ENUM('Electronic', 'Paper') NOT NULL DEFAULT 'Electronic',  -- 发票类型
    `invoice_amount` DECIMAL(10,2) NOT NULL,      -- 开票金额
    `tax_number` VARCHAR(50) NULL DEFAULT NULL,   -- 纳税人识别号（如企业用户）
    `invoice_status` ENUM('pending', 'issued', 'cancelled') NOT NULL DEFAULT 'pending',  -- 发票状态
    `issue_time` TIMESTAMP NULL DEFAULT NULL,     -- 开票时间
    `remark` VARCHAR(255) NULL DEFAULT NULL,      -- 备注（如开票失败原因）
    CONSTRAINT `fk_invoice_order` FOREIGN KEY (`order_id`) REFERENCES `hotelorder_v1`(`order_id`) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX `idx_invoice_order` (`order_id`),  -- 提高查询效率
    INDEX `idx_invoice_status` (`invoice_status`)  -- 便于按状态查询
);
