#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

def check_alert_data():
    try:
        # 连接数据库
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=== 检查告警规则数据 ===")
        # 检查告警规则表
        cursor.execute("SELECT COUNT(*) FROM alert_rule")
        rule_count = cursor.fetchone()[0]
        print(f"告警规则总数: {rule_count}")
        
        if rule_count > 0:
            cursor.execute("SELECT rule_id, rule_name, monitor_item_id, threshold_value, is_enabled FROM alert_rule LIMIT 5")
            rules = cursor.fetchall()
            print("\n前5条告警规则:")
            for rule in rules:
                print(f"  ID: {rule[0]}, 名称: {rule[1]}, 监控项ID: {rule[2]}, 阈值: {rule[3]}, 启用: {rule[4]}")
        
        print("\n=== 检查告警事件数据 ===")
        # 检查告警事件表
        cursor.execute("SELECT COUNT(*) FROM alert_event")
        alert_count = cursor.fetchone()[0]
        print(f"告警事件总数: {alert_count}")
        
        if alert_count > 0:
            cursor.execute("SELECT event_id, rule_id, severity, status, start_time FROM alert_event ORDER BY start_time DESC LIMIT 5")
            alerts = cursor.fetchall()
            print("\n最近5条告警事件:")
            for alert in alerts:
                print(f"  ID: {alert[0]}, 规则ID: {alert[1]}, 级别: {alert[2]}, 状态: {alert[3]}, 时间: {alert[4]}")
        
        print("\n=== 检查监控项数据 ===")
        cursor.execute("SELECT COUNT(*) FROM monitor_item")
        item_count = cursor.fetchone()[0]
        print(f"监控项总数: {item_count}")
        
        if item_count > 0:
            cursor.execute("SELECT item_id, item_name, item_code FROM monitor_item LIMIT 5")
            items = cursor.fetchall()
            print("\n前5个监控项:")
            for item in items:
                print(f"  ID: {item[0]}, 名称: {item[1]}, 代码: {item[2]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"数据库连接或查询错误: {e}")

if __name__ == "__main__":
    check_alert_data()