#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控指标初始化脚本
用于在数据库中初始化常用的监控指标
"""

import pymysql
import uuid
from datetime import datetime

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3308,
    'user': 'root',
    'password': '123456',
    'database': 'app_monitor_db',
    'charset': 'utf8mb4'
}

# 默认监控指标配置
DEFAULT_MONITOR_ITEMS = [
    {
        'item_name': 'CPU使用率',
        'item_code': 'cpu_usage',
        'metric_type': 'CPU',
        'collect_interval': 60,
        'unit': '%',
        'threshold_warning': 70.0,
        'threshold_critical': 90.0
    },
    {
        'item_name': '内存使用率',
        'item_code': 'memory_usage',
        'metric_type': 'MEMORY',
        'collect_interval': 60,
        'unit': '%',
        'threshold_warning': 80.0,
        'threshold_critical': 95.0
    },
    {
        'item_name': '磁盘使用率',
        'item_code': 'disk_usage',
        'metric_type': 'DISK',
        'collect_interval': 300,
        'unit': '%',
        'threshold_warning': 80.0,
        'threshold_critical': 95.0
    },
    {
        'item_name': '网络入流量',
        'item_code': 'network_in',
        'metric_type': 'NETWORK',
        'collect_interval': 60,
        'unit': 'MB/s',
        'threshold_warning': 100.0,
        'threshold_critical': 500.0
    },
    {
        'item_name': '网络出流量',
        'item_code': 'network_out',
        'metric_type': 'NETWORK',
        'collect_interval': 60,
        'unit': 'MB/s',
        'threshold_warning': 100.0,
        'threshold_critical': 500.0
    },
    {
        'item_name': '请求响应时间',
        'item_code': 'response_time',
        'metric_type': 'REQUEST',
        'collect_interval': 30,
        'unit': 'ms',
        'threshold_warning': 1000.0,
        'threshold_critical': 3000.0
    },
    {
        'item_name': '请求成功率',
        'item_code': 'success_rate',
        'metric_type': 'REQUEST',
        'collect_interval': 60,
        'unit': '%',
        'threshold_warning': 95.0,
        'threshold_critical': 90.0
    },
    {
        'item_name': '并发连接数',
        'item_code': 'concurrent_connections',
        'metric_type': 'CONNECTION',
        'collect_interval': 60,
        'unit': '个',
        'threshold_warning': 1000.0,
        'threshold_critical': 2000.0
    },
    {
        'item_name': 'JVM堆内存使用率',
        'item_code': 'jvm_heap_usage',
        'metric_type': 'JVM',
        'collect_interval': 60,
        'unit': '%',
        'threshold_warning': 80.0,
        'threshold_critical': 95.0
    },
    {
        'item_name': 'GC频率',
        'item_code': 'gc_frequency',
        'metric_type': 'JVM',
        'collect_interval': 60,
        'unit': '次/分钟',
        'threshold_warning': 10.0,
        'threshold_critical': 30.0
    },
    {
        'item_name': '数据库连接数',
        'item_code': 'db_connections',
        'metric_type': 'DATABASE',
        'collect_interval': 60,
        'unit': '个',
        'threshold_warning': 80.0,
        'threshold_critical': 100.0
    },
    {
        'item_name': '队列长度',
        'item_code': 'queue_length',
        'metric_type': 'QUEUE',
        'collect_interval': 30,
        'unit': '个',
        'threshold_warning': 1000.0,
        'threshold_critical': 5000.0
    }
]

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

def init_monitor_items():
    """初始化监控指标"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查是否已有数据
        cursor.execute("SELECT COUNT(*) FROM monitor_item")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"监控指标表中已有 {count} 条数据，将追加新的监控指标")
        else:
            print("监控指标表为空，开始初始化默认监控指标")
        
        # 插入默认监控指标（跳过已存在的）
        insert_sql = """
            INSERT INTO monitor_item (
                item_id, item_name, item_code, metric_type, collect_interval, 
                unit, threshold_warning, threshold_critical, is_enabled
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        check_sql = "SELECT COUNT(*) FROM monitor_item WHERE item_code = %s"
        
        inserted_count = 0
        skipped_count = 0
        
        for item in DEFAULT_MONITOR_ITEMS:
            # 检查是否已存在
            cursor.execute(check_sql, (item['item_code'],))
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                print(f"⚠ 跳过已存在的监控指标: {item['item_name']} ({item['metric_type']})")
                skipped_count += 1
                continue
            
            # 插入新的监控指标
            item_id = str(uuid.uuid4())
            cursor.execute(insert_sql, (
                item_id,
                item['item_name'],
                item['item_code'],
                item['metric_type'],
                item['collect_interval'],
                item['unit'],
                item['threshold_warning'],
                item['threshold_critical'],
                1  # is_enabled
            ))
            inserted_count += 1
            print(f"✓ 已添加监控指标: {item['item_name']} ({item['metric_type']})")
        
        conn.commit()
        if inserted_count > 0:
            print(f"\n成功添加 {inserted_count} 个新的监控指标！")
        if skipped_count > 0:
            print(f"跳过 {skipped_count} 个已存在的监控指标。")
        if inserted_count == 0 and skipped_count > 0:
            print("\n所有监控指标都已存在，无需添加新指标。")
        
        # 显示初始化结果
        cursor.execute("""
            SELECT item_name, metric_type, unit, threshold_warning, threshold_critical
            FROM monitor_item 
            ORDER BY metric_type, item_name
        """)
        
        print("\n当前监控指标列表:")
        print("-" * 80)
        print(f"{'指标名称':<20} {'类型':<12} {'单位':<8} {'警告阈值':<10} {'严重阈值':<10}")
        print("-" * 80)
        
        for row in cursor.fetchall():
            print(f"{row[0]:<20} {row[1]:<12} {row[2]:<8} {row[3]:<10} {row[4]:<10}")
        
    except Exception as e:
        print(f"初始化失败: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def main():
    """主函数"""
    print("=" * 60)
    print("应用运维监控系统 - 监控指标初始化工具")
    print("=" * 60)
    print()
    
    try:
        # 测试数据库连接
        conn = get_db_connection()
        conn.close()
        print("✓ 数据库连接成功")
        
        # 初始化监控指标
        init_monitor_items()
        
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        print("请检查数据库配置和连接状态")

if __name__ == '__main__':
    main()