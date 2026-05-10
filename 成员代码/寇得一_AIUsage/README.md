# AIUsage: 受控的 macOS 自动化代理

AIUsage 是一个面向 macOS 场景的自动化代理原型项目，目标不是“让模型直接替用户操作系统”，而是构建一个 **可审计、可中断、可确认** 的受控执行流程。

项目把“先规划、再确认、后执行”作为核心约束，强调以下三点：

- 所有真实操作都必须经过 `Approval Gate`
- 执行器一次只执行一个动作，避免连续失控
- 每一步都留下日志和证据，便于回溯与复盘

这使它更适合作为“安全代理系统设计”的课程实践项目，而不是一个追求全自动化的黑盒助手。

## 项目目标

这个项目主要用来验证以下设计思路：

- 如何让 LLM 只生成结构化动作，而不是直接执行系统操作
- 如何在执行前加入人工确认，降低误操作风险
- 如何基于风险等级对工具进行分层管理
- 如何为代理行为保留审计记录和证据文件

## 核心特性

- `Approval Gate` 硬闸门：所有操作必须确认
- 单步执行：每次只推进一步，降低连续误操作风险
- 风险分级：支持 `low / medium / high` 三档策略
- 审计日志：记录会话、草案、决策、执行结果
- 证据收集：为部分动作保存证据路径，便于复盘
- 多工具执行：支持文件、网页、微信、备忘录等模块
- 配置化策略：可通过 YAML 调整模型参数和风险策略

## 目录结构

```text
寇得一_AIUsage/
├── README.md
├── requirements.txt
├── run_check.py
├── api/
│   ├── openai_client.py
│   ├── auto_loader.py
│   ├── base_client.py
│   └── config_example.yaml
├── app/
│   ├── main.py
│   ├── orchestrator.py
│   ├── approval_gate.py
│   ├── audit_log.py
│   ├── config_manager.py
│   ├── context.py
│   ├── llm_client.py
│   └── schema.py
├── config/
│   ├── config.yaml.example
│   ├── logging.yaml
│   └── policy.yaml
├── examples/
└── tools/
    ├── executor.py
    ├── fs_tools.py
    ├── web_tools.py
    ├── wx_tools.py
    ├── notes_tools.py
    ├── evidence.py
    ├── log_viewer.py
    └── log_analyzer.py
```

## 架构说明

### 1. Orchestrator

`app/orchestrator.py` 负责整个任务状态机：

- 创建会话
- 收集上下文
- 调用 LLM 生成下一步动作
- 将动作交给 Approval Gate 确认
- 调用执行器完成单步操作
- 写入历史、日志和结果

它是整个系统的主控制器，保证代理不会跳过确认环节直接执行。

### 2. Approval Gate

`app/approval_gate.py` 是系统最重要的安全控制点。

它会根据 `config/policy.yaml` 中的风险策略，对动作进行分级：

- `low`：低风险操作，可按策略决定是否会话内自动放行
- `medium`：中风险操作，每次都要求显式确认
- `high`：高风险操作，需要二次确认和确认词

这个设计可以避免高风险工具被模型“一次误判后连续执行”。

### 3. LLM Client

`app/llm_client.py` 与 `api/` 目录负责模型调用与客户端加载。当前默认使用 OpenAI 配置，也预留了兼容其他 API 提供商的扩展入口。

LLM 的职责是生成结构化动作草案，而不是直接接管执行环境。

### 4. Executor

`tools/executor.py` 是统一执行入口，负责把动作路由到具体工具模块：

- `fs.*`：文件系统操作
- `web.*`：网页打开、点击、输入、抓取
- `wx.*`：微信聊天相关操作
- `notes.*`：备忘录搜索和写入

### 5. Audit Log

`app/audit_log.py` 负责记录：

- 会话开始与结束
- LLM 生成的动作草案
- 用户确认、编辑或拒绝的决策
- 实际执行结果
- 证据文件路径

这使项目具备“事后可解释性”和“问题可追踪性”。

## 环境要求

- macOS
- Python 3.8 及以上
- 可用的 OpenAI API Key
- 浏览器自动化依赖（如需使用 `web.*` 工具）

