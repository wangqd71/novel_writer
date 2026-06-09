import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
from ui.style import COLORS, FONTS

class EditorPanel(ctk.CTkFrame):
    """中央编辑面板：Markdown 文本编辑器"""

    def __init__(self, master, on_save=None, **kwargs):
        super().__init__(master, fg_color=COLORS["editor_bg"], **kwargs)
        self.on_save = on_save
        self.current_file = None
        self.is_modified = False
        self._create_widgets()

    def _create_widgets(self):
        self.toolbar = ctk.CTkFrame(self, fg_color=COLORS["bg_medium"], height=40)
        self.toolbar.pack(fill="x")
        self.toolbar.pack_propagate(False)
        self.file_label = ctk.CTkLabel(self.toolbar, text="未打开文件", font=FONTS["small"],
                                        text_color=COLORS["text_secondary"])
        self.file_label.pack(side="left", padx=10)
        self.save_btn = ctk.CTkButton(self.toolbar, text="保存", width=60, height=28,
                                       font=FONTS["small"], fg_color=COLORS["success"],
                                       hover_color="#27ae60", command=self.save_file)
        self.save_btn.pack(side="right", padx=10, pady=5)
        self.char_label = ctk.CTkLabel(self.toolbar, text="0 字", font=FONTS["small"],
                                        text_color=COLORS["text_dim"])
        self.char_label.pack(side="right", padx=5)
        editor_frame = ctk.CTkFrame(self, fg_color="transparent")
        editor_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        self.text_editor = ctk.CTkTextbox(
            editor_frame,
            font=FONTS["editor"],
            fg_color=COLORS["bg_dark"],
            text_color=COLORS["text_primary"],
            corner_radius=6,
            border_width=1,
            border_color=COLORS["border"],
            wrap="word",
            spacing1=2,
            spacing2=2,
            spacing3=4,
        )
        self.text_editor.pack(fill="both", expand=True)
        self.text_editor.bind("<<Modified>>", self._on_modified)
        self.text_editor.bind("<KeyRelease>", self._update_char_count)
        self.text_editor.bind("<Control-s>", lambda e: self.save_file())

    def open_file(self, file_path):
        if self.is_modified and self.current_file:
            if messagebox.askyesno("保存", "当前文件已修改，是否保存？"):
                self.save_file()
        if not os.path.exists(file_path):
            return
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.text_editor.delete("1.0", "end")
        self.text_editor.insert("1.0", content)
        self.current_file = file_path
        self.is_modified = False
        self.text_editor.edit_reset()
        name = os.path.basename(file_path).replace(".md", "")
        self.file_label.configure(text=name, text_color=COLORS["text_primary"])
        self._update_char_count()

    def save_file(self):
        if not self.current_file:
            return
        content = self.text_editor.get("1.0", "end-1c")
        with open(self.current_file, "w", encoding="utf-8") as f:
            f.write(content)
        self.is_modified = False
        self.text_editor.edit_modified(False)
        if self.on_save:
            self.on_save(self.current_file, content)

    def get_content(self):
        return self.text_editor.get("1.0", "end-1c")

    def set_content(self, content):
        self.text_editor.delete("1.0", "end")
        self.text_editor.insert("1.0", content)
        self._update_char_count()

    def insert_text(self, text):
        self.text_editor.insert("end", text)
        self._update_char_count()

    def _on_modified(self, event=None):
        if self.text_editor.edit_modified():
            self.is_modified = True
            name = os.path.basename(self.current_file).replace(".md", "") if self.current_file else "未打开文件"
            self.file_label.configure(text=f"* {name}", text_color=COLORS["warning"])
            self.text_editor.edit_modified(False)

    def _update_char_count(self, event=None):
        content = self.text_editor.get("1.0", "end-1c")
        count = len(content.replace(" ", "").replace("\n", ""))
        self.char_label.configure(text=f"{count} 字")
