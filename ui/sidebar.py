import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import os
from ui.style import COLORS, FONTS, FOLDER_LABELS

class Sidebar(ctk.CTkFrame):
    """左侧项目文件树"""

    def __init__(self, master, on_file_select=None, **kwargs):
        super().__init__(master, width=260, fg_color=COLORS["sidebar_bg"], **kwargs)
        self.on_file_select = on_file_select
        self.current_project_path = None
        self.file_map = {}
        self.pack_propagate(False)
        self._create_widgets()

    def _create_widgets(self):
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(title_frame, text="项目结构", font=FONTS["heading"],
                      text_color=COLORS["text_primary"]).pack(side="left")
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 5))
        self.new_file_btn = ctk.CTkButton(btn_frame, text="+ 新建文件", width=100, height=28,
                                           font=FONTS["small"], fg_color=COLORS["accent"],
                                           hover_color=COLORS["accent_hover"],
                                           command=self._on_new_file)
        self.new_file_btn.pack(side="left", padx=(0, 5))
        self.refresh_btn = ctk.CTkButton(btn_frame, text="刷新", width=60, height=28,
                                          font=FONTS["small"], fg_color=COLORS["bg_light"],
                                          hover_color=COLORS["accent"],
                                          command=self._refresh_tree)
        self.refresh_btn.pack(side="left")
        tree_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=6)
        tree_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                         background=COLORS["bg_dark"],
                         foreground=COLORS["text_primary"],
                         fieldbackground=COLORS["bg_dark"],
                         borderwidth=0,
                         font=FONTS["small"],
                         rowheight=28)
        style.configure("Custom.Treeview.Indent", indent=16)
        style.map("Custom.Treeview",
                   background=[("selected", COLORS["accent"])],
                   foreground=[("selected", "white")])
        style.configure("Custom.Treeview",
                         background=COLORS["bg_dark"],
                         foreground=COLORS["text_primary"])
        self.tree = ttk.Treeview(tree_frame, style="Custom.Treeview", selectmode="browse")
        self.tree.pack(fill="both", expand=True, padx=2, pady=2)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Button-3>", self._on_right_click)

    def load_project(self, project_path):
        self.current_project_path = project_path
        self._refresh_tree()

    def _refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.file_map.clear()
        if not self.current_project_path or not os.path.exists(self.current_project_path):
            return
        proj_name = os.path.basename(self.current_project_path)
        root_node = self.tree.insert("", "end", text=f" {proj_name}", open=True)
        self.file_map[root_node] = {"type": "folder", "path": self.current_project_path}
        for folder_key in ["chapters", "roles", "settings", "notes"]:
            folder_path = os.path.join(self.current_project_path, folder_key)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path, exist_ok=True)
                continue
            label = FOLDER_LABELS.get(folder_key, folder_key)
            folder_node = self.tree.insert(root_node, "end", text=f" {label}", open=(folder_key == "chapters"))
            self.file_map[folder_node] = {"type": "folder", "path": folder_path}
            for fname in sorted(os.listdir(folder_path)):
                if fname.endswith(".md"):
                    display_name = fname.replace(".md", "")
                    file_node = self.tree.insert(folder_node, "end", text=f" {display_name}")
                    self.file_map[file_node] = {"type": "file", "path": os.path.join(folder_path, fname)}
        for fname in sorted(os.listdir(self.current_project_path)):
            if fname.endswith(".md"):
                display_name = fname.replace(".md", "")
                file_node = self.tree.insert(root_node, "end", text=f" {display_name}")
                self.file_map[file_node] = {"type": "file", "path": os.path.join(self.current_project_path, fname)}

    def _on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        node_id = selection[0]
        info = self.file_map.get(node_id)
        if info and info["type"] == "file" and self.on_file_select:
            self.on_file_select(info["path"])

    def _on_new_file(self):
        if not self.current_project_path:
            messagebox.showwarning("提示", "请先打开或创建一个项目")
            return
        dialog = NewFileDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            name, folder = dialog.result
            if not name.endswith(".md"):
                name += ".md"
            folder_path = os.path.join(self.current_project_path, folder)
            os.makedirs(folder_path, exist_ok=True)
            file_path = os.path.join(folder_path, name)
            if os.path.exists(file_path):
                messagebox.showwarning("提示", f"文件 '{name}' 已存在")
                return
            from ui.style import FOLDER_LABELS
            folder_label = FOLDER_LABELS.get(folder, folder)
            templates = {
                "chapters": f"# {name.replace('.md', '')}\n\n> 开始写作...\n",
                "roles": f"# 角色：{name.replace('.md', '')}\n\n## 基本信息\n- 姓名: \n- 性别: \n- 年龄: \n- 身份: \n\n## 外貌特征\n\n\n## 性格特征\n\n\n## 能力成长\n\n\n## 关系网络\n\n",
                "settings": f"# 设定：{name.replace('.md', '')}\n\n> 在此编写世界观设定...\n",
                "notes": f"# 笔记：{name.replace('.md', '')}\n\n> 在此记录灵感和笔记...\n",
            }
            content = templates.get(folder, f"# {name.replace('.md', '')}\n\n")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            self._refresh_tree()
            if self.on_file_select:
                self.on_file_select(file_path)

    def _on_right_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        self.tree.selection_set(item)
        info = self.file_map.get(item)
        if not info or info["type"] != "file":
            return
        menu = tk.Menu(self, tearoff=0, bg=COLORS["bg_medium"], fg=COLORS["text_primary"],
                        activebackground=COLORS["accent"], activeforeground="white",
                        font=FONTS["small"])
        menu.add_command(label="删除", command=lambda: self._delete_file(item, info["path"]))
        menu.add_command(label="重命名", command=lambda: self._rename_file(item, info["path"]))
        menu.tk_popup(event.x_root, event.y_root)

    def _delete_file(self, node, path):
        if messagebox.askyesno("确认", f"确定要删除文件吗？"):
            os.remove(path)
            self._refresh_tree()

    def _rename_file(self, node, path):
        old_name = os.path.basename(path).replace(".md", "")
        new_name = simpledialog.askstring("重命名", "输入新名称:", initialvalue=old_name)
        if new_name and new_name != old_name:
            if not new_name.endswith(".md"):
                new_name += ".md"
            new_path = os.path.join(os.path.dirname(path), new_name)
            os.rename(path, new_path)
            self._refresh_tree()


class NewFileDialog(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("新建文件")
        self.geometry("360x260")
        self.resizable(False, False)
        self.result = None
        self.transient(master)
        self.grab_set()
        ctk.CTkLabel(self, text="文件名称:", font=FONTS["body"]).pack(pady=(20, 5))
        self.name_entry = ctk.CTkEntry(self, width=280, font=FONTS["body"])
        self.name_entry.pack(pady=5)
        ctk.CTkLabel(self, text="存放位置:", font=FONTS["body"]).pack(pady=(15, 5))
        self.folder_var = ctk.StringVar(value="chapters")
        folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        folder_frame.pack(pady=5)
        for key, label in [("chapters", "章节"), ("roles", "角色"), ("settings", "设定"), ("notes", "笔记")]:
            ctk.CTkRadioButton(folder_frame, text=label, variable=self.folder_var,
                                value=key, font=FONTS["small"]).pack(side="left", padx=5)
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
            return
        self.result = (name, self.folder_var.get())
        self.destroy()
