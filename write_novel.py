import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.ai_client import AIClient
from core.project_manager import ProjectManager

NOVEL_NAME = "重生之都市系统"
PROJECTS_DIR = "projects"
CHAPTERS_DIR = "chapters"
TARGET_CHAPTERS = 45
WORDS_PER_CHAPTER = 2500

GENRE = "都市重生+系统"
DESCRIPTION = "2026年，程序员林远因公司破产、女友背叛、车祸身亡，意外重生到2016年大学时代。觉醒'人生重置系统'后，他凭借十年记忆和系统能力，从零开始逆袭人生：创办科技公司、破解商业阴谋、收获真挚爱情，最终成为改变世界的科技巨头。"

SYSTEM_PROMPT = f"""你是一位专业的网络小说作家，擅长写{GENRE}类型的小说。

写作要求：
1. 每章约{WORDS_PER_CHAPTER}字，不少于2300字
2. 保持紧凑的节奏，每章要有冲突或悬念
3. 塑造立体的角色，对话要自然
4. 世界观设定要合理，前后逻辑一致
5. 适当设置爽点，让读者有代入感
6. 文笔流畅，避免过度描写和水字数

小说信息：
- 书名：《{NOVEL_NAME}》
- 类型：{GENRE}
- 简介：{DESCRIPTION}

请严格按以下格式输出，不要输出任何多余内容：
直接输出章节正文，以"# 第X章 标题"开头，不要加其他标记。"""

CHAPTER_OUTLINES = [
    "第一章：林远在2026年遭遇人生最低谷，公司破产、女友背叛、车祸身亡，意识消散前看到十年前的自己，重生回到2016年大学开学日。系统觉醒，发布第一个任务。",
    "第二章：林远适应重生后的生活，系统介绍基本功能（属性面板、任务系统、商城）。他决定先解决经济问题，利用前世记忆发现第一个商机——比特币。",
    "第三章：林远用仅有的积蓄买入比特币，引起室友王浩的注意。系统发布支线任务：参加校园创业大赛。林远与前世的好兄弟重逢。",
    "第四章：创业大赛报名，林远组建团队。前世暗恋的校花苏念雪出现，这次他决定主动出击。系统提示：苏念雪身上隐藏着重大秘密。",
    "第五章：比特币暴涨，林远获得第一桶金。创业大赛初赛，林远团队以移动支付方案惊艳全场。竞争对手赵天明登场——前世的死对头。",
    "第六章：赵天明暗中调查林远的背景，发现他的商业眼光异常精准。林远和苏念雪的关系升温，系统发布新任务：进入互联网行业。",
    "第七章：林远注册公司'远星科技'，开发校园外卖平台。团队扩张，技术天才李明加入。系统解锁新功能：商业洞察（可分析市场趋势）。",
    "第八章：外卖平台上线首日遭遇服务器崩溃，林远利用系统优化能力解决。日订单突破1000，引起投资人注意。赵天明开始模仿林远的商业模式。",
    "第九章：天使投资人周总约见林远，提出投资意向。林远凭借前世经验识破对方的真实意图——想控制公司。他选择拒绝，寻找更好的合作伙伴。",
    "第十章：比特币再次暴涨，林远资金充裕。他开始布局移动支付赛道，与支付宝、微信抢占校园市场。系统发布限时任务：30天内用户突破10万。",
    "第十一章：推广陷入瓶颈，林远想出'扫码领红包'的营销方案（前世的经典策略）。效果惊人，用户暴涨。苏念雪主动约林远吃饭，两人关系更进一步。",
    "第十二章：赵天明联合校方领导，试图打压林远的公司。林远利用系统情报提前布局，反将一军。系统奖励：解锁'人心洞察'技能。",
    "第十三章：林远发现苏念雪的家族背景不简单——她是苏氏集团的千金，家族正面临商业危机。系统发布隐藏任务：帮助苏念雪。",
    "第十四章：林远与苏念雪坦诚相待，两人开始合作。他利用前世记忆，帮苏家避开了一个致命的商业陷阱。苏念雪对林远刮目相看。",
    "第十五章：毕业季来临，林远的公司估值已过千万。他决定All in人工智能赛道，招募AI人才。系统发布主线任务：成为中国AI领域的领军人物。",
    "第十六章：林远开发出第一款AI产品——智能客服系统，获得多家企业订单。竞争对手开始模仿，价格战爆发。林远选择差异化竞争。",
    "第十七章：赵天明的公司获得资本注入，开始疯狂扩张。林远不为所动，专注于技术壁垒。系统警告：赵天明背后有更大的势力。",
    "第十八章：林远发现赵天明的幕后支持者是前世害他破产的陈家。复仇的火焰点燃，但他决定用商业手段而非阴谋。",
    "第十九章：林远推出AI写作助手产品，一炮而红。公司估值飙升，成为行业新星。苏念雪正式加入远星科技，担任战略总监。",
    "第二十章：公司获得A轮融资，估值破亿。林远与苏念雪的感情也水到渠成。但系统发出警告：危机即将来临。",
    "第二十一章：陈家出手，联合多家公司围剿远星科技。林远利用系统分析对手弱点，逐一击破。商战进入白热化。",
    "第二十二章：赵天明叛变，倒向林远。原来他也被陈家利用，幡然醒悟。林远获得重要情报，准备反击。",
    "第二十三章：林远召开发布会，公布陈家的商业丑闻。舆论哗然，陈家股价暴跌。系统奖励：解锁'商业帝国'技能。",
    "第二十四章：远星科技成为行业龙头，林远被评为'30岁以下最具影响力企业家'。苏念雪怀孕，人生圆满。",
    "第二十五章：林远布局新能源赛道，投资电池技术。系统发布终极任务：改变世界。他开始思考人生的意义。",
    "第二十六章：新能源项目取得突破，远星科技市值破千亿。林远成立慈善基金，回馈社会。系统最终提示：任务完成。",
    "第二十七章：林远在巅峰时刻，选择急流勇退，将公司交给职业经理人。他和苏念雪环游世界，享受人生。系统消失，留下最后一句话：你已经不需要系统了。",
]

