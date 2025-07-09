-- 应用运维监控系统数据库初始化脚本
-- 版本: 1.0
-- 创建日期: 2024-01-01

-- 如果数据库已存在则删除（谨慎使用）
-- DROP DATABASE IF EXISTS app_monitor_db;

-- 创建数据库
CREATE DATABASE IF NOT EXISTS app_monitor_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE app_monitor_db;

-- 1. 应用表 (APPLICATION)
CREATE TABLE IF NOT EXISTS application (
    app_id VARCHAR(36) PRIMARY KEY,
    app_name VARCHAR(100) NOT NULL,
    app_code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    owner_team VARCHAR(100),
    business_domain VARCHAR(100),
    critical_level TINYINT COMMENT '1-5, 5为最高',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status TINYINT DEFAULT 1 COMMENT '0-禁用,1-启用'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. 服务器表 (SERVER)
CREATE TABLE IF NOT EXISTS server (
    server_id VARCHAR(36) PRIMARY KEY,
    hostname VARCHAR(100) NOT NULL,
    ip_address VARCHAR(15) NOT NULL,
    os_type VARCHAR(20),
    os_version VARCHAR(50),
    cpu_cores INT,
    memory_gb DECIMAL(5,1),
    disk_gb INT,
    rack_location VARCHAR(100),
    data_center VARCHAR(50),
    status TINYINT DEFAULT 1 COMMENT '0-下线,1-在线,2-维护',
    last_heartbeat DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 实例表 (INSTANCE)
CREATE TABLE IF NOT EXISTS instance (
    instance_id VARCHAR(36) PRIMARY KEY,
    app_id VARCHAR(36) NOT NULL,
    server_id VARCHAR(36) NOT NULL,
    instance_name VARCHAR(100) NOT NULL,
    instance_type TINYINT COMMENT '1-容器,2-虚拟机,3-物理机',
    deploy_path VARCHAR(255),
    port INT,
    start_cmd VARCHAR(255),
    health_check_url VARCHAR(255),
    status TINYINT DEFAULT 1 COMMENT '0-停止,1-运行,2-异常',
    start_time DATETIME,
    FOREIGN KEY (app_id) REFERENCES application(app_id) ON DELETE CASCADE,
    FOREIGN KEY (server_id) REFERENCES server(server_id) ON DELETE CASCADE,
    INDEX idx_app_id (app_id),
    INDEX idx_server_id (server_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. 监控指标表 (MONITOR_ITEM)
CREATE TABLE IF NOT EXISTS monitor_item (
    item_id VARCHAR(36) PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    item_code VARCHAR(50) UNIQUE NOT NULL,
    app_id VARCHAR(36),
    instance_id VARCHAR(36),
    metric_type VARCHAR(50) NOT NULL COMMENT 'CPU/MEMORY/DISK/REQUEST_COUNT等',
    collect_interval INT COMMENT '采集间隔(秒)',
    unit VARCHAR(20),
    threshold_warning DECIMAL(10,2),
    threshold_critical DECIMAL(10,2),
    is_enabled TINYINT DEFAULT 1,
    FOREIGN KEY (app_id) REFERENCES application(app_id) ON DELETE CASCADE,
    FOREIGN KEY (instance_id) REFERENCES instance(instance_id) ON DELETE CASCADE,
    INDEX idx_app_id (app_id),
    INDEX idx_instance_id (instance_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. 告警规则表 (ALERT_RULE)
CREATE TABLE IF NOT EXISTS alert_rule (
    rule_id VARCHAR(36) PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    item_id VARCHAR(36) NOT NULL,
    condition_type TINYINT COMMENT '1-大于,2-小于,3-等于,4-不等于',
    threshold_value DECIMAL(10,2),
    severity TINYINT COMMENT '1-信息,2-警告,3-严重,4-致命',
    continuous_count INT DEFAULT 1 COMMENT '连续触发次数',
    summary_template VARCHAR(255),
    description_template TEXT,
    is_enabled TINYINT DEFAULT 1,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES monitor_item(item_id) ON DELETE CASCADE,
    INDEX idx_item_id (item_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. 告警事件表 (ALERT_EVENT)
CREATE TABLE IF NOT EXISTS alert_event (
    event_id VARCHAR(36) PRIMARY KEY,
    rule_id VARCHAR(36) NOT NULL,
    instance_id VARCHAR(36) NOT NULL,
    trigger_value DECIMAL(10,2),
    severity TINYINT,
    status TINYINT DEFAULT 0 COMMENT '0-新建,1-已确认,2-已解决',
    start_time DATETIME,
    end_time DATETIME,
    acknowledge_by VARCHAR(50),
    acknowledge_time DATETIME,
    FOREIGN KEY (rule_id) REFERENCES alert_rule(rule_id) ON DELETE CASCADE,
    FOREIGN KEY (instance_id) REFERENCES instance(instance_id) ON DELETE CASCADE,
    INDEX idx_rule_id (rule_id),
    INDEX idx_instance_id (instance_id),
    INDEX idx_status (status),
    INDEX idx_start_time (start_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. 指标数据表 (METRIC_DATA)
-- 注意：分区表不支持外键约束，主键必须包含分区字段
CREATE TABLE IF NOT EXISTS metric_data (
    data_id BIGINT AUTO_INCREMENT,
    item_id VARCHAR(36) NOT NULL,
    instance_id VARCHAR(36) NOT NULL,
    metric_value DECIMAL(15,2),
    collect_time DATETIME NOT NULL,
    PRIMARY KEY (data_id, collect_time),
    INDEX idx_collect_time (collect_time),
    INDEX idx_item_instance (item_id, instance_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
PARTITION BY RANGE (TO_DAYS(collect_time)) (
    PARTITION p0 VALUES LESS THAN (TO_DAYS('2024-01-01')),
    PARTITION p1 VALUES LESS THAN (TO_DAYS('2024-04-01')),
    PARTITION p2 VALUES LESS THAN (TO_DAYS('2024-07-01')),
    PARTITION p3 VALUES LESS THAN (TO_DAYS('2024-10-01')),
    PARTITION p4 VALUES LESS THAN (TO_DAYS('2025-01-01')),
    PARTITION pmax VALUES LESS THAN MAXVALUE
);

-- 8. 通知配置表 (NOTIFICATION)
CREATE TABLE IF NOT EXISTS notification (
    notify_id VARCHAR(36) PRIMARY KEY,
    rule_id VARCHAR(36) NOT NULL,
    notify_type VARCHAR(20) COMMENT 'EMAIL/SMS/WECHAT/WEBHOOK等',
    notify_target VARCHAR(255) NOT NULL,
    notify_template TEXT,
    is_enabled TINYINT DEFAULT 1,
    FOREIGN KEY (rule_id) REFERENCES alert_rule(rule_id) ON DELETE CASCADE,
    INDEX idx_rule_id (rule_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. 维护窗口表 (MAINTENANCE)
CREATE TABLE IF NOT EXISTS maintenance (
    maintenance_id VARCHAR(36) PRIMARY KEY,
    app_id VARCHAR(36),
    instance_id VARCHAR(36),
    server_id VARCHAR(36),
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    reason TEXT,
    created_by VARCHAR(50) NOT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (app_id) REFERENCES application(app_id) ON DELETE CASCADE,
    FOREIGN KEY (instance_id) REFERENCES instance(instance_id) ON DELETE CASCADE,
    FOREIGN KEY (server_id) REFERENCES server(server_id) ON DELETE CASCADE,
    INDEX idx_app_id (app_id),
    INDEX idx_instance_id (instance_id),
    INDEX idx_server_id (server_id),
    INDEX idx_time_range (start_time, end_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建完成后输出成功信息
SELECT '应用运维监控系统数据库表结构创建完成' AS message;