# Agent Patterns Lab (Python, uv, offline-first)

用 **纯 Python**（允许第三方库，但不依赖 LangChain/LangGraph）从 0 到 1 复现常见 **Agent Design Patterns** 的参考实现仓库。  
默认所有 `examples/`、`tests/` 都用 **MockLLM**，离线可跑；真实模型（OpenAI/Anthropic）做成可选适配器（extras）。

## 文档入口

- `AGENT_DESIGN_PATTERNS_REPORT.md`：模式全景大纲 + Mermaid 流程图（概念/解决的问题）
- `ITERATION_PLAN.md`：整体迭代计划（每轮输入/输出/验收）

## 快速开始（uv）

```bash
# If you have normal network access:
uv sync
uv run python -m unittest discover -s tests
uv run python examples/00_single_shot.py
```

## 真实模型（可选 extras：OpenAI / Anthropic SDK）

本仓库的核心 `runtime/`、`patterns/`、`tests/` 默认 **不依赖任何第三方 SDK**（离线可跑）。  
当你想接入真实 LLM 时，再通过 `uv` 的 `--extra` 安装对应 SDK，并使用适配器：

```bash
uv sync --extra openai
# or
uv sync --extra anthropic
```

运行示例（需要环境变量）：

```bash
export OPENAI_API_KEY="..."
UV_CACHE_DIR=.uv_cache PYTHONPATH=src uv run --no-sync --extra openai python examples/70_openai_sdk_optional.py

export ANTHROPIC_API_KEY="..."
UV_CACHE_DIR=.uv_cache PYTHONPATH=src uv run --no-sync --extra anthropic python examples/71_anthropic_sdk_optional.py
```

## 在受限/离线环境运行（例如无法访问 PyPI）

本仓库默认无第三方依赖；但 `uv sync` 可能会尝试构建并安装本项目，从而需要下载构建依赖（如 `setuptools`）。在无网络环境可以这样跑：

```bash
UV_CACHE_DIR=.uv_cache uv sync --no-install-project

# Run tests / examples without installing the package
UV_CACHE_DIR=.uv_cache PYTHONPATH=src uv run --no-sync python -m unittest discover -s tests
UV_CACHE_DIR=.uv_cache PYTHONPATH=src uv run --no-sync python examples/00_single_shot.py
```

> 真实模型（OpenAI/Anthropic）适配器会在后续迭代加入（见 `ITERATION_PLAN.md`），并保持“薄封装”，不影响离线示例与测试。

## Eval Harness（离线回归报告）

运行全套离线评测任务（覆盖 workflow / agent loop / RAG / planning / multi-agent / governance 等类别）：

```bash
UV_CACHE_DIR=.uv_cache PYTHONPATH=src uv run --no-sync python -m agent_patterns_lab.runtime.evals --mode offline
```

产物：
- `.evals/`：Markdown 报告 + JSON 结果（可作为 baseline 做回归对比）
- `.traces/evals/`：每个 task 的 trace（JSONL）

## 文档写作质量（review → revise → polish + rubric）

当你要批量润色 `docs/` 页面（并对每一页按 rubric 打分）时，可以用内置的 editorial pipeline：

```bash
# Offline：只做启发式打分/建议（不改文件）
UV_CACHE_DIR=.uv_cache PYTHONPATH=src uv run --no-sync python -m agent_patterns_lab.runtime.editorial \
  --mode offline --input docs --out-dir .editorial

# Live（OpenAI）：需要 OPENAI_API_KEY，且安装 extra
uv sync --extra openai
export OPENAI_API_KEY="..."
UV_CACHE_DIR=.uv_cache PYTHONPATH=src uv run --no-sync --extra openai python -m agent_patterns_lab.runtime.editorial \
  --mode openai --input docs --out-dir .editorial

# Live（Anthropic）：需要 ANTHROPIC_API_KEY，且安装 extra
uv sync --extra anthropic
export ANTHROPIC_API_KEY="..."
UV_CACHE_DIR=.uv_cache PYTHONPATH=src uv run --no-sync --extra anthropic python -m agent_patterns_lab.runtime.editorial \
  --mode anthropic --input docs --out-dir .editorial
```

输出：
- `.editorial/reports/`：每个页面的 review/revise/polish 分数与建议（JSON）
- `.editorial/REPORT.md`：聚合报表（均分 + 最低分页面）
- `.editorial/out/`：live 模式下的“重写副本”（未 `--apply` 时）

如需直接覆盖源文件（谨慎使用；通常用于 live 模式）：

```bash
UV_CACHE_DIR=.uv_cache PYTHONPATH=src uv run --no-sync python -m agent_patterns_lab.runtime.editorial \
  --mode offline --input docs --out-dir .editorial --apply
```

## 文档站点（MkDocs + 双语）

本仓库提供了一个 **MkDocs + Material** 的文档站点配置（`mkdocs.yml`），并通过 `mkdocs-static-i18n` 生成 **中英双语** 文档。

> 注意：`mkdocs.yml` 默认指向 `lifeodyssey/agent-patterns-lab`。
> 如果你 fork 了仓库，可以在构建前用环境变量覆盖 `repo_url/repo_name/edit_uri`。
> 这依赖 MkDocs 的 `!ENV` 配置语法。

```bash
uv sync --extra docs

# Preview
UV_CACHE_DIR=.uv_cache uv run --no-sync --extra docs mkdocs serve

# Build static site
UV_CACHE_DIR=.uv_cache uv run --no-sync --extra docs mkdocs build
```

覆盖仓库链接（可选）：

```bash
export REPO_URL="https://github.com/<you>/<repo>"
export REPO_NAME="<you>/<repo>"
export EDIT_URI="edit/main/docs/"
UV_CACHE_DIR=.uv_cache uv run --no-sync --extra docs mkdocs build --clean
```

## 部署到 Cloudflare Pages（使用本地 Cloudflare CLI / wrangler）

先构建静态站点（输出到 `site/`）：

```bash
UV_CACHE_DIR=.uv_cache uv run --no-sync --extra docs mkdocs build --clean
```

首次部署：创建 Pages 项目（只需一次）：

```bash
npx -y wrangler pages project create <project-name> --production-branch main
```

部署构建产物：

```bash
npx -y wrangler pages deploy site --project-name <project-name> --branch main
```

如果遇到 `wrangler` 报错 `fetch failed` / `API timed out`，且日志提示检测到 proxy 环境变量，可以先临时关闭代理环境变量再试：

```bash
unset all_proxy http_proxy https_proxy ALL_PROXY HTTP_PROXY HTTPS_PROXY
npx -y wrangler pages deploy site --project-name <project-name> --branch main
```

默认语言为英文（根路径），中文在 `/zh/`：
- `https://<project-name>.pages.dev/`
- `https://<project-name>.pages.dev/zh/`
