import json
import os
import glob


def analyze_logs():
    log_files = glob.glob("logs/run_*.json")
    if not log_files:
        print("暂无日志")
        return

    all_runs = []
    for f in sorted(log_files):
        with open(f, encoding="utf-8") as fp:
            all_runs.append(json.load(fp))

    print(f"总运行次数：{len(all_runs)}\n")

    # 各 Agent 平均耗时
    agent_times = {}
    agent_scores = {"accuracy": [], "completeness": [], "readability": []}

    for run in all_runs:
        for step in run["trace"]:
            name = step["agent"]
            agent_times.setdefault(name, []).append(step["elapsed_seconds"])

        scores = run.get("scores", {})
        for key in agent_scores:
            if key in scores:
                agent_scores[key].append(scores[key])

    print("各 Agent 平均耗时（秒）：")
    for agent, times in agent_times.items():
        avg = sum(times) / len(times)
        print(f"  {agent}: {avg:.2f}s")

    print("\n平均评分：")
    for key, vals in agent_scores.items():
        if vals:
            avg = sum(vals) / len(vals)
            print(f"  {key}: {avg:.1f}/10")


if __name__ == "__main__":
    analyze_logs()