def create_novel_project():
    pm = ProjectManager(PROJECTS_DIR)
    if NOVEL_NAME in [p["name"] for p in pm.list_projects()]:
        pm.open_project(NOVEL_NAME)
        return pm
    pm.create_project(NOVEL_NAME, DESCRIPTION, GENRE, "112500")
    return pm

def write_chapter(pm, client, chapter_num, outline):
    print(f"\n{'='*60}")
    print(f"正在创作第 {chapter_num} 章...")
    print(f"{'='*60}")

    chapters_path = os.path.join(pm.current_project["path"], "chapters")
    os.makedirs(chapters_path, exist_ok=True)

    context = build_context(pm, chapter_num)
    prompt = f"""请创作第{chapter_num}章的内容。

章节大纲：{outline}

{context}

要求：
1. 约{WORDS_PER_CHAPTER}字
2. 保持与前文的连贯性
3. 结尾设置悬念
4. 直接输出正文，不要任何解释"""

    messages = [{"role": "user", "content": prompt}]

    print("AI 生成中...")
    result = client.chat(messages)
    print(f"生成完成，字数：{len(result)}")

    filename = f"第{chapter_num:02d}章.md"
    filepath = os.path.join(chapters_path, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(result)
    print(f"已保存：{filename}")

    time.sleep(2)
    return result

def build_context(pm, current_chapter):
    if current_chapter <= 1:
        return ""
    parts = []
    chapters_path = os.path.join(pm.current_project["path"], "chapters")
    for i in range(max(1, current_chapter - 3), current_chapter):
        fname = f"第{i:02d}章.md"
        fpath = os.path.join(chapters_path, fname)
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            summary = content[-500:] if len(content) > 500 else content
            parts.append(f"第{i}章结尾：\n{summary}")
    if parts:
        return "以下是前几章的结尾，用于保持连贯性：\n\n" + "\n\n".join(parts)
    return ""

def main():
    print("="*60)
    print(f"  《{NOVEL_NAME}》自动创作系统")
    print(f"  类型：{GENRE}")
    print(f"  目标：{TARGET_CHAPTERS} 章 × {WORDS_PER_CHAPTER} 字")
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

    pm = create_novel_project()
    print(f"\n项目已创建：{pm.current_project['path']}")

    with open(os.path.join(pm.current_project["path"], "整体大纲.md"), "w", encoding="utf-8") as f:
        f.write(f"# 《{NOVEL_NAME}》整体大纲\n\n")
        f.write(f"## 基本信息\n")
        f.write(f"- 类型：{GENRE}\n")
        f.write(f"- 简介：{DESCRIPTION}\n")
        f.write(f"- 目标字数：{TARGET_CHAPTERS * WORDS_PER_CHAPTER} 字\n\n")
        f.write(f"## 章节大纲\n\n")
        for i, outline in enumerate(CHAPTER_OUTLINES, 1):
            f.write(f"{outline}\n\n")

    with open(os.path.join(pm.current_project["path"], "roles", "主角-林远.md"), "w", encoding="utf-8") as f:
        f.write(f"# 角色：林远\n\n## 基本信息\n- 姓名：林远\n- 性别：男\n- 年龄：26岁（重生时16岁）\n- 身份：程序员 → 大学生 → 科技公司CEO\n\n## 外貌特征\n- 身高：180cm\n- 特征：剑眉星目，眼神深邃，气质沉稳\n- 标志性物品：智能手表（系统载体）\n\n## 性格特征\n- 核心性格：沉稳老练（36岁灵魂16岁身体）、果断、重情义\n- 优点：商业眼光独到、技术功底扎实、重情重义\n- 缺点：有时过于激进、对前世仇人难以释怀\n\n## 能力成长\n| 阶段 | 状态 | 关键能力 |\n|------|------|----------|\n| 重生初期 | 大学生 | 前世记忆、系统基础功能 |\n| 创业阶段 | CEO | 商业洞察、技术视野 |\n| 崛起阶段 | 行业领袖 | 商业帝国技能、AI技术 |\n| 巅峰阶段 | 科技巨头 | 系统完成使命，回归平凡 |\n\n## 关系网络\n- 恋人/妻子：苏念雪（校花，苏氏集团千金）\n- 好兄弟：王浩（室友）、李明（技术天才）\n- 宿敌：赵天明（后和解）、陈家（最终对手）\n\n## 角色弧线\n从人生失败者到重生逆袭，最终明白人生的意义不在于财富和权力，而在于身边的人和内心的平静。")

    with open(os.path.join(pm.current_project["path"], "roles", "女主-苏念雪.md"), "w", encoding="utf-8") as f:
        f.write(f"# 角色：苏念雪\n\n## 基本信息\n- 姓名：苏念雪\n- 性别：女\n- 年龄：18岁（初登场）\n- 身份：校花 → 苏氏集团千金 → 远星科技战略总监\n\n## 外貌特征\n- 身高：168cm\n- 特征：明眸皓齿，气质清冷，笑起来很甜\n- 标志性：长发及腰，喜欢穿白色连衣裙\n\n## 性格特征\n- 核心性格：外冷内热、聪明独立、重感情\n- 优点：商业天赋、善良正直、忠诚\n- 缺点：家族负担重、有时过于要强\n\n## 角色弧线\n从被家族束缚的千金小姐，到独立自主的职场女性，最终成为林远的贤内助和事业伙伴。")

    with open(os.path.join(pm.current_project["path"], "settings", "世界观设定.md"), "w", encoding="utf-8") as f:
        f.write(f"# 世界观设定\n\n## 时代背景\n- 故事时间：2016年-2026年\n- 现实世界，无超自然元素\n- 重点行业：互联网、人工智能、新能源\n\n## 系统设定\n- 名称：人生重置系统\n- 功能：\n  - 属性面板（智力、魅力、体力等）\n  - 任务系统（主线、支线、限时）\n  - 商城（可兑换技能、知识）\n  - 商业洞察（分析市场趋势）\n  - 人心洞察（判断他人真实想法）\n- 限制：不能直接给予金钱、不能改变物理规律\n- 最终目标：帮助宿主实现人生圆满后自动消失\n\n## 势力分布\n- 远星科技：林远创立，后成为行业龙头\n- 苏氏集团：传统企业，后与远星合作\n- 陈家：商业世家，主要反派\n- 各大互联网公司：阿里巴巴、腾讯、百度等背景势力")

    print("\n开始创作正文...")
    total_words = 0
    for i, outline in enumerate(CHAPTER_OUTLINES, 1):
        chapter_text = write_chapter(pm, client, i, outline)
        total_words += len(chapter_text)
        print(f"累计字数：{total_words}")

    stats = pm.get_project_stats()
    print(f"\n{'='*60}")
    print(f"  创作完成！")
    print(f"  总章数：{len(CHAPTER_OUTLINES)}")
    print(f"  总字数：{stats.get('total_chars', total_words)}")
    print(f"  项目路径：{pm.current_project['path']}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
