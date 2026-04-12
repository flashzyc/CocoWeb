<div align="center">

# CocoWeb Open Source Community

**A course-driven, community-built open-source repository for web security, AI practice, and software engineering projects.**  
**一个面向 Web 安全、AI 实践与软件工程协作的课程型开源社区仓库。**

[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E.svg)](./LICENSE)
[![Community](https://img.shields.io/badge/Type-Open%20Source%20Community-0EA5E9.svg)](#)
[![Security Lab](https://img.shields.io/badge/Core-CocoWeb%20Security%20Lab-F97316.svg)](./漏洞靶场)
[![Languages](https://img.shields.io/badge/Stack-PHP%20%7C%20Python%20%7C%20Java-8B5CF6.svg)](./PROJECTS.md)
[![Contributing](https://img.shields.io/badge/Contributing-Welcome-EAB308.svg)](./CONTRIBUTING.md)

[中文](#中文) | [English](#english) | [Projects](./PROJECTS.md) | [Contributing](./CONTRIBUTING.md) | [License](./LICENSE)

</div>

---

## 中文

### 目录

- [项目简介](#项目简介)
- [核心亮点](#核心亮点)
- [仓库结构](#仓库结构)
- [精选项目](#精选项目)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [截图占位](#截图占位)
- [开源社区协作](#开源社区协作)
- [贡献方式](#贡献方式)
- [安全声明](#安全声明)

### 项目简介

**CocoWeb Open Source Community** 是一个综合型开源仓库，围绕 **CocoWeb 本地 Web 安全靶场** 展开，并收录社区成员在 **AI、自动化代理、深度学习、代码分析、后端工程** 等方向的项目实践。

这个仓库不是单一产品仓库，而是一个 **主项目 + 成员项目 + 课程成果 + 社区协作** 的混合型空间。它既适合作为课程项目展示页，也适合作为长期维护的开源社区入口。

你可以把它理解为：

- 一个可用于安全学习的本地实验场
- 一个成员项目作品集仓库
- 一个多技术栈的工程实践样本集合
- 一个持续演进的开源社区门面

### 核心亮点

- 以 `漏洞靶场/` 为主线，具备明确的 Web 安全教学价值
- 汇集多个成员项目，覆盖安全、AI、后端、深度学习等方向
- 同时包含 PHP、Python、Java 等多种常见技术栈
- 适合课程答辩、社群展示、开源协作、项目归档与技术交流
- 既有完整度较高的项目，也有实验型、练习型、研究型内容

### 仓库结构

```text
cocoweb/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── PROJECTS.md
├── 漏洞靶场/
│   ├── index.php
│   ├── setup.php
│   ├── security.php
│   ├── xss_reflected.php
│   ├── xss_stored.php
│   ├── sqli.php
│   ├── ssrf.php
│   ├── csrf.php
│   ├── seed.sql
│   └── includes/
└── 成员代码/
    ├── 楚柏纶_Transformer/
    ├── 郎竟茗_CNN_ImageClassification/
    ├── 张亦潮_HarmonyShoppingMall/
    ├── 寇得一_AIUsage/
    └── 苏禹宽_GithubProjectAnalyzer/
```

### 精选项目

#### 1. CocoWeb 漏洞靶场

路径：[`漏洞靶场/`](./漏洞靶场)

这是仓库当前最完整、最适合作为主页主推的项目。它是一个基于 **PHP + MySQL** 的本地 Web 安全实验环境，覆盖：

- Reflected XSS
- Stored XSS
- SQL Injection
- SSRF
- CSRF

并支持 **Low / Medium / High** 三档安全级别，适合用来讲解从“漏洞形成”到“防护改进”的完整过程。

更多说明见 [`漏洞靶场/README.md`](./漏洞靶场/README.md)。

#### 2. GitHub Project Analyzer

路径：[`成员代码/苏禹宽_GithubProjectAnalyzer/`](./成员代码/苏禹宽_GithubProjectAnalyzer)

一个多智能体 GitHub 仓库分析系统，支持：

- GitHub 仓库信息抓取
- 上下文画像与代码级洞察
- 按不同分析方向生成报告
- Web UI 与 CLI 双模式
- Markdown / HTML / DOCX 多格式输出

这是仓库中工程化程度较高的成员项目之一。

#### 3. AIUsage

路径：[`成员代码/寇得一_AIUsage/`](./成员代码/寇得一_AIUsage)

一个强调 **Approval Gate、审计日志、单步执行** 的 macOS 自动化代理项目，适合展示“受控代理系统”的工程设计思路。

#### 4. Harmony Shopping Mall

路径：[`成员代码/张亦潮_HarmonyShoppingMall/`](./成员代码/张亦潮_HarmonyShoppingMall)

一个 Java 后端项目，包含 controller、service、repository、entity、dto 等典型分层结构，适合作为课程型后端工程示例。

#### 5. Transformer / CNN 学习项目

路径：

- [`成员代码/楚柏纶_Transformer/`](./成员代码/楚柏纶_Transformer)
- [`成员代码/郎竟茗_CNN_ImageClassification/`](./成员代码/郎竟茗_CNN_ImageClassification)

这两个项目更偏向深度学习课程实践与原理理解，分别覆盖：

- 简化版 Transformer / Causal LM 结构实现
- CNN 图像分类、训练可视化、Grad-CAM 与混淆矩阵

更多项目概览见 [`PROJECTS.md`](./PROJECTS.md)。

### 技术栈

- PHP
- MySQL / MariaDB
- Python
- Flask
- TensorFlow
- NumPy
- Java
- Spring Boot
- HTML / CSS / JavaScript

### 快速开始

#### 方式一：体验主项目 CocoWeb

1. 克隆仓库

```bash
git clone <your-repo-url>
cd cocoweb
```

2. 进入 [`漏洞靶场/`](./漏洞靶场) 并阅读其说明文档

3. 根据 [`漏洞靶场/README.md`](./漏洞靶场/README.md) 配置数据库

4. 打开 `setup.php` 初始化数据库并开始实验

#### 方式二：浏览成员项目

进入 [`成员代码/`](./成员代码) 后，可以根据各子项目 README 分别运行和学习。

推荐浏览顺序：

1. `漏洞靶场`
2. `苏禹宽_GithubProjectAnalyzer`
3. `寇得一_AIUsage`
4. `张亦潮_HarmonyShoppingMall`
5. `楚柏纶_Transformer`
6. `郎竟茗_CNN_ImageClassification`

### 截图占位

后续可以在仓库中新增 `docs/images/` 目录，并将以下图片接入 README：

| 位置 | 建议图片 |
| --- | --- |
| Hero 展示图 | CocoWeb 首页或靶场总览截图 |
| 漏洞靶场 | 安全级别切换界面、实验页面截图 |
| GitHub Project Analyzer | Web UI 首页、报告预览页 |
| AIUsage | 菜单栏界面、执行流程示意图 |
| Harmony Shopping Mall | 接口结构图或后端模块图 |

推荐占位方式：

```md
![CocoWeb Home](./docs/images/cocoweb-home.png)
![Security Lab](./docs/images/security-lab.png)
![GitHub Project Analyzer UI](./docs/images/github-project-analyzer-ui.png)
```

### 开源社区协作

这是一个 **主项目 + 成员项目** 的开源社区仓库，因此不同项目可能在成熟度、代码风格、依赖管理和文档完整度上存在差异。

这并不是缺点，而是这个仓库的真实价值所在：它完整保留了社区成员的实践轨迹、工程能力和探索过程。

如果你希望把它建设成一个更强的 GitHub 门面，建议继续补充：

- 统一的项目模板
- 每个成员项目的运行说明
- 更多截图、架构图和示意图
- Issue 模板、PR 模板、代码规范文档
- 根目录级别的发布说明和更新日志

### 贡献方式

欢迎以以下方式参与共建：

- 提交新的成员项目
- 改进 README、PROJECTS 和导航结构
- 修复问题并提交 Pull Request
- 补充测试、部署文档和截图
- 为已有项目补充 License、依赖说明与示例数据

建议先阅读 [`CONTRIBUTING.md`](./CONTRIBUTING.md)。

### 安全声明

本仓库中的漏洞靶场内容仅用于 **授权学习、教学演示与本地实验**。

- 请勿部署到公网环境
- 请勿将脆弱代码直接用于生产环境
- 请勿将相关技术用于任何未授权攻击行为

使用本仓库即表示你理解并接受相应责任。

---

## English

### Table of Contents

- [Overview](#overview)
- [Highlights](#highlights)
- [Repository Structure](#repository-structure)
- [Featured Projects](#featured-projects)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Screenshot Placeholders](#screenshot-placeholders)
- [Community Collaboration](#community-collaboration)
- [Contributing](#contributing)
- [Security Notice](#security-notice)

### Overview

**CocoWeb Open Source Community** is a multi-project repository built around **CocoWeb**, a local web security playground, and extended with community member projects in **AI, automation, deep learning, code analysis, and backend engineering**.

This is not a single-product repository. It is a **core project + member projects + course outcomes + open-source collaboration** space. It works well both as a class showcase and as a long-term community repository.

You can think of it as:

- A local lab for web security learning
- A portfolio repository for community member projects
- A cross-stack engineering practice collection
- A growing open-source community front page

### Highlights

- A clear and educational security lab as the repository core
- Multiple member-contributed projects across different domains
- A cross-stack collection including PHP, Python, and Java
- Suitable for demos, class presentations, technical sharing, and open collaboration
- Includes both polished subprojects and exploratory learning projects

### Repository Structure

```text
cocoweb/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── PROJECTS.md
├── 漏洞靶场/                     # Security playground
└── 成员代码/                     # Community member projects
```

### Featured Projects

#### 1. CocoWeb Security Playground

Path: [`漏洞靶场/`](./漏洞靶场)

This is the most complete and presentation-ready project in the repository. It is a **PHP + MySQL** local web security lab covering:

- Reflected XSS
- Stored XSS
- SQL Injection
- SSRF
- CSRF

It supports **Low / Medium / High** security levels, making it ideal for demonstrating the full path from vulnerable implementation to safer patterns.

See [`漏洞靶场/README.md`](./漏洞靶场/README.md) for details.

#### 2. GitHub Project Analyzer

Path: [`成员代码/苏禹宽_GithubProjectAnalyzer/`](./成员代码/苏禹宽_GithubProjectAnalyzer)

A multi-agent GitHub repository analysis system with:

- repository crawling
- context profiling and code insight
- report generation for different analysis tracks
- web UI and CLI modes
- Markdown / HTML / DOCX output

This is one of the most engineering-complete member projects in the repository.

#### 3. AIUsage

Path: [`成员代码/寇得一_AIUsage/`](./成员代码/寇得一_AIUsage)

A controlled macOS automation agent focused on **approval gates, audit logs, and step-based execution**.

#### 4. Harmony Shopping Mall

Path: [`成员代码/张亦潮_HarmonyShoppingMall/`](./成员代码/张亦潮_HarmonyShoppingMall)

A Java backend project with a layered controller/service/repository/entity/dto architecture.

#### 5. Transformer and CNN Learning Projects

Paths:

- [`成员代码/楚柏纶_Transformer/`](./成员代码/楚柏纶_Transformer)
- [`成员代码/郎竟茗_CNN_ImageClassification/`](./成员代码/郎竟茗_CNN_ImageClassification)

These projects are more learning-oriented and focus on:

- simplified Transformer / causal language model implementation
- CNN image classification, visualization, Grad-CAM, and confusion matrix workflows

See [`PROJECTS.md`](./PROJECTS.md) for a broader repository map.

### Tech Stack

- PHP
- MySQL / MariaDB
- Python
- Flask
- TensorFlow
- NumPy
- Java
- Spring Boot
- HTML / CSS / JavaScript

### Quick Start

#### Option 1: Explore the main CocoWeb lab

1. Clone the repository

```bash
git clone <your-repo-url>
cd cocoweb
```

2. Open [`漏洞靶场/`](./漏洞靶场) and read its documentation

3. Follow [`漏洞靶场/README.md`](./漏洞靶场/README.md) to configure the database

4. Open `setup.php` to initialize the database and start the lab

#### Option 2: Browse member projects

Open [`成员代码/`](./成员代码) and explore each subproject independently.

Suggested order:

1. `漏洞靶场`
2. `苏禹宽_GithubProjectAnalyzer`
3. `寇得一_AIUsage`
4. `张亦潮_HarmonyShoppingMall`
5. `楚柏纶_Transformer`
6. `郎竟茗_CNN_ImageClassification`

### Screenshot Placeholders

You can later add a `docs/images/` directory and connect the following assets to this README:

| Slot | Suggested asset |
| --- | --- |
| Hero image | CocoWeb homepage or dashboard screenshot |
| Security lab | security level selector and lab pages |
| GitHub Project Analyzer | web UI and report preview |
| AIUsage | menu bar app UI or workflow diagram |
| Harmony Shopping Mall | API structure or architecture diagram |

Suggested placeholder syntax:

```md
![CocoWeb Home](./docs/images/cocoweb-home.png)
![Security Lab](./docs/images/security-lab.png)
![GitHub Project Analyzer UI](./docs/images/github-project-analyzer-ui.png)
```

### Community Collaboration

This is a **core project + member project** repository, so different subprojects may vary in maturity, coding style, dependency management, and documentation quality.

That is part of the repository's real value: it preserves the actual engineering path, learning process, and community contributions of its members.

To make it even stronger on GitHub, future improvements could include:

- a standard template for member projects
- clearer run instructions for each subproject
- more screenshots, diagrams, and architecture notes
- issue templates, PR templates, and coding standards
- root-level release notes and changelog practices

### Contributing

Contributions are welcome in many forms:

- add new member projects
- improve README, PROJECTS, and navigation
- fix issues and submit pull requests
- add tests, deployment notes, and screenshots
- improve licensing, dependency setup, and sample data

Please read [`CONTRIBUTING.md`](./CONTRIBUTING.md) first.

### Security Notice

The vulnerability lab content in this repository is intended only for **authorized learning, local testing, and educational demonstration**.

- Do not deploy it to the public Internet
- Do not reuse intentionally vulnerable code in production
- Do not use related techniques against systems without authorization

By using this repository, you agree to act responsibly and lawfully.
