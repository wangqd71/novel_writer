# NovelWriter - AI 小说写作智能体

专为小说创作者打造的 AI 写作桌面客户端，参考 [FeelFish](https://www.feelfish.com) 产品设计。

## 功能特性

- **对话即创作** — 右侧 AI 面板直接对话，支持流式输出
- **智能上下文** — 自动携带项目角色/设定/大纲信息给 AI，保障剧情一致性
- **项目管理** — 章节/角色/设定/笔记分类管理，本地 Markdown 存储
- **AI 快捷操作** — 续写、润色、大纲、角色设计、检查剧情漏洞一键触发
- **多模型支持** — 小米 MiMo / DeepSeek / 千问 / OpenAI，可自定义 API
- **智能开篇** — 根据项目设定自动生成开篇内容

## 界面预览

```
┌────────────┬──────────────────────────────┬──────────────────┐
│            │                              │                  │
│  项目结构   │       Markdown 编辑器         │   AI 对话面板     │
│            │                              │                  │
│  + 章节    │                              │  [续写][润色]     │
│  + 角色    │                              │  [大纲][检查]     │
│  + 设定    │                              │                  │
│  + 笔记    │                              │  输入框...        │
│            │                              │                  │
├────────────┴──────────────────────────────┴──────────────────┤
│  状态栏: 当前文件 | 字数统计                                    │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

### 方式一：运行源码

```bash
pip install customtkinter requests Pillow
python main.py
```

### 方式二：打包为 EXE

```bash
pip install customtkinter requests Pillow pyinstaller
python build.py
```

生成的 `NovelWriter.exe` 位于 `dist/` 目录。

## 使用说明

1. 启动后，菜单 → **文件** → **新建项目**，输入小说名称和类型
2. 菜单 → **AI** → **AI 设置**，配置 API Key 和模型
3. 左侧项目栏创建章节文件，开始写作
4. 右侧 AI 面板输入需求，AI 会基于项目上下文辅助创作
5. 快捷按钮：续写 / 润色 / 大纲 / 角色 / 检查

## AI 模型配置

默认使用小米 MiMo 模型，也支持以下预设：

| 模型 | API 地址 | 模型名称 |
|------|----------|----------|
| MiMo | `https://token-plan-cn.xiaomimimo.com/v1` | `mimo-v2.5-pro` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| 千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o` |

## 项目结构

```
novel_writer/
├── main.py                  # 入口
├── build.py                 # PyInstaller 打包脚本
├── config.json              # 运行时配置（API Key 等）
├── requirements.txt
├── core/
│   ├── project_manager.py   # 项目管理（创建/打开/文件操作）
│   ├── ai_client.py         # AI 客户端（OpenAI 兼容协议）
│   └── context_manager.py   # 智能上下文管理
└── ui/
    ├── main_window.py       # 主窗口（三栏布局 + 菜单）
    ├── sidebar.py           # 左侧文件树
    ├── editor_panel.py      # 中央 Markdown 编辑器
    ├── chat_panel.py        # 右侧 AI 对话面板
    ├── settings_dialog.py   # 设置对话框
    └── style.py             # 主题样式
```

## 依赖

- Python 3.10+
- customtkinter >= 5.2.0
- requests >= 2.28.0
- Pillow >= 9.0.0

## License

MIT
