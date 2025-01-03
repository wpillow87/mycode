from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import base64
import uuid
import webbrowser
from urllib.parse import parse_qs
import threading
import time

class DeviceHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/devices':
            try:
                # 确保devices.json文件存在
                if not os.path.exists('devices.json'):
                    with open('devices.json', 'w', encoding='utf-8') as f:
                        json.dump([], f)
                
                with open('devices.json', 'r', encoding='utf-8') as f:
                    data = f.read()
                
                self.send_response(200)
                # 添加禁用缓存的响应头
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(data.encode())
            except Exception as e:
                print(f"Error loading devices: {str(e)}")
                self.send_error(500, str(e))
        else:
            # 对于其他请求（如 HTML 文件），也添加禁用缓存的响应头
            self.send_response(200)
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/api/save':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                devices_data = json.loads(post_data.decode('utf-8'))
                
                # 确保images文件夹存在
                if not os.path.exists('images'):
                    os.makedirs('images')

                # 处理每个设备的图片
                for i, device in enumerate(devices_data):
                    if device.get('imageSrc', '').startswith('data:image'):
                        try:
                            # 从Base64提取图片数据
                            img_data = device['imageSrc'].split(',')[1]
                            img_binary = base64.b64decode(img_data)
                            
                            # 生成唯一文件名，包含设备索引
                            filename = f"device_{i}_{uuid.uuid4()}.jpg"
                            filepath = os.path.join('images', filename)
                            
                            # 保存图片
                            with open(filepath, 'wb') as f:
                                f.write(img_binary)
                            
                            # 使用相对路径保存
                            device['imageSrc'] = f'./images/{filename}'
                        except Exception as e:
                            print(f"Error saving image for device {i}: {str(e)}")
                            continue

                # 保存更新后的设备数据（包含分组信息）
                with open('devices.json', 'w', encoding='utf-8') as f:
                    json.dump(devices_data, f, ensure_ascii=False, indent=2)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())
            except Exception as e:
                print(f"Error saving devices: {str(e)}")
                self.send_error(500, str(e))
        else:
            return SimpleHTTPRequestHandler.do_POST(self)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def open_browser():
    # 等待服务器启动
    time.sleep(1)
    # 使用默认浏览器打开页面
    webbrowser.open('http://localhost:8000/power_calculator.html')

def cleanup_unused_images():
    # 获取所有已保存的设备数据
    if not os.path.exists('devices.json'):
        return
    
    with open('devices.json', 'r', encoding='utf-8') as f:
        devices = json.load(f)
    
    # 收集所有正在使用的图片文件名
    used_images = set()
    for device in devices:
        image_path = device.get('imageSrc', '')
        if image_path.startswith('./images/') or image_path.startswith('http://localhost:8000/images/'):
            filename = image_path.split('/')[-1]
            used_images.add(filename)
    
    # 检查images文件夹中的所有图片
    if not os.path.exists('images'):
        return
        
    for filename in os.listdir('images'):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            if filename not in used_images:
                try:
                    os.remove(os.path.join('images', filename))
                    print(f"已删除未使用的图片: {filename}")
                except Exception as e:
                    print(f"删除图片 {filename} 时出错: {str(e)}")

def run(server_class=HTTPServer, handler_class=DeviceHandler, port=8000):
    cleanup_unused_images()
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    threading.Thread(target=open_browser, daemon=True).start()
    httpd.serve_forever()

if __name__ == '__main__':
    run()
