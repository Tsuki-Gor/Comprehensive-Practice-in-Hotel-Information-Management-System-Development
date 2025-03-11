DROP TABLE IF EXISTS `hotelorder_v1`;
CREATE TABLE `hotelorder_v1` (
  `order_id` INT AUTO_INCREMENT PRIMARY KEY,  -- 新增自增主键
  `id` VARCHAR(255) NOT NULL,                 -- 客户 ID 或 团队 ID（保持）
  `ordertype` VARCHAR(255) NOT NULL,          -- 个人/团队
  `start_time` DATE NOT NULL,
  `end_time` DATE NOT NULL,
  `rid` VARCHAR(255) NOT NULL,                -- 房间号
  `pay_type` VARCHAR(50) NULL DEFAULT NULL,   -- 支付方式
  `pay_status` ENUM('pending', 'paid', 'failed') NOT NULL DEFAULT 'pending',  -- 支付状态
  `money` DECIMAL(10,2) NOT NULL,             -- 房费金额，改为 DECIMAL
  `order_status` ENUM('pending', 'paid', 'cancelled', 'completed') NOT NULL DEFAULT 'pending', -- 订单状态
  `remark` VARCHAR(255) NULL DEFAULT NULL,    -- 订单备注
  `order_time` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `register_sid` VARCHAR(255) NULL DEFAULT NULL, -- 员工 ID
  INDEX `idx_hotelorder_id` (`id`),           -- 为客户/团队 ID 添加索引，加速查询
  INDEX `idx_hotelorder_start_time` (`start_time`),  -- 为入住时间添加索引
  CONSTRAINT `hotelorder_v1_ibfk_1` FOREIGN KEY (`rid`) REFERENCES `room` (`rid`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `hotelorder_v1_ibfk_2` FOREIGN KEY (`register_sid`) REFERENCES `staff` (`sid`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
