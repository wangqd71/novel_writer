import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.ai_client import AIClient
from core.project_manager import ProjectManager

NOVEL_NAME = "重生之都市系统"
PROJECTS_DIR = "projects"
WORDS_PER_CHAPTER = 2500

CHAPTER_OUTLINES = {
    2: "第二章：林远适应重生后的生活，系统介绍基本功能（属性面板、任务系统、商城）。他决定先解决经济问题，利用前世记忆发现第一个商机——比特币。",
    4: "第四章：创业大赛报名，林远组建团队。前世暗恋的校花苏念雪出现，这次他决定主动出击。系统提示：苏念雪身上隐藏着重大秘密。",
    5: "第五章：比特币暴涨，林远获得第一桶金。创业大赛初赛，林远团队以移动支付方案惊艳全场。竞争对手赵天明登场——前世的死对头。",
    6: "第六章：赵天明暗中调查林远的背景，发现他的商业眼光异常精准。林远和苏念雪的关系升温，系统发布新任务：进入互联网行业。",
    7: "第七章：林远注册公司'远星科技'，开发校园外卖平台。团队扩张，技术天才李明加入。系统解锁新功能：商业洞察（可分析市场趋势）。",
    8: "第八章：外卖平台上线首日遭遇服务器崩溃，林远利用系统优化能力解决。日订单突破1000，引起投资人注意。赵天明开始模仿林远的商业模式。",
    9: "第九章：天使投资人周总约见林远，提出投资意向。林远凭借前世经验识破对方的真实意图——想控制公司。他选择拒绝，寻找更好的合作伙伴。",
    10: "第十章：比特币再次暴涨，林远资金充裕。他开始布局移动支付赛道，与支付宝、微信抢占校园市场。系统发布限时任务：30天内用户突破10万。",
    11: "第十一章：推广陷入瓶颈，林远想出'扫码领红包'的营销方案（前世的经典策略）。效果惊人，用户暴涨。苏念雪主动约林远吃饭，两人关系更进一步。",
    12: "第十二章：赵天明联合校方领导，试图打压林远的公司。林远利用系统情报提前布局，反将一军。系统奖励：解锁'人心洞察'技能。",
    13: "第十三章：林远发现苏念雪的家族背景不简单——她是苏氏集团的千金，家族正面临商业危机。系统发布隐藏任务：帮助苏念雪。",
    14: "第十四章：林远与苏念雪坦诚相待，两人开始合作。他利用前世记忆，帮苏家避开了一个致命的商业陷阱。苏念雪对林远刮目相看。",
    15: "第十五章：毕业季来临，林远的公司估值已过千万。他决定All in人工智能赛道，招募AI人才。系统发布主线任务：成为中国AI领域的领军人物。",
    16: "第十六章：林远开发出第一款AI产品——智能客服系统，获得多家企业订单。竞争对手开始模仿，价格战爆发。林远选择差异化竞争。",
    17: "第十七章：赵天明的公司获得资本注入，开始疯狂扩张。林远不为所动，专注于技术壁垒。系统警告：赵天明背后有更大的势力。",
    18: "第十八章：林远发现赵天明的幕后支持者是前世害他破产的陈家。复仇的火焰点燃，但他决定用商业手段而非阴谋。",
    19: "第十九章：林远推出AI写作助手产品，一炮而红。公司估值飙升，成为行业新星。苏念雪正式加入远星科技，担任战略总监。",
    20: "第二十章：公司获得A轮融资，估值破亿。林远与苏念雪的感情也水到渠成。但系统发出警告：危机即将来临。",
    21: "第二十一章：陈家出手，联合多家公司围剿远星科技。林远利用系统分析对手弱点，逐一击破。商战进入白热化。",
    22: "第二十二章：赵天明叛变，倒向林远。原来他也被陈家利用，幡然醒悟。林远获得重要情报，准备反击。",
    23: "第二十三章：林远召开发布会，公布陈家的商业丑闻。舆论哗然，陈家股价暴跌。系统奖励：解锁'商业帝国'技能。",
    24: "第二十四章：远星科技成为行业龙头，林远被评为'30岁以下最具影响力企业家'。苏念雪怀孕，人生圆满。",
    25: "第二十五章：林远布局新能源赛道，投资电池技术。系统发布终极任务：改变世界。他开始思考人生的意义。",
    26: "第二十六章：新能源项目取得突破，远星科技市值破千亿。林远成立慈善基金，回馈社会。系统最终提示：任务完成。",
    27: "第二十七章：林远在巅峰时刻，选择急流勇退，将公司交给职业经理人。他和苏念雪环游世界，享受人生。系统消失，留下最后一句话：你已经不需要系统了。",
}

