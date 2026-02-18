# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import os
import re

class SQLMapGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SQLmap GUI")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)

        # 设置窗口图标和样式
        self.setup_styles()

        # 创建主界面
        self.create_widgets()

    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')

        # 配置样式
        style.configure('Title.TLabel', font=('微软雅黑', 16, 'bold'), background='#2c3e50', foreground='white')
        style.configure('Section.TLabel', font=('微软雅黑', 12, 'bold'), background='#ecf0f1')
        style.configure('Scan.TButton', font=('微软雅黑', 11, 'bold'))

    def create_widgets(self):
        """创建界面组件"""
        # 顶部标题栏
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', padx=5, pady=5)
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="SQLmap 图形化扫描工具",
                font=('微软雅黑', 18, 'bold'), bg='#2c3e50', fg='white').pack(pady=15)

        # 主容器
        main_container = tk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=5, pady=5)

        # 左侧面板 - 扫描选项
        left_panel = self.create_left_panel(main_container)
        left_panel.pack(side='left', fill='both', expand=True)

        # 中间面板 - URL和输出
        middle_panel = self.create_middle_panel(main_container)
        middle_panel.pack(side='left', fill='both', expand=True, padx=5)

        # 右侧面板 - 高级选项
        right_panel = self.create_right_panel(main_container)
        right_panel.pack(side='left', fill='both', expand=True)

        # 底部状态栏
        self.create_status_bar()

    def create_left_panel(self, parent):
        """创建左侧面板"""
        frame = tk.Frame(parent, bg='#ecf0f1')

        # URL快速选择
        url_frame = tk.LabelFrame(frame, text="快速选择", font=('微软雅黑', 10, 'bold'),
                                  bg='#ecf0f1', padx=10, pady=10)
        url_frame.pack(fill='x', padx=10, pady=10)

        targets = [
            ("SQL Labs", "http://127.0.0.1/sql-labs/Less-1/?id=1"),
            ("DVWA", "http://127.0.0.1/dvwa/vulnerabilities/sqli/"),
            ("Pikachu", "http://127.0.0.1/pikachu/vul/sqli/sqli_id.php"),
            ("Upload", "http://127.0.0.1/upload-labs/upload.php"),
        ]

        for name, url in targets:
            btn = tk.Button(url_frame, text=name, width=15,
                          command=lambda u=url: self.set_url(u),
                          bg='#3498db', fg='white', font=('微软雅黑', 9))
            btn.pack(pady=2)

        # 基础选项
        basic_frame = tk.LabelFrame(frame, text="基础选项", font=('微软雅黑', 10, 'bold'),
                                   bg='#ecf0f1', padx=10, pady=10)
        basic_frame.pack(fill='x', padx=10, pady=10)

        # 测试级别
        tk.Label(basic_frame, text="测试级别 (1-5):", bg='#ecf0f1').pack(anchor='w')
        self.level_var = tk.StringVar(value='2')
        level_frame = tk.Frame(basic_frame, bg='#ecf0f1')
        level_frame.pack(fill='x', pady=2)
        for i in range(1, 6):
            tk.Radiobutton(level_frame, text=str(i), variable=self.level_var,
                          value=str(i), bg='#ecf0f1').pack(side='left')

        # 风险级别
        tk.Label(basic_frame, text="风险级别 (1-3):", bg='#ecf0f1').pack(anchor='w', pady=(10,0))
        self.risk_var = tk.StringVar(value='1')
        risk_frame = tk.Frame(basic_frame, bg='#ecf0f1')
        risk_frame.pack(fill='x', pady=2)
        for i in range(1, 4):
            tk.Radiobutton(risk_frame, text=str(i), variable=self.risk_var,
                          value=str(i), bg='#ecf0f1').pack(side='left')

        # 线程数
        tk.Label(basic_frame, text="线程数:", bg='#ecf0f1').pack(anchor='w', pady=(10,0))
        self.threads_var = tk.StringVar(value="1")
        tk.Entry(basic_frame, textvariable=self.threads_var, width=10).pack(anchor='w')

        # 扫描选项
        scan_frame = tk.LabelFrame(frame, text="扫描选项", font=('微软雅黑', 10, 'bold'),
                                   bg='#ecf0f1', padx=10, pady=10)
        scan_frame.pack(fill='x', padx=10, pady=10)

        self.options = {}
        options_list = [
            ("current_db", "获取当前数据库"),
            ("current_user", "获取当前用户"),
            ("is_dba", "检查DBA权限"),
            ("dbs", "枚举数据库"),
            ("tables", "枚举表名"),
            ("columns", "枚举列名"),
            ("dump", "导出数据"),
            ("dump_all", "一键脱库"),
            ("batch", "默认应答"),
        ]

        for key, text in options_list:
            self.options[key] = tk.BooleanVar()
            tk.Checkbutton(scan_frame, text=text, variable=self.options[key],
                          bg='#ecf0f1').pack(anchor='w')

        return frame

    def create_middle_panel(self, parent):
        """创建中间面板"""
        frame = tk.Frame(parent, bg='white')

        # URL输入
        url_label = tk.Label(frame, text="目标URL", font=('微软雅黑', 12, 'bold'),
                           bg='white', fg='#2c3e50')
        url_label.pack(pady=(10,5))

        self.url_entry = tk.Entry(frame, font=('Consolas', 11), width=80,
                                 relief='solid', borderwidth=2)
        self.url_entry.pack(padx=20, fill='x', pady=5)
        self.url_entry.insert(0, "http://127.0.0.1/sql-labs/Less-1/?id=1")

        # 输出区域
        output_label = tk.Label(frame, text="扫描输出", font=('微软雅黑', 12, 'bold'),
                               bg='white', fg='#2c3e50')
        output_label.pack(pady=(20,5))

        # 输出文本框
        self.output_text = scrolledtext.ScrolledText(frame, height=25, width=80,
                                                    font=('Consolas', 10),
                                                    bg='#2d3436', fg='#ecf0f1',
                                                    relief='solid', borderwidth=2)
        self.output_text.pack(padx=20, pady=5, fill='both', expand=True)

        return frame

    def create_right_panel(self, parent):
        """创建右侧面板"""
        frame = tk.Frame(parent, bg='#ecf0f1')

        # 高级选项
        adv_frame = tk.LabelFrame(frame, text="高级选项", font=('微软雅黑', 10, 'bold'),
                                 bg='#ecf0f1', padx=10, pady=10)
        adv_frame.pack(fill='x', padx=10, pady=10)

        # 代理设置
        tk.Label(adv_frame, text="代理设置", bg='#ecf0f1').pack(anchor='w')
        self.proxy_var = tk.StringVar()
        tk.Entry(adv_frame, textvariable=self.proxy_var, width=25).pack(fill='x', pady=2)

        # 注入技术
        tk.Label(adv_frame, text="注入技术", bg='#ecf0f1').pack(anchor='w', pady=(10,0))
        self.technique_var = tk.StringVar(value="BUT")
        technique_combo = ttk.Combobox(adv_frame, textvariable=self.technique_var,
                                     values=["B", "E", "U", "S", "T", "Q", "BUT"],
                                     width=10, state='readonly')
        technique_combo.pack(fill='x', pady=2)

        # 数据库类型
        tk.Label(adv_frame, text="数据库类型", bg='#ecf0f1').pack(anchor='w', pady=(10,0))
        self.dbms_var = tk.StringVar()
        dbms_combo = ttk.Combobox(adv_frame, textvariable=self.dbms_var,
                               values=["mysql", "oracle", "postgresql", "mssql"],
                               width=15, state='readonly')
        dbms_combo.pack(fill='x', pady=2)

        # 自定义参数
        tk.Label(adv_frame, text="自定义参数", bg='#ecf0f1').pack(anchor='w', pady=(10,0))
        self.custom_var = tk.StringVar()
        tk.Entry(adv_frame, textvariable=self.custom_var, width=25).pack(fill='x', pady=2)

        # 操作按钮
        button_frame = tk.Frame(frame, bg='#ecf0f1')
        button_frame.pack(fill='x', padx=10, pady=20)

        self.scan_button = tk.Button(button_frame, text="开始扫描",
                                    command=self.start_scan,
                                    bg='#27ae60', fg='white',
                                    font=('微软雅黑', 11, 'bold'),
                                    padx=20, pady=10)
        self.scan_button.pack(fill='x', pady=5)

        clear_button = tk.Button(button_frame, text="清空输出",
                               command=self.clear_output,
                               bg='#e74c3c', fg='white',
                               font=('微软雅黑', 11),
                               padx=20, pady=5)
        clear_button.pack(fill='x', pady=5)

        help_button = tk.Button(button_frame, text="帮助",
                              command=self.show_help,
                              bg='#3498db', fg='white',
                              font=('微软雅黑', 11),
                              padx=20, pady=5)
        help_button.pack(fill='x', pady=5)

        return frame

    def create_status_bar(self):
        """创建状态栏"""
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")

        status_bar = tk.Label(self.root, textvariable=self.status_var,
                            relief='sunken', anchor='w',
                            bg='#95a5a6', fg='white',
                            font=('微软雅黑', 10))
        status_bar.pack(fill='x', side='bottom')

    def set_url(self, url):
        """设置URL"""
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url)
        self.status_var.set(f"已选择: {url}")

    def clear_output(self):
        """清空输出"""
        self.output_text.delete(1.0, tk.END)
        self.status_var.set("输出已清空")

    def show_help(self):
        """显示帮助"""
        help_text = """SQLmap GUI 使用说明

1. 在URL输入框中输入目标网址
2. 设置测试级别和风险级别
3. 选择需要的功能选项
4. 点击"开始扫描"开始测试
5. 查看扫描结果

注意：
- 请确保获得授权后再进行测试
- 建议先在测试环境使用
- 高风险级别可能导致系统不稳定

支持的靶场：
- SQL Labs: http://127.0.0.1/sql-labs/
- DVWA: http://127.0.0.1/dvwa/
- Pikachu: http://127.0.0.1/pikachu/"""

        messagebox.showinfo("使用说明", help_text)

    def start_scan(self):
        """开始扫描"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("错误", "请输入目标URL！")
            return

        if not url.startswith(('http://', 'https://')):
            messagebox.showerror("错误", "URL必须以http://或https://开头！")
            return

        # 清空输出
        self.clear_output()

        # 禁用按钮
        self.scan_button.config(state='disabled')
        self.status_var.set("正在扫描...")

        # 在新线程中执行扫描
        scan_thread = threading.Thread(target=self.run_scan, args=(url,))
        scan_thread.daemon = True
        scan_thread.start()

    def run_scan(self, url):
        """执行SQLMap扫描"""
        try:
            # 构建命令
            cmd = ['python', 'sqlmap.py', '-u', url]

            # 添加选项
            cmd.append(f'--level={self.level_var.get()}')
            cmd.append(f'--risk={self.risk_var.get()}')

            if self.threads_var.get():
                cmd.append(f'--threads={self.threads_var.get()}')

            # 添加勾选的选项
            if self.options['current_db'].get():
                cmd.append('--current-db')
            if self.options['current_user'].get():
                cmd.append('--current-user')
            if self.options['is_dba'].get():
                cmd.append('--is-dba')
            if self.options['dbs'].get():
                cmd.append('--dbs')
            if self.options['tables'].get():
                cmd.append('--tables')
            if self.options['columns'].get():
                cmd.append('--columns')
            if self.options['dump'].get():
                cmd.append('--dump')
            if self.options['dump_all'].get():
                cmd.append('--dump-all')
            if self.options['batch'].get():
                cmd.append('--batch')

            # 添加高级选项
            if self.technique_var.get():
                cmd.append(f'--technique={self.technique_var.get()}')
            if self.dbms_var.get():
                cmd.append(f'--dbms={self.dbms_var.get()}')
            if self.custom_var.get():
                cmd.append(self.custom_var.get())

            self.output_text.insert(tk.END, f"执行命令: {' '.join(cmd)}\n")
            self.output_text.insert(tk.END, "="*50 + "\n\n")

            # 执行命令并实时输出
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    universal_newlines=True, bufsize=1)

            for line in iter(process.stdout.readline, ''):
                # 过滤无用信息
                line = line.strip()
                if line and not line.startswith('Enter'):
                    self.output_text.insert(tk.END, line + "\n")
                    self.output_text.see(tk.END)

            process.wait()

            if process.returncode == 0:
                self.output_text.insert(tk.END, "\n扫描完成！\n")
                self.status_var.set("扫描完成")
            else:
                self.output_text.insert(tk.END, f"\n扫描失败，返回码: {process.returncode}\n")
                self.status_var.set("扫描失败")

        except Exception as e:
            self.output_text.insert(tk.END, f"\n错误: {str(e)}\n")
            self.status_var.set("发生错误")
        finally:
            # 重新启用按钮
            self.scan_button.config(state='normal')
            if hasattr(process, 'stdout'):
                process.stdout.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = SQLMapGUI(root)
    root.mainloop()