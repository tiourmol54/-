import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import os
import subprocess
import threading
import random
import sys
import ctypes  # <--- 引入这个库用来隐藏文件

# ================= 配置区域 =================
DEFAULT_IMAGE_FOLDER = r"D:\\料号"
# ===========================================

# --- 手机版代码模板 ---
MOBILE_CODE_TEMPLATE = '''
import streamlit as st
import os
from PIL import Image

IMAGE_FOLDER = r"D:\\料号"

st.set_page_config(page_title="工厂查图手机版", layout="centered")
st.title("🏭 工厂物料查询系统")
st.write(f"图库路径：{IMAGE_FOLDER}")

if not os.path.exists(IMAGE_FOLDER):
    st.error(f"❌ 找不到文件夹 {IMAGE_FOLDER}")
    st.stop()

part_number = st.text_input("🔍 输入料号 (回车搜索)：", "")

if part_number:
    part_number = part_number.strip()
    extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.webp', '.JPG', '.PNG', '.WEBP']
    found_path = None
    for ext in extensions:
        temp_path = os.path.join(IMAGE_FOLDER, part_number + ext)
        if os.path.exists(temp_path):
            found_path = temp_path
            break

    if found_path:
        st.success(f"✅ 找到：{part_number}")
        try:
            image = Image.open(found_path)
            st.image(image, caption=f"文件名: {os.path.basename(found_path)}", use_column_width="auto")
        except Exception as e:
            st.error(f"图片损坏: {e}")
    else:
        st.error(f"❌ 未找到：{part_number}")
'''


