CREATE DATABASE `binance_demo` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;


-- binance_demo.sys_user definition

CREATE TABLE `sys_user` (
  `id` int(100) NOT NULL,
  `type` char(1) DEFAULT NULL,
  `user_name` varchar(100) DEFAULT NULL,
  `create_time` datetime DEFAULT current_timestamp,
  `del_flag` char(1) NOT NULL DEFAULT '0' COMMENT '删除标志位：0未删除，1删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- binance_demo.order_book definition

CREATE TABLE `order_book` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `type` enum('buy','sell') NOT NULL,
  `order_price` decimal(10,2) NOT NULL COMMENT '期望价格',
  `order_amount` decimal(10,2) NOT NULL COMMENT '请求数额',
  `processed_amount` decimal(10,2) DEFAULT NULL COMMENT '已交易部分数额',
  `status` char(1) NOT NULL DEFAULT '0' COMMENT '订单状态: 0未完成，1完成',
  `create_time` datetime DEFAULT current_timestamp,
  `update_time` datetime ON UPDATE current_timestamp DEFAULT current_timestamp,
  `del_flag` char(1) NOT NULL DEFAULT '0' COMMENT '删除标志位：0未删除，1删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- binance_demo.trade_record definition

CREATE TABLE `trade_record` (
  `id` int(11) NOT NULL,
  `buyer_id` int(11) DEFAULT NULL,
  `seller_id` int(11) DEFAULT NULL,
  `trade_price` decimal(10,2) NOT NULL,
  `trade_amount` decimal(10,2) NOT NULL,
  `create_time` datetime DEFAULT current_timestamp,
  `del_flag` char(1) NOT NULL DEFAULT '0' COMMENT '删除标志位：0未删除，1删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
