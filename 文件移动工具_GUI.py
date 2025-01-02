import os
import shutil
import streamlit as st
from datetime import datetime
import pathlib

# 预定义的文件类型
PREDEFINED_EXTENSIONS = {
    '视频文件': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'],
    'PDF文件': ['.pdf'],
    '文档文件': ['.doc', '.docx', '.txt', '.xlsx', '.xls'],
    '图片文件': ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
}

def generate_html_structure(directory, selected_extensions):
    """生成目录结构的HTML报告"""
    html_content = [
        '<!DOCTYPE html>',
        '<html>',
        '<head>',
        '<meta charset="utf-8">',
        '<title>文件夹结构报告</title>',
        '<style>',
        'body { font-family: Arial, sans-serif; margin: 20px; }',
        '.folder { color: #2c3e50; }',
        '.file { color: #e74c3c; margin-left: 20px; }',
        '</style>',
        '</head>',
        '<body>',
        f'<h2>文件夹结构报告 - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</h2>'
    ]
    
    def scan_directory(path):
        content = []
        try:
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    content.append(f'<p class="folder">📁 {item}</p>')
                    content.extend([f'<div style="margin-left:20px">{line}</div>' for line in scan_directory(item_path)])
                elif any(item.lower().endswith(ext.lower()) for ext in selected_extensions):
                    content.append(f'<p class="file">📄 {item}</p>')
        except Exception as e:
            content.append(f'<p style="color: red;">Error reading directory: {str(e)}</p>')
        return content

    html_content.extend(scan_directory(directory))
    html_content.extend(['</body>', '</html>'])
    return '\n'.join(html_content)

def get_all_files(directory):
    """获取目录下所有文件的树形结构"""
    file_tree = {"files": [], "dirs": {}}
    try:
        for root, dirs, files in os.walk(directory):
            current_level = file_tree
            path_parts = os.path.relpath(root, directory).split(os.sep)
            
            # 处理根目录
            if path_parts[0] == '.':
                path_parts = path_parts[1:]
            
            # 创建目录树结构
            for part in path_parts:
                if part:
                    if part not in current_level["dirs"]:
                        current_level["dirs"][part] = {"files": [], "dirs": {}}
                    current_level = current_level["dirs"][part]
            
            # 添加文件
            current_level["files"] = files
    except Exception as e:
        st.error(f"读取目录时出错: {str(e)}")
    return file_tree

def display_file_tree(tree, selected_extensions, indent=0):
    """递归显示文件树"""
    # 显示当前文件夹中的文件
    for file in sorted(tree["files"]):
        if any(file.lower().endswith(ext.lower()) for ext in selected_extensions):
            st.markdown("&nbsp;" * (indent * 4) + f"📄 {file}")
    
    # 递归显示子文件夹
    for folder_name, folder_content in sorted(tree["dirs"].items()):
        st.markdown("&nbsp;" * (indent * 4) + f"📁 {folder_name}")
        display_file_tree(folder_content, selected_extensions, indent + 1)

