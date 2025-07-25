#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用运维监控系统
主应用程序入口
"""

import uuid
from flask import Flask, render_template, jsonify, request, send_from_directory
import pymysql
from contextlib import contextmanager

app = Flask(__name__)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3308,
    'user': 'root',
    'password': '123456',
    'database': 'app_monitor_db',
    'charset': 'utf8mb4'
}

@contextmanager
def get_db_connection():
    """数据库连接上下文管理器"""
    connection = None
    try:
        connection = pymysql.connect(**DB_CONFIG)
        yield connection
    except Exception as e:
        if connection:
            connection.rollback()
        raise e
    finally:
        if connection:
            connection.close()

@app.route('/')
def index():
    """首页 - 监控概览"""
    return render_template('index.html')



@app.route('/alert-rules')
def alert_rules_page():
    """告警规则配置页面"""
    return send_from_directory('templates', 'alert_rules.html')

@app.route('/alerts')
def alerts_page():
    """告警管理页面"""
    return render_template('alerts.html')

@app.route('/api/dashboard')
def dashboard_data():
    """获取仪表板数据"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            # 应用总数
            cursor.execute("SELECT COUNT(*) as count FROM application WHERE status = 1")
            app_count = cursor.fetchone()['count']
            
            # 服务器总数
            cursor.execute("SELECT COUNT(*) as count FROM server WHERE status = 1")
            server_count = cursor.fetchone()['count']
            
            # 实例总数
            cursor.execute("SELECT COUNT(*) as count FROM instance WHERE status = 1")
            instance_count = cursor.fetchone()['count']
            
            # 活跃告警数
            cursor.execute("SELECT COUNT(*) as count FROM alert_event WHERE status = 0")
            alert_count = cursor.fetchone()['count']
            
            return jsonify({
                'success': True,
                'data': {
                    'app_count': app_count,
                    'server_count': server_count,
                    'instance_count': instance_count,
                    'alert_count': alert_count
                }
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/applications')
def get_applications():
    """获取应用列表"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
                SELECT app_id, app_name, app_code, description, owner_team, 
                       business_domain, critical_level, status, create_time
                FROM application 
                ORDER BY create_time DESC
            """)
            applications = cursor.fetchall()
            

            
            return jsonify({
                'success': True,
                'data': applications
            })
    except Exception as e:

        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/servers')
def get_servers():
    """获取服务器列表"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
                SELECT server_id, hostname, ip_address, os_type, os_version,
                       cpu_cores, memory_gb, disk_gb, status, last_heartbeat
                FROM server 
                ORDER BY hostname
            """)
            servers = cursor.fetchall()
            

            
            return jsonify({
                'success': True,
                'data': servers
            })
    except Exception as e:

        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/alerts', methods=['GET', 'POST'])
