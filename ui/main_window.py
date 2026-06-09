import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import sys

from ui.style import COLORS, FONTS, apply_theme
from ui.sidebar import Sidebar
from ui.editor_panel import EditorPanel
from ui.chat_panel import ChatPanel
from ui.settings_dialog import SettingsDialog
from core.project_manager import ProjectManager
from core.ai_client import AIClient
from core.context_manager import ContextManager

CONFIG_FILE = "config.json"

class MainWindow(ctk.CTk):
    """主窗口：三栏布局 — 侧边栏 | 编辑器 | AI对话面板"""

    def __init__(self):
        super().__init__()
        apply_theme()
        self.title("NovelWriter - AI 小说写作智能体")
        self.geometry("1400x850")
        self.minsize(1000, 600)
        self._load_config()
        self._init_core()
        self._create_menu()
        self._create_ui()
        self._load_last_project()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _get_config_path(self):
        if getattr(sys, 'frozen', False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, CONFIG_FILE)

    def _load_config(self):
        self.config_path = self._get_config_path()
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.app_config = json.load(f)
        else:
            self.app_config = {}

    def _save_config(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.app_config, f, ensure_ascii=False, indent=2)

    def _init_core(self):
        base_dir = self.app_config.get("projects_dir", "projects")
        if getattr(sys, 'frozen', False):
            base_dir = os.path.join(os.path.dirname(sys.executable), base_dir)
        self.project_manager = ProjectManager(base_dir)
        self.ai_client = AIClient(self.app_config.get("ai", {}))
        self.context_manager = ContextManager(self.project_manager)

    def _create_menu(self):
        menubar = tk.Menu(self, bg=COLORS["bg_dark"], fg=COLORS["text_primary"],
                           activebackground=COLORS["accent"], activeforeground="white",
                           font=FONTS["small"])
        file_menu = tk.Menu(menubar, tearoff=0, bg=COLORS["bg_medium"], fg=COLORS["text_primary"],
                             activebackground=COLORS["accent"], font=FONTS["small"])
        file_menu.add_command(label="新建项目", command=self._new_project)
        file_menu.add_command(label="打开项目", command=self._open_project)
        file_menu.add_separator()
        file_menu.add_command(label="保存当前文件", command=self._save_current)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._on_close)
        menubar.add_cascade(label="文件", menu=file_menu)
        ai_menu = tk.Menu(menubar, tearoff=0, bg=COLORS["bg_medium"], fg=COLORS["text_primary"],
                           activebackground=COLORS["accent"], font=FONTS["small"])
        ai_menu.add_command(label="AI 设置", command=self._open_settings)
        ai_menu.add_command(label="发送上下文到 AI", command=self._send_context)
        ai_menu.add_separator()
        ai_menu.add_command(label="智能开篇", command=self._ai_smart_start)
        ai_menu.add_command(label="续写当前章节", command=self._ai_continue)
        ai_menu.add_command(label="润色当前章节", command=self._ai_polish)
        ai_menu.add_command(label="检查剧情漏洞", command=self._ai_check_plot)
        menubar.add_cascade(label="AI", menu=ai_menu)
        help_menu = tk.Menu(menubar, tearoff=0, bg=COLORS["bg_medium"], fg=COLORS["text_primary"],
                              activebackground=COLORS["accent"], font=FONTS["small"])
        help_menu.add_command(label="使用帮助", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)
        self.config(menu=menubar)

    def _create_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.sidebar = Sidebar(self, on_file_select=self._on_file_select)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 1))
        self.editor = EditorPanel(self, on_save=self._on_file_saved)
        self.editor.grid(row=0, column=1, sticky="nsew", padx=1, pady=1)
        self.chat_panel = ChatPanel(self, ai_client=self.ai_client,
                                     context_manager=self.context_manager)
        self.chat_panel.grid(row=0, column=2, sticky="nsew", padx=(1, 0))
        status_bar = ctk.CTkFrame(self, fg_color=COLORS["bg_medium"], height=28)
        status_bar.grid(row=1, column=0, columnspan=3, sticky="ew")
        status_bar.pack_propagate(False)
        self.status_label = ctk.CTkLabel(status_bar, text="欢迎使用 NovelWriter",
                                          font=FONTS["small"], text_color=COLORS["text_secondary"])
        self.status_label.pack(side="left", padx=10)
        self.stats_label = ctk.CTkLabel(status_bar, text="", font=FONTS["small"],
                                         text_color=COLORS["text_dim"])
        self.stats_label.pack(side="right", padx=10)

    def _load_last_project(self):
        last = self.app_config.get("last_project")
        if last and os.path.exists(last):
            try:
                self.project_manager.open_project(os.path.basename(last))
                self.sidebar.load_project(last)
                self._update_status(f"已加载项目: {os.path.basename(last)}")
                self._update_stats()
            except Exception:
                pass

    def _new_project(self):
        dialog = NewProjectDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            name, desc, genre, target = dialog.result
            try:
                path = self.project_manager.create_project(name, desc, genre, target)
                self.sidebar.load_project(path)
                self.app_config["last_project"] = path
                self._save_config()
                self._update_status(f"已创建项目: {name}")
                self._update_stats()
            except Exception as e:
                messagebox.showerror("错误", str(e))

    def _open_project(self):
        projects = self.project_manager.list_projects()
        if not projects:
            messagebox.showinfo("提示", "暂无项目，请先创建一个新项目")
            return
        dialog = OpenProjectDialog(self, projects)
        self.wait_window(dialog)
        if dialog.result:
            try:
                path = self.project_manager.open_project(dialog.result)
                self.sidebar.load_project(path)
                self.app_config["last_project"] = path
                self._save_config()
                self._update_status(f"已打开项目: {dialog.result}")
                self._update_stats()
            except Exception as e:
                messagebox.showerror("错误", str(e))

    def _on_file_select(self, file_path):
        self.editor.open_file(file_path)
        self._update_status(f"正在编辑: {os.path.basename(file_path)}")

    def _on_file_saved(self, file_path, content):
        self._update_status(f"已保存: {os.path.basename(file_path)}")
        self._update_stats()

    def _save_current(self):
        self.editor.save_file()

    def _open_settings(self):
        SettingsDialog(self, current_config=self.app_config.get("ai", {}),
                        on_save=self._on_settings_saved)

    def _on_settings_saved(self, config):
        self.app_config["ai"] = config
        self._save_config()
        self.ai_client.update_config(config)
        self._update_status("AI 设置已保存")

    def _send_context(self):
        self.chat_panel._send_context()

    def _ai_smart_start(self):
        if not self.project_manager.current_project:
            messagebox.showwarning("提示", "请先打开一个项目")
            return
        config = self.project_manager.current_project.get("config", {})
        prompt = (
            f"请帮我为一部小说设计开篇。以下是我的设定：\n"
            f"- 小说类型: {config.get('genre', '未设定')}\n"
            f"- 小说简介: {config.get('description', '未设定')}\n\n"
            f"请生成：\n1. 开篇第一章的内容（约2000字）\n2. 主要角色设定\n3. 世界观设定\n"
            f"请分别用 # 第一章、# 角色设定、# 世界观设定 作为标题。"
        )
        self.chat_panel._set_input(prompt)

    def _ai_continue(self):
        if not self.editor.current_file:
            messagebox.showwarning("提示", "请先打开一个章节文件")
            return
        content = self.editor.get_content()
        if not content.strip():
            prompt = "请帮我写这个章节的开头，约1000字。"
        else:
            prompt = f"请帮我续写以下章节内容，保持风格一致，续写约1000字：\n\n{content[-2000:]}"
        self.chat_panel._set_input(prompt)

    def _ai_polish(self):
        content = self.editor.get_content()
        if not content.strip():
            messagebox.showwarning("提示", "编辑器中没有内容")
            return
        prompt = f"请帮我润色以下内容，提升文学性和可读性，保持原意不变：\n\n{content[:3000]}"
        self.chat_panel._set_input(prompt)

    def _ai_check_plot(self):
        content = self.editor.get_content()
        if not content.strip():
            messagebox.showwarning("提示", "编辑器中没有内容")
            return
        prompt = f"请检查以下小说内容是否存在逻辑漏洞、前后矛盾、角色行为不合理等问题，并给出修改建议：\n\n{content[:3000]}"
        self.chat_panel._set_input(prompt)

    def _show_help(self):
        help_text = (
            "NovelWriter 使用帮助\n\n"
            "1. 文件菜单\n"
            "   - 新建项目：创建新的小说项目\n"
            "   - 打开项目：打开已有的小说项目\n\n"
            "2. AI 菜单\n"
            "   - AI 设置：配置 API Key 和模型\n"
            "   - 智能开篇：AI 帮你设计开篇\n"
            "   - 续写当前章节：AI 续写当前内容\n"
            "   - 润色当前章节：AI 优化文字表达\n"
            "   - 检查剧情漏洞：AI 检查逻辑问题\n\n"
            "3. 右侧 AI 面板\n"
            "   - 直接与 AI 对话，讨论创作思路\n"
            "   - 快捷按钮：续写/润色/大纲/角色/检查\n\n"
            "4. 左侧项目栏\n"
            "   - 右键菜单可删除或重命名文件\n"
            "   - 支持创建章节/角色/设定/笔记文件"
        )
        messagebox.showinfo("使用帮助", help_text)

    def _show_about(self):
        messagebox.showinfo("关于",
            "NovelWriter - AI 小说写作智能体\n\n"
            "版本: v1.0\n"
            "参考: FeelFish 产品设计\n\n"
            "专为小说创作者打造的 AI 写作助手\n"
            "支持对话创作、智能上下文、角色管理等功能")

    def _update_status(self, text):
        self.status_label.configure(text=text)

    def _update_stats(self):
        stats = self.project_manager.get_project_stats()
        total = stats.get("total_chars", 0)
        files = stats.get("total_files", 0)
        self.stats_label.configure(text=f"共 {files} 个文件 / {total} 字")

    def _on_close(self):
        if self.editor.is_modified:
            if messagebox.askyesno("保存", "当前文件已修改，是否保存？"):
                self.editor.save_file()
        self.destroy()