def move_files(source_dir, selected_extensions):
    """移动文件并删除空文件夹"""
    moved_files = []
    empty_folders = []
    
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if any(file.lower().endswith(ext.lower()) for ext in selected_extensions):
                src_path = os.path.join(root, file)
                folder_name = os.path.basename(os.path.dirname(src_path))
                new_name = f"{folder_name}_{file}"
                dst_path = os.path.join(source_dir, new_name)
                
                try:
                    shutil.move(src_path, dst_path)
                    moved_files.append((file, new_name))
                except Exception as e:
                    st.error(f"移动文件 {file} 时出错: {str(e)}")
    
    # 删除空文件夹
    for root, dirs, files in os.walk(source_dir, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.listdir(dir_path):
                try:
                    os.rmdir(dir_path)
                    empty_folders.append(dir_name)
                except Exception as e:
                    st.error(f"删除文件夹 {dir_name} 时出错: {str(e)}")
    
    return moved_files, empty_folders

def main():
    st.set_page_config(page_title="文件移动工具", layout="wide")
    
    # 使用自定义CSS美化界面
    st.markdown("""
        <style>
        .stButton > button {
            background: linear-gradient(to right, #4880EC, #019CAD);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            width: 100%;
            margin-top: 10px;
            margin-bottom: 10px;
        }
        .stButton > button:hover {
            background: linear-gradient(to right, #019CAD, #4880EC);
        }
        .report-btn > button {
            background: linear-gradient(to right, #11998e, #38ef7d);
        }
        .report-btn > button:hover {
            background: linear-gradient(to right, #38ef7d, #11998e);
        }
        /* 自定义侧边栏样式 */
        .sidebar-text {
            font-size: 0.9em !important;
        }
        .sidebar-header {
            font-size: 1.2em !important;
            margin-bottom: 0.5em !important;
        }
        /* 修改确认按钮样式 */
        .small-button > button {
            padding: 0px 8px !important;
            height: 38px !important;  /* 与输入框高度一致 */
            margin: 0 !important;
            min-height: 38px !important;
            line-height: 38px !important;
            font-size: 0.9em !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 主标题
    st.title("文件移动工具")
    
    # 创建左侧边栏
    with st.sidebar:
        st.markdown('<p class="sidebar-header">设置</p>', unsafe_allow_html=True)
        
        # 选择文件夹
        st.markdown('<p class="sidebar-header">1. 选择待整理文件夹</p>', unsafe_allow_html=True)
        col1, col2 = st.columns([4, 1])
        folder_path = col1.text_input("请输入或粘贴文件夹路径：", key="folder_path_input", label_visibility="collapsed")
        confirm_path = col2.button("OK", key="confirm_path", type="primary", use_container_width=True)
        
        if folder_path and (confirm_path or st.session_state.get('path_confirmed')):
            if not os.path.exists(folder_path):
                st.error("❌ 所选文件夹不存在")
            else:
                st.session_state['path_confirmed'] = True
                st.success("✅ 文件夹路径有效")
                
                # 文件类型选择
                st.markdown('<p class="sidebar-header">2. 选择文件类型</p>', unsafe_allow_html=True)
                selected_types = {}
                
                # 预定义文件类型的复选框
                for type_name, extensions in PREDEFINED_EXTENSIONS.items():
                    selected_types[type_name] = st.checkbox(
                        f"{type_name} ({', '.join(extensions)})", 
                        key=f"checkbox_{type_name}",
                        help=f"选择所有{type_name}"
                    )
                
                # 自定义文件类型
                st.markdown('<p class="sidebar-header">2.1 自定义文件类型</p>', unsafe_allow_html=True)
                custom_extensions = st.text_input(
                    "输入自定义文件扩展名",
                    placeholder=".txt, .doc",
                    key="custom_extensions_input",
                    help="多个扩展名用逗号分隔"
                )
                
                # 合并所有选中的扩展名
                selected_extensions = []
                for type_name, selected in selected_types.items():
                    if selected:
                        selected_extensions.extend(PREDEFINED_EXTENSIONS[type_name])
                if custom_extensions:
                    selected_extensions.extend([ext.strip() for ext in custom_extensions.split(",")])
                
                if selected_extensions:
                    st.markdown("---")
                    st.subheader("3. 操作")
                    
                    # 移动文件按钮
                    if st.button("📦 移动文件", use_container_width=True):
                        with st.spinner("正在移动文件..."):
                            moved_files, empty_folders = move_files(folder_path, selected_extensions)
                            if moved_files:
                                st.success("✅ 文件移动完成！")
                                with st.expander("查看详细信息"):
                                    st.write("已移动的文件：")
                                    for old_name, new_name in moved_files:
                                        st.write(f"- {old_name} → {new_name}")
                                    if empty_folders:
                                        st.write("已删除的空文件夹：")
                                        for folder in empty_folders:
                                            st.write(f"- {folder}")
                    
                    # 生成报告按钮
                    if st.button("📄 生成HTML报告", use_container_width=True, key="report_btn"):
                        with st.spinner("正在生成报告..."):
                            html_content = generate_html_structure(folder_path, selected_extensions)
                            report_path = os.path.join(folder_path, 'folder_structure_report.html')
                            try:
                                with open(report_path, 'w', encoding='utf-8') as f:
                                    f.write(html_content)
                                st.success(f"✅ HTML报告已保存至: {report_path}")
                            except Exception as e:
                                st.error(f"❌ 生成报告时出错: {str(e)}")
                else:
                    st.warning("⚠️ 请选择至少一种文件类型")
        
    # 主界面显示使用说明
    if not (folder_path and st.session_state.get('path_confirmed') and selected_extensions):
        st.header("📚 使用说明")
        
        st.markdown("""
        ### 功能介绍
        这是一个文件整理工具，可以帮助你：
        - 📂 从多个子文件夹中提取特定类型的文件
        - 🏷️ 自动为提取的文件添加原文件夹名称作为前缀
        - 🗑️ 自动清理空文件夹
        - 📝 生成文件结构报告
        
        ### 使用步骤
        1. **选择文件夹**
           - 在左侧输入或粘贴需要整理的文件夹路径
           - 点击确认按钮或按回车键确认
        
        2. **选择文件类型**
           - 勾选预定义的文件类型（视频、图片、文档等）
           - 或者在自定义区域输入特定的文件扩展名
        
        3. **执行操作**
           - 点击"移动文件"按钮开始整理
           - 或者点击"生成HTML报告"查看文件结构
        
        ### 注意事项
        - 移动文件操作不可撤销，请确保选择了正确的文件夹
        - 建议先生成报告预览文件结构
        - 所有文件将被移动到选择的根目录下
        """)
    
    # 主界面显示文件树
    if folder_path and st.session_state.get('path_confirmed') and selected_extensions:
        st.header("📁 文件结构")
        st.caption("当前显示的文件类型: " + ", ".join(selected_extensions))
        
        file_tree = get_all_files(folder_path)
        display_file_tree(file_tree, selected_extensions)

if __name__ == "__main__":
    main() 