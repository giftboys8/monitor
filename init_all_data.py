#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用运维监控系统 - 统一数据初始化脚本
整合了监控项初始化和完整系统数据初始化功能
"""

import pymysql
import uuid
from datetime import datetime, timedelta
import random
import sys

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3308,
    'user': 'root',
    'password': '123456',
    'database': 'app_monitor_db',
    'charset': 'utf8mb4'
}

def generate_uuid():
    """生成UUID"""
    return str(uuid.uuid4())

def init_basic_monitor_items(cursor):
    """初始化基础监控项（通用监控指标）"""
    print("正在初始化基础监控项...")
    
    # 基础监控指标定义
    basic_monitor_items = [
        {
            'item_name': 'CPU使用率',
            'item_code': 'cpu_usage',
            'metric_type': 'CPU',
            'collect_interval': 60,
            'unit': '%',
            'threshold_warning': 70.0,
            'threshold_critical': 85.0
        },
        {
            'item_name': '内存使用率',
            'item_code': 'memory_usage',
            'metric_type': 'MEMORY',
            'collect_interval': 60,
            'unit': '%',
            'threshold_warning': 75.0,
            'threshold_critical': 90.0
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
            'threshold_critical': 200.0
        },
        {
            'item_name': '网络出流量',
            'item_code': 'network_out',
            'metric_type': 'NETWORK',
            'collect_interval': 60,
            'unit': 'MB/s',
            'threshold_warning': 100.0,
            'threshold_critical': 200.0
        },
        {
            'item_name': '请求响应时间',
            'item_code': 'response_time',
            'metric_type': 'REQUEST',
            'collect_interval': 30,
            'unit': 'ms',
            'threshold_warning': 500.0,
            'threshold_critical': 1000.0
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
            'threshold_warning': 70.0,
            'threshold_critical': 85.0
        },
        {
            'item_name': 'GC频率',
            'item_code': 'gc_frequency',
            'metric_type': 'JVM',
            'collect_interval': 60,
            'unit': '次/分钟',
            'threshold_warning': 10.0,
            'threshold_critical': 20.0
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
            'threshold_warning': 100.0,
            'threshold_critical': 500.0
        }
    ]
    
    added_count = 0
    skipped_count = 0
    
    for item_data in basic_monitor_items:
        try:
            # 检查是否已存在相同的item_code
            cursor.execute("SELECT COUNT(*) FROM monitor_item WHERE item_code = %s", (item_data['item_code'],))
            if cursor.fetchone()[0] > 0:
                print(f"  跳过已存在的监控项: {item_data['item_name']}")
                skipped_count += 1
                continue
            
            # 插入新的监控项
            item_data['item_id'] = generate_uuid()
            item_data['is_enabled'] = 1
            
            cursor.execute("""
                INSERT INTO monitor_item (item_id, item_name, item_code, metric_type, 
                                        collect_interval, unit, threshold_warning, 
                                        threshold_critical, is_enabled)
                VALUES (%(item_id)s, %(item_name)s, %(item_code)s, %(metric_type)s,
                       %(collect_interval)s, %(unit)s, %(threshold_warning)s,
                       %(threshold_critical)s, %(is_enabled)s)
            """, item_data)
            
            added_count += 1
            print(f"  添加监控项: {item_data['item_name']}")
            
        except Exception as e:
            print(f"  添加监控项失败 {item_data['item_name']}: {e}")
    
    print(f"基础监控项初始化完成: 新增 {added_count} 个，跳过 {skipped_count} 个")
    
    # 返回所有监控项ID
    cursor.execute("SELECT item_id FROM monitor_item WHERE is_enabled = 1")
    return [row[0] for row in cursor.fetchall()]

def init_applications(cursor):
    """初始化应用数据"""
    print("正在初始化应用数据...")
    
    applications = [
        {
            'app_id': generate_uuid(),
            'app_name': '用户管理系统',
            'app_code': 'user-mgmt',
            'description': '负责用户注册、登录、权限管理等功能',
            'owner_team': '用户中心团队',
            'business_domain': '用户服务',
            'critical_level': 5
        },
        {
            'app_id': generate_uuid(),
            'app_name': '订单处理系统',
            'app_code': 'order-service',
            'description': '处理订单创建、支付、发货等业务流程',
            'owner_team': '交易团队',
            'business_domain': '电商交易',
            'critical_level': 5
        },
        {
            'app_id': generate_uuid(),
            'app_name': '商品管理系统',
            'app_code': 'product-mgmt',
            'description': '商品信息管理、库存管理、价格管理',
            'owner_team': '商品团队',
            'business_domain': '商品服务',
            'critical_level': 4
        },
        {
            'app_id': generate_uuid(),
            'app_name': '支付网关',
            'app_code': 'payment-gateway',
            'description': '统一支付接口，对接多种支付方式',
            'owner_team': '支付团队',
            'business_domain': '支付服务',
            'critical_level': 5
        },
        {
            'app_id': generate_uuid(),
            'app_name': '数据分析平台',
            'app_code': 'data-analytics',
            'description': '业务数据分析、报表生成、数据挖掘',
            'owner_team': '数据团队',
            'business_domain': '数据服务',
            'critical_level': 3
        }
    ]
    
    for app in applications:
        cursor.execute("""
            INSERT INTO application (app_id, app_name, app_code, description, 
                                   owner_team, business_domain, critical_level, status)
            VALUES (%(app_id)s, %(app_name)s, %(app_code)s, %(description)s,
                   %(owner_team)s, %(business_domain)s, %(critical_level)s, 1)
        """, app)
    
    print(f"已初始化 {len(applications)} 个应用")
    return [app['app_id'] for app in applications]

def init_servers(cursor):
    """初始化服务器数据"""
    print("正在初始化服务器数据...")
    
    servers = [
        {
            'server_id': generate_uuid(),
            'hostname': 'web-server-01',
            'ip_address': '192.168.1.10',
            'os_type': 'Ubuntu',
            'os_version': '20.04 LTS',
            'cpu_cores': 8,
            'memory_gb': 16.0,
            'disk_gb': 500,
            'rack_location': 'A1-01',
            'data_center': '北京数据中心'
        },
        {
            'server_id': generate_uuid(),
            'hostname': 'web-server-02',
            'ip_address': '192.168.1.11',
            'os_type': 'Ubuntu',
            'os_version': '20.04 LTS',
            'cpu_cores': 8,
            'memory_gb': 16.0,
            'disk_gb': 500,
            'rack_location': 'A1-02',
            'data_center': '北京数据中心'
        },
        {
            'server_id': generate_uuid(),
            'hostname': 'db-server-01',
            'ip_address': '192.168.1.20',
            'os_type': 'CentOS',
            'os_version': '7.9',
            'cpu_cores': 16,
            'memory_gb': 64.0,
            'disk_gb': 2000,
            'rack_location': 'B1-01',
            'data_center': '北京数据中心'
        },
        {
            'server_id': generate_uuid(),
            'hostname': 'cache-server-01',
            'ip_address': '192.168.1.30',
            'os_type': 'Ubuntu',
            'os_version': '18.04 LTS',
            'cpu_cores': 4,
            'memory_gb': 32.0,
            'disk_gb': 200,
            'rack_location': 'C1-01',
            'data_center': '北京数据中心'
        },
        {
            'server_id': generate_uuid(),
            'hostname': 'app-server-01',
            'ip_address': '192.168.1.40',
            'os_type': 'Ubuntu',
            'os_version': '20.04 LTS',
            'cpu_cores': 12,
            'memory_gb': 32.0,
            'disk_gb': 1000,
            'rack_location': 'D1-01',
            'data_center': '北京数据中心'
        }
    ]
    
    for server in servers:
        server['last_heartbeat'] = datetime.now()
        cursor.execute("""
            INSERT INTO server (server_id, hostname, ip_address, os_type, os_version,
                              cpu_cores, memory_gb, disk_gb, rack_location, 
                              data_center, status, last_heartbeat)
            VALUES (%(server_id)s, %(hostname)s, %(ip_address)s, %(os_type)s, %(os_version)s,
                   %(cpu_cores)s, %(memory_gb)s, %(disk_gb)s, %(rack_location)s,
                   %(data_center)s, 1, %(last_heartbeat)s)
        """, server)
    
    print(f"已初始化 {len(servers)} 台服务器")
    return [server['server_id'] for server in servers]

def init_instances(cursor, app_ids, server_ids):
    """初始化实例数据"""
    print("正在初始化实例数据...")
    
    instances = []
    instance_types = [1, 2, 3]  # 1-容器,2-虚拟机,3-物理机
    ports = [8080, 8081, 8082, 8083, 8084, 9000, 9001, 9002]
    
    # 为每个应用在不同服务器上创建实例
    for i, app_id in enumerate(app_ids):
        for j in range(2):  # 每个应用创建2个实例
            server_id = server_ids[(i * 2 + j) % len(server_ids)]
            instance = {
                'instance_id': generate_uuid(),
                'app_id': app_id,
                'server_id': server_id,
                'instance_name': f'instance-{i+1}-{j+1}',
                'instance_type': random.choice(instance_types),
                'deploy_path': f'/opt/apps/app-{i+1}/instance-{j+1}',
                'port': ports[(i * 2 + j) % len(ports)],
                'start_cmd': f'java -jar app-{i+1}.jar --server.port={ports[(i * 2 + j) % len(ports)]}',
                'health_check_url': f'http://localhost:{ports[(i * 2 + j) % len(ports)]}/health',
                'status': random.choice([1, 1, 1, 2]),  # 大部分运行正常
                'start_time': datetime.now() - timedelta(days=random.randint(1, 30))
            }
            instances.append(instance)
    
    for instance in instances:
        cursor.execute("""
            INSERT INTO instance (instance_id, app_id, server_id, instance_name,
                                instance_type, deploy_path, port, start_cmd,
                                health_check_url, status, start_time)
            VALUES (%(instance_id)s, %(app_id)s, %(server_id)s, %(instance_name)s,
                   %(instance_type)s, %(deploy_path)s, %(port)s, %(start_cmd)s,
                   %(health_check_url)s, %(status)s, %(start_time)s)
        """, instance)
    
    print(f"已初始化 {len(instances)} 个实例")
    return [instance['instance_id'] for instance in instances]

def init_alert_rules(cursor, item_ids):
    """初始化告警规则数据"""
    print("正在初始化告警规则数据...")
    
    alert_rules = []
    
    # 为前10个监控项创建告警规则
    for item_id in item_ids[:10]:
        # 为每个监控项创建警告和严重两个级别的规则
        for severity, condition in [(2, 1), (3, 1)]:  # 2-警告,3-严重; 1-大于
            rule = {
                'rule_id': generate_uuid(),
                'rule_name': f'监控项告警规则-{severity}级',
                'item_id': item_id,
                'condition_type': condition,
                'threshold_value': 80.0 if severity == 2 else 95.0,
                'severity': severity,
                'continuous_count': 2 if severity == 2 else 1,
                'summary_template': f'监控指标超过阈值',
                'description_template': f'监控指标持续超过{"警告" if severity == 2 else "严重"}阈值'
            }
            alert_rules.append(rule)
    
    for rule in alert_rules:
        cursor.execute("""
            INSERT INTO alert_rule (rule_id, rule_name, item_id, condition_type,
                                  threshold_value, severity, continuous_count,
                                  summary_template, description_template, is_enabled)
            VALUES (%(rule_id)s, %(rule_name)s, %(item_id)s, %(condition_type)s,
                   %(threshold_value)s, %(severity)s, %(continuous_count)s,
                   %(summary_template)s, %(description_template)s, 1)
        """, rule)
    
    print(f"已初始化 {len(alert_rules)} 个告警规则")
    return [rule['rule_id'] for rule in alert_rules]

def init_alert_events(cursor, rule_ids, instance_ids):
    """初始化告警事件数据"""
    print("正在初始化告警事件数据...")
    
    alert_events = []
    
    # 创建一些测试告警事件
    for i in range(15):
        rule_id = random.choice(rule_ids)
        instance_id = random.choice(instance_ids)
        start_time = datetime.now() - timedelta(hours=random.randint(1, 72))
        
        event = {
            'event_id': generate_uuid(),
            'rule_id': rule_id,
            'instance_id': instance_id,
            'trigger_value': random.uniform(85.0, 98.0),
            'severity': random.choice([2, 3, 4]),
            'status': random.choice([0, 0, 1, 2]),  # 大部分未处理
            'start_time': start_time,
            'end_time': None,
            'acknowledge_by': None,
            'acknowledge_time': None
        }
        
        # 如果状态不是新建，设置确认信息
        if event['status'] > 0:
            event['acknowledge_by'] = f'admin{random.randint(1, 3)}'
            event['acknowledge_time'] = start_time + timedelta(minutes=random.randint(10, 120))
        
        # 如果状态是已解决，设置结束时间
        if event['status'] == 2:
            event['end_time'] = event['acknowledge_time'] + timedelta(minutes=random.randint(30, 180))
        
        alert_events.append(event)
    
    for event in alert_events:
        cursor.execute("""
            INSERT INTO alert_event (event_id, rule_id, instance_id, trigger_value,
                                   severity, status, start_time, end_time,
                                   acknowledge_by, acknowledge_time)
            VALUES (%(event_id)s, %(rule_id)s, %(instance_id)s, %(trigger_value)s,
                   %(severity)s, %(status)s, %(start_time)s, %(end_time)s,
                   %(acknowledge_by)s, %(acknowledge_time)s)
        """, event)
    
    print(f"已初始化 {len(alert_events)} 个告警事件")

def init_metric_data(cursor, item_ids, instance_ids):
    """初始化指标数据"""
    print("正在初始化指标数据...")
    
    metric_data = []
    
    # 为每个监控项生成最近24小时的数据
    for item_id in item_ids[:15]:  # 限制数据量，只为前15个监控项生成数据
        instance_id = random.choice(instance_ids)
        
        # 生成最近24小时的数据，每10分钟一个数据点
        for i in range(144):  # 24 * 60 / 10 = 144
            collect_time = datetime.now() - timedelta(minutes=i * 10)
            
            # 根据监控项类型生成不同范围的随机值
            if 'CPU' in item_id or 'MEMORY' in item_id or 'DISK' in item_id:
                metric_value = random.uniform(20.0, 85.0)
            elif 'REQUEST_COUNT' in item_id:
                metric_value = random.uniform(100.0, 1500.0)
            elif 'RESPONSE_TIME' in item_id:
                metric_value = random.uniform(50.0, 800.0)
            else:
                metric_value = random.uniform(0.0, 100.0)
            
            data = {
                'item_id': item_id,
                'instance_id': instance_id,
                'metric_value': round(metric_value, 2),
                'collect_time': collect_time
            }
            metric_data.append(data)
    
    # 批量插入数据
    batch_size = 500
    for i in range(0, len(metric_data), batch_size):
        batch = metric_data[i:i + batch_size]
        for data in batch:
            cursor.execute("""
                INSERT INTO metric_data (item_id, instance_id, metric_value, collect_time)
                VALUES (%(item_id)s, %(instance_id)s, %(metric_value)s, %(collect_time)s)
            """, data)
    
    print(f"已初始化 {len(metric_data)} 条指标数据")

def clear_existing_data(cursor):
    """清空现有数据"""
    print("清空现有数据...")
    tables = ['metric_data', 'alert_event', 'notification', 'alert_rule', 
             'monitor_item', 'maintenance', 'instance', 'server', 'application']
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
        print(f"  已清空表: {table}")

def init_monitor_items_only():
    """仅初始化监控项"""
    print("=== 仅初始化基础监控项 ===")
    
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # 初始化基础监控项
        init_basic_monitor_items(cursor)
        
        # 提交事务
        connection.commit()
        print("\n监控项初始化完成！")
        
    except Exception as e:
        print(f"初始化失败: {e}")
        if connection:
            connection.rollback()
    finally:
        if connection:
            connection.close()

def init_full_system(clear_data=False):
    """初始化完整系统数据"""
    print("=== 初始化完整系统数据 ===")
    
    try:
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # 是否清空现有数据
        if clear_data:
            clear_existing_data(cursor)
        
        # 初始化数据
        item_ids = init_basic_monitor_items(cursor)
        app_ids = init_applications(cursor)
        server_ids = init_servers(cursor)
        instance_ids = init_instances(cursor, app_ids, server_ids)
        rule_ids = init_alert_rules(cursor, item_ids)
        init_alert_events(cursor, rule_ids, instance_ids)
        init_metric_data(cursor, item_ids, instance_ids)
        
        # 提交事务
        connection.commit()
        print("\n完整系统数据初始化完成！")
        
    except Exception as e:
        print(f"初始化失败: {e}")
        if connection:
            connection.rollback()
    finally:
        if connection:
            connection.close()

def main():
    """主函数"""
    print("应用运维监控系统 - 统一数据初始化工具")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        print("请选择初始化模式:")
        print("1. 仅初始化监控项 (monitor-only)")
        print("2. 初始化完整系统数据 (full)")
        print("3. 清空并重新初始化完整系统数据 (full-clean)")
        
        choice = input("\n请输入选择 (1/2/3): ").strip()
        
        if choice == '1':
            mode = 'monitor-only'
        elif choice == '2':
            mode = 'full'
        elif choice == '3':
            mode = 'full-clean'
        else:
            print("无效选择，退出程序")
            return
    
    try:
        # 测试数据库连接
        connection = pymysql.connect(**DB_CONFIG)
        connection.close()
        print(f"数据库连接成功: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        print()
        
    except Exception as e:
        print(f"数据库连接失败: {e}")
        print("请检查数据库配置和服务状态")
        return
    
    # 根据模式执行相应的初始化
    if mode == 'monitor-only':
        init_monitor_items_only()
    elif mode == 'full':
        init_full_system(clear_data=False)
    elif mode == 'full-clean':
        confirm = input("警告：此操作将清空所有现有数据！确认继续？(yes/no): ")
        if confirm.lower() == 'yes':
            init_full_system(clear_data=True)
        else:
            print("操作已取消")
    else:
        print(f"未知模式: {mode}")
        print("支持的模式: monitor-only, full, full-clean")

if __name__ == '__main__':
    main()