def build_context(pm, current_chapter):
    parts = []
    chapters_path = os.path.join(pm.current_project["path"], "chapters")
    for i in range(max(1, current_chapter - 3), current_chapter):
        fname = f"第{i:02d}章.md"
        fpath = os.path.join(chapters_path, fname)
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            if len(content) > 100:
                summary = content[-800:] if len(content) > 800 else content
                parts.append(f"第{i}章结尾：\n{summary}")
    if parts:
        return "以下是前几章的结尾，用于保持连贯性：\n\n" + "\n\n".join(parts)
    return ""

def write_chapter(pm, client, chapter_num, outline, max_retries=3):
    print(f"\n{'='*60}")
    print(f"正在创作第 {chapter_num} 章...")
    print(f"大纲：{outline[:50]}...")
    print(f"{'='*60}")

    chapters_path = os.path.join(pm.current_project["path"], "chapters")
    os.makedirs(chapters_path, exist_ok=True)

    context = build_context(pm, chapter_num)
    prompt = f"""请创作第{chapter_num}章的内容。

章节大纲：{outline}

{context}

要求：
1. 约{WORDS_PER_CHAPTER}字，不少于2300字
2. 保持与前文的连贯性
3. 结尾设置悬念
4. 直接输出正文，不要任何解释
5. 以"# 第X章 标题"开头"""

    messages = [{"role": "user", "content": prompt}]

    for attempt in range(max_retries):
        try:
            print(f"AI 生成中... (尝试 {attempt+1}/{max_retries})")
            result = client.chat(messages)
            if len(result) > 100:
                print(f"生成完成，字数：{len(result)}")
                filename = f"第{chapter_num:02d}章.md"
                filepath = os.path.join(chapters_path, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(result)
                print(f"已保存：{filename}")
                time.sleep(3)
                return result
            else:
                print(f"生成内容过短，重试...")
                time.sleep(5)
        except Exception as e:
            print(f"错误：{e}")
            time.sleep(10)

    print(f"第 {chapter_num} 章创作失败")
    return None

def main():
    print("="*60)
    print(f"  《{NOVEL_NAME}》续写系统")
    print("="*60)

    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    client = AIClient(config.get("ai", {}))
    print(f"\n模型：{client.model}")
    print(f"API：{client.base_url}")

    print("\n测试 API 连通性...")
    ok, msg = client.test_connection()
    if not ok:
        print(f"连接失败：{msg}")
        return
    print(f"连接成功！")

    pm = ProjectManager(PROJECTS_DIR)
    pm.open_project(NOVEL_NAME)
    print(f"\n项目路径：{pm.current_project['path']}")

    chapters_path = os.path.join(pm.current_project["path"], "chapters")
    existing = {}
    if os.path.exists(chapters_path):
        for f in os.listdir(chapters_path):
            if f.endswith(".md"):
                fpath = os.path.join(chapters_path, f)
                with open(fpath, "r", encoding="utf-8") as fh:
                    content = fh.read()
                num_str = f.replace("第", "").replace("章.md", "")
                try:
                    num = int(num_str)
                    existing[num] = len(content)
                except:
                    pass

    print("\n检查章节状态：")
    to_write = []
    for num, outline in CHAPTER_OUTLINES.items():
        size = existing.get(num, 0)
        status = "OK" if size > 1000 else "NEED WRITE"
        print(f"  第{num}章: {size} 字 - {status}")
        if size < 1000:
            to_write.append((num, outline))

    if not to_write:
        print("\n所有章节已完成！")
        return

    print(f"\n需要续写 {len(to_write)} 章：{[t[0] for t in to_write]}")
    print("开始续写...")

    total_written = 0
    for num, outline in to_write:
        result = write_chapter(pm, client, num, outline)
        if result:
            total_written += len(result)
            print(f"本章字数：{len(result)}，累计续写：{total_written}")

    print(f"\n{'='*60}")
    print(f"  续写完成！共写 {total_written} 字")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
