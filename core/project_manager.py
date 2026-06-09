import os
import json
import shutil
from datetime import datetime

class ProjectManager:
    """管理小说项目：创建、打开、文件结构维护"""

    DEFAULT_STRUCTURE = {
        "chapters": [],
        "roles": [],
        "settings": [],
        "notes": []
    }

    def __init__(self, base_dir="projects"):
        self.base_dir = base_dir
        self.current_project = None
        os.makedirs(base_dir, exist_ok=True)

    def list_projects(self):
        if not os.path.exists(self.base_dir):
            return []
        projects = []
        for name in os.listdir(self.base_dir):
            proj_path = os.path.join(self.base_dir, name)
            config_path = os.path.join(proj_path, "project.json")
            if os.path.isdir(proj_path) and os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                projects.append({"name": name, "path": proj_path, "config": config})
        return projects

    def create_project(self, name, description="", genre="", target_words=""):
        proj_path = os.path.join(self.base_dir, name)
        if os.path.exists(proj_path):
            raise ValueError(f"项目 '{name}' 已存在")
        os.makedirs(proj_path, exist_ok=True)
        for folder in ["chapters", "roles", "settings", "notes"]:
            os.makedirs(os.path.join(proj_path, folder), exist_ok=True)
        config = {
            "name": name,
            "description": description,
            "genre": genre,
            "target_words": target_words,
            "created_at": datetime.now().isoformat(),
            "modified_at": datetime.now().isoformat(),
        }
        with open(os.path.join(proj_path, "project.json"), "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        ctx_path = os.path.join(proj_path, "context_rules.md")
        with open(ctx_path, "w", encoding="utf-8") as f:
            f.write(f"# {name} - 智能上下文规则\n\n")
            f.write(f"## 项目信息\n- 类型: {genre}\n- 简介: {description}\n\n")
            f.write("## 主要角色\n（AI 将自动更新此部分）\n\n")
            f.write("## 世界观设定\n（AI 将自动更新此部分）\n\n")
            f.write("## 剧情记录\n（AI 将自动更新此部分）\n\n")
        outline_path = os.path.join(proj_path, "整体大纲.md")
        with open(outline_path, "w", encoding="utf-8") as f:
            f.write(f"# {name} - 整体大纲\n\n> 请在此处编写小说大纲\n")
        self.current_project = {"name": name, "path": proj_path, "config": config}
        return proj_path

    def open_project(self, name):
        proj_path = os.path.join(self.base_dir, name)
        config_path = os.path.join(proj_path, "project.json")
        if not os.path.exists(config_path):
            raise ValueError(f"项目 '{name}' 不存在")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        self.current_project = {"name": name, "path": proj_path, "config": config}
        return proj_path

    def get_project_files(self, proj_path=None):
        if proj_path is None and self.current_project:
            proj_path = self.current_project["path"]
        if not proj_path or not os.path.exists(proj_path):
            return {}
        result = {}
        for folder in ["chapters", "roles", "settings", "notes"]:
            folder_path = os.path.join(proj_path, folder)
            if os.path.exists(folder_path):
                files = []
                for f in sorted(os.listdir(folder_path)):
                    if f.endswith(".md"):
                        files.append({"name": f, "path": os.path.join(folder_path, f)})
                result[folder] = files
            else:
                result[folder] = []
        root_files = []
        for f in os.listdir(proj_path):
            if f.endswith(".md"):
                root_files.append({"name": f, "path": os.path.join(proj_path, f)})
        result["root"] = root_files
        return result

    def create_file(self, proj_path, folder, filename, content=""):
        if not filename.endswith(".md"):
            filename += ".md"
        file_path = os.path.join(proj_path, folder, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        self._update_modified(proj_path)
        return file_path

    def read_file(self, file_path):
        if not os.path.exists(file_path):
            return ""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def write_file(self, file_path, content):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        if self.current_project:
            self._update_modified(self.current_project["path"])

    def delete_file(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)

    def rename_file(self, old_path, new_name):
        if not new_name.endswith(".md"):
            new_name += ".md"
        new_path = os.path.join(os.path.dirname(old_path), new_name)
        os.rename(old_path, new_path)
        return new_path

    def delete_project(self, name):
        proj_path = os.path.join(self.base_dir, name)
        if os.path.exists(proj_path):
            shutil.rmtree(proj_path)

    def get_context_file(self, proj_path=None):
        if proj_path is None and self.current_project:
            proj_path = self.current_project["path"]
        return os.path.join(proj_path, "context_rules.md") if proj_path else None

    def _update_modified(self, proj_path):
        config_path = os.path.join(proj_path, "project.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            config["modified_at"] = datetime.now().isoformat()
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

    def get_project_stats(self, proj_path=None):
        if proj_path is None and self.current_project:
            proj_path = self.current_project["path"]
        if not proj_path:
            return {}
        total_chars = 0
        total_files = 0
        for folder in ["chapters", "roles", "settings", "notes"]:
            folder_path = os.path.join(proj_path, folder)
            if os.path.exists(folder_path):
                for f in os.listdir(folder_path):
                    if f.endswith(".md"):
                        fpath = os.path.join(folder_path, f)
                        content = self.read_file(fpath)
                        total_chars += len(content)
                        total_files += 1
        return {"total_chars": total_chars, "total_files": total_files}
