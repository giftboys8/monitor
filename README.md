# 应用运维监控系统

一个基于Flask的应用运维监控系统，提供应用、服务器、实例的监控和告警功能。

## 功能特性

- 📊 **实时监控**: 监控应用、服务器、实例的运行状态
- 🚨 **智能告警**: 基于规则的告警系统，支持多种告警级别
- 📈 **数据可视化**: 直观的仪表板展示监控数据
- 🔧 **维护管理**: 维护窗口管理，避免误报
- 📱 **响应式设计**: 支持桌面和移动设备访问

## 系统架构

```
应用运维监控系统
├── Web界面 (Flask + HTML/CSS/JS)
├── API接口 (RESTful API)
├── 数据库 (MySQL 8.0)
└── 监控数据收集
```

## 数据库表结构

- `application`: 应用信息
- `server`: 服务器信息
- `instance`: 实例信息
- `monitor_item`: 监控项配置
- `alert_rule`: 告警规则
- `alert_event`: 告警事件
- `metric_data`: 监控数据（分区表）
- `notification`: 通知配置
- `maintenance`: 维护窗口

## 快速开始

### 1. 启动MySQL数据库

```bash
# 进入项目目录
cd /opt/work/ai_training/monitor

# 启动MySQL容器
docker-compose -f docs/db/share_docker_compose.yml up -d
```

### 2. 初始化数据库

```bash
# 连接到MySQL并执行初始化脚本
docker exec -i mysql_persistent mysql -uroot -p123456 < docs/db/init.sql
```

### 3. 安装Python依赖

```bash
# 安装依赖包
pip install -r requirements.txt
```

### 4. 初始化测试数据

```bash
# 运行数据初始化脚本
python init_data.py
```

### 5. 启动应用

```bash
# 启动Flask应用
python app.py
```

### 6. 访问系统

打开浏览器访问: http://localhost:8081

## API接口

### 仪表板数据
- `GET /api/dashboard` - 获取仪表板统计数据

### 应用管理
- `GET /api/applications` - 获取应用列表

### 服务器管理
- `GET /api/servers` - 获取服务器列表

### 告警管理
- `GET /api/alerts` - 获取告警列表

### 监控数据
- `GET /api/metrics/<instance_id>` - 获取实例监控数据

## 配置说明

### 数据库配置

在 `app.py` 中修改数据库连接配置:

```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 3308,
    'user': 'root',
    'password': '123456',
    'database': 'app_monitor_db',
    'charset': 'utf8mb4'
}
```

### Docker配置

MySQL容器配置在 `docs/db/share_docker_compose.yml` 中:

- 端口映射: 3308:3306
- 数据持久化: ./data:/var/lib/mysql
- 时区: Asia/Shanghai

## 监控指标

系统支持以下监控指标:

- **CPU使用率** (CPU_USAGE): 百分比
- **内存使用率** (MEMORY_USAGE): 百分比
- **磁盘使用率** (DISK_USAGE): 百分比
- **请求数量** (REQUEST_COUNT): 请求/分钟
- **响应时间** (RESPONSE_TIME): 毫秒

## 告警级别

- **信息** (1): 一般信息提示
- **警告** (2): 需要关注的问题
- **严重** (3): 影响业务的问题
- **致命** (4): 严重影响业务的问题

## 开发说明

### 项目结构

```
monitor/
├── app.py                 # 主应用程序
├── init_data.py          # 数据初始化脚本
├── requirements.txt      # Python依赖
├── README.md            # 项目说明
├── templates/           # HTML模板
│   └── index.html      # 主页面
└── docs/               # 文档
    └── db/            # 数据库相关
        ├── init.sql   # 数据库初始化脚本
        └── share_docker_compose.yml  # Docker配置
```

### 扩展功能

1. **添加新的监控指标**: 在 `monitor_item` 表中添加新的指标类型
2. **自定义告警规则**: 在 `alert_rule` 表中配置告警条件
3. **通知集成**: 在 `notification` 表中配置邮件、短信、微信等通知方式
4. **数据收集**: 可以集成Prometheus、Grafana等监控工具

## 注意事项

1. 生产环境请修改默认密码
2. 建议配置数据库备份策略
3. 监控数据表使用了分区，注意分区维护
4. 大量数据时建议优化查询性能

## 许可证

MIT License