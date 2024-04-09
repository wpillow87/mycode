###  需要把logo.jpg放到同目录下。
import tkinter as tk
import os
from PIL import Image, ImageTk
from tkinter import filedialog


def merge_images():
    # 打开图片1（logo.jpg）
    file_path1 = "resources/logo.png"
    image1 = Image.open(file_path1)
    
    # 获取图片2的路径
    file_path2 = filedialog.askopenfilename(title="选择第二个图片文件")
    if not file_path2:
        return
    image2 = Image.open(file_path2)

    # 打开图片2
    image2 = Image.open(file_path2)

    # 调整图片1的大小为图片2大小的1/4
    width, height = image2.size
    new_size = (width // 2, height // 2)
    image1_resized = image1.resize(new_size)

    # 创建一个新的图像对象，大小为图片2的大小，并设置为透明背景
    merged_image = Image.new('RGBA', (width, height), (255, 255, 255, 0))

    # 将图片2复制到新图像的左上角
    merged_image.paste(image2, (0, 0))

    # 计算图片1在图片2右下角的位置
    position = (width - new_size[0], height - new_size[1])

    # 将调整大小后的图片1复制到新图像的右下角
    merged_image.paste(image1_resized, position)

    # 获取图片2的文件名
    file_name2 = os.path.basename(file_path2)

    # 构造合并后的图像文件名
    merged_image_filename = file_name2.split('.')[0] + "liubin.png"

    # 获取图片2所在的目录
    image2_dir = os.path.dirname(file_path2)

    # 保存合并后的图像到图片2所在的目录
    merged_image_path = os.path.join(image2_dir, merged_image_filename)
    merged_image.save(merged_image_path)

    result_label.config(text=f"合并后的图像已保存到 {merged_image_path}")

# 创建主窗口
root = tk.Tk()
root.title("图片合并工具")
root.eval('tk::PlaceWindow %s center' % root.winfo_toplevel())#窗口出现的位置在屏幕中间
#显示图片1
image1 = Image.open("resources/logo.png")
image1 = image1.resize((60, 60))
image1 = ImageTk.PhotoImage(image1)
label1 = tk.Label(root, image=image1)
label1.pack()


# 创建按钮来选择并合并图片
merge_button = tk.Button(root, text="选择要合并的图片", command=merge_images)
merge_button.pack(pady=10)

# 创建标签用于显示操作结果
result_label = tk.Label(root, text="")
result_label.pack(pady=10)

# 运行主循环
root.mainloop()
