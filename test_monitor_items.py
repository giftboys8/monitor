#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试监控指标是否已成功初始化
"""

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

def test_monitor_items():
    """测试监控指标数据"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 查询监控指标数量
        cursor.execute("SELECT COUNT(*) FROM monitor_item")
        count = cursor.fetchone()[0]
        print(f"监控指标总数: {count}")
        
        if count > 0:
            # 查询所有监控指标
            cursor.execute("""
                SELECT item_name, metric_type, unit, threshold_warning, threshold_critical, is_enabled
                FROM monitor_item 
                ORDER BY metric_type, item_name
            """)
            
            print("\n监控指标列表:")
            print("-" * 80)
            print(f"{'指标名称':<20} {'类型':<12} {'单位':<8} {'警告阈值':<10} {'严重阈值':<10} {'状态':<6}")
            print("-" * 80)
            
            for row in cursor.fetchall():
                status = "启用" if row[5] == 1 else "禁用"
                print(f"{row[0]:<20} {row[1]:<12} {row[2]:<8} {row[3]:<10} {row[4]:<10} {status:<6}")
        else:
            print("监控指标表为空，需要运行初始化脚本")
        
    except Exception as e:
        print(f"查询失败: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    test_monitor_items()