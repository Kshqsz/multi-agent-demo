import json
import os
from datetime import datetime
from orchestrator import run_pipeline


def main():
    question = input("请输入研究问题：").strip()
    if not question:
        question = "量子计算对密码学的影响是什么？"

    result = run_pipeline(question)

    # 打印报告
    print(f"\n{'='*50}")
    print("最终报告：")
    print(result["report"])
    print(f"\n评分：{result['scores']}")

    # 保存日志
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = f"logs/run_{timestamp}.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n日志已保存：{log_path}")


if __name__ == "__main__":
    main()