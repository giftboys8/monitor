#!/bin/bash

# 应用运维监控系统启动脚本
# 使用方法: ./start.sh [选项]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${2}${1}${NC}"
}

# 检查Docker和Docker Compose是否安装
check_dependencies() {
    print_message "检查依赖..." "$BLUE"
    
    if ! command -v docker &> /dev/null; then
        print_message "错误: Docker 未安装" "$RED"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_message "错误: Docker Compose 未安装" "$RED"
        exit 1
    fi
    
    print_message "依赖检查通过" "$GREEN"
}

# 创建必要的目录
create_directories() {
    print_message "创建必要的目录..." "$BLUE"
    
    mkdir -p logs
    
    print_message "目录创建完成" "$GREEN"
}

# 复制环境变量文件
setup_env() {
    if [ ! -f .env ]; then
        print_message "复制环境变量配置文件..." "$BLUE"
        cp .env.example .env
        print_message "请编辑 .env 文件以配置您的环境变量" "$YELLOW"
    fi
}

# 构建镜像
build_images() {
    print_message "构建Docker镜像..." "$BLUE"
    docker-compose build --no-cache
    print_message "镜像构建完成" "$GREEN"
}

# 启动服务
start_services() {
    print_message "启动服务..." "$BLUE"
    
    docker-compose up -d monitor_app
    
    print_message "服务启动完成" "$GREEN"
}

# 等待服务就绪
wait_for_services() {
    print_message "等待服务就绪..." "$BLUE"
    
    # 等待应用就绪
    echo "等待应用启动..."
    until curl -f http://localhost:8081/api/dashboard &> /dev/null; do
        echo -n "."
        sleep 2
    done
    echo
    
    print_message "应用服务已就绪" "$GREEN"
}

# 显示服务状态
show_status() {
    print_message "服务状态:" "$BLUE"
    docker-compose ps
    
    echo
    print_message "访问地址:" "$BLUE"
    echo "应用地址: http://localhost:8081"
    echo "MySQL地址: localhost:3308 (使用已存在的容器)"
}

# 显示日志
show_logs() {
    if [ -n "$1" ]; then
        docker-compose logs -f "$1"
    else
        docker-compose logs -f
    fi
}

# 停止服务
stop_services() {
    print_message "停止服务..." "$BLUE"
    docker-compose down
    print_message "服务已停止" "$GREEN"
}

# 清理数据
clean_data() {
    print_message "清理应用数据..." "$YELLOW"
    read -p "确定要删除应用日志数据吗? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v
        sudo rm -rf logs/*
        print_message "应用数据清理完成" "$GREEN"
    else
        print_message "取消清理" "$BLUE"
    fi
}

# 显示帮助信息
show_help() {
    echo "应用运维监控系统启动脚本"
    echo
    echo "使用方法: $0 [选项]"
    echo
    echo "选项:"
    echo "  start                 启动应用服务"
    echo "  stop                  停止服务"
    echo "  restart               重启服务"
    echo "  status                显示服务状态"
    echo "  logs [service]        显示日志 (可指定服务名)"
    echo "  build                 构建镜像"
    echo "  clean                 清理应用数据"
    echo "  help                  显示帮助信息"
    echo
    echo "示例:"
    echo "  $0 start              # 启动应用服务"
    echo "  $0 logs monitor_app   # 查看应用日志"
    echo "  $0 clean              # 清理应用日志数据"
    echo
    echo "注意: 使用已存在的MySQL容器，请确保MySQL服务在localhost:3308端口可用"
}

# 主函数
main() {
    case "$1" in
        "start")
            check_dependencies
            create_directories
            setup_env
            start_services "$2"
            wait_for_services
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 2
            start_services "$2"
            wait_for_services
            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "$2"
            ;;
        "build")
            check_dependencies
            build_images
            ;;
        "clean")
            clean_data
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        "")
            print_message "请指定操作，使用 --help 查看帮助" "$YELLOW"
            ;;
        *)
            print_message "未知选项: $1" "$RED"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"