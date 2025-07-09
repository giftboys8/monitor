#!/usr/bin/env python3
import pymysql

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3308,
    'user': 'root',
    'password': '123456',
    'database': 'app_monitor_db',
    'charset': 'utf8mb4'
}

def create_tables():
    """创建所有必要的表"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 创建server表
        cursor.execute("""
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
                status TINYINT DEFAULT 1,
                last_heartbeat DATETIME
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("server表创建成功")
        
        # 创建instance表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS instance (
                instance_id VARCHAR(36) PRIMARY KEY,
                app_id VARCHAR(36) NOT NULL,
                server_id VARCHAR(36) NOT NULL,
                instance_name VARCHAR(100) NOT NULL,
                instance_type TINYINT,
                deploy_path VARCHAR(255),
                port INT,
                start_cmd VARCHAR(255),
                health_check_url VARCHAR(255),
                status TINYINT DEFAULT 1,
                start_time DATETIME,
                INDEX idx_app_id (app_id),
                INDEX idx_server_id (server_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("instance表创建成功")
        
        # 创建monitor_item表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitor_item (
                item_id VARCHAR(36) PRIMARY KEY,
                item_name VARCHAR(100) NOT NULL,
                item_code VARCHAR(50) UNIQUE NOT NULL,
                app_id VARCHAR(36),
                instance_id VARCHAR(36),
                metric_type VARCHAR(50) NOT NULL,
                collect_interval INT,
                unit VARCHAR(20),
                threshold_warning DECIMAL(10,2),
                threshold_critical DECIMAL(10,2),
                is_enabled TINYINT DEFAULT 1,
                INDEX idx_app_id (app_id),
                INDEX idx_instance_id (instance_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("monitor_item表创建成功")
        
        # 创建alert_rule表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_rule (
                rule_id VARCHAR(36) PRIMARY KEY,
                rule_name VARCHAR(100) NOT NULL,
                item_id VARCHAR(36) NOT NULL,
                condition_type TINYINT,
                threshold_value DECIMAL(10,2),
                severity TINYINT,
                continuous_count INT DEFAULT 1,
                summary_template VARCHAR(255),
                description_template TEXT,
                is_enabled TINYINT DEFAULT 1,
                create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_item_id (item_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("alert_rule表创建成功")
        
        # 创建alert_event表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_event (
                event_id VARCHAR(36) PRIMARY KEY,
                rule_id VARCHAR(36) NOT NULL,
                instance_id VARCHAR(36) NOT NULL,
                trigger_value DECIMAL(10,2),
                severity TINYINT,
                status TINYINT DEFAULT 0,
                start_time DATETIME,
                end_time DATETIME,
                acknowledge_by VARCHAR(50),
                acknowledge_time DATETIME,
                INDEX idx_rule_id (rule_id),
                INDEX idx_instance_id (instance_id),
                INDEX idx_status (status),
                INDEX idx_start_time (start_time)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("alert_event表创建成功")
        
        conn.commit()
        
        # 验证表是否创建成功
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"数据库中的表: {[table[0] for table in tables]}")
        
        conn.close()
        print("所有表创建完成")
        
    except Exception as e:
        print(f"创建表失败: {e}")

if __name__ == '__main__':
    create_tables()