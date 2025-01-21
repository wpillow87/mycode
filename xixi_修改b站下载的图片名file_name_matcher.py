import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import re

class FileNameMatcher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("文件名匹配工具")
        self.root.geometry("1200x800")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 初始化当前文件夹路径
        self.current_folder = os.path.dirname(os.path.abspath(__file__))
        
        # 存储文件对信息
        self.file_pairs = []
        
        # 创建文件对比区域
        self.create_comparison_area()
        
        # 创建字符替换区域
        self.create_replacement_area()
        
    def create_comparison_area(self):
        # 文件夹选择区域
        folder_frame = ttk.Frame(self.main_frame)
        folder_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        self.folder_path_var = tk.StringVar(value=self.current_folder)
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path_var, width=80)
        folder_entry.grid(row=0, column=0, padx=5)
        
        ttk.Button(folder_frame, text="选择文件夹", command=self.choose_folder).grid(row=0, column=1, padx=5)
        
        # 文件对比区域标题
        ttk.Label(self.main_frame, text="文件名匹配", font=('Arial', 12, 'bold')).grid(row=1, column=0, pady=10)
        
        # 创建Treeview来显示文件对
        columns = ('序号', '选择', '图片文件名', '选择', '视频文件名')
        self.tree = ttk.Treeview(self.main_frame, columns=columns, show='headings', height=20)
        
        # 设置列标题和宽度
        self.tree.heading('序号', text='序号')
        self.tree.column('序号', width=60, anchor='center')
        
        self.tree.heading('选择', text='')
        self.tree.column('选择', width=30, anchor='center')
        
        self.tree.heading('图片文件名', text='图片文件名')
        self.tree.column('图片文件名', width=450)
        
        self.tree.heading('选择', text='')
        self.tree.column('选择', width=30, anchor='center')
        
        self.tree.heading('视频文件名', text='视频文件名')
        self.tree.column('视频文件名', width=450)
        
        self.tree.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=2, column=4, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 创建功能按钮框架
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=10, sticky=(tk.W, tk.E))
        
        # 左侧功能区
        left_frame = ttk.Frame(button_frame)
        left_frame.pack(side=tk.LEFT, padx=5)
        
        # 序号调整选项
        self.pad_numbers = tk.BooleanVar(value=False)
        ttk.Checkbutton(left_frame, text="补齐序号位数", variable=self.pad_numbers, 
                       command=self.refresh_display).pack(side=tk.LEFT, padx=5)
        
        # 图片后缀选项
        ttk.Label(left_frame, text="添加图片后缀:").pack(side=tk.LEFT, padx=5)
        self.suffix_var = tk.StringVar(value="无")
        suffix_combo = ttk.Combobox(left_frame, textvariable=self.suffix_var, 
                                  values=["无", "-thumb", "-poster"], width=10)
        suffix_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(left_frame, text="应用后缀", command=self.apply_suffix).pack(side=tk.LEFT, padx=5)
        
        # 右侧确认按钮
        right_frame = ttk.Frame(button_frame)
        right_frame.pack(side=tk.RIGHT, padx=5)
        
        # 确认重命名按钮
        confirm_btn = ttk.Button(right_frame, text="确认全部重命名", command=self.apply_all_rename)
        confirm_btn.pack(side=tk.RIGHT, padx=5)
        
        # 调整字符替换区域的位置
        self.create_replacement_area()
        
    def create_replacement_area(self):
        # 字符替换区域
        replace_frame = ttk.LabelFrame(self.main_frame, text="字符替换", padding="5")
        replace_frame.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(replace_frame, text="要删除的字符:").grid(row=0, column=0, padx=5)
        self.chars_to_remove = ttk.Entry(replace_frame, width=30)
        self.chars_to_remove.grid(row=0, column=1, padx=5)
        
        ttk.Button(replace_frame, text="删除字符", command=self.remove_chars).grid(row=0, column=2, padx=5)
        
    def get_number_from_filename(self, filename):
        numbers = re.findall(r'\d+', filename)
        return int(numbers[0]) if numbers else None
        
    def get_extension(self, filename):
        return os.path.splitext(filename)[1].lower()
        
    def is_image(self, filename):
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        return self.get_extension(filename) in image_extensions
        
    def is_video(self, filename):
        video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.mkv'}
        return self.get_extension(filename) in video_extensions
        
    def process_folder(self, folder_path):
        files = os.listdir(folder_path)
        
        # 将文件按序号分类
        number_files = {}
        for file in files:
            number = self.get_number_from_filename(file)
            if number is not None:
                if number not in number_files:
                    number_files[number] = {'image': None, 'video': None}
                    
                if self.is_image(file):
                    number_files[number]['image'] = file
                elif self.is_video(file):
                    number_files[number]['video'] = file
        
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 添加文件对到Treeview
        self.file_pairs = []
        for number, files in number_files.items():
            if files['image'] and files['video']:
                image_name = os.path.splitext(files['image'])[0]
                video_name = os.path.splitext(files['video'])[0]
                
                if image_name != video_name:
                    # 如果选择补齐序号位数，则在显示时补齐
                    display_number = str(number)
                    if self.pad_numbers.get():
                        display_number = str(number).zfill(2)
                    
                    self.file_pairs.append({
                        'number': number,
                        'image': files['image'],
                        'video': files['video'],
                        'choice': 'video'  # 默认选择视频文件名
                    })
                    
                    # 使用特殊字符表示单选框状态
                    image_radio = "○"
                    video_radio = "●"  # 默认选中视频名
                    
                    self.tree.insert('', 'end', values=(
                        display_number,
                        image_radio,
                        files['image'],
                        video_radio,
                        files['video']
                    ))
        
        # 绑定单击事件来切换选择
        self.tree.bind('<ButtonRelease-1>', self.handle_click)
        
    def handle_click(self, event):
        # 获取点击的列和项
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)
            
            # 只处理"选择"列的点击（第2列和第4列）
            if column == "#2" or column == "#4":
                values = self.tree.item(item)['values']
                number = values[0]
                
                # 更新选择状态
                for pair in self.file_pairs:
                    if str(pair['number']) == str(number):
                        # 根据点击的列决定选择图片还是视频
                        pair['choice'] = 'image' if column == "#2" else 'video'
                        
                        # 更新显示
                        self.tree.item(item, values=(
                            number,
                            "●" if pair['choice'] == 'image' else "○",
                            values[2],
                            "●" if pair['choice'] == 'video' else "○",
                            values[4]
                        ))
                        break
        
    def apply_changes(self):
        for pair in self.file_pairs:
            image_path = os.path.join(self.current_folder, pair['image'])
            video_path = os.path.join(self.current_folder, pair['video'])
            
            # 获取基本名称和扩展名
            if pair['choice'] == 'image':
                base_name = os.path.splitext(pair['image'])[0]
                ext = self.get_extension(pair['video'])
            else:
                base_name = os.path.splitext(pair['video'])[0]
                ext = self.get_extension(pair['image'])
            
            # 如果需要补齐序号位数
            if self.pad_numbers.get():
                number = self.get_number_from_filename(base_name)
                if number is not None:
                    # 替换原有序号为补齐后的序号
                    old_number = str(number)
                    new_number = str(number).zfill(2)
                    base_name = base_name.replace(old_number, new_number)
            
            if pair['choice'] == 'image':
                new_name = base_name + ext
                os.rename(video_path, os.path.join(self.current_folder, new_name))
            else:
                new_name = base_name + ext
                os.rename(image_path, os.path.join(self.current_folder, new_name))
                
        messagebox.showinfo("完成", "文件名已更新")
        self.process_folder(self.current_folder)
        
    def remove_chars(self):
        chars = self.chars_to_remove.get()
        if not chars:
            messagebox.showwarning("警告", "请输入要删除的字符")
            return
            
        files = os.listdir(self.current_folder)
        
        renamed_count = 0
        for file in files:
            # 获取文件名和扩展名
            name, ext = os.path.splitext(file)
            
            # 只有当文件名中完全匹配要删除的字符串时才删除
            if chars in name:  # 注意这里不再使用translate，而是直接检查是否包含完整字符串
                new_name = name.replace(chars, '') + ext
                
                if new_name != file:
                    try:
                        os.rename(
                            os.path.join(self.current_folder, file),
                            os.path.join(self.current_folder, new_name)
                        )
                        renamed_count += 1
                    except OSError as e:
                        messagebox.showerror("错误", f"重命名文件 {file} 时出错：{str(e)}")
                        
        if renamed_count > 0:
            messagebox.showinfo("完成", f"成功删除字符串 '{chars}'，共处理 {renamed_count} 个文件")
        else:
            messagebox.showinfo("完成", f"没有找到包含字符串 '{chars}' 的文件")
            
        # 刷新显示
        self.process_folder(self.current_folder)
        
    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.current_folder)
        if folder:
            self.current_folder = folder
            self.folder_path_var.set(folder)
            self.process_folder(folder)
            
    def refresh_display(self):
        self.process_folder(self.current_folder)
        
    def apply_suffix(self):
        suffix = self.suffix_var.get()
        if suffix == "无":
            return
            
        for file in os.listdir(self.current_folder):
            if self.is_image(file):
                name, ext = os.path.splitext(file)
                # 如果已经有后缀，先移除
                name = name.replace('-thumb', '').replace('-poster', '')
                new_name = f"{name}{suffix}{ext}"
                if new_name != file:
                    os.rename(
                        os.path.join(self.current_folder, file),
                        os.path.join(self.current_folder, new_name)
                    )
        
        self.process_folder(self.current_folder)
        messagebox.showinfo("完成", "图片后缀添加完成")
        
    def apply_all_rename(self):
        if not self.file_pairs:
            messagebox.showwarning("警告", "没有需要重命名的文件")
            return
        
        renamed_count = 0
        for pair in self.file_pairs:
            image_path = os.path.join(self.current_folder, pair['image'])
            video_path = os.path.join(self.current_folder, pair['video'])
            
            try:
                # 获取基本名称和扩展名
                if pair['choice'] == 'image':
                    base_name = os.path.splitext(pair['image'])[0]
                    ext = self.get_extension(pair['video'])
                    new_name = base_name + ext
                    # 重命名视频文件以匹配图片名
                    os.rename(video_path, os.path.join(self.current_folder, new_name))
                else:
                    base_name = os.path.splitext(pair['video'])[0]
                    ext = self.get_extension(pair['image'])
                    new_name = base_name + ext
                    # 重命名图片文件以匹配视频名
                    os.rename(image_path, os.path.join(self.current_folder, new_name))
                renamed_count += 1
            except OSError as e:
                messagebox.showerror("错误", f"重命名文件时出错：{str(e)}")
        
        # 刷新显示
        self.process_folder(self.current_folder)
        messagebox.showinfo("完成", f"重命名完成，共处理 {renamed_count} 个文件对")

if __name__ == "__main__":
    matcher = FileNameMatcher()
    matcher.process_folder(matcher.current_folder)
    matcher.root.mainloop() 