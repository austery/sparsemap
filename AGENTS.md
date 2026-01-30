# AGENTS.md - SparseMap V1 Foundation Plan

## 问题与目标
基于提供的 Spec，将 SparseMap 从零搭建为“Foundation”级别的可演进项目：保留轻量前端，后端采用 FastAPI + SQLModel + Alembic，严格数据契约，并实现 ETL + LLM 校验补全（方案 B）。

## 参考项目现状（linklog）
- 单体 FastAPI + 静态前端（Cytoscape）
- LLM 调用与 JSON 修复逻辑
- URL 抓取 + HTML 清洗
- 无数据库与迁移体系

## 方案假设与确认
- LLM 策略：方案 B（基于文章内容 + 追加 suggested_best_practice 节点）
- V1 含数据库与迁移（Postgres + SQLModel + Alembic）
- 前端保持轻量 HTML/Cytoscape
- 失败重试：LLM schema 校验失败重试 2 次
- 代码结构：src/sparsemap 包布局

## 工作计划
- [ ] 1. 初始化工程与依赖
  - 使用 uv init sparsemap --app（或等效结构）
  - 配置 pyproject.toml（FastAPI, SQLModel, Alembic, httpx, bs4, openai, ruff 等）
  - 创建 src/sparsemap 包结构与基础模块

- [ ] 2. 定义领域模型与数据契约
  - Pydantic/SQLModel：Node, Edge, Graph, AnalysisResult
  - Enum：NodeType(main/dependency/suggested_best_practice), Priority(critical/optional)
  - JSONB 存储与读写校验

- [ ] 3. 基础架构与配置
  - core/config.py（环境变量/配置）
  - core/logging.py（结构化日志最小实现）
  - infra/db.py（SQLModel Session + 引擎）
  - migrations 初始化（Alembic）

- [ ] 4. ETL + LLM 服务实现
  - services/extractor.py：抓取、清洗、长度校验
  - services/llm.py：提示词 + schema 校验 + 失败重试 2 次
  - 提示词加入“best practice 缺失补全”规则（type: suggested_best_practice）

- [ ] 5. API 层与路由
  - api/routes/analyze.py：/api/analyze
  - 请求体支持 urls/texts
  - 返回 graph + sources
  - OpenAPI 自动文档

- [ ] 6. 前端最小化接入
  - 复用 linklog 的静态页面结构（Cytoscape）
  - 调整 API 地址与响应结构

- [ ] 7. 基础测试与运行
  - 提供最小测试/检查脚本（可选）
  - 启动指引与 README 更新

## 说明与注意事项
- 目标是“钢铁主线”：功能最小化，架构完整可演进
- 优先复用 linklog 的成熟逻辑，但要迁移到分层架构
- 任何数据写入前必须通过 Pydantic 校验
