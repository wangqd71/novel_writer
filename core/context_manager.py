import os
import re

class ContextManager:
    """智能上下文管理：扫描项目文件，构建AI可用的上下文信息"""

    def __init__(self, project_manager):
        self.pm = project_manager

    def build_full_context(self, proj_path=None):
        """构建完整的项目上下文"""
        if proj_path is None and self.pm.current_project:
            proj_path = self.pm.current_project["path"]
        if not proj_path:
            return ""
        parts = []
        config = self._load_config(proj_path)
        if config:
            parts.append(f"## 项目信息\n- 名称: {config.get('name', '')}\n- 类型: {config.get('genre', '')}\n- 简介: {config.get('description', '')}")
        ctx_content = self._read_context_rules(proj_path)
        if ctx_content:
            parts.append(ctx_content)
        outline = self._read_file(proj_path, "整体大纲.md")
        if outline:
            parts.append(f"## 整体大纲\n{outline}")
        roles = self._read_folder(proj_path, "roles")
        if roles:
            parts.append(f"## 角色设定\n{roles}")
        settings = self._read_folder(proj_path, "settings")
        if settings:
            parts.append(f"## 世界观设定\n{settings}")
        chapters = self._read_chapters_summary(proj_path)
        if chapters:
            parts.append(f"## 已有章节概要\n{chapters}")
        return "\n\n---\n\n".join(parts)

    def build_chapter_context(self, chapter_path, proj_path=None):
        """构建用于续写特定章节的上下文"""
        if proj_path is None and self.pm.current_project:
            proj_path = self.pm.current_project["path"]
        if not proj_path:
            return ""
        parts = []
        config = self._load_config(proj_path)
        if config:
            parts.append(f"小说名称: {config.get('name', '')}，类型: {config.get('genre', '')}")
        roles = self._read_folder(proj_path, "roles")
        if roles:
            parts.append(f"## 角色设定\n{roles}")
        ctx_content = self._read_context_rules(proj_path)
        if ctx_content:
            parts.append(ctx_content)
        chapter_content = self.pm.read_file(chapter_path)
        if chapter_content:
            parts.append(f"## 当前章节内容\n{chapter_content}")
        return "\n\n---\n\n".join(parts)

    def _load_config(self, proj_path):
        import json
        config_path = os.path.join(proj_path, "project.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def _read_context_rules(self, proj_path):
        ctx_path = os.path.join(proj_path, "context_rules.md")
        if os.path.exists(ctx_path):
            return self.pm.read_file(ctx_path)
        return ""

    def _read_file(self, proj_path, filename):
        fpath = os.path.join(proj_path, filename)
        if os.path.exists(fpath):
            return self.pm.read_file(fpath)
        return ""

    def _read_folder(self, proj_path, folder):
        folder_path = os.path.join(proj_path, folder)
        if not os.path.exists(folder_path):
            return ""
        parts = []
        for f in sorted(os.listdir(folder_path)):
            if f.endswith(".md"):
                content = self.pm.read_file(os.path.join(folder_path, f))
                if content.strip():
                    parts.append(content)
        return "\n\n".join(parts)

    def _read_chapters_summary(self, proj_path, max_chars=3000):
        chapters_path = os.path.join(proj_path, "chapters")
        if not os.path.exists(chapters_path):
            return ""
        parts = []
        total = 0
        for f in sorted(os.listdir(chapters_path)):
            if f.endswith(".md"):
                content = self.pm.read_file(os.path.join(chapters_path, f))
                summary = content[:500] + ("..." if len(content) > 500 else "")
                parts.append(f"### {f}\n{summary}")
                total += len(summary)
                if total >= max_chars:
                    parts.append("（更多章节已省略）")
                    break
        return "\n\n".join(parts)

    def extract_characters(self, proj_path=None):
        """提取角色列表"""
        if proj_path is None and self.pm.current_project:
            proj_path = self.pm.current_project["path"]
        if not proj_path:
            return []
        roles_path = os.path.join(proj_path, "roles")
        if not os.path.exists(roles_path):
            return []
        characters = []
        for f in os.listdir(roles_path):
            if f.endswith(".md"):
                name = f.replace(".md", "")
                content = self.pm.read_file(os.path.join(roles_path, f))
                characters.append({"name": name, "content": content})
        return characters
