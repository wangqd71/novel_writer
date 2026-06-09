import customtkinter as ctk

COLORS = {
    "bg_dark": "#1a1a2e",
    "bg_medium": "#16213e",
    "bg_light": "#0f3460",
    "accent": "#e94560",
    "accent_hover": "#ff6b81",
    "text_primary": "#eaeaea",
    "text_secondary": "#a0a0a0",
    "text_dim": "#666666",
    "success": "#2ecc71",
    "warning": "#f39c12",
    "error": "#e74c3c",
    "border": "#2a2a4a",
    "sidebar_bg": "#1e1e3a",
    "editor_bg": "#1a1a2e",
    "chat_bg": "#16213e",
    "input_bg": "#252547",
    "button_bg": "#e94560",
    "button_hover": "#ff6b81",
    "user_msg_bg": "#2d4a7a",
    "ai_msg_bg": "#1e3a5f",
}

FONTS = {
    "title": ("微软雅黑", 18, "bold"),
    "heading": ("微软雅黑", 14, "bold"),
    "body": ("微软雅黑", 12),
    "small": ("微软雅黑", 10),
    "mono": ("Consolas", 12),
    "editor": ("微软雅黑", 13),
}

FOLDER_LABELS = {
    "root": "项目文件",
    "chapters": "章节",
    "roles": "角色",
    "settings": "设定",
    "notes": "笔记",
}

def apply_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
