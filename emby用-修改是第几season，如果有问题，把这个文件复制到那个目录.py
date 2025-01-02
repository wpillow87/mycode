import tkinter as tk
from tkinter import ttk
import os
import xml.etree.ElementTree as ET
from typing import List, Tuple
from tkinter import filedialog

class NFOEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("NFO文件编辑器")
        
        # 设置窗口初始大小
        self.root.geometry("1075x680")  # 修改为原来的一半
        
        # 添加当前文件夹变量
        self.current_folder = os.getcwd()
        
        # 创建主框架
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # 创建左侧文件列表区域
        self.create_file_list_area()
        
        # 创建中间排序区域
        self.create_sorting_area()
        
        # 创建右侧功能区域
        self.create_function_area()
        
        # 加载NFO文件
        self.load_nfo_files()

    def create_file_list_area(self):
        # 文件列表框架
        file_frame = ttk.LabelFrame(self.main_frame, text="文件列表")
        file_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # 添加选择文件夹按钮和全部添加按钮的框架
        btn_frame = ttk.Frame(file_frame)
        btn_frame.pack(pady=5)
        
        # 选择文件夹按钮
        folder_btn = ttk.Button(btn_frame, text="选择文件夹", command=self.choose_folder)
        folder_btn.pack(side=tk.LEFT, padx=5)
        
        # 全部添加按钮
        add_all_btn = ttk.Button(btn_frame, text="全部添加", command=self.add_all_to_sorting)
        add_all_btn.pack(side=tk.LEFT, padx=5)
        
        # 创建Treeview用于显示文件
        self.file_tree = ttk.Treeview(file_frame, columns=("文件名", "Season", "Episode"), show="headings", height=25)  # 增加高度
        self.file_tree.heading("文件名", text="文件名", command=lambda: self.treeview_sort_column(self.file_tree, "文件名", False))
        self.file_tree.heading("Season", text="Season", command=lambda: self.treeview_sort_column(self.file_tree, "Season", False))
        self.file_tree.heading("Episode", text="Episode", command=lambda: self.treeview_sort_column(self.file_tree, "Episode", False))
        
        # 设置列宽和对齐方式
        self.file_tree.column("文件名", width=300)
        self.file_tree.column("Season", width=60, anchor="e")
        self.file_tree.column("Episode", width=60, anchor="e")
        
        self.file_tree.pack(fill=tk.BOTH, expand=True)
        
        # 选中按钮
        self.select_btn = ttk.Button(file_frame, text="选中", command=self.move_to_sorting)
        self.select_btn.pack(pady=5)

    def create_sorting_area(self):
        # 排序区域框架
        sort_frame = ttk.LabelFrame(self.main_frame, text="排序区域")
        sort_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        # 创建Treeview用于显示排序文件
        self.sort_tree = ttk.Treeview(sort_frame, columns=("文件名", "Season", "Episode"), show="headings", height=25)
        self.sort_tree.heading("文件名", text="文件名", command=lambda: self.treeview_sort_column(self.sort_tree, "文件名", False))
        self.sort_tree.heading("Season", text="Season", command=lambda: self.treeview_sort_column(self.sort_tree, "Season", False))
        self.sort_tree.heading("Episode", text="Episode", command=lambda: self.treeview_sort_column(self.sort_tree, "Episode", False))
        
        # 设置列宽和对齐方式
        self.sort_tree.column("文件名", width=300)
        self.sort_tree.column("Season", width=60, anchor="e")
        self.sort_tree.column("Episode", width=60, anchor="e")
        
        self.sort_tree.pack(fill=tk.BOTH, expand=True)
        
        # 添加按钮框架
        btn_frame = ttk.Frame(sort_frame)
        btn_frame.pack(pady=5)
        
        # 上移下移按钮和清空按钮
        ttk.Button(btn_frame, text="上移", command=self.move_up).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="下移", command=self.move_down).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="清空", command=self.clear_sorting_area).pack(side=tk.LEFT, padx=5)

    def create_function_area(self):
        # 功能区域框架
        func_frame = ttk.LabelFrame(self.main_frame, text="功能设置")
        func_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        
        # Season设置
        ttk.Label(func_frame, text="设置Season:").pack(pady=5)
        self.season_var = tk.StringVar()
        self.season_entry = ttk.Entry(func_frame, textvariable=self.season_var)
        self.season_entry.pack(pady=5)
        
        # Episode设置
        ttk.Label(func_frame, text="设置起始Episode:").pack(pady=5)
        self.episode_var = tk.StringVar()
        self.episode_entry = ttk.Entry(func_frame, textvariable=self.episode_var)
        self.episode_entry.pack(pady=5)
        
        # 执行按钮
        ttk.Button(func_frame, text="执行", command=self.execute_changes).pack(pady=20)

    def load_nfo_files(self):
        # 获取当前目录下的所有nfo文件
        nfo_files = [f for f in os.listdir() if f.endswith('.nfo')]
        
        for file in nfo_files:
            season, episode = self.read_nfo_tags(file)
            self.file_tree.insert("", "end", values=(file, season, episode))

    def read_nfo_tags(self, filename: str) -> Tuple[str, str]:
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            
            season = root.find('season')
            episode = root.find('episode')
            
            season_text = season.text if season is not None else "无"
            episode_text = episode.text if episode is not None else "无"
            
            return season_text, episode_text
        except:
            return "无", "无"

    def move_to_sorting(self):
        # 获取选中的项目
        selected_items = self.file_tree.selection()
        
        # 移动到排序区域
        for item in selected_items:
            values = self.file_tree.item(item)['values']
            # 使用完整文件名
            filename = os.path.basename(values[0])
            self.sort_tree.insert("", "end", values=(values[0], values[1], values[2]))
            self.sort_tree.set(self.sort_tree.get_children()[-1], "文件名", filename)
            self.file_tree.delete(item)

    def move_up(self):
        selected = self.sort_tree.selection()
        if not selected:
            return
        
        for item in selected:
            idx = self.sort_tree.index(item)
            if idx > 0:
                # 获取当前项和上一项的值
                current_values = self.sort_tree.item(item)['values']
                prev_item = self.sort_tree.prev(item)
                prev_values = self.sort_tree.item(prev_item)['values']
                
                # 交换值
                self.sort_tree.item(item, values=prev_values)
                self.sort_tree.item(prev_item, values=current_values)
                
                # 保持选中状态
                self.sort_tree.selection_set(prev_item)

    def move_down(self):
        selected = self.sort_tree.selection()
        if not selected:
            return
        
        for item in reversed(selected):
            next_item = self.sort_tree.next(item)
            if next_item:
                # 获取当前项和下一项的值
                current_values = self.sort_tree.item(item)['values']
                next_values = self.sort_tree.item(next_item)['values']
                
                # 交换值
                self.sort_tree.item(item, values=next_values)
                self.sort_tree.item(next_item, values=current_values)
                
                # 保持选中状态
                self.sort_tree.selection_set(next_item)

    def execute_changes(self):
        try:
            season = self.season_var.get()
            start_episode = int(self.episode_var.get())
            
            # 获取排序区域的所有项目
            items = self.sort_tree.get_children()
            
            for idx, item in enumerate(items):
                try:
                    filename = self.sort_tree.item(item)['values'][0]
                    
                    # 检查文件是否存在
                    if not os.path.exists(filename):
                        print(f"文件不存在: {filename}")
                        continue
                    
                    # 更新XML文件
                    tree = ET.parse(filename)
                    root = tree.getroot()
                    
                    # 更新season
                    season_elem = root.find('season')
                    if season_elem is None:
                        season_elem = ET.SubElement(root, 'season')
                    season_elem.text = str(season)
                    
                    # 更新episode
                    episode_elem = root.find('episode')
                    if episode_elem is None:
                        episode_elem = ET.SubElement(root, 'episode')
                    episode_elem.text = str(start_episode + idx)
                    
                    # 保存文件
                    tree.write(filename, encoding='utf-8', xml_declaration=True)
                    
                    # 更新显示
                    display_name = os.path.basename(filename)  # 使用完整文件名
                    self.sort_tree.item(item, values=(filename, season, start_episode + idx))
                    self.sort_tree.set(item, "文件名", display_name)
                    
                except Exception as e:
                    print(f"处理文件时出错: {str(e)}")
                    print(f"问题文件: {filename}")
                    continue
                
        except ValueError:
            print("请输入有效的数字")
            return
        except Exception as e:
            print(f"执行过程中出错: {str(e)}")

    def choose_folder(self):
        # 打开文件夹选择对话框
        folder_path = filedialog.askdirectory(title="选择包含NFO文件的文件夹")
        if folder_path:
            try:
                # 清空当前文件列表
                for item in self.file_tree.get_children():
                    self.file_tree.delete(item)
                
                # 保存当前工作目录
                self.current_folder = folder_path
                
                # 加载新文件夹中的NFO文件
                nfo_files = [f for f in os.listdir(folder_path) if f.endswith('.nfo')]
                
                for file in nfo_files:
                    try:
                        full_path = os.path.abspath(os.path.join(folder_path, file))
                        if os.path.exists(full_path):
                            season, episode = self.read_nfo_tags(full_path)
                            # 显示完整文件名（包含扩展名）
                            self.file_tree.insert("", "end", values=(full_path, season, episode))
                            self.file_tree.set(self.file_tree.get_children()[-1], "文件名", file)
                    except Exception as e:
                        print(f"处理文件 {file} 时出错: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"加载文件夹时出错: {str(e)}")

    def treeview_sort_column(self, tree, col, reverse):
        """排序Treeview的某一列"""
        l = [(tree.set(k, col), k) for k in tree.get_children("")]
        
        # 对Season和Episode列进行数值排序
        if col in ["Season", "Episode"]:
            # 将"无"转换为-1进行排序
            l = [(int(v[0]) if v[0] != "无" else -1, v[1]) for v in l]
        
        l.sort(reverse=reverse)
        
        # 重新排序
        for index, (val, k) in enumerate(l):
            tree.move(k, "", index)
        
        # 下次点击时反向排序
        tree.heading(col, command=lambda: self.treeview_sort_column(tree, col, not reverse))

    def add_all_to_sorting(self):
        # 获取所有文件
        all_items = self.file_tree.get_children()
        
        # 移动所有文件到排序区域
        for item in all_items:
            values = self.file_tree.item(item)['values']
            # 使用完整文件名
            filename = os.path.basename(values[0])
            self.sort_tree.insert("", "end", values=(values[0], values[1], values[2]))
            self.sort_tree.set(self.sort_tree.get_children()[-1], "文件名", filename)
        
        # 清空文件列表
        for item in all_items:
            self.file_tree.delete(item)

    def clear_sorting_area(self):
        """清空排序区域"""
        # 获取所有项目
        items = self.sort_tree.get_children()
        
        # 删除所有项目
        for item in items:
            self.sort_tree.delete(item)

if __name__ == "__main__":
    root = tk.Tk()
    app = NFOEditor(root)
    
    # 设置列权重，使得窗口可以自适应大小
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    
    # 设置主框架的列权重
    app.main_frame.grid_columnconfigure(0, weight=1)
    app.main_frame.grid_columnconfigure(1, weight=1)
    app.main_frame.grid_columnconfigure(2, weight=1)
    
    root.mainloop()
