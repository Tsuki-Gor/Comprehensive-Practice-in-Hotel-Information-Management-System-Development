CREATE TABLE `order_history` (
    `history_id` INT AUTO_INCREMENT PRIMARY KEY,  -- 唯一日志ID
    `order_id` INT NOT NULL,                      -- 关联 hotelorder_v1 订单ID
    `previous_status` ENUM('pending', 'paid', 'cancelled', 'completed') NOT NULL,  -- 变更前状态
    `new_status` ENUM('pending', 'paid', 'cancelled', 'completed') NOT NULL,  -- 变更后状态
    `change_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 变更时间
    `changed_by` VARCHAR(255) NOT NULL,  -- 操作员工 ID
    `remark` VARCHAR(255) NULL DEFAULT NULL,  -- 备注（如取消原因）
    CONSTRAINT `fk_order_history_order` FOREIGN KEY (`order_id`) REFERENCES `hotelorder_v1`(`order_id`) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX `idx_order_history_order` (`order_id`)  -- 提高查询效率
);
