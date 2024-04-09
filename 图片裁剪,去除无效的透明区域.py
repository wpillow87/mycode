import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Radiobutton
from PIL import Image
import datetime

def crop_and_resize_images(input_folder, output_folder, time_range, target_height=500):
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 获取输入文件夹中的所有图片文件
    image_files = [f for f in os.listdir(input_folder) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    # 计算时间范围
    now = datetime.datetime.now()
    if time_range == "最近30分钟":
        start_time = now - datetime.timedelta(minutes=30)
    elif time_range == "最近1小时":
        start_time = now - datetime.timedelta(hours=1)
    else:
        start_time = datetime.datetime.min

    for image_file in image_files:
        # 构建输入文件的完整路径
        input_path = os.path.join(input_folder, image_file)

        # 获取文件创建时间
        creation_time = datetime.datetime.fromtimestamp(os.path.getctime(input_path))

        # 检查是否在所选时间范围内
        if start_time <= creation_time <= now:
            # 构建输出文件的完整路径
            output_path = os.path.join(output_folder, image_file)

            # 打开图片
            img = Image.open(input_path)

            # 找到非空白区域的边界
            bbox = img.getbbox()

            # 裁剪图片以删除空白
            img = img.crop(bbox)

            # 计算缩放比例以保持宽高比
            width, height = img.size
            aspect_ratio = width / height
            target_width = int(target_height * aspect_ratio)

            # 缩放图片，使用BILINEAR作为滤波器
            img = img.resize((target_width, target_height), Image.BILINEAR)

            # 保存结果图片
            img.save(output_path)

    # 处理完成后，弹出提示消息框
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
    time_range = selected_time.get()
    crop_and_resize_images(input_folder, output_folder, time_range)
    root.destroy()

# 创建主窗口
root = tk.Tk()
root.title("时间选择器")
root.geometry("300x300")  # 窗口大小为300*300
root.eval('tk::PlaceWindow %s center' % root.winfo_toplevel())  # 窗口出现的位置在屏幕中间

# 创建输入文件夹路径文本框
input_folder_entry = tk.Entry(root)
input_folder_entry.pack()

# 创建选择输入文件夹按钮
input_folder_button = tk.Button(root, text="选择输入文件夹", command=choose_input_folder)
input_folder_button.pack()

# 创建输出文件夹路径文本框
output_folder_entry = tk.Entry(root)
output_folder_entry.pack()

# 创建选择输出文件夹按钮
output_folder_button = tk.Button(root, text="选择输出文件夹", command=choose_output_folder)
output_folder_button.pack()

# 创建时间范围选择器
time_range_label = tk.Label(root, text="选择时间范围:")
time_range_label.pack()

selected_time = tk.StringVar(value="最近30分钟")

radiobutton1 = Radiobutton(root, text="最近30分钟", value="最近30分钟", variable=selected_time)
radiobutton1.pack()

radiobutton2 = Radiobutton(root, text="最近1小时", value="最近1小时", variable=selected_time)
radiobutton2.pack()

radiobutton3 = Radiobutton(root, text="所有时间", value="所有时间", variable=selected_time)
radiobutton3.pack()

# 创建运行按钮
run_button = tk.Button(root, text="运行", command=run_program)
run_button.pack()

# 默认文件夹为桌面
input_folder_entry.insert(0, os.path.expanduser("~/Desktop"))
output_folder_entry.insert(0, os.path.expanduser("~/Desktop"))

# 运行主循环
root.mainloop()
