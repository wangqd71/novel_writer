import customtkinter as ctk
import threading
from ui.style import COLORS, FONTS

class ChatPanel(ctk.CTkFrame):
    """右侧 AI 对话面板"""

    def __init__(self, master, ai_client=None, context_manager=None, **kwargs):
        super().__init__(master, width=380, fg_color=COLORS["chat_bg"], **kwargs)
        self.ai_client = ai_client
        self.context_manager = context_manager
        self.history = []
        self.pack_propagate(False)
        self._create_widgets()

    def _create_widgets(self):
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_medium"], height=40)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="AI 写作助手", font=FONTS["heading"],
                      text_color=COLORS["text_primary"]).pack(side="left", padx=10)
        self.clear_btn = ctk.CTkButton(header, text="清空", width=50, height=26,
                                        font=FONTS["small"], fg_color=COLORS["bg_light"],
                                        hover_color=COLORS["accent"],
                                        command=self._clear_chat)
        self.clear_btn.pack(side="right", padx=10, pady=7)
        self.context_btn = ctk.CTkButton(header, text="发送上下文", width=80, height=26,
                                          font=FONTS["small"], fg_color=COLORS["bg_light"],
                                          hover_color=COLORS["accent"],
                                          command=self._send_context)
        self.context_btn.pack(side="right", padx=2, pady=7)
        self.chat_display = ctk.CTkTextbox(
            self,
            font=FONTS["body"],
            fg_color=COLORS["bg_dark"],
            text_color=COLORS["text_primary"],
            corner_radius=0,
            border_width=0,
            wrap="word",
            spacing1=4,
            spacing2=2,
            spacing3=4,
            state="disabled"
        )
        self.chat_display.pack(fill="both", expand=True, padx=5, pady=5)
        self.chat_display.tag_config("user_name", foreground=COLORS["accent"])
        self.chat_display.tag_config("ai_name", foreground=COLORS["success"])
        self.chat_display.tag_config("msg_text", foreground=COLORS["text_primary"])
        self.chat_display.tag_config("error_text", foreground=COLORS["error"])
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=5, pady=(0, 8))
        quick_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        quick_frame.pack(fill="x", pady=(0, 4))
        quick_cmds = [
            ("续写", "请帮我续写这个章节，保持风格一致"),
            ("润色", "请帮我润色这段文字，提升文学性"),
            ("大纲", "请帮我设计一个故事大纲"),
            ("角色", "请帮我设计一个角色"),
            ("检查", "请检查当前章节是否有逻辑漏洞"),
        ]
        for label, cmd in quick_cmds:
            btn = ctk.CTkButton(quick_frame, text=label, width=50, height=24,
                                 font=("微软雅黑", 9), fg_color=COLORS["bg_light"],
                                 hover_color=COLORS["accent"],
                                 command=lambda c=cmd: self._set_input(c))
            btn.pack(side="left", padx=1)
        self.input_box = ctk.CTkTextbox(
            input_frame,
            font=FONTS["body"],
            fg_color=COLORS["input_bg"],
            text_color=COLORS["text_primary"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
            height=80,
            wrap="word"
        )
        self.input_box.pack(fill="x", pady=(0, 4))
        self.input_box.bind("<Return>", self._on_enter)
        self.input_box.bind("<Shift-Return>", lambda e: None)
        btn_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        btn_row.pack(fill="x")
        self.send_btn = ctk.CTkButton(
            btn_row, text="发送 (Enter)", height=32,
            font=FONTS["body"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=self._send_message
        )
        self.send_btn.pack(side="right")
        self.status_label = ctk.CTkLabel(btn_row, text="就绪", font=FONTS["small"],
                                          text_color=COLORS["text_dim"])
        self.status_label.pack(side="left", padx=5)

    def set_ai_client(self, client):
        self.ai_client = client

    def set_context_manager(self, cm):
        self.context_manager = cm

    def _set_input(self, text):
        self.input_box.delete("1.0", "end")
        self.input_box.insert("1.0", text)
        self.input_box.focus_set()

    def _on_enter(self, event):
        if not event.state & 0x1:
            self._send_message()
            return "break"

    def _send_message(self):
        user_msg = self.input_box.get("1.0", "end-1c").strip()
        if not user_msg:
            return "break"
        self.input_box.delete("1.0", "end")
        self._append_message("你", user_msg, "user_name")
        self.history.append({"role": "user", "content": user_msg})
        self._start_ai_response(user_msg)
        return "break"

    def _send_context(self):
        if not self.context_manager:
            self._append_message("系统", "请先打开一个项目", "error_text")
            return
        ctx = self.context_manager.build_full_context()
        if ctx:
            self.input_box.delete("1.0", "end")
            self.input_box.insert("1.0", f"请基于以下上下文帮助我创作：\n\n{ctx[:3000]}")
            self.input_box.focus_set()
        else:
            self._append_message("系统", "项目上下文为空", "error_text")

    def _start_ai_response(self, user_msg):
        if not self.ai_client or not self.ai_client.api_key:
            self._append_message("AI", "请先在设置中配置 API Key（菜单 → 设置）", "error_text")
            return
        self.send_btn.configure(state="disabled", text="生成中...")
        self.status_label.configure(text="AI 正在思考...", text_color=COLORS["warning"])
        ctx_messages = None
        if self.context_manager and self.context_manager.pm.current_project:
            ctx = self.context_manager.build_full_context()
            if ctx:
                ctx_messages = ctx
        messages = self.ai_client.build_writing_context(ctx_messages, user_msg, self.history[:-1])

        def stream_callback(token):
            self.after(0, lambda: self._append_stream_token(token))

        def do_request():
            try:
                result = self.ai_client.chat(messages, callback=stream_callback)
                self.after(0, lambda: self._finish_response(result))
            except Exception as e:
                self.after(0, lambda: self._finish_response(f"错误: {str(e)}", is_error=True))

        self._current_response = ""
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", "\nAI: ", "ai_name")
        self.chat_display.configure(state="disabled")
        threading.Thread(target=do_request, daemon=True).start()

    def _append_stream_token(self, token):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", token, "msg_text")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")
        self._current_response += token

    def _finish_response(self, result, is_error=False):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", "\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")
        if not is_error and result:
            self.history.append({"role": "assistant", "content": result})
        self.send_btn.configure(state="normal", text="发送 (Enter)")
        self.status_label.configure(text="就绪", text_color=COLORS["text_dim"])

    def _append_message(self, sender, message, tag):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"\n{sender}: {message}\n\n", tag)
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def _clear_chat(self):
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.configure(state="disabled")
        self.history.clear()

    def show_message(self, sender, message, tag="msg_text"):
        self._append_message(sender, message, tag)
