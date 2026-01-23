# gettoken.py - 获取解锁密钥实用程序
import api
import random
import json
import os
import time
from datetime import datetime  # 新增：用于获取当前时间戳

# 答题规则
TOTAL_QUESTIONS = 10
PASS_SCORE = 80
SCORE_PER_QUESTION = 10

# 审核阈值
SINGLE_QUESTION_FAST_THRESHOLD = 2    # 单题过快阈值（秒）
FAST_QUESTION_COUNT_THRESHOLD = 3     # 过快题数阈值
AVERAGE_TIME_FAST_THRESHOLD = 3       # 平均用时阈值

# 题库路径
QUESTION_BANK_PATH = r'%s\apps\question_bank.json' % os.getcwd()

# 颜色常量
RED_COLOR = "\033[91m"
GREEN_COLOR = "\033[92m"
RESET_COLOR = "\033[0m"
YELLOW_COLOR = "\033[93m"

# 程序主逻辑
def main():
    print("获取解锁密钥实用程序")
    print("注意：此密钥包含一些设备的敏感数据，请勿泄露！")
    print(f"解锁需要您判断一些选项（共{TOTAL_QUESTIONS}道题，一道题{SCORE_PER_QUESTION}分，大于等于{PASS_SCORE}分可获取密钥）。\n")

    # 读取题库及历史记录
    question_bank = {}
    try:
        with open(QUESTION_BANK_PATH, 'r', encoding='utf-8') as f:
            question_bank = json.load(f)
            # 确保history字段存在
            if "history" not in question_bank:
                question_bank["history"] = []
    except FileNotFoundError:
        print(f"错误：题库文件不存在，路径：{QUESTION_BANK_PATH}")
        print("请确认question_bank.json文件位置后重试！")
        return
    except json.JSONDecodeError:
        print("错误：题库文件格式错误（非合法JSON）")
        return

    # 检查题库数量
    if len(question_bank.get("questions", [])) < TOTAL_QUESTIONS:
        print(f"错误：题库数量不足！当前题库有{len(question_bank.get('questions', []))}道题，需要至少{TOTAL_QUESTIONS}道")
        return

    # 检查是否有历史记录并询问是否重新答题
    history = question_bank["history"]
    if history:
        # 获取最近的一条记录
        latest_record = history[-1]
        print("检测到有历史答题数据，以下是历史数据")
        print(f"上次得分：{latest_record['score']}分，状态：{'通过' if latest_record['pass'] else '未通过'}，答题时间：{latest_record['timestamp']}，平均答题时间：{latest_record['avg_time']}秒")
        if not api.api_confirm("是否重新答题？（y/n）"):
            # 不重新答题，检查是否通过
            if latest_record["pass"] and latest_record["score"] >= PASS_SCORE:
                print(f"{GREEN_COLOR}您已通过测试，以下是你的解锁密钥{RESET_COLOR}")
                print(f"解锁密钥（请妥善保管）: {api.return_token()}")
                return
            else:
                print(f"{YELLOW_COLOR}您上次未通过测试，无法获取密钥，请重新答题。{RESET_COLOR}")
                return

    # 随机抽题
    selected_questions = random.sample(question_bank["questions"], TOTAL_QUESTIONS)
    score = 0
    answer_times = []

    # 答题环节
    for idx, q in enumerate(selected_questions, 1):
        start_ts = time.time()
        user_ans = api.api_confirm(f"{idx}. {q['question']}")
        end_ts = time.time()
        cost_time = round(end_ts - start_ts, 2)
        answer_times.append(cost_time)

        if user_ans == q["answer"]:
            score += SCORE_PER_QUESTION
            api.api_ok(f"答对了！（用时：{cost_time}秒）")
        else:
            api.api_warn(f"答错了，不加分。（用时：{cost_time}秒）")

    # 计算过快答题数量
    fast_question_count = sum(1 for t in answer_times if t < SINGLE_QUESTION_FAST_THRESHOLD)
    # 计算平均答题时间
    avg_answer_time = round(sum(answer_times) / len(answer_times), 2) if answer_times else 0
    # 判断是否作弊
    is_cheating = fast_question_count >= FAST_QUESTION_COUNT_THRESHOLD or avg_answer_time < AVERAGE_TIME_FAST_THRESHOLD
    # 判断是否通过
    is_pass = score >= PASS_SCORE and not is_cheating

    # 记录答题结果到history
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_record = {
        "timestamp": current_time,
        "score": score,
        "pass": is_pass,
        "avg_time": avg_answer_time,
        "fast_questions": fast_question_count
    }
    question_bank["history"].append(new_record)

    # 写入题库文件
    try:
        with open(QUESTION_BANK_PATH, 'w', encoding='utf-8') as f:
            json.dump(question_bank, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"{RED_COLOR}错误：记录答题历史失败 - {str(e)}{RESET_COLOR}")

    # 结果输出
    print("\n" + "="*50)
    if score >= PASS_SCORE:
        if not is_cheating:
            print(f"{GREEN_COLOR}恭喜！得分：{score}分（及格线{PASS_SCORE}分）{RESET_COLOR}")
            print(f"答题统计：平均用时{avg_answer_time}秒 | 过快答题{fast_question_count}道")
            print("审核通过，以下是你的解锁密钥")
            print(f"解锁密钥（请妥善保管）: {api.return_token()}")
            return
        else:
            print(f"{YELLOW_COLOR}得分：{score}分（达到及格线，但审核未通过）{RESET_COLOR}")
            print(f"审核异常原因：")
            print(f"   - 平均答题时间{avg_answer_time}秒（阈值{AVERAGE_TIME_FAST_THRESHOLD}秒）")
            print(f"   - 过快答题{fast_question_count}道（阈值{FAST_QUESTION_COUNT_THRESHOLD}道）")
            print(f"{RED_COLOR}疑似抄答案行为，暂无法获取密钥，请稍后重试。{RESET_COLOR}")
            return
    else:
        print(f"{YELLOW_COLOR}未通过测试：得分{score}分（及格线{PASS_SCORE}分）{RESET_COLOR}")
        print(f"答题统计：平均用时{avg_answer_time}秒 | 过快答题{fast_question_count}道")
        print("请重新学习相关知识后再尝试。")
        return

if __name__ == "__exec__":
    try:
        main()
    except Exception as e:
        print(f"程序运行出错：{str(e)}")
else:
    raise SystemError("请不要直接运行本程序")