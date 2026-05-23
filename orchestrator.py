import json
import os
import time
import yaml
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


def load_config():
    with open("agents.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def call_agent(agent_name: str, agent_config: dict, user_message: str, model: str) -> dict:
    """调用单个 Agent 并返回结果"""
    start_time = time.time()

    response = client.chat.completions.create(
        model=model,
        max_tokens=2048,
        messages=[
            {"role": "system", "content": agent_config["system_prompt"]},
            {"role": "user", "content": user_message},
        ],
        temperature=agent_config.get("temperature", 0.5),
    )

    elapsed = round(time.time() - start_time, 2)
    output = response.choices[0].message.content

    return {
        "agent": agent_name,
        "input": user_message,
        "output": output,
        "elapsed_seconds": elapsed,
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
    }


def run_pipeline(question: str) -> dict:
    """执行完整的多智能体流水线"""
    config = load_config()
    agents = config["agents"]
    model = config["model"]
    trace = []  # 记录每一步的执行情况

    print(f"\n问题：{question}\n{'='*50}")

    # Step 1: Planner 拆解任务
    print("[1/4] Planner 拆解任务...")
    plan_result = call_agent("planner", agents["planner"], question, model)
    trace.append(plan_result)

    try:
        subtasks = json.loads(plan_result["output"])
    except json.JSONDecodeError:
        subtasks = [question]  # 解析失败则直接用原问题

    print(f"  拆解为 {len(subtasks)} 个子任务：{subtasks}")

    # Step 2: Researcher 并行研究每个子任务
    print("[2/4] Researcher 研究各子任务...")
    research_results = []
    for i, subtask in enumerate(subtasks):
        print(f"  研究子任务 {i+1}/{len(subtasks)}: {subtask}")
        result = call_agent("researcher", agents["researcher"], subtask, model)
        trace.append(result)
        research_results.append(result["output"])

    # Step 3: Writer 整合报告
    print("[3/4] Writer 整合报告...")
    combined_research = "\n\n---\n\n".join(
        [f"子任务：{subtasks[i]}\n\n{r}" for i, r in enumerate(research_results)]
    )
    writer_input = f"原始问题：{question}\n\n研究结果：\n{combined_research}"
    writer_result = call_agent("writer", agents["writer"], writer_input, model)
    trace.append(writer_result)

    # Step 4: Reviewer 评审报告
    print("[4/4] Reviewer 评审报告...")
    reviewer_result = call_agent(
        "reviewer", agents["reviewer"], writer_result["output"], model
    )
    trace.append(reviewer_result)

    try:
        scores = json.loads(reviewer_result["output"])
    except json.JSONDecodeError:
        scores = {"error": "解析评分失败"}

    return {
        "question": question,
        "report": writer_result["output"],
        "scores": scores,
        "trace": trace,
    }