class NewProjectDialog(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("新建项目")
        self.geometry("420x380")
        self.resizable(False, False)
        self.result = None
        self.transient(master)
        self.grab_set()
        ctk.CTkLabel(self, text="创建新小说项目", font=FONTS["heading"]).pack(pady=(15, 10))
        ctk.CTkLabel(self, text="项目名称:", font=FONTS["body"]).pack(anchor="w", padx=30, pady=(5, 2))
        self.name_entry = ctk.CTkEntry(self, width=360, font=FONTS["body"])
        self.name_entry.pack(padx=30, pady=2)
        ctk.CTkLabel(self, text="小说类型:", font=FONTS["body"]).pack(anchor="w", padx=30, pady=(8, 2))
        self.genre_entry = ctk.CTkEntry(self, width=360, font=FONTS["body"],
                                         placeholder_text="如：玄幻、都市、科幻、悬疑...")
        self.genre_entry.pack(padx=30, pady=2)
        ctk.CTkLabel(self, text="简介:", font=FONTS["body"]).pack(anchor="w", padx=30, pady=(8, 2))
        self.desc_box = ctk.CTkTextbox(self, width=360, height=80, font=FONTS["body"],
                                        fg_color=COLORS["input_bg"])
        self.desc_box.pack(padx=30, pady=2)
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text="创建", width=100, fg_color=COLORS["accent"],
                       hover_color=COLORS["accent_hover"], command=self._ok).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="取消", width=100, fg_color=COLORS["bg_light"],
                       hover_color=COLORS["text_dim"], command=self.destroy).pack(side="left", padx=5)
        self.name_entry.focus_set()

    def _ok(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("提示", "请输入项目名称")
            return
        genre = self.genre_entry.get().strip()
        desc = self.desc_box.get("1.0", "end-1c").strip()
        self.result = (name, desc, genre, "")
        self.destroy()


class OpenProjectDialog(ctk.CTkToplevel):
    def __init__(self, master, projects):
        super().__init__(master)
        self.title("打开项目")
        self.geometry("400x350")
        self.resizable(False, False)
        self.result = None
        self.projects = projects
        self.transient(master)
        self.grab_set()
        ctk.CTkLabel(self, text="选择项目", font=FONTS["heading"]).pack(pady=(15, 10))
        list_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"])
        list_frame.pack(fill="both", expand=True, padx=20, pady=5)
        self.listbox = ctk.CTkScrollableFrame(list_frame, fg_color=COLORS["bg_dark"])
        self.listbox.pack(fill="both", expand=True, padx=5, pady=5)
        for proj in projects:
            btn = ctk.CTkButton(
                self.listbox,
                text=f"{proj['name']}  ({proj['config'].get('genre', '未分类')})",
                font=FONTS["body"],
                fg_color=COLORS["bg_medium"],
                hover_color=COLORS["accent"],
                anchor="w",
                height=36,
                command=lambda n=proj['name']: self._select(n)
            )
            btn.pack(fill="x", pady=2)
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="删除选中", width=100, fg_color=COLORS["error"],
                       hover_color="#c0392b", command=self._delete).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="取消", width=100, fg_color=COLORS["bg_light"],
                       hover_color=COLORS["text_dim"], command=self.destroy).pack(side="left", padx=5)

    def _select(self, name):
        self.result = name
        self.destroy()

    def _delete(self):
        if not self.result:
            messagebox.showwarning("提示", "请先选择一个项目")
            return
        if messagebox.askyesno("确认", f"确定要删除项目 '{self.result}' 吗？此操作不可撤销。"):
            from core.project_manager import ProjectManager
            import sys
            base = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            pm = ProjectManager(os.path.join(base, "projects"))
            pm.delete_project(self.result)
            self.result = None
            messagebox.showinfo("提示", "项目已删除")
