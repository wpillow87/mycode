import os
from datetime import datetime
import codecs
import json
import tkinter as tk
from tkinter import filedialog, messagebox

def scan_directory(path):
    tree_data = []
    try:
        for item in os.scandir(path):
            node = {
                'name': item.name,
                'path': os.path.abspath(item.path)  # 保存完整路径
            }
            
            if item.is_file():
                node['type'] = 'file'
                node['size'] = format_size(item.stat().st_size)
                node['ext'] = os.path.splitext(item.name)[1][1:] or ''
            else:
                node['type'] = 'directory'
                node['children'] = scan_directory(item.path)
            
            tree_data.append(node)
        
        # 按照文件夹在前，文件在后，然后按名称排序
        tree_data.sort(key=lambda x: (x['type'] != 'directory', x['name'].lower()))
        return tree_data
    except Exception as e:
        print(f"扫描目录 {path} 时出错: {str(e)}")
        return []

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

def select_directory():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    directory = filedialog.askdirectory(title="选择要扫描的目录")
    return directory if directory else None

def select_save_directory():
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory(title="选择保存位置")
    return directory if directory else None

def generate_html(tree_data, source_path, save_path):
    # 将树形数据转换为JSON字符串
    tree_data_json = json.dumps(tree_data)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>文件树形结构报告</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            font-size: 13px;
            height: 100vh;
            box-sizing: border-box;
        }}
        .container {{
            display: flex;
            flex-direction: column;
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
            height: 100vh;
        }}
        .main-content {{
            display: flex;
            flex: 1;
            gap: 20px;
            margin-top: 20px;
            min-height: 0;
        }}
        .left-panel {{
            display: flex;
            flex-direction: column;
            flex: 1;
            min-height: 0;
        }}
        .right-panel {{
            width: 300px;
            display: flex;
            flex-direction: column;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 10px;
        }}
        .staged-items {{
            flex: 1;
            overflow-y: auto;
            min-height: 0;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            background-color: white;
            margin-top: 10px;
        }}
        .staged-item {{
            padding: 8px;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .staged-item:last-child {{
            border-bottom: none;
        }}
        .staged-item-content {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .item-name {{
            font-weight: 500;
        }}
        .staged-item .remove {{
            cursor: pointer;
            color: #dc3545;
            padding: 0 5px;
            font-size: 18px;
            line-height: 1;
        }}
        .staged-item .remove:hover {{
            color: #c82333;
        }}
        .panel-title {{
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
            padding: 5px;
            background-color: #e9ecef;
            border-radius: 4px;
            text-align: center;
        }}
        .search-container {{
            margin: 10px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 4px;
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        .search-input {{
            flex: 1;
            padding: 5px 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 13px;
        }}
        .search-options {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        .toolbar {{
            margin: 10px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 4px;
            flex-shrink: 0;
        }}
        .toolbar button {{
            margin-right: 10px;
            padding: 5px 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: white;
            cursor: pointer;
        }}
        .toolbar button:hover {{
            background-color: #e9ecef;
        }}
        .selected-items {{
            margin: 10px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 4px;
            max-height: 100px;
            overflow-y: auto;
            display: none;
        }}
        .selected-items.has-items {{
            display: block;
        }}
        .selected-item {{
            display: inline-block;
            margin: 2px 5px;
            padding: 2px 8px;
            background-color: #e9ecef;
            border-radius: 3px;
            font-size: 12px;
        }}
        .selected-item .remove {{
            margin-left: 5px;
            cursor: pointer;
            color: #dc3545;
        }}
        .virtual-tree {{
            flex: 1;
            overflow: auto;
            position: relative;
            border: 1px solid #ddd;
            border-radius: 4px;
            min-height: 200px;
        }}
        .tree-content {{
            position: absolute;
            width: 100%;
        }}
        .tree-item {{
            padding: 4px 8px;
            display: flex;
            align-items: center;
            cursor: pointer;
        }}
        .tree-item:hover {{
            background-color: #f8f9fa;
        }}
        .tree-item.selected {{
            background-color: #e3f2fd;
        }}
        .indent {{
            width: 20px;
            height: 1px;
            display: inline-block;
        }}
        .icon {{
            margin-right: 5px;
        }}
        .toggle {{
            width: 16px;
            text-align: center;
            cursor: pointer;
        }}
        .size, .type {{
            margin-left: 10px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>文件树形结构报告</h1>
        
        <div class="search-container">
            <input type="text" class="search-input" placeholder="搜索文件或文件夹..." id="searchInput">
            <div class="search-options">
                <label>
                    <input type="checkbox" id="searchInContent" checked>
                    在内容中搜索
                </label>
                <label>
                    <input type="checkbox" id="caseSensitive">
                    区分大小写
                </label>
            </div>
        </div>

        <div class="toolbar">
            <button onclick="expandSelected()">展开选中</button>
            <button onclick="collapseSelected()">收起选中</button>
            <button onclick="expandAll()">展开全部</button>
            <button onclick="collapseAll()">收起全部</button>
            <button onclick="expandSelectedDeep()">展开选中到最深</button>
            <button onclick="collapseSelectedTop()">收起选中到顶层</button>
            <button onclick="clearSelection()">清除选择</button>
            <button onclick="stageSelected()">暂存选中项</button>
            <button onclick="saveStaged()">保存暂存项</button>
            <button onclick="clearStaged()">清除暂存区</button>
        </div>

        <div class="main-content">
            <div class="left-panel">
                <div class="selected-items" id="selectedItems"></div>
                <div id="virtual-tree" class="virtual-tree">
                    <div id="tree-content" class="tree-content"></div>
                </div>
            </div>
            
            <div class="right-panel">
                <div class="panel-title">暂存区</div>
                <div class="staged-items" id="stagedItems"></div>
            </div>
        </div>
    </div>
    <script>
        // 树形数据
        const treeData = {tree_data_json};
        
        // 扁平化的显示数据
        let flattenedItems = [];
        // 项目高度
        const ITEM_HEIGHT = 28;
        const tree = document.getElementById('virtual-tree');
        const content = document.getElementById('tree-content');
        
        // 初始化树形结构
        function initializeTree(data, level = 0) {{
            for (let i = 0; i < data.length; i++) {{
                const item = data[i];
                const flatItem = {{
                    ...item,
                    level,
                    visible: level === 0,
                    expanded: false,
                    selected: false
                }};
                flattenedItems.push(flatItem);
                
                if (item.type === 'directory' && item.children) {{
                    initializeTree(item.children, level + 1);
                }}
            }}
        }}

        // 渲染可见项目
        function renderVisibleItems() {{
            const scrollTop = tree.scrollTop;
            const containerHeight = tree.clientHeight;
            
            // 获取所有可见项目
            const visibleFlatItems = flattenedItems.filter(item => item.visible);
            
            // 增加缓冲区大小，提前渲染更多项目
            const bufferSize = 200; // 上下各多渲染200行
            const startIndex = Math.max(0, Math.floor(scrollTop / ITEM_HEIGHT) - bufferSize);
            const endIndex = Math.min(
                Math.ceil((scrollTop + containerHeight) / ITEM_HEIGHT) + bufferSize,
                visibleFlatItems.length
            );
            
            // 设置内容区域的总高度
            content.style.height = `${{visibleFlatItems.length * ITEM_HEIGHT}}px`;
            
            // 计算内容的起始位置
            const topOffset = startIndex * ITEM_HEIGHT;
            content.style.top = `${{topOffset}}px`;
            
            // 分批渲染以提高性能
            const itemsToRender = visibleFlatItems.slice(startIndex, endIndex);
            const chunkSize = 100; // 每批处理100个项目
            
            let html = '';
            for (let i = 0; i < itemsToRender.length; i += chunkSize) {{
                const chunk = itemsToRender.slice(i, i + chunkSize);
                html += chunk.map(item => {{
                    const displayData = {{
                        icon: item.type === 'directory' ? '📁' : '📄',
                        toggle: item.type === 'directory' ? (item.expanded ? '▼' : '▶') : ' ',
                        name: item.name,
                        size: item.type === 'file' ? item.size : '',
                        type: item.type === 'file' ? item.ext : '',
                        indent: item.level * 20,
                        selected: item.selected ? ' selected' : '',
                        index: flattenedItems.indexOf(item)
                    }};

                    const itemHtml = [
                        `<div class="tree-item${{displayData.selected ? ' selected' : ''}}${{displayData.highlight ? ' highlight' : ''}}" `,
                        `data-index="${{displayData.index}}" `,
                        `style="padding-left: ${{displayData.indent}}px">`,
                        `<label class="checkbox-container">`,
                        `<input type="checkbox" class="checkbox" `,
                        `{{displayData.selected ? 'checked' : ''}}`,
                        `onclick="toggleSelect(${{displayData.index}}); event.stopPropagation();">`,
                        `</label>`,
                        `<span class="toggle">${{displayData.toggle}}</span>`,
                        `<span class="icon">${{displayData.icon}}</span>`,
                        `<span class="name">${{item.name}}</span>`
                    ];

                    if (displayData.size) {{
                        itemHtml.push(`<span class="size">${{displayData.size}}</span>`);
                    }}
                    if (displayData.type) {{
                        itemHtml.push(`<span class="type">${{displayData.type}}</span>`);
                    }}

                    itemHtml.push('</div>');
                    return itemHtml.join('');
                }}).join('');
            }}
            
            content.innerHTML = html;
        }}

        // 切换展开/收起状态
        function toggleItem(index) {{
            const item = flattenedItems[index];
            if (item.type !== 'directory') return;
            
            item.expanded = !item.expanded;
            updateVisibility();
            renderVisibleItems();
        }}

        // 更新可见性
        function updateVisibility() {{
            flattenedItems.forEach((item, index) => {{
                if (index === 0) {{
                    item.visible = true;
                    return;
                }}
                
                let parent = findParent(index);
                item.visible = parent ? parent.expanded && parent.visible : true;
            }});
        }}

        // 查找父项目
        function findParent(index) {{
            const item = flattenedItems[index];
            for (let i = index - 1; i >= 0; i--) {{
                if (flattenedItems[i].level < item.level) {{
                    return flattenedItems[i];
                }}
            }}
            return null;
        }}

        // 选择项目
        function toggleSelect(index) {{
            const item = flattenedItems[index];
            item.selected = !item.selected;
            updateSelectedItems();
            renderVisibleItems();
        }}

        // 展开选中
        function expandSelected() {{
            flattenedItems.forEach(item => {{
                if (item.selected && item.type === 'directory') {{
                    item.expanded = true;
                }}
            }});
            updateVisibility();
            renderVisibleItems();
        }}

        // 收起选中
        function collapseSelected() {{
            flattenedItems.forEach(item => {{
                if (item.selected && item.type === 'directory') {{
                    item.expanded = false;
                }}
            }});
            updateVisibility();
            renderVisibleItems();
        }}

        // 展开所有
        function expandAll() {{
            flattenedItems.forEach(item => {{
                if (item.type === 'directory') {{
                    item.expanded = true;
                }}
            }});
            updateVisibility();
            renderVisibleItems();
        }}

        // 收起所有
        function collapseAll() {{
            flattenedItems.forEach(item => {{
                if (item.type === 'directory') {{
                    item.expanded = false;
                }}
            }});
            updateVisibility();
            renderVisibleItems();
        }}

        // 展开选中到最深
        function expandSelectedDeep() {{
            const selected = flattenedItems.filter(item => item.selected);
            selected.forEach(item => {{
                if (item.type === 'directory') {{
                    // 找到所有子项
                    const startIndex = flattenedItems.indexOf(item);
                    let level = item.level;
                    let i = startIndex + 1;
                    while (i < flattenedItems.length && flattenedItems[i].level > level) {{
                        if (flattenedItems[i].type === 'directory') {{
                            flattenedItems[i].expanded = true;
                        }}
                        i++;
                    }}
                }}
            }});
            updateVisibility();
            renderVisibleItems();
            updateSelectedItems();
        }}

        // 收起选中到顶层
        function collapseSelectedTop() {{
            const selected = flattenedItems.filter(item => item.selected);
            selected.forEach(item => {{
                // 找到所有父项并收起
                let parent = findParent(flattenedItems.indexOf(item));
                while (parent) {{
                    parent.expanded = false;
                    parent = findParent(flattenedItems.indexOf(parent));
                }}
            }});
            updateVisibility();
            renderVisibleItems();
            updateSelectedItems();
        }}

        // 清除选择
        function clearSelection() {{
            flattenedItems.forEach(item => item.selected = false);
            updateSelectedItems();
            renderVisibleItems();
        }}

        // 更新选中项显示
        function updateSelectedItems() {{
            const selectedItemsContainer = document.getElementById('selectedItems');
            const selected = flattenedItems.filter(item => item.selected);
            
            if (selected.length === 0) {{
                selectedItemsContainer.classList.remove('has-items');
                selectedItemsContainer.innerHTML = '';
                return;
            }}

            selectedItemsContainer.classList.add('has-items');
            selectedItemsContainer.innerHTML = selected.map(item => `
                <span class="selected-item">
                    ${{item.type === 'directory' ? '📁' : '📄'}} ${{item.name}}
                    <span class="remove" onclick="unselectItem(${{flattenedItems.indexOf(item)}})">×</span>
                </span>
            `).join('');
        }}

        // 取消选中项
        function unselectItem(index) {{
            flattenedItems[index].selected = false;
            updateSelectedItems();
            renderVisibleItems();
        }}

        // 搜索功能
        const searchInput = document.getElementById('searchInput');
        const searchInContent = document.getElementById('searchInContent');
        const caseSensitive = document.getElementById('caseSensitive');

        function searchItems() {{
            const searchTerm = searchInput.value;
            const inContent = searchInContent.checked;
            const isCaseSensitive = caseSensitive.checked;
            
            if (!searchTerm) {{
                flattenedItems.forEach(item => {{
                    item.visible = true;
                    item.highlight = false;
                }});
                updateVisibility();
                renderVisibleItems();
                return;
            }}

            const searchValue = isCaseSensitive ? searchTerm : searchTerm.toLowerCase();
            
            flattenedItems.forEach(item => {{
                const itemName = isCaseSensitive ? item.name : item.name.toLowerCase();
                const matches = itemName.includes(searchValue);
                
                if (inContent) {{
                    item.visible = true;
                    item.highlight = matches;
                }} else {{
                    item.visible = matches;
                    item.highlight = matches;
                }}
            }});

            if (inContent) {{
                // 确保匹配项的父目录可见
                flattenedItems.forEach(item => {{
                    if (item.highlight) {{
                        let parent = findParent(flattenedItems.indexOf(item));
                        while (parent) {{
                            parent.visible = true;
                            parent.expanded = true;
                            parent = findParent(flattenedItems.indexOf(parent));
                        }}
                    }}
                }});
            }}

            updateVisibility();
            renderVisibleItems();
        }}

        // 添加搜索事件监听
        searchInput.addEventListener('input', searchItems);
        searchInContent.addEventListener('change', searchItems);
        caseSensitive.addEventListener('change', searchItems);

        // 优化滚动处理
        let scrollTimeout;
        tree.addEventListener('scroll', () => {{
            if (scrollTimeout) {{
                window.cancelAnimationFrame(scrollTimeout);
            }}
            scrollTimeout = window.requestAnimationFrame(() => {{
                renderVisibleItems();
            }});
        }});

        // 点击事件处理
        content.addEventListener('click', (e) => {{
            const item = e.target.closest('.tree-item');
            if (!item) return;
            
            const index = parseInt(item.dataset.index);
            if (e.target.classList.contains('toggle')) {{
                toggleItem(index);
            }} else {{
                toggleSelect(index);
            }}
        }});

        // 暂存功能
        let stagedItems = new Set();

        function stageSelected() {{
            const selected = flattenedItems.filter(item => item.selected);
            if (selected.length === 0) {{
                alert('请先选择要暂存的项目');
                return;
            }}

            selected.forEach(item => {{
                stagedItems.add({{
                    name: item.name,
                    type: item.type,
                    path: item.path
                }});
                // 清除选中状态
                item.selected = false;
            }});
            
            // 更新暂存区显示
            updateStagedItems();
            // 更新选中项显示
            updateSelectedItems();
            // 更新树形显示
            renderVisibleItems();
        }}

        function updateStagedItems() {{
            const stagedItemsContainer = document.getElementById('stagedItems');
            
            if (stagedItems.size === 0) {{
                stagedItemsContainer.innerHTML = '<div style="padding: 10px; text-align: center; color: #666;">暂无暂存项</div>';
                return;
            }}

            let html = '';
            stagedItems.forEach(item => {{
                html += `
                    <div class="staged-item">
                        <div class="staged-item-content">
                            <span>${{item.type === 'directory' ? '📁' : '📄'}} ${{item.name}}</span>
                        </div>
                        <span class="remove" onclick="unstageItem('${{item.path}}')">×</span>
                    </div>
                `;
            }});
            stagedItemsContainer.innerHTML = html;
        }}

        function unstageItem(path) {{
            for (let item of stagedItems) {{
                if (item.path === path) {{
                    stagedItems.delete(item);
                    break;
                }}
            }}
            updateStagedItems();
        }}

        function clearStaged() {{
            stagedItems.clear();
            updateStagedItems();
        }}

        function saveStaged() {{
            if (stagedItems.size === 0) {{
                alert('暂存区为空，没有可保存的项目');
                return;
            }}

            const paths = Array.from(stagedItems).map(item => item.path);
            const content = paths.join('\\n');
            
            const element = document.createElement('a');
            const file = new Blob([content], {{type: 'text/plain'}});
            element.href = URL.createObjectURL(file);
            element.download = `staged_paths_${{new Date().toISOString().slice(0,19).replace(/[:-]/g, '')}}.txt`;
            
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
        }}

        // 初始化
        initializeTree(treeData);
        updateVisibility();
        renderVisibleItems();
    </script>
</body>
</html>
    """
    
    # 确保保存路径存在
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    # 保存HTML文件
    file_path = os.path.join(save_path, 'file_report.html')
    with codecs.open(file_path, 'w', 'utf-8') as f:
        f.write(html_content)
    return file_path

def generate_text_tree(tree_data, indent=""):
    result = []
    for item in tree_data:
        if item['type'] == 'file':
            result.append(f"{indent}├── 📄 {item['name']} ({item['size']})")
        else:
            result.append(f"{indent}├── 📁 {item['name']}")
            if 'children' in item:
                result.extend(generate_text_tree(item['children'], indent + "│   "))
    return result

def generate_markdown(tree_data, indent=""):
    result = []
    for item in tree_data:
        if item['type'] == 'file':
            result.append(f"{indent}* 📄 `{item['name']}` - {item['size']}")
        else:
            result.append(f"{indent}* 📁 **{item['name']}**")
            if 'children' in item:
                result.extend(generate_markdown(item['children'], indent + "  "))
    return result

def generate_json(tree_data, source_path):
    import json
    output = {
        "scan_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "source_path": source_path,
        "tree_data": tree_data
    }
    return json.dumps(output, ensure_ascii=False, indent=2)

def generate_xml(tree_data, source_path):
    def item_to_xml(item, indent="  "):
        if item['type'] == 'file':
            return f'{indent}<file name="{item["name"]}" size="{item["size"]}" type="{item["ext"]}"/>'
        else:
            result = [f'{indent}<directory name="{item["name"]}">']
            if 'children' in item:
                for child in item['children']:
                    result.append(item_to_xml(child, indent + "  "))
            result.append(f'{indent}</directory>')
            return '\n'.join(result)

    header = '<?xml version="1.0" encoding="UTF-8"?>\n'
    root_start = f'<file_tree scan_time="{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" source_path="{source_path}">\n'
    content = '\n'.join(item_to_xml(item) for item in tree_data)
    root_end = '\n</file_tree>'
    
    return header + root_start + content + root_end

def generate_csv(tree_data):
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Type', 'Name', 'Size', 'Extension', 'Path'])
    
    def add_to_csv(items, current_path=""):
        for item in items:
            path = current_path + "/" + item['name'] if current_path else item['name']
            if item['type'] == 'file':
                writer.writerow(['File', item['name'], item['size'], item['ext'], path])
            else:
                writer.writerow(['Directory', item['name'], '', '', path])
                if 'children' in item:
                    add_to_csv(item['children'], path)
    
    add_to_csv(tree_data)
    return output.getvalue()

def main():
    try:
        # 选择要扫描的目录
        source_path = select_directory()
        if not source_path:
            print("未选择目录，程序退出")
            return

        # 选择保存位置
        save_path = select_save_directory()
        if not save_path:
            print("未选择保存位置，程序退出")
            return

        print(f"开始扫描目录: {source_path}")
        print(f"文件将保存到: {save_path}")

        # 扫描目录
        tree_data = scan_directory(source_path)
        if not tree_data:
            print("扫描结果为空，请检查目录是否有访问权限")
            return

        # 生成并保存所有报告
        file_paths = []
        
        try:
            # 生成HTML报告
            html_path = generate_html(tree_data, source_path, save_path)
            file_paths.append(('HTML报告', html_path))
            
            # 生成文本树形报告
            txt_path = os.path.join(save_path, 'file_report.txt')
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f"扫描路径: {source_path}\n")
                f.write(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write('\n'.join(generate_text_tree(tree_data)))
            file_paths.append(('文本树形报告', txt_path))
            
            # 显示完成消息
            message = "文件已保存到以下位置：\n\n"
            for name, path in file_paths:
                message += f"{name}：{path}\n"
            
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo("完成", message)
            
            # 自动打开HTML报告
            import webbrowser
            webbrowser.open(f'file://{html_path}')
            
        except Exception as e:
            print(f"生成报告时出错: {str(e)}")
            messagebox.showerror("错误", f"生成报告时出错: {str(e)}")

    except Exception as e:
        print(f"程序运行出错: {str(e)}")
        messagebox.showerror("错误", f"程序运行出错: {str(e)}")
    
    finally:
        input("按回车键退出...")  # 防止窗口立即关闭

if __name__ == '__main__':
    main()