class FactorySystem:
    def __init__(self, root):
        self.root = root
        self.root.title("工厂图纸总控系统 (隐形版)")
        self.root.geometry("900x700")

        self.image_folder = DEFAULT_IMAGE_FOLDER
        self.current_image_path = None

        # === 顶部工具栏 ===
        frame_tools = tk.Frame(root, bg="#f0f0f0", pady=5)
        frame_tools.pack(side=tk.TOP, fill=tk.X)

        tk.Label(frame_tools, text="🔧 工具箱:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)

        btn_folder = tk.Button(frame_tools, text="📂 更改文件夹", command=self.select_folder, bg="white")
        btn_folder.pack(side=tk.LEFT, padx=5)

        btn_gen = tk.Button(frame_tools, text="🎨 生成测试图片", command=self.generate_samples, bg="#fff8dc")
        btn_gen.pack(side=tk.LEFT, padx=5)

        btn_mobile = tk.Button(
            frame_tools,
            text="📱 启动手机模式",
            command=self.launch_mobile_mode,
            bg="#e6f7ff",
            fg="#0056b3",
        )
        btn_mobile.pack(side=tk.RIGHT, padx=10)

        # === 核心操作区 ===
        frame_main = tk.Frame(root, pady=10)
        frame_main.pack(side=tk.TOP, fill=tk.X)

        tk.Label(frame_main, text="输入料号:", font=("Arial", 16, "bold")).pack(side=tk.LEFT, padx=15)

        self.entry_code = tk.Entry(frame_main, font=("Arial", 16), width=20, bd=2)
        self.entry_code.pack(side=tk.LEFT, padx=5)
        self.entry_code.bind('<Return>', self.search_image)

        btn_search = tk.Button(
            frame_main,
            text="🔍 立即查找",
            command=self.search_image,
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            height=1,
        )
        btn_search.pack(side=tk.LEFT, padx=15)

        # === 信息显示区 ===
        self.lbl_info = tk.Label(root, text="准备就绪", font=("微软雅黑", 20, "bold"), fg="#666666")
        self.lbl_info.pack(pady=(10, 0))

        self.lbl_hint = tk.Label(root, text="( 双击图片可查看原图 )", font=("Arial", 9), fg="#888888")
        self.lbl_hint.pack(pady=(0, 5))

        # === 图片显示区 ===
        self.label_image = tk.Label(root, text="", bg="#eeeeee", cursor="hand2")
        self.label_image.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        self.label_image.bind('<Double-1>', self.open_external_image)

        # === 底部状态栏 ===
        self.lbl_status = tk.Label(root, text=f"当前图库: {self.image_folder}", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.lbl_status.pack(side=tk.BOTTOM, fill=tk.X)

        self.check_folder()

    def check_folder(self):
        if not os.path.exists(self.image_folder):
            self.lbl_info.config(text="⚠️ 文件夹不存在", fg="red")
            self.lbl_hint.config(text="请点击上方【生成测试图片】或【更改文件夹】", fg="red")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.image_folder = folder
            self.lbl_status.config(text=f"当前图库: {folder}")
            messagebox.showinfo("成功", "图库路径已更新")

    def search_image(self, event=None):
        part_number = self.entry_code.get().strip()
        self.entry_code.delete(0, tk.END)

        if not part_number:
            return

        if not os.path.exists(self.image_folder):
            messagebox.showerror("错误", "图库文件夹不存在")
            return

        self.lbl_info.config(text=f"正在查找 {part_number} ...", fg="black")
        self.current_image_path = None

        extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.webp', '.JPG', '.PNG', '.WEBP']
        found = False

        for ext in extensions:
            temp_path = os.path.join(self.image_folder, part_number + ext)
            if os.path.exists(temp_path):
                self.current_image_path = temp_path
                self.display_image(temp_path)
                self.lbl_info.config(text=f"✅ 料号：{part_number}", fg="#0056b3")
                found = True
                break

        if not found:
            self.label_image.config(image='', text="❌ 无此图片", fg="#999")
            self.lbl_info.config(text=f"❌ 未找到：{part_number}", fg="red")

    def display_image(self, path):
        try:
            pil_image = Image.open(path)
            w = self.root.winfo_width() - 60
            h = self.root.winfo_height() - 250
            if w < 100:
                w = 800
            if h < 100:
                h = 600

            pil_image.thumbnail((w, h))
            self.tk_image = ImageTk.PhotoImage(pil_image)
            self.label_image.config(image=self.tk_image, text="")
        except Exception as e:
            self.lbl_info.config(text="图片无法读取", fg="red")

    def open_external_image(self, event):
        if self.current_image_path:
            try:
                os.startfile(self.current_image_path)
            except:
                pass

    def generate_samples(self):
        target_dir = self.image_folder
        if not os.path.exists(target_dir):
            try:
                os.makedirs(target_dir)
            except:
                return

        codes = ["1001", "1002", "A-888", "B-666", "X-999"]
        for code in codes:
            fpath = os.path.join(target_dir, f"{code}.jpg")
            if not os.path.exists(fpath):
                color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
                img = Image.new('RGB', (600, 400), color)
                draw = ImageDraw.Draw(img)
                draw.rectangle([150, 100, 450, 300], outline="white", width=5)
                draw.text((20, 20), f"SAMPLE: {code}", fill="white")
                img.save(fpath)
        messagebox.showinfo("完成", f"测试图片已生成在 {target_dir}")

    def launch_mobile_mode(self):
        mobile_script_name = "mobile_server_temp.py"
        try:
            # 1. 生成文件
            with open(mobile_script_name, "w", encoding="utf-8") as f:
                f.write(MOBILE_CODE_TEMPLATE)

            # 2. 【核心魔法】将文件设置为“隐藏”属性 (Windows系统)
            # 0x02 是隐藏属性的代码
            ctypes.windll.kernel32.SetFileAttributesW(mobile_script_name, 0x02)

        except Exception as e:
            messagebox.showerror("文件错误", f"无法生成文件: {e}")
            return

        def run_server():
            cmd = f"python -m streamlit run {mobile_script_name}"
            subprocess.run(cmd, shell=True)

        if messagebox.askyesno("启动", "即将启动手机版，请勿关闭黑框窗口。\n是否继续？"):
            t = threading.Thread(target=run_server)
            t.daemon = True
            t.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = FactorySystem(root)
    root.mainloop()
