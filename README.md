# Multi-Agent Demo

多智能体编排演示项目 — 一个由 4 个 AI Agent 协作生成研究报告的流水线系统。

用户输入一个问题 → **Planner** 拆解为子任务 → **Researcher** 逐一研究 → **Writer** 整合报告 → **Reviewer** 评分建议。

配套 3 个 Claude Code Skill（`/review-orchestration`、`/optimize-agent`、`/add-agent`），支持通过日志驱动、迭代优化的方式持续改进 Agent 表现。

---

## 快速开始

### 前置条件

- Python 3.10+
- DeepSeek API Key（或其他兼容 OpenAI 接口的 LLM）

### 安装

```bash
# 克隆项目
git clone <your-repo-url> && cd multi-agent-demo

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install openai pyyaml python-dotenv

# 配置 API Key
echo "DEEPSEEK_API_KEY=sk-your-key-here" > .env
```

### 运行

```bash
python run.py
```

输入研究问题后，系统依次执行 4 个 Agent，输出最终报告、评分，并自动保存日志到 `logs/` 目录。

查看多轮统计数据：

```bash
python stats.py
```

---

## 系统架构

```
用户输入问题
     ▼
┌──────────┐    JSON 子任务列表
│ Planner  │ ──────────────────► ┌──────────────┐
│ (拆解)   │                     │  Researcher  │ ◄── 子任务 1
└──────────┘                     │  (研究)      │ ◄── 子任务 2
                                 │              │ ◄── 子任务 3
                                 └──────┬───────┘ ◄── 子任务 4
                                        ▼
                                 研究成果汇总
                                        │
                                        ▼
                               ┌──────────────┐
                               │    Writer    │
                               │   (整合报告) │
                               └──────┬───────┘
                                        ▼
                                    完整报告
                                        │
                                        ▼
                               ┌──────────────┐
                               │   Reviewer   │
                               │   (评分建议) │
                               └──────┬───────┘
                                        ▼
                              最终报告 + 评分
                              日志保存到 logs/
```

---

## Agent 说明

| Agent | 角色 | 输入 | 输出 | Temperature |
|-------|------|------|------|:-----------:|
| **Planner** | 任务规划者 | 用户原始问题 | JSON 子任务数组 | 0.3 |
| **Researcher** | 研究者 | 单个子任务 | 结构化研究结果 | 0.3 |
| **Writer** | 报告撰写者 | 所有研究成果 + 原始问题 | 完整报告 | 0.7 |
| **Reviewer** | 质量评审者 | 生成的报告 | JSON 评分 + 改进建议 | 0.2 |

所有 Agent 配置定义在 `agents.yaml`，可通过 Skill 自动优化。

---

## 优化工作流

本项目的核心能力在于**持续迭代优化**。标准流程如下：

```
1. python run.py              # 运行流水线，生成日志
2. /review-orchestration       # 分析日志，定位瓶颈
3. /optimize-agent researcher  # 根据分析结果优化 Agent prompt
4. python run.py               # 验证优化效果
5. python stats.py             # 对比多轮统计评分
6. 重复步骤 1-5
```

### 配套 Skill

| Skill | 用途 | 示例 |
|-------|------|------|
| `/review-orchestration` | 分析日志，找出性能瓶颈和质量问题 | 在项目目录直接运行 |
| `/optimize-agent <名称>` | 重写指定 Agent 的 system_prompt | `/optimize-agent planner` |
| `/add-agent <描述>` | 添加新的 Agent 到流水线 | `/add-agent 事实核查员` |

---

## 项目结构

```
multi-agent-demo/
├── agents.yaml           # Agent 配置（角色、prompt、temperature）
├── orchestrator.py       # 编排器：加载配置、调用 LLM、调度流水线
├── run.py                # 入口脚本：接收输入、执行、保存日志
├── stats.py              # 日志统计分析脚本
├── .env                  # API Key（不提交 git）
├── .gitignore
├── README.md
└── logs/                 # 运行日志（JSON 格式，每次运行一个文件）
    ├── run_20260523_151708.json
    ├── run_20260523_175004.json
    └── run_20260523_180247.json
```

---

## 配置参考

### agents.yaml

```yaml
model: deepseek-v4-flash     # LLM 模型名称

agents:
  planner:
    description: "任务规划者"
    system_prompt: "..."
    temperature: 0.3

  researcher:
    description: "研究者"
    system_prompt: "..."
    temperature: 0.3

  writer:
    description: "撰写者"
    system_prompt: "..."
    temperature: 0.7

  reviewer:
    description: "评审者"
    system_prompt: "..."
    temperature: 0.2
```

### 切换模型

修改 `agents.yaml` 中的 `model` 字段即可切换为其他兼容 OpenAI 接口的模型（如 GPT-4、Claude API 等），同时修改 `orchestrator.py` 中的 `base_url` 指向对应服务端点。

### 调整 Token 上限

在 `orchestrator.py` 的 `call_agent()` 函数中修改 `max_tokens` 参数（默认 2048）。

---

## 日志格式

每次运行生成的 JSON 日志包含完整的 trace，可用于分析和调试：

```json
{
  "question": "用户问题",
  "report": "最终报告",
  "scores": { "accuracy": 9, "completeness": 9, "readability": 9, "suggestions": [...] },
  "trace": [
    { "agent": "planner", "input": "...", "output": "...", "elapsed_seconds": 3.87, "input_tokens": 92, "output_tokens": 177 },
    ...
  ]
}
```

---

## License

MIT
