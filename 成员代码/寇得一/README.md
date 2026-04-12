# macOS 自动化代理

一个受控的 macOS 自动化代理，核心约束：所有真实操作必须经过 Approval Gate 确认，执行器每次只执行一个动作。

## 架构

- **Orchestrator**: 任务编排和状态机，确保单步执行
- **Approval Gate**: 硬闸门，所有操作必须确认
- **LLM Client**: OpenAI API 封装，生成结构化动作
- **Executor**: 工具执行层，支持文件、浏览器、微信、备忘录等
- **Audit Log**: 完整的审计日志和证据收集

## 安装

```bash
pip install -r requirements.txt
playwright install chromium
```

## 配置

1. 复制 `config/config.yaml.example` 到 `config/config.yaml`
2. 填入 OpenAI API 密钥
3. 根据需要调整 `config/policy.yaml` 的风险策略

## 运行

```bash
python -m app.main
```

## 使用

通过菜单栏图标访问：
- **新任务**: 输入自然语言任务
- **查看日志**: 打开审计日志目录
- **配置**: 打开配置目录
- **退出**: 退出应用

## 安全特性

- 所有操作必须经过用户确认
- 风险分级：low/medium/high
- 完整审计日志和证据收集
- 路径白名单和输入校验
