import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Radiobutton
from PIL import Image
import datetime

def convert_image(input_path, output_path, target_format):
    """转换图片格式"""
    try:
        img = Image.open(input_path)
        # 保持透明通道
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            img = img.convert('RGBA')
        else:
            img = img.convert('RGB')
        img.save(output_path, target_format.upper())
    except Exception as e:
        print(f"转换 {input_path} 时出错: {str(e)}")

def process_images(input_folder, output_folder, target_format, target_size=None):
    """处理所有图片"""
    os.makedirs(output_folder, exist_ok=True)
    image_files = [f for f in os.listdir(input_folder) 
                  if f.lower().endswith(('.svg', '.ico', '.jpg', '.jpeg', '.gif', '.png'))]
    
    for image_file in image_files:
        input_path = os.path.join(input_folder, image_file)
        output_filename = os.path.splitext(image_file)[0] + f'.{target_format}'
        output_path = os.path.join(output_folder, output_filename)
        
        img = Image.open(input_path)
        
        # 确保图片有透明通道
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # 裁剪空白区域
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)

        if target_size and target_size != "original":
            target_size = int(target_size)
            # 计算缩放尺寸，保持比例
            width, height = img.size
            ratio = min(target_size/width, target_size/height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)

            # 创建新的透明画布
            new_img = Image.new('RGBA', (target_size, target_size), (0, 0, 0, 0))
            
            # 缩放原图
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # 将缩放后的图片居中放置
            x = (target_size - new_width) // 2
            y = (target_size - new_height) // 2
            new_img.paste(resized_img, (x, y))
            img = new_img

        img.save(output_path, target_format.upper())

    messagebox.showinfo("完成", "图片处理完成！")

def choose_input_folder():
    input_folder = filedialog.askdirectory(title="选择输入文件夹")
    input_folder_entry.delete(0, tk.END)
    input_folder_entry.insert(0, input_folder)

def choose_output_folder():
    output_folder = filedialog.askdirectory(title="选择输出文件夹")
    output_folder_entry.delete(0, tk.END)
    output_folder_entry.insert(0, output_folder)

def run_program():
    input_folder = input_folder_entry.get()
    output_folder = output_folder_entry.get()
    target_size = selected_size.get()
    target_format = selected_format.get()
    process_images(input_folder, output_folder, target_format, target_size)
    root.destroy()

# 创建主窗口
root = tk.Tk()
root.title("图标标准化")
root.geometry("500x300")
root.eval('tk::PlaceWindow %s center' % root.winfo_toplevel())
root.resizable(False, False)

# 创建左右两个主Frame
left_frame = tk.Frame(root, padx=20, pady=20)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

right_frame = tk.Frame(root, padx=20, pady=20)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# 左侧Frame - 文件夹选择
folder_label = tk.Label(left_frame, text="文件夹选择", font=('Arial', 12, 'bold'))
folder_label.pack(pady=(0, 20))

# 输入文件夹
input_frame = tk.Frame(left_frame)
input_frame.pack(fill=tk.X, pady=(0, 10))
tk.Label(input_frame, text="输入文件夹:").pack(anchor=tk.W)
input_folder_entry = tk.Entry(input_frame)
input_folder_entry.pack(fill=tk.X, pady=(5, 5))
input_folder_button = tk.Button(input_frame, text="浏览", command=choose_input_folder)
input_folder_button.pack()

# 输出文件夹
output_frame = tk.Frame(left_frame)
output_frame.pack(fill=tk.X, pady=(10, 0))
tk.Label(output_frame, text="输出文件夹:").pack(anchor=tk.W)
output_folder_entry = tk.Entry(output_frame)
output_folder_entry.pack(fill=tk.X, pady=(5, 5))
output_folder_button = tk.Button(output_frame, text="浏览", command=choose_output_folder)
output_folder_button.pack()

# 右侧Frame - 选项设置
options_label = tk.Label(right_frame, text="选项设置", font=('Arial', 12, 'bold'))
options_label.pack(pady=(0, 20))

# 格式选择
format_frame = tk.Frame(right_frame)
format_frame.pack(fill=tk.X, pady=(0, 20))
format_label = tk.Label(format_frame, text="输出格式:")
format_label.pack(anchor=tk.W)

selected_format = tk.StringVar(value="png")
format_radio1 = Radiobutton(format_frame, text="PNG", value="png", variable=selected_format)
format_radio1.pack(anchor=tk.W)
format_radio2 = Radiobutton(format_frame, text="ICO", value="ico", variable=selected_format)
format_radio2.pack(anchor=tk.W)

# 尺寸选择
size_frame = tk.Frame(right_frame)
size_frame.pack(fill=tk.X)
size_label = tk.Label(size_frame, text="目标尺寸:")
size_label.pack(anchor=tk.W)

selected_size = tk.StringVar(value="64")
size_radio1 = Radiobutton(size_frame, text="256x256", value="256", variable=selected_size)
size_radio1.pack(anchor=tk.W)
size_radio2 = Radiobutton(size_frame, text="64x64", value="64", variable=selected_size)
size_radio2.pack(anchor=tk.W)
size_radio3 = Radiobutton(size_frame, text="32x32", value="32", variable=selected_size)
size_radio3.pack(anchor=tk.W)
size_radio4 = Radiobutton(size_frame, text="原始大小", value="original", variable=selected_size)
size_radio4.pack(anchor=tk.W)

# 运行按钮
run_button = tk.Button(root, text="开始处理", command=run_program, width=20, height=2)
run_button.pack(side=tk.BOTTOM, pady=20)

# 设置默认文件夹
default_input_folder = os.path.expanduser("~/Desktop")
default_output_folder = os.path.join(os.path.expanduser("~/Desktop"), "图标标准化")
os.makedirs(default_output_folder, exist_ok=True)

input_folder_entry.insert(0, default_input_folder)
output_folder_entry.insert(0, default_output_folder)

# 运行主循环
root.mainloop()
