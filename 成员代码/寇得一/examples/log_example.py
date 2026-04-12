"""日志系统使用示例"""

from app.logger import init_logger, get_logger
from tools.log_viewer import LogViewer
from tools.log_analyzer import LogAnalyzer


def example_basic_logging():
    """基本日志使用示例"""
    print("=== 基本日志使用 ===")
    
    # 初始化日志系统
    logger = init_logger()
    
    # 获取不同模块的 logger
    app_logger = get_logger("app")
    tools_logger = get_logger("tools")
    api_logger = get_logger("api")
    
    # 记录不同级别的日志
    app_logger.debug("这是 DEBUG 级别的日志")
    app_logger.info("这是 INFO 级别的日志")
    app_logger.warning("这是 WARNING 级别的日志")
    app_logger.error("这是 ERROR 级别的日志")
    
    # 记录异常
    try:
        raise ValueError("示例错误")
    except Exception as e:
        app_logger.error("捕获到异常", exc_info=True)
    
    # 记录 API 调用
    logger.log_api_call(
        provider="openai",
        endpoint="/v1/chat/completions",
        method="POST",
        status_code=200,
        duration=1.23
    )
    
    # 记录结构化动作
    from app.logger import LogLevel
    logger.log_action(
        action_type="file_move",
        action_data={"src": "/path/src", "dst": "/path/dst"},
        module="tools",
        level=LogLevel.INFO
    )


def example_log_viewer():
    """日志查看器使用示例"""
    print("\n=== 日志查看器使用 ===")
    
    viewer = LogViewer()
    
    # 读取最近 50 行日志
    logs = viewer.read_runtime_log("app.log", lines=50)
    print(f"最近 50 行日志: {len(logs)} 条")
    
    # 只读取 ERROR 级别
    errors = viewer.read_runtime_log("app.log", level="ERROR", lines=20)
    print(f"最近错误: {len(errors)} 条")
    
    # 搜索日志
    results = viewer.search_logs("error", log_file="app.log")
    print(f"搜索 'error': {len(results)} 条结果")
    
    # 获取错误摘要
    summary = viewer.get_error_summary(days=7)
    print(f"7 天内错误总数: {summary['total']}")
    print(f"按级别统计: {summary['by_level']}")
    
    # 列出所有会话
    sessions = viewer.list_sessions(limit=10)
    print(f"最近会话: {len(sessions)} 个")
    for session in sessions[:3]:
        print(f"  - {session['session_id']}: {session['start_time']}")


def example_log_analyzer():
    """日志分析器使用示例"""
    print("\n=== 日志分析器使用 ===")
    
    analyzer = LogAnalyzer()
    
    # 分析性能
    performance = analyzer.analyze_performance()
    print(f"总动作数: {performance['total_actions']}")
    print(f"平均执行时间: {performance['avg_execution_time']:.2f}s")
    print(f"慢操作数: {len(performance['slow_actions'])}")
    
    # 分析使用模式
    patterns = analyzer.analyze_usage_patterns(days=30)
    print(f"\n工具使用统计:")
    for tool, count in list(patterns['tool_usage'].items())[:5]:
        print(f"  {tool}: {count} 次")
    
    # 查找问题
    issues = analyzer.find_issues()
    print(f"\n发现问题: {len(issues)} 个")
    for issue in issues:
        print(f"  [{issue['severity']}] {issue['message']}")
    
    # 生成报告
    report_path = analyzer.generate_report("logs/analysis_report.json")
    print(f"\n报告已生成: {report_path}")


if __name__ == "__main__":
    # 运行示例
    example_basic_logging()
    example_log_viewer()
    example_log_analyzer()
    
    print("\n✅ 所有示例运行完成！")
