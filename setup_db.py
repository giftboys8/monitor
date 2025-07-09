#!/usr/bin/env python3
import pymysql

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3308,
    'user': 'root',
    'password': '123456',
    'charset': 'utf8mb4'
}

def execute_sql_file(file_path):
    """执行SQL文件"""
    try:
        # 连接到MySQL服务器（不指定数据库）
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 读取SQL文件
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割SQL语句并执行
        sql_statements = sql_content.split(';')
        
        for statement in sql_statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    print(f"执行成功: {statement[:50]}...")
                except Exception as e:
                    print(f"执行失败: {statement[:50]}... 错误: {e}")
        
        conn.commit()
        print("SQL文件执行完成")
        
        # 验证表是否创建成功
        cursor.execute("USE app_monitor_db")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"创建的表: {[table[0] for table in tables]}")
        
        conn.close()
        
    except Exception as e:
        print(f"执行SQL文件失败: {e}")

if __name__ == '__main__':
    execute_sql_file('/opt/work/ai_training/monitor/docs/db/init.sql')