import customtkinter as ctk
import json
import os
from ui.style import COLORS, FONTS

class SettingsDialog(ctk.CTkToplevel):
    """设置对话框：API 配置"""

    def __init__(self, master, current_config=None, on_save=None):
        super().__init__(master)
        self.title("设置")
        self.geometry("520x500")
        self.resizable(False, False)
        self.on_save = on_save
        self.current_config = current_config or {}
        self.transient(master)
        self.grab_set()
        self._create_widgets()

    def _create_widgets(self):
        ctk.CTkLabel(self, text="AI 模型配置", font=FONTS["heading"]).pack(pady=(15, 10))
        tabview = ctk.CTkTabview(self, width=480, height=340,
                                  fg_color=COLORS["bg_dark"],
                                  segmented_button_fg_color=COLORS["bg_medium"],
                                  segmented_button_selected_color=COLORS["accent"])
        tabview.pack(padx=20, pady=5, fill="both", expand=True)
        tab1 = tabview.add("基础配置")
        tab2 = tabview.add("高级配置")
        ctk.CTkLabel(tab1, text="API Key:", font=FONTS["body"]).pack(anchor="w", padx=20, pady=(15, 2))
        self.api_key_entry = ctk.CTkEntry(tab1, width=420, font=FONTS["body"],
                                           show="*", placeholder_text="输入你的 API Key")
        self.api_key_entry.pack(padx=20, pady=2)
        if self.current_config.get("api_key"):
            self.api_key_entry.insert(0, self.current_config["api_key"])
        ctk.CTkLabel(tab1, text="API 基础地址:", font=FONTS["body"]).pack(anchor="w", padx=20, pady=(12, 2))
        self.base_url_entry = ctk.CTkEntry(tab1, width=420, font=FONTS["body"],
                                            placeholder_text="https://api.deepseek.com/v1")
        self.base_url_entry.pack(padx=20, pady=2)
        if self.current_config.get("base_url"):
            self.base_url_entry.insert(0, self.current_config["base_url"])
        ctk.CTkLabel(tab1, text="模型名称:", font=FONTS["body"]).pack(anchor="w", padx=20, pady=(12, 2))
        preset_frame = ctk.CTkFrame(tab1, fg_color="transparent")
        preset_frame.pack(fill="x", padx=20, pady=2)
        presets = [
            ("MiMo", "https://token-plan-cn.xiaomimimo.com/v1", "mimo-v2.5-pro"),
            ("DeepSeek", "https://api.deepseek.com/v1", "deepseek-chat"),
            ("千问", "https://dashscope.aliyuncs.com/compatible-mode/v1", "qwen-plus"),
            ("OpenAI", "https://api.openai.com/v1", "gpt-4o"),
        ]
        for name, url, model in presets:
            ctk.CTkButton(preset_frame, text=name, width=80, height=26, font=FONTS["small"],
                           fg_color=COLORS["bg_light"], hover_color=COLORS["accent"],
                           command=lambda u=url, m=model, n=name: self._set_preset(u, m, n)
                           ).pack(side="left", padx=2)
        self.model_entry = ctk.CTkEntry(tab1, width=420, font=FONTS["body"],
                                         placeholder_text="deepseek-chat")
        self.model_entry.pack(padx=20, pady=(4, 2))
        if self.current_config.get("model"):
            self.model_entry.insert(0, self.current_config["model"])
        ctk.CTkLabel(tab2, text="Temperature (创造性 0-1):", font=FONTS["body"]).pack(anchor="w", padx=20, pady=(15, 2))
        self.temp_slider = ctk.CTkSlider(tab2, from_=0, to=1, number_of_steps=20,
                                          width=420)
        self.temp_slider.pack(padx=20, pady=2)
        self.temp_slider.set(self.current_config.get("temperature", 0.8))
        self.temp_label = ctk.CTkLabel(tab2, text=f"当前值: {self.current_config.get('temperature', 0.8)}",
                                         font=FONTS["small"])
        self.temp_label.pack(padx=20)
        self.temp_slider.configure(command=lambda v: self.temp_label.configure(text=f"当前值: {v:.2f}"))
        ctk.CTkLabel(tab2, text="最大 Token 数:", font=FONTS["body"]).pack(anchor="w", padx=20, pady=(12, 2))
        self.max_tokens_entry = ctk.CTkEntry(tab2, width=420, font=FONTS["body"])
        self.max_tokens_entry.pack(padx=20, pady=2)
        self.max_tokens_entry.insert(0, str(self.current_config.get("max_tokens", 4096)))
        ctk.CTkLabel(tab2, text="自定义系统提示词:", font=FONTS["body"]).pack(anchor="w", padx=20, pady=(12, 2))
        self.system_prompt_box = ctk.CTkTextbox(tab2, width=420, height=100, font=FONTS["small"],
                                                  fg_color=COLORS["input_bg"])
        self.system_prompt_box.pack(padx=20, pady=2)
        sp = self.current_config.get("system_prompt", "")
        if sp:
            self.system_prompt_box.insert("1.0", sp)
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text="测试连接", width=100, fg_color=COLORS["bg_light"],
                       hover_color=COLORS["warning"], command=self._test_connection).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="保存", width=100, fg_color=COLORS["accent"],
                       hover_color=COLORS["accent_hover"], command=self._save).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="取消", width=100, fg_color=COLORS["bg_light"],
                       hover_color=COLORS["text_dim"], command=self.destroy).pack(side="left", padx=5)
        self.test_label = ctk.CTkLabel(self, text="", font=FONTS["small"])
        self.test_label.pack(pady=(0, 10))

    def _set_preset(self, url, model, name):
        self.base_url_entry.delete(0, "end")
        self.base_url_entry.insert(0, url)
        self.model_entry.delete(0, "end")
        self.model_entry.insert(0, model)

    def _test_connection(self):
        from core.ai_client import AIClient
        config = self._get_config()
        client = AIClient(config)
        self.test_label.configure(text="测试中...", text_color=COLORS["warning"])
        self.update()
        import threading
        def do_test():
            ok, msg = client.test_connection()
            self.after(0, lambda: self._show_test_result(ok, msg))
        threading.Thread(target=do_test, daemon=True).start()

    def _show_test_result(self, ok, msg):
        if ok:
            self.test_label.configure(text=f"✓ {msg}", text_color=COLORS["success"])
        else:
            self.test_label.configure(text=f"✗ {msg}", text_color=COLORS["error"])

    def _get_config(self):
        try:
            max_tokens = int(self.max_tokens_entry.get())
        except ValueError:
            max_tokens = 4096
        sp = self.system_prompt_box.get("1.0", "end-1c").strip()
        return {
            "api_key": self.api_key_entry.get().strip(),
            "base_url": self.base_url_entry.get().strip() or "https://api.deepseek.com/v1",
            "model": self.model_entry.get().strip() or "deepseek-chat",
            "temperature": self.temp_slider.get(),
            "max_tokens": max_tokens,
            "system_prompt": sp if sp else None,
        }

    def _save(self):
        config = self._get_config()
        if self.on_save:
            self.on_save(config)
        self.destroy()