> 说明：项目使用了 `rumps`、`tkinter`、`open` 等 macOS 相关能力，因此不适合直接在 Windows 环境运行。

## 安装步骤

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 安装 Playwright 浏览器驱动

```bash
playwright install chromium
```

3. 初始化配置文件

```bash
cp config/config.yaml.example config/config.yaml
```

4. 在 `config/config.yaml` 中填写你的 OpenAI API Key

5. 如有需要，调整 `config/policy.yaml` 中的风险分级策略

## 配置说明

### `config/config.yaml`

该文件用于管理模型和运行参数，主要包括：

- `api_provider`：当前使用的模型提供商
- `openai.api_key`：API 密钥
- `openai.model`：模型名称
- `openai.temperature`：生成温度
- `openai.max_tokens`：单步输出上限
- `paths.home_directory`：允许操作的主目录
- `session.max_steps`：单次任务最大步数

建议将 `paths.home_directory` 限定在自己的工作目录范围内，避免代理访问过宽的文件区域。

### `config/policy.yaml`

该文件用于定义风险策略，例如：

- 哪些工具属于低风险
- 哪些工具属于高风险
- 高风险操作是否需要确认词
- 是否允许低风险操作在同一会话内自动放行

如果你希望强调“安全优先”，建议保持高风险操作必须二次确认。

## 运行方式

### 方式一：先做环境检查

```bash
python run_check.py
```

该脚本会检查：

- Python 版本
- 依赖是否安装
- 配置文件是否存在
- API Key 是否已填写
- 日志目录是否可创建

### 方式二：启动主程序

```bash
python -m app.main
```

程序启动后会以菜单栏应用的形式运行，提供以下入口：

- `新任务`：输入自然语言任务描述
- `继续执行`：继续当前任务的下一步
- `查看日志`：打开日志目录
- `配置`：打开配置文件
- `退出`：退出应用

## 典型执行流程

一次完整任务通常按下面的顺序进行：

1. 用户输入自然语言任务
2. Orchestrator 创建新会话并收集上下文
3. LLM 生成下一步结构化动作
4. Approval Gate 根据风险等级弹窗确认
5. Executor 执行该单步动作
6. Audit Log 记录草案、决策、结果和证据
7. 用户决定是否继续下一步

这个流程刻意牺牲了一部分“全自动效率”，换取更强的可控性和安全性。

## 安全设计说明

这个项目的重点不在于“功能越多越好”，而在于“默认谨慎”：

- 不允许模型绕过确认机制直接落地操作
- 不默认连续自动执行多步动作
- 对高风险操作启用更严格的确认策略
- 把日志与证据作为默认产物，而不是事后补充

如果把它用于课程展示，可以重点强调：这是一个 **受控代理系统**，不是一个 **无限权限代理**。

## 日志与运行产物

运行过程中通常会生成以下本地内容：

- `logs/runtime/`
- `logs/sessions/`
- 可能的证据文件或调试输出

这些内容通常是本地运行产物，不建议提交到仓库。

## 当前局限

目前项目仍然是课程原型，存在一些明确边界：

- 工具覆盖面有限
- 依赖 macOS 图形环境
- 微信、浏览器等能力对本地环境依赖较强
- 缺少更系统的自动化测试
- 对异常恢复和长任务管理还可以继续增强

## 后续可扩展方向

- 增加更多工具适配器
- 为动作增加更细粒度的权限策略
- 引入任务回滚或补救提示
- 增加结构化测试用例与模拟执行模式
- 为日志提供可视化分析页面

## 快速验证建议

如果用于课程答辩或 PR 说明，可以按以下方式验证项目：

1. 运行 `python run_check.py`
2. 确认配置文件与依赖检查通过
3. 启动 `python -m app.main`
4. 创建一个低风险任务，观察是否经过确认再执行
5. 检查 `logs/` 目录下是否生成会话日志

## 相关文件

- [主入口](./app/main.py)
- [任务编排器](./app/orchestrator.py)
- [确认闸门](./app/approval_gate.py)
- [策略配置](./config/policy.yaml)
- [示例配置](./config/config.yaml.example)
