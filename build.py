import PyInstaller.__main__
import os
import shutil

base_dir = os.path.dirname(os.path.abspath(__file__))
dist_dir = os.path.join(base_dir, "dist")
build_dir = os.path.join(base_dir, "build")
spec_file = os.path.join(base_dir, "NovelWriter.spec")

args = [
    os.path.join(base_dir, "main.py"),
    "--name=NovelWriter",
    "--onefile",
    "--windowed",
    "--noconfirm",
    "--clean",
    f"--distpath={dist_dir}",
    f"--workpath={build_dir}",
    f"--specpath={base_dir}",
    "--add-data=core;core",
    "--add-data=ui;ui",
    "--hidden-import=customtkinter",
    "--hidden-import=darkdetect",
    "--hidden-import=requests",
    "--hidden-import=PIL",
    "--hidden-import=PIL._tkinter_finder",
    "--hidden-import=urllib3",
    "--hidden-import=certifi",
    "--hidden-import=charset_normalizer",
    "--hidden-import=idna",
    "--collect-all=customtkinter",
    "--collect-all=darkdetect",
]

print("开始打包 NovelWriter...")
print(f"工作目录: {base_dir}")
print(f"输出目录: {dist_dir}")
print()

try:
    PyInstaller.__main__.run(args)
    print()
    exe_path = os.path.join(dist_dir, "NovelWriter.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"打包成功!")
        print(f"可执行文件: {exe_path}")
        print(f"文件大小: {size_mb:.1f} MB")
        final_path = os.path.join(base_dir, "NovelWriter.exe")
        shutil.copy2(exe_path, final_path)
        print(f"已复制到: {final_path}")
    else:
        print("打包失败：未找到生成的可执行文件")
except Exception as e:
    print(f"打包过程中出现错误: {e}")