def handle_alerts():
    """获取告警列表或创建新告警"""
    if request.method == 'GET':
        try:
            # 获取分页参数
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 20))
            offset = (page - 1) * page_size
            
            # 获取筛选参数
            status = request.args.get('status')
            instance_id = request.args.get('instance_id')
            app_id = request.args.get('app_id')
            rule_name = request.args.get('rule_name')
            
            with get_db_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                
                # 构建WHERE条件
                where_conditions = []
                params = []
                
                if status is not None and status != '':
                    where_conditions.append("ae.status = %s")
                    params.append(int(status))
                
                if instance_id:
                    where_conditions.append("ae.instance_id = %s")
                    params.append(instance_id)
                
                if app_id:
                    where_conditions.append("a.app_id = %s")
                    params.append(app_id)
                
                if rule_name:
                    where_conditions.append("ar.rule_name LIKE %s")
                    params.append(f"%{rule_name}%")
                
                where_clause = ""
                if where_conditions:
                    where_clause = "WHERE " + " AND ".join(where_conditions)
                
                # 查询总数
                count_sql = f"""
                    SELECT COUNT(*) as total
                    FROM alert_event ae
                    JOIN alert_rule ar ON ae.rule_id = ar.rule_id
                    JOIN instance i ON ae.instance_id = i.instance_id
                    JOIN application a ON i.app_id = a.app_id
                    {where_clause}
                """
                cursor.execute(count_sql, params)
                total = cursor.fetchone()['total']
                
                # 查询数据
                data_sql = f"""
                    SELECT ae.event_id, ae.trigger_value, ae.severity, ae.status,
                           ae.start_time, ae.end_time, ar.rule_name, 
                           a.app_name, a.app_id, i.instance_name, i.instance_id
                    FROM alert_event ae
                    JOIN alert_rule ar ON ae.rule_id = ar.rule_id
                    JOIN instance i ON ae.instance_id = i.instance_id
                    JOIN application a ON i.app_id = a.app_id
                    {where_clause}
                    ORDER BY ae.start_time DESC
                    LIMIT %s OFFSET %s
                """
                params.extend([page_size, offset])
                cursor.execute(data_sql, params)
                alerts = cursor.fetchall()
                
                # 计算分页信息
                total_pages = (total + page_size - 1) // page_size
                
                return jsonify({
                    'success': True,
                    'data': alerts,
                    'pagination': {
                        'page': page,
                        'page_size': page_size,
                        'total': total,
                        'total_pages': total_pages,
                        'has_next': page < total_pages,
                        'has_prev': page > 1
                    }
                })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            event_id = str(uuid.uuid4())
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO alert_event 
                    (event_id, rule_id, instance_id, trigger_value, severity, status, start_time)
                    VALUES (%s, %s, %s, %s, %s, 0, NOW())
                """, (
                    event_id,
                    data['rule_id'],
                    data['instance_id'],
                    data['trigger_value'],
                    data['severity']
                ))
                conn.commit()
                

                return jsonify({
                    'success': True,
                    'data': {'event_id': event_id}
                })
        except Exception as e:

            return jsonify({'success': False, 'error': str(e)})

@app.route('/api/alert-rules', methods=['GET', 'POST'])
def handle_alert_rules():
    """获取告警规则列表或创建新告警规则"""
    if request.method == 'GET':
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute("""
                    SELECT rule_id, rule_name, threshold_value, severity, is_enabled
                    FROM alert_rule 
                    WHERE is_enabled = 1
                    ORDER BY rule_name
                """)
                rules = cursor.fetchall()
                
                return jsonify({
                    'success': True,
                    'data': rules
                })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO alert_rule (rule_name, item_id, condition_type, threshold_value, 
                                          severity, continuous_count, description_template, is_enabled, create_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 1, NOW())
                """, (
                    data['rule_name'],
                    data['item_id'],
                    data['condition_type'],
                    data['threshold_value'],
                    data['severity'],
                    data['continuous_count'],
                    data['description_template']
                ))
                
                conn.commit()
                return jsonify({'success': True, 'message': '告警规则创建成功'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

@app.route('/api/alert-rules/<rule_id>', methods=['DELETE'])
def delete_alert_rule(rule_id):
    """删除告警规则"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM alert_rule WHERE rule_id = %s", (rule_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                return jsonify({'success': True, 'message': '告警规则删除成功'})
            else:
                return jsonify({'success': False, 'error': '告警规则不存在'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/instances')
def get_instances():
    """获取实例列表"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
                SELECT i.instance_id, i.instance_name, a.app_name
                FROM instance i
                JOIN application a ON i.app_id = a.app_id
                WHERE i.status = 1
                ORDER BY a.app_name, i.instance_name
            """)
            instances = cursor.fetchall()
            
            return jsonify({
                'success': True,
                'data': instances
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/alert-rules-all')
def get_all_alert_rules():
    """获取所有告警规则（包括禁用的）"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
                SELECT ar.rule_id, ar.rule_name, ar.threshold_value, ar.severity, 
                       ar.is_enabled, ar.create_time, mi.item_name, mi.metric_type
                FROM alert_rule ar
                LEFT JOIN monitor_item mi ON ar.item_id = mi.item_id
                ORDER BY ar.create_time DESC
            """)
            rules = cursor.fetchall()
            
            return jsonify({
                'success': True,
                'data': rules
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/monitor-items')
def get_monitor_items():
    """获取监控指标列表"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
                SELECT item_id, item_name, metric_type, unit
                FROM monitor_item
                WHERE is_enabled = 1
                ORDER BY item_name
            """)
            items = cursor.fetchall()
            
            return jsonify({
                'success': True,
                'data': items
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/metrics/<instance_id>')
def get_metrics(instance_id):
    """获取实例监控指标数据"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
                SELECT md.metric_value, md.collect_time, mi.metric_type, mi.unit
                FROM metric_data md
                JOIN monitor_item mi ON md.item_id = mi.item_id
                WHERE md.instance_id = %s 
                AND md.collect_time >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
                ORDER BY md.collect_time DESC
            """, (instance_id,))
            metrics = cursor.fetchall()
            
            return jsonify({
                'success': True,
                'data': metrics
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)