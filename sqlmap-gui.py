# -*- coding: utf-8 -*-
"""
SQLMap GUI v1.0 - 图形化SQL注入扫描工具
基于汉化版sqlmap: https://github.com/honmashironeko/sqlmap-gui/
作者: bae
日期: 2026/2/28
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
import os
import json
import platform

# 检测操作系统
IS_WINDOWS = platform.system() == 'Windows'

# 配色方案
COLORS = {
    'bg_primary': '#0f172a',
    'bg_secondary': '#1e293b',
    'bg_card': '#334155',
    'bg_input': '#1e293b',
    'accent_primary': '#3b82f6',
    'accent_success': '#10b981',
    'accent_warning': '#f59e0b',
    'accent_danger': '#ef4444',
    'accent_info': '#06b6d4',
    'text_primary': '#f8fafc',
    'text_secondary': '#94a3b8',
    'border': '#475569',
    'terminal_bg': '#0d1117',
    'terminal_green': '#3fb950',
    'terminal_yellow': '#d29922',
    'terminal_red': '#f85149',
    'terminal_blue': '#58a6ff',
}

class SQLMapGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SQLMap GUI v1.0")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        self.root.configure(bg=COLORS['bg_primary'])
        
        # 配置
        self.config_file = "sqlmap_gui_config.json"
        self.python_cmd = 'python' if IS_WINDOWS else 'python3'
        self.font_size = 10
        self.load_settings()
        
        # 扫描状态
        self.scan_process = None
        self.is_scanning = False
        self.is_paused = False
        self.current_tab = 0
        
        # 创建界面
        self.create_widgets()
        self.load_config()
    
    def create_widgets(self):
        # 顶部标题栏
        self.create_header()
        
        # 主内容区
        main = tk.Frame(self.root, bg=COLORS['bg_primary'])
        main.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 左侧面板
        left = tk.Frame(main, bg=COLORS['bg_primary'], width=420)
        left.pack(side='left', fill='y', padx=(0, 10))
        left.pack_propagate(False)
        self.create_left_panel(left)
        
        # 右侧面板
        right = tk.Frame(main, bg=COLORS['bg_primary'])
        right.pack(side='left', fill='both', expand=True)
        self.create_right_panel(right)
        
        # 状态栏
        self.create_status_bar()
    
    def create_header(self):
        header = tk.Frame(self.root, bg=COLORS['bg_secondary'], height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # 标题
        tk.Label(header, text="🛡️ SQLMap GUI", 
                font=('Microsoft YaHei', 18, 'bold'),
                bg=COLORS['bg_secondary'], fg=COLORS['accent_primary']).pack(side='left', padx=15, pady=10)
        
        tk.Label(header, text="v1.0", 
                font=('Microsoft YaHei', 10),
                bg=COLORS['bg_secondary'], fg=COLORS['text_secondary']).pack(side='left', pady=15)
        
        # 按钮
        btn_frame = tk.Frame(header, bg=COLORS['bg_secondary'])
        btn_frame.pack(side='right', padx=15, pady=12)
        
        buttons = [
            ("⚙️ 设置", self.show_settings, COLORS['bg_card']),
            ("📋 命令", self.show_command, COLORS['accent_info']),
            ("💾 保存", self.save_config, COLORS['accent_success']),
            ("📂 加载", self.load_config_dialog, COLORS['accent_warning']),
            ("❓ 帮助", self.show_help, COLORS['bg_card']),
        ]
        
        for text, cmd, color in buttons:
            btn = tk.Button(btn_frame, text=text, command=cmd,
                           bg=color, fg=COLORS['text_primary'],
                           font=('Microsoft YaHei', 9), relief='flat',
                           padx=10, pady=5, cursor='hand2')
            btn.pack(side='left', padx=3)
    
    def create_left_panel(self, parent):
        # 标签页按钮
        tab_frame = tk.Frame(parent, bg=COLORS['bg_primary'])
        tab_frame.pack(fill='x', pady=(0, 5))
        
        self.tab_buttons = []
        tabs = [("🎯 目标", 0), ("📡 请求", 1), ("💉 注入", 2), ("📊 枚举", 3), ("⚙️ 高级", 4)]
        
        for text, idx in tabs:
            btn = tk.Button(tab_frame, text=text, 
                           command=lambda i=idx: self.switch_tab(i),
                           bg=COLORS['bg_card'] if idx != 0 else COLORS['accent_primary'],
                           fg=COLORS['text_primary'],
                           font=('Microsoft YaHei', 10), relief='flat',
                           padx=8, pady=5, cursor='hand2')
            btn.pack(side='left', padx=2)
            self.tab_buttons.append(btn)
        
        # 创建Canvas用于滚动
        self.canvas = tk.Canvas(parent, bg=COLORS['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # 创建内容框架
        self.content_frame = tk.Frame(self.canvas, bg=COLORS['bg_primary'])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw", width=400)
        
        self.content_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        
        # 鼠标滚轮
        def on_mousewheel(event):
            if IS_WINDOWS:
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            else:
                self.canvas.yview_scroll(int(-1*event.delta), "units")
        
        self.canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # 创建各个标签页
        self.tab_frames = []
        for i in range(5):
            frame = tk.Frame(self.content_frame, bg=COLORS['bg_primary'])
            self.create_tab_content(frame, i)
            self.tab_frames.append(frame)
        
        self.tab_frames[0].pack(fill='both', expand=True)
    
    def create_tab_content(self, parent, tab_idx):
        if tab_idx == 0:
            self.create_target_tab(parent)
        elif tab_idx == 1:
            self.create_request_tab(parent)
        elif tab_idx == 2:
            self.create_injection_tab(parent)
        elif tab_idx == 3:
            self.create_enum_tab(parent)
        elif tab_idx == 4:
            self.create_advanced_tab(parent)
    
    def create_card(self, parent, title):
        card = tk.LabelFrame(parent, text=title, 
                            font=('Microsoft YaHei', 11, 'bold'),
                            bg=COLORS['bg_card'], fg=COLORS['accent_primary'],
                            padx=10, pady=8)
        card.pack(fill='x', pady=5, padx=2)
        return card
    
    def create_entry(self, parent, textvariable=None, width=40, show=None):
        entry = tk.Entry(parent, textvariable=textvariable, width=width, show=show or '',
                        font=('Microsoft YaHei', 10),
                        bg=COLORS['bg_input'], fg=COLORS['text_primary'],
                        insertbackground=COLORS['accent_primary'],
                        relief='flat', highlightthickness=1,
                        highlightcolor=COLORS['accent_primary'],
                        highlightbackground=COLORS['border'])
        entry.pack(fill='x', pady=3)
        return entry
    
    def create_target_tab(self, parent):
        # 目标URL
        card = self.create_card(parent, "目标URL")
        self.url_var = tk.StringVar()
        self.create_entry(card, self.url_var)
        
        # 快速选择
        quick = tk.Frame(card, bg=COLORS['bg_card'])
        quick.pack(fill='x', pady=5)
        
        for name, url in [("SQL Labs", "http://127.0.0.1/sql-labs/Less-1/?id=1"),
                          ("DVWA", "http://127.0.0.1/dvwa/vulnerabilities/sqli/?id=1"),
                          ("Pikachu", "http://127.0.0.1/pikachu/vul/sqli/sqli_id.php?id=1")]:
            btn = tk.Button(quick, text=name, command=lambda u=url: self.url_var.set(u),
                           bg=COLORS['accent_primary'], fg=COLORS['text_primary'],
                           font=('Microsoft YaHei', 9), relief='flat', padx=8, pady=3)
            btn.pack(side='left', padx=2)
        
        # 批量目标
        card2 = self.create_card(parent, "批量目标")
        
        tk.Label(card2, text="URL列表文件:", bg=COLORS['bg_card'], fg=COLORS['text_secondary'],
                font=('Microsoft YaHei', 10)).pack(anchor='w')
        
        f1 = tk.Frame(card2, bg=COLORS['bg_card'])
        f1.pack(fill='x', pady=3)
        self.url_file_var = tk.StringVar()
        tk.Entry(f1, textvariable=self.url_file_var, font=('Microsoft YaHei', 10),
                bg=COLORS['bg_input'], fg=COLORS['text_primary'], relief='flat').pack(side='left', fill='x', expand=True)
        tk.Button(f1, text="浏览", command=lambda: self.browse_file(self.url_file_var),
                 bg=COLORS['accent_info'], fg=COLORS['text_primary'], relief='flat', padx=10).pack(side='left', padx=5)
        
        tk.Label(card2, text="HTTP请求文件:", bg=COLORS['bg_card'], fg=COLORS['text_secondary'],
                font=('Microsoft YaHei', 10)).pack(anchor='w', pady=(8, 0))
        
        f2 = tk.Frame(card2, bg=COLORS['bg_card'])
        f2.pack(fill='x', pady=3)
        self.req_file_var = tk.StringVar()
        tk.Entry(f2, textvariable=self.req_file_var, font=('Microsoft YaHei', 10),
                bg=COLORS['bg_input'], fg=COLORS['text_primary'], relief='flat').pack(side='left', fill='x', expand=True)
        tk.Button(f2, text="浏览", command=lambda: self.browse_file(self.req_file_var),
                 bg=COLORS['accent_info'], fg=COLORS['text_primary'], relief='flat', padx=10).pack(side='left', padx=5)
        
        tk.Label(card2, text="Google Dork:", bg=COLORS['bg_card'], fg=COLORS['text_secondary'],
                font=('Microsoft YaHei', 10)).pack(anchor='w', pady=(8, 0))
        self.dork_var = tk.StringVar()
        self.create_entry(card2, self.dork_var)
    
    def create_request_tab(self, parent):
        # POST数据
        card = self.create_card(parent, "POST数据")
        self.post_var = tk.StringVar()
        self.create_entry(card, self.post_var)
        tk.Label(card, text="格式: id=1&name=test", bg=COLORS['bg_card'], 
                fg=COLORS['text_secondary'], font=('Microsoft YaHei', 9)).pack(anchor='w')
        
        # Cookie
        card2 = self.create_card(parent, "Cookie")
        self.cookie_var = tk.StringVar()
        self.create_entry(card2, self.cookie_var)
        
        # User-Agent
        card3 = self.create_card(parent, "User-Agent")
        self.ua_var = tk.StringVar()
        self.create_entry(card3, self.ua_var)
        self.random_ua_var = tk.BooleanVar()
        tk.Checkbutton(card3, text="使用随机User-Agent", variable=self.random_ua_var,
                      bg=COLORS['bg_card'], fg=COLORS['text_primary'],
                      selectcolor=COLORS['bg_secondary'], font=('Microsoft YaHei', 10)).pack(anchor='w', pady=3)
        
        # Headers
        card4 = self.create_card(parent, "自定义Headers")
        self.headers_text = tk.Text(card4, height=3, font=('Consolas', 10),
                                   bg=COLORS['bg_input'], fg=COLORS['text_primary'],
                                   relief='flat', wrap='word')
        self.headers_text.pack(fill='x', pady=3)
        tk.Label(card4, text="每行一个: Name: Value", bg=COLORS['bg_card'], 
                fg=COLORS['text_secondary'], font=('Microsoft YaHei', 9)).pack(anchor='w')
        
        # 代理
        card5 = self.create_card(parent, "代理设置")
        self.proxy_var = tk.StringVar()
        self.create_entry(card5, self.proxy_var)
        
        f = tk.Frame(card5, bg=COLORS['bg_card'])
        f.pack(fill='x', pady=3)
        self.tor_var = tk.BooleanVar()
        tk.Checkbutton(f, text="使用Tor", variable=self.tor_var,
                      bg=COLORS['bg_card'], fg=COLORS['text_primary'],
                      selectcolor=COLORS['bg_secondary'], font=('Microsoft YaHei', 10)).pack(side='left', padx=(0, 15))
        self.check_tor_var = tk.BooleanVar()
        tk.Checkbutton(f, text="检查Tor", variable=self.check_tor_var,
                      bg=COLORS['bg_card'], fg=COLORS['text_primary'],
                      selectcolor=COLORS['bg_secondary'], font=('Microsoft YaHei', 10)).pack(side='left')
    
    def create_injection_tab(self, parent):
        # 检测设置
        card = self.create_card(parent, "检测设置")
        
        tk.Label(card, text="测试级别 (Level):", bg=COLORS['bg_card'], 
                fg=COLORS['text_primary'], font=('Microsoft YaHei', 10, 'bold')).pack(anchor='w')
        
        f1 = tk.Frame(card, bg=COLORS['bg_card'])
        f1.pack(fill='x', pady=5)
        self.level_var = tk.IntVar(value=1)
        for i in range(1, 6):
            tk.Radiobutton(f1, text=str(i), variable=self.level_var, value=i,
                          bg=COLORS['bg_card'], fg=COLORS['text_primary'],
                          selectcolor=COLORS['accent_primary'], font=('Microsoft YaHei', 10)).pack(side='left', padx=5)
        
        tk.Label(card, text="风险级别 (Risk):", bg=COLORS['bg_card'], 
                fg=COLORS['text_primary'], font=('Microsoft YaHei', 10, 'bold')).pack(anchor='w', pady=(10, 0))
        
        f2 = tk.Frame(card, bg=COLORS['bg_card'])
        f2.pack(fill='x', pady=5)
        self.risk_var = tk.IntVar(value=1)
        for i in range(1, 4):
            tk.Radiobutton(f2, text=str(i), variable=self.risk_var, value=i,
                          bg=COLORS['bg_card'], fg=COLORS['text_primary'],
                          selectcolor=COLORS['accent_primary'], font=('Microsoft YaHei', 10)).pack(side='left', padx=5)
        
        # 注入技术
        card2 = self.create_card(parent, "注入技术")
        self.techniques = {}
        for code, name in [('B', '布尔盲注'), ('E', '报错注入'), ('U', '联合查询'),
                          ('S', '堆叠查询'), ('T', '时间盲注'), ('Q', '内联查询')]:
            var = tk.BooleanVar(value=True)
            self.techniques[code] = var
            tk.Checkbutton(card2, text=f"{code} - {name}", variable=var,
                          bg=COLORS['bg_card'], fg=COLORS['text_primary'],
                          selectcolor=COLORS['bg_secondary'], font=('Microsoft YaHei', 10)).pack(anchor='w', pady=2)
        
        # 数据库类型
        card3 = self.create_card(parent, "数据库类型")
        self.dbms_var = tk.StringVar(value="自动检测")
        dbms = ttk.Combobox(card3, textvariable=self.dbms_var, state='readonly',
                           values=['自动检测', 'MySQL', 'Oracle', 'PostgreSQL', 'Microsoft SQL Server', 'SQLite'],
                           font=('Microsoft YaHei', 10))
        dbms.pack(fill='x', pady=3)
        
        # 注入参数
        card4 = self.create_card(parent, "注入参数")
        self.param_var = tk.StringVar()
        self.create_entry(card4, self.param_var)
        tk.Label(card4, text="指定要测试的参数名", bg=COLORS['bg_card'], 
                fg=COLORS['text_secondary'], font=('Microsoft YaHei', 9)).pack(anchor='w')
    
    def create_enum_tab(self, parent):
        # 枚举选项
        card = self.create_card(parent, "枚举选项")
        
        self.enum_options = {}
        enums = [
            ('banner', '获取Banner', True),
            ('current_user', '当前用户', False),
            ('current_db', '当前数据库', False),
            ('hostname', '主机名', False),
            ('is_dba', '检查DBA权限', False),
            ('users', '枚举所有用户', False),
            ('passwords', '枚举密码哈希', False),
            ('privileges', '枚举权限', False),
            ('dbs', '枚举数据库', False),
            ('tables', '枚举表', False),
            ('columns', '枚举列', False),
            ('schema', '枚举模式', False),
            ('dump', '导出数据', False),
            ('dump_all', '导出所有数据', False),
        ]
        
        for key, name, default in enums:
            var = tk.BooleanVar(value=default)
            self.enum_options[key] = var
            tk.Checkbutton(card, text=name, variable=var,
                          bg=COLORS['bg_card'], fg=COLORS['text_primary'],
                          selectcolor=COLORS['bg_secondary'], font=('Microsoft YaHei', 10)).pack(anchor='w', pady=2)
        
        # 指定目标
        card2 = self.create_card(parent, "指定目标")
        
        tk.Label(card2, text="数据库 (-D):", bg=COLORS['bg_card'], 
                fg=COLORS['text_secondary'], font=('Microsoft YaHei', 10)).pack(anchor='w')
        self.db_var = tk.StringVar()
        self.create_entry(card2, self.db_var)
        
        tk.Label(card2, text="表名 (-T):", bg=COLORS['bg_card'], 
                fg=COLORS['text_secondary'], font=('Microsoft YaHei', 10)).pack(anchor='w', pady=(8, 0))
        self.table_var = tk.StringVar()
        self.create_entry(card2, self.table_var)
        
        tk.Label(card2, text="列名 (-C):", bg=COLORS['bg_card'], 
                fg=COLORS['text_secondary'], font=('Microsoft YaHei', 10)).pack(anchor='w', pady=(8, 0))
        self.column_var = tk.StringVar()
        self.create_entry(card2, self.column_var)
    
    def create_advanced_tab(self, parent):
        # 性能设置
        card = self.create_card(parent, "性能设置")
        
        tk.Label(card, text="线程数:", bg=COLORS['bg_card'], 
                fg=COLORS['text_primary'], font=('Microsoft YaHei', 10)).pack(anchor='w')
        self.threads_var = tk.IntVar(value=1)
        tk.Scale(card, from_=1, to=20, orient='horizontal', variable=self.threads_var,
                bg=COLORS['bg_card'], fg=COLORS['text_primary'], 
                highlightthickness=0, troughcolor=COLORS['bg_secondary']).pack(fill='x', pady=3)
        
        tk.Label(card, text="超时时间(秒):", bg=COLORS['bg_card'], 
                fg=COLORS['text_primary'], font=('Microsoft YaHei', 10)).pack(anchor='w', pady=(8, 0))
        self.timeout_var = tk.IntVar(value=30)
        self.create_entry(card, self.timeout_var)
        
        # Tamper脚本
        card2 = self.create_card(parent, "Tamper脚本")
        self.tamper_var = tk.StringVar()
        tamper = ttk.Combobox(card2, textvariable=self.tamper_var, state='readonly',
                             values=['', 'base64encode', 'between', 'charencode', 
                                    'equaltolike', 'greatest', 'randomcase', 
                                    'space2comment', 'space2dash', 'space2hash'],
                             font=('Microsoft YaHei', 10))
        tamper.pack(fill='x', pady=3)
        
        # OS访问
        card3 = self.create_card(parent, "操作系统访问")
        self.os_shell_var = tk.BooleanVar()
        tk.Checkbutton(card3, text="获取OS Shell (--os-shell)", variable=self.os_shell_var,
                      bg=COLORS['bg_card'], fg=COLORS['text_primary'],
                      selectcolor=COLORS['bg_secondary'], font=('Microsoft YaHei', 10)).pack(anchor='w', pady=3)
        
        # 其他选项
        card4 = self.create_card(parent, "其他选项")
        self.batch_var = tk.BooleanVar(value=True)
        tk.Checkbutton(card4, text="自动应答 (--batch)", variable=self.batch_var,
                      bg=COLORS['bg_card'], fg=COLORS['text_primary'],
                      selectcolor=COLORS['bg_secondary'], font=('Microsoft YaHei', 10)).pack(anchor='w', pady=3)
        self.flush_var = tk.BooleanVar()
        tk.Checkbutton(card4, text="刷新会话 (--flush-session)", variable=self.flush_var,
                      bg=COLORS['bg_card'], fg=COLORS['text_primary'],
                      selectcolor=COLORS['bg_secondary'], font=('Microsoft YaHei', 10)).pack(anchor='w', pady=3)
        
        tk.Label(card4, text="详细级别 (-v):", bg=COLORS['bg_card'], 
                fg=COLORS['text_primary'], font=('Microsoft YaHei', 10)).pack(anchor='w', pady=(8, 0))
        f = tk.Frame(card4, bg=COLORS['bg_card'])
        f.pack(fill='x', pady=3)
        self.verbose_var = tk.IntVar(value=1)
        for i in range(0, 7):
            tk.Radiobutton(f, text=str(i), variable=self.verbose_var, value=i,
                          bg=COLORS['bg_card'], fg=COLORS['text_primary'],
                          selectcolor=COLORS['accent_primary'], font=('Microsoft YaHei', 10)).pack(side='left', padx=5)
    
    def create_right_panel(self, parent):
        # 命令显示
        cmd_frame = tk.Frame(parent, bg=COLORS['bg_secondary'], height=50)
        cmd_frame.pack(fill='x', pady=(0, 8))
        cmd_frame.pack_propagate(False)
        
        tk.Label(cmd_frame, text="命令:", bg=COLORS['bg_secondary'], 
                fg=COLORS['text_secondary'], font=('Microsoft YaHei', 11, 'bold')).pack(side='left', padx=10, pady=12)
        
        self.cmd_var = tk.StringVar(value=f"{self.python_cmd} sqlmap.py -u \"\" --batch")
        self.cmd_entry = tk.Entry(cmd_frame, textvariable=self.cmd_var,
                                 font=('Consolas', self.font_size),
                                 bg=COLORS['bg_secondary'], fg=COLORS['accent_info'],
                                 insertbackground=COLORS['text_primary'],
                                 relief='flat', highlightthickness=0)
        self.cmd_entry.pack(side='left', fill='x', expand=True, padx=5, pady=10)
        
        tk.Button(cmd_frame, text="编辑", command=self.edit_cmd,
                 bg=COLORS['accent_info'], fg=COLORS['text_primary'], 
                 relief='flat', padx=10).pack(side='left', padx=3)
        tk.Button(cmd_frame, text="复制", command=self.copy_cmd,
                 bg=COLORS['accent_success'], fg=COLORS['text_primary'], 
                 relief='flat', padx=10).pack(side='left', padx=3)
        
        # 终端输出
        term_frame = tk.Frame(parent, bg=COLORS['terminal_bg'])
        term_frame.pack(fill='both', expand=True)
        
        # 终端标题栏
        term_header = tk.Frame(term_frame, bg=COLORS['bg_secondary'], height=35)
        term_header.pack(fill='x')
        term_header.pack_propagate(False)
        
        tk.Label(term_header, text="🖥️ 终端输出", bg=COLORS['bg_secondary'],
                fg=COLORS['text_primary'], font=('Microsoft YaHei', 11, 'bold')).pack(side='left', padx=10, pady=5)
        
        btn_frame = tk.Frame(term_header, bg=COLORS['bg_secondary'])
        btn_frame.pack(side='right', padx=10, pady=3)
        
        for text, cmd, color in [("清空", self.clear_output, COLORS['accent_danger']),
                                  ("复制", self.copy_output, COLORS['accent_info']),
                                  ("保存", self.save_output, COLORS['accent_success'])]:
            tk.Button(btn_frame, text=text, command=cmd, bg=color,
                     fg=COLORS['text_primary'], relief='flat', padx=12).pack(side='left', padx=2)
        
        # 终端文本框
        self.terminal = tk.Text(term_frame, wrap='word',
                               font=('Consolas', self.font_size),
                               bg=COLORS['terminal_bg'], fg=COLORS['text_primary'],
                               relief='flat', padx=10, pady=10)
        self.terminal.pack(fill='both', expand=True, side='left')
        
        scrollbar = ttk.Scrollbar(term_frame, command=self.terminal.yview)
        scrollbar.pack(side='right', fill='y')
        self.terminal.config(yscrollcommand=scrollbar.set)
        
        # 配置标签
        self.terminal.tag_configure('info', foreground=COLORS['terminal_blue'])
        self.terminal.tag_configure('success', foreground=COLORS['terminal_green'])
        self.terminal.tag_configure('warning', foreground=COLORS['terminal_yellow'])
        self.terminal.tag_configure('error', foreground=COLORS['terminal_red'])
        self.terminal.tag_configure('command', foreground=COLORS['terminal_yellow'])
        
        # 控制按钮
        ctrl_frame = tk.Frame(parent, bg=COLORS['bg_primary'], height=50)
        ctrl_frame.pack(fill='x', pady=(8, 0))
        ctrl_frame.pack_propagate(False)
        
        self.scan_btn = tk.Button(ctrl_frame, text="▶ 开始扫描", command=self.toggle_scan,
                                 bg=COLORS['accent_success'], fg=COLORS['text_primary'],
                                 font=('Microsoft YaHei', 11, 'bold'), relief='flat',
                                 padx=20, pady=6, cursor='hand2')
        self.scan_btn.pack(side='left', padx=10, pady=7)
        
        self.pause_btn = tk.Button(ctrl_frame, text="⏸ 暂停", command=self.toggle_pause,
                                  bg=COLORS['accent_warning'], fg=COLORS['text_primary'],
                                  font=('Microsoft YaHei', 11), relief='flat',
                                  padx=15, pady=6, cursor='hand2', state='disabled')
        self.pause_btn.pack(side='left', padx=5, pady=7)
        
        self.stop_btn = tk.Button(ctrl_frame, text="⏹ 停止", command=self.stop_scan,
                                 bg=COLORS['accent_danger'], fg=COLORS['text_primary'],
                                 font=('Microsoft YaHei', 11), relief='flat',
                                 padx=15, pady=6, cursor='hand2', state='disabled')
        self.stop_btn.pack(side='left', padx=5, pady=7)
        
        tk.Button(ctrl_frame, text="🔄 更新命令", command=self.update_cmd,
                 bg=COLORS['accent_info'], fg=COLORS['text_primary'],
                 font=('Microsoft YaHei', 11, 'bold'), relief='flat',
                 padx=15, pady=6, cursor='hand2').pack(side='left', padx=15, pady=7)
    
    def create_status_bar(self):
        status = tk.Frame(self.root, bg=COLORS['bg_secondary'], height=30)
        status.pack(fill='x', side='bottom')
        status.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="就绪")
        tk.Label(status, textvariable=self.status_var, bg=COLORS['bg_secondary'],
                fg=COLORS['text_secondary'], font=('Microsoft YaHei', 10)).pack(side='left', padx=15, pady=4)
        
        tk.Label(status, text="SQLMap GUI v1.0 | 作者: bae | 2026/2/28",
                bg=COLORS['bg_secondary'], fg=COLORS['text_secondary'],
                font=('Microsoft YaHei', 9)).pack(side='right', padx=15, pady=4)
    
    def switch_tab(self, idx):
        for i, btn in enumerate(self.tab_buttons):
            btn.config(bg=COLORS['accent_primary'] if i == idx else COLORS['bg_card'])
        self.tab_frames[self.current_tab].pack_forget()
        self.tab_frames[idx].pack(fill='both', expand=True)
        self.current_tab = idx
    
    def browse_file(self, var):
        filename = filedialog.askopenfilename(filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
        if filename:
            var.set(filename)
    
    def edit_cmd(self):
        self.cmd_entry.config(state='normal', bg=COLORS['bg_input'])
        self.cmd_entry.focus_set()
        self.status_var.set("编辑模式 - 修改后按Enter确认")
        self.cmd_entry.bind('<Return>', lambda e: self.cmd_entry.config(state='readonly', bg=COLORS['bg_secondary']) or self.status_var.set("命令已更新"))
    
    def copy_cmd(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.cmd_var.get())
        self.status_var.set("命令已复制")
    
    def update_cmd(self):
        cmd = self.build_command()
        self.cmd_var.set(' '.join(cmd))
        self.status_var.set("命令已更新")
    
    def build_command(self):
        # 从命令框获取命令，如果用户编辑过则使用编辑后的
        cmd_text = self.cmd_var.get()
        if cmd_text and cmd_text != f'{self.python_cmd} sqlmap.py -u "" --batch':
            # 解析命令
            parts = cmd_text.split()
            if len(parts) >= 2 and 'sqlmap.py' in parts[1]:
                return parts
        
        # 构建新命令
        cmd = [self.python_cmd, 'sqlmap.py']
        
        # 目标
        url = self.url_var.get().strip()
        if url:
            cmd.extend(['-u', url])
        elif self.url_file_var.get().strip():
            cmd.extend(['-m', self.url_file_var.get().strip()])
        elif self.req_file_var.get().strip():
            cmd.extend(['-r', self.req_file_var.get().strip()])
        elif self.dork_var.get().strip():
            cmd.extend(['-g', self.dork_var.get().strip()])
        
        # 请求
        if self.post_var.get().strip():
            cmd.extend(['--data', self.post_var.get().strip()])
        if self.cookie_var.get().strip():
            cmd.extend(['--cookie', self.cookie_var.get().strip()])
        if self.ua_var.get().strip():
            cmd.extend(['--user-agent', self.ua_var.get().strip()])
        if self.random_ua_var.get():
            cmd.append('--random-agent')
        
        # headers
        headers = self.headers_text.get(1.0, 'end').strip()
        if headers:
            for line in headers.split('\n'):
                if line.strip():
                    cmd.extend(['--header', line.strip()])
        
        # 代理
        if self.proxy_var.get().strip():
            cmd.extend(['--proxy', self.proxy_var.get().strip()])
        if self.tor_var.get():
            cmd.append('--tor')
        if self.check_tor_var.get():
            cmd.append('--check-tor')
        
        # 注入
        cmd.extend(['--level', str(self.level_var.get())])
        cmd.extend(['--risk', str(self.risk_var.get())])
        
        techs = ''.join([k for k, v in self.techniques.items() if v.get()])
        if techs:
            cmd.extend(['--technique', techs])
        
        if self.dbms_var.get() != '自动检测':
            cmd.extend(['--dbms', self.dbms_var.get()])
        if self.param_var.get().strip():
            cmd.extend(['-p', self.param_var.get().strip()])
        
        # 枚举
        for key, var in self.enum_options.items():
            if var.get():
                cmd.append(f'--{key.replace("_", "-")}')
        
        if self.db_var.get().strip():
            cmd.extend(['-D', self.db_var.get().strip()])
        if self.table_var.get().strip():
            cmd.extend(['-T', self.table_var.get().strip()])
        if self.column_var.get().strip():
            cmd.extend(['-C', self.column_var.get().strip()])
        
        # 高级
        cmd.extend(['--threads', str(self.threads_var.get())])
        cmd.extend(['--timeout', str(self.timeout_var.get())])
        
        if self.tamper_var.get():
            cmd.extend(['--tamper', self.tamper_var.get()])
        if self.os_shell_var.get():
            cmd.append('--os-shell')
        if self.batch_var.get():
            cmd.append('--batch')
        if self.flush_var.get():
            cmd.append('--flush-session')
        
        cmd.extend(['-v', str(self.verbose_var.get())])
        
        return cmd
    
    def toggle_scan(self):
        if self.is_scanning:
            return
        
        cmd = self.build_command()
        if len(cmd) <= 2:
            messagebox.showerror("错误", "请先设置目标URL")
            return
        
        self.is_scanning = True
        self.is_paused = False
        self.scan_btn.config(text="⏳ 扫描中...", state='disabled')
        self.pause_btn.config(state='normal')
        self.stop_btn.config(state='normal')
        self.status_var.set("正在扫描...")
        
        self.terminal.delete(1.0, 'end')
        self.append_terminal(f"$ {' '.join(cmd)}\n\n", 'command')
        
        thread = threading.Thread(target=self.run_scan, args=(cmd,))
        thread.daemon = True
        thread.start()
    
    def run_scan(self, cmd):
        try:
            self.scan_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True, bufsize=1,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if IS_WINDOWS else 0
            )
            
            for line in iter(self.scan_process.stdout.readline, ''):
                if not self.is_scanning:
                    break
                
                while self.is_paused and self.is_scanning:
                    import time
                    time.sleep(0.1)
                
                # 检测标签
                tag = None
                if '[INFO]' in line or '[*]' in line:
                    tag = 'info'
                elif '[SUCCESS]' in line or '[+]' in line:
                    tag = 'success'
                elif '[WARNING]' in line or '[!]' in line:
                    tag = 'warning'
                elif '[ERROR]' in line or '[-]' in line:
                    tag = 'error'
                
                self.append_terminal(line, tag)
            
            self.scan_process.wait()
            
            if self.scan_process.returncode == 0:
                self.append_terminal("\n[+] 扫描完成!\n", 'success')
                self.status_var.set("扫描完成")
            else:
                self.append_terminal(f"\n[*] 扫描结束 (返回码: {self.scan_process.returncode})\n", 'info')
                self.status_var.set("扫描结束")
                
        except Exception as e:
            self.append_terminal(f"\n[ERROR] {str(e)}\n", 'error')
            self.status_var.set("发生错误")
        finally:
            self.is_scanning = False
            self.is_paused = False
            self.scan_btn.config(text="▶ 开始扫描", state='normal')
            self.pause_btn.config(text="⏸ 暂停", state='disabled')
            self.stop_btn.config(state='disabled')
    
    def append_terminal(self, text, tag=None):
        self.terminal.insert('end', text, tag)
        self.terminal.see('end')
    
    def toggle_pause(self):
        if not self.is_scanning:
            return
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.config(text="▶ 继续")
            self.status_var.set("已暂停")
        else:
            self.pause_btn.config(text="⏸ 暂停")
            self.status_var.set("继续扫描...")
    
    def stop_scan(self):
        if self.scan_process:
            try:
                if IS_WINDOWS:
                    self.scan_process.send_signal(subprocess.signal.CTRL_BREAK_EVENT)
                else:
                    self.scan_process.terminate()
            except:
                pass
        self.is_scanning = False
        self.is_paused = False
        self.append_terminal("\n[!] 扫描已停止\n", 'warning')
        self.status_var.set("扫描已停止")
        self.scan_btn.config(text="▶ 开始扫描", state='normal')
        self.pause_btn.config(text="⏸ 暂停", state='disabled')
        self.stop_btn.config(state='disabled')
    
    def clear_output(self):
        self.terminal.delete(1.0, 'end')
        self.status_var.set("输出已清空")
    
    def copy_output(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.terminal.get(1.0, 'end'))
        self.status_var.set("输出已复制")
    
    def save_output(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.terminal.get(1.0, 'end'))
            self.status_var.set(f"已保存: {filename}")
    
    def show_settings(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("设置")
        dialog.geometry("400x250")
        dialog.configure(bg=COLORS['bg_primary'])
        dialog.transient(self.root)
        
        tk.Label(dialog, text="⚙️ 设置", bg=COLORS['bg_primary'], 
                fg=COLORS['text_primary'], font=('Microsoft YaHei', 14, 'bold')).pack(pady=15)
        
        # Python命令
        frame1 = tk.Frame(dialog, bg=COLORS['bg_primary'])
        frame1.pack(fill='x', padx=20, pady=5)
        tk.Label(frame1, text="Python命令:", bg=COLORS['bg_primary'],
                fg=COLORS['text_primary'], font=('Microsoft YaHei', 10)).pack(anchor='w')
        python_var = tk.StringVar(value=self.python_cmd)
        tk.Entry(frame1, textvariable=python_var, font=('Microsoft YaHei', 10),
                bg=COLORS['bg_input'], fg=COLORS['text_primary'], relief='flat').pack(fill='x', pady=3)
        
        # 字体大小
        frame2 = tk.Frame(dialog, bg=COLORS['bg_primary'])
        frame2.pack(fill='x', padx=20, pady=5)
        tk.Label(frame2, text="字体大小:", bg=COLORS['bg_primary'],
                fg=COLORS['text_primary'], font=('Microsoft YaHei', 10)).pack(anchor='w')
        font_var = tk.IntVar(value=self.font_size)
        tk.Scale(frame2, from_=8, to=16, orient='horizontal', variable=font_var,
                bg=COLORS['bg_primary'], fg=COLORS['text_primary'],
                highlightthickness=0, troughcolor=COLORS['bg_secondary']).pack(fill='x')
        
        def save():
            self.python_cmd = python_var.get()
            self.font_size = font_var.get()
            self.save_settings()
            self.terminal.config(font=('Consolas', self.font_size))
            self.cmd_entry.config(font=('Consolas', self.font_size))
            messagebox.showinfo("成功", "设置已保存", parent=dialog)
            dialog.destroy()
        
        tk.Button(dialog, text="保存", command=save, bg=COLORS['accent_success'],
                 fg=COLORS['text_primary'], relief='flat', padx=20, pady=5).pack(pady=15)
    
    def show_command(self):
        cmd = self.build_command()
        cmd_str = ' '.join(cmd)
        
        dialog = tk.Toplevel(self.root)
        dialog.title("命令预览")
        dialog.geometry("700x200")
        dialog.configure(bg=COLORS['bg_primary'])
        dialog.transient(self.root)
        
        tk.Label(dialog, text="生成的命令:", bg=COLORS['bg_primary'],
                fg=COLORS['text_primary'], font=('Microsoft YaHei', 12, 'bold')).pack(pady=10)
        
        text = tk.Text(dialog, wrap='word', font=('Consolas', 11),
                      bg=COLORS['bg_secondary'], fg=COLORS['text_primary'],
                      relief='flat', padx=10, pady=10, height=4)
        text.pack(fill='x', padx=20, pady=5)
        text.insert(1.0, cmd_str)
        text.config(state='disabled')
        
        def copy():
            self.root.clipboard_clear()
            self.root.clipboard_append(cmd_str)
            messagebox.showinfo("成功", "已复制", parent=dialog)
        
        tk.Button(dialog, text="复制", command=copy, bg=COLORS['accent_success'],
                 fg=COLORS['text_primary'], relief='flat', padx=20, pady=5).pack(pady=10)
    
    def save_config(self):
        config = {
            'url': self.url_var.get(),
            'url_file': self.url_file_var.get(),
            'req_file': self.req_file_var.get(),
            'dork': self.dork_var.get(),
            'post': self.post_var.get(),
            'cookie': self.cookie_var.get(),
            'ua': self.ua_var.get(),
            'random_ua': self.random_ua_var.get(),
            'headers': self.headers_text.get(1.0, 'end'),
            'proxy': self.proxy_var.get(),
            'tor': self.tor_var.get(),
            'check_tor': self.check_tor_var.get(),
            'level': self.level_var.get(),
            'risk': self.risk_var.get(),
            'techniques': {k: v.get() for k, v in self.techniques.items()},
            'dbms': self.dbms_var.get(),
            'param': self.param_var.get(),
            'enum_options': {k: v.get() for k, v in self.enum_options.items()},
            'db': self.db_var.get(),
            'table': self.table_var.get(),
            'column': self.column_var.get(),
            'threads': self.threads_var.get(),
            'timeout': self.timeout_var.get(),
            'tamper': self.tamper_var.get(),
            'os_shell': self.os_shell_var.get(),
            'batch': self.batch_var.get(),
            'flush': self.flush_var.get(),
            'verbose': self.verbose_var.get(),
        }
        
        filename = filedialog.asksaveasfilename(defaultextension=".json",
                                               filetypes=[("JSON", "*.json"), ("所有文件", "*.*")])
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.status_var.set(f"配置已保存: {filename}")
    
    def load_config_dialog(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("所有文件", "*.*")])
        if filename:
            self.load_config(filename)
            self.status_var.set(f"配置已加载: {filename}")
    
    def load_config(self, filename=None):
        filename = filename or self.config_file
        if not os.path.exists(filename):
            return
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.url_var.set(config.get('url', ''))
            self.url_file_var.set(config.get('url_file', ''))
            self.req_file_var.set(config.get('req_file', ''))
            self.dork_var.set(config.get('dork', ''))
            self.post_var.set(config.get('post', ''))
            self.cookie_var.set(config.get('cookie', ''))
            self.ua_var.set(config.get('ua', ''))
            self.random_ua_var.set(config.get('random_ua', False))
            self.headers_text.delete(1.0, 'end')
            self.headers_text.insert(1.0, config.get('headers', ''))
            self.proxy_var.set(config.get('proxy', ''))
            self.tor_var.set(config.get('tor', False))
            self.check_tor_var.set(config.get('check_tor', False))
            self.level_var.set(config.get('level', 1))
            self.risk_var.set(config.get('risk', 1))
            
            for k, v in config.get('techniques', {}).items():
                if k in self.techniques:
                    self.techniques[k].set(v)
            
            self.dbms_var.set(config.get('dbms', '自动检测'))
            self.param_var.set(config.get('param', ''))
            
            for k, v in config.get('enum_options', {}).items():
                if k in self.enum_options:
                    self.enum_options[k].set(v)
            
            self.db_var.set(config.get('db', ''))
            self.table_var.set(config.get('table', ''))
            self.column_var.set(config.get('column', ''))
            self.threads_var.set(config.get('threads', 1))
            self.timeout_var.set(config.get('timeout', 30))
            self.tamper_var.set(config.get('tamper', ''))
            self.os_shell_var.set(config.get('os_shell', False))
            self.batch_var.set(config.get('batch', True))
            self.flush_var.set(config.get('flush', False))
            self.verbose_var.set(config.get('verbose', 1))
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def save_settings(self):
        try:
            config = {'python_cmd': self.python_cmd, 'font_size': self.font_size}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except:
            pass
    
    def load_settings(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.python_cmd = config.get('python_cmd', self.python_cmd)
                self.font_size = config.get('font_size', self.font_size)
        except:
            pass
    
    def show_help(self):
        help_text = """SQLMap GUI v1.0 使用帮助

【快速开始】
1. 在"目标"标签页输入目标URL
2. 点击"更新命令"预览生成的命令
3. 点击"开始扫描"执行测试

【主要功能】
- 目标设置: URL、批量文件、请求文件、Google Dork
- 请求设置: POST数据、Cookie、User-Agent、Headers、代理
- 注入设置: Level、Risk、注入技术、数据库类型
- 枚举设置: 数据库、表、列、数据导出
- 高级设置: 线程、Tamper脚本、OS Shell

【控制按钮】
- 开始扫描: 开始执行sqlmap
- 暂停: 暂停/继续扫描
- 停止: 立即停止扫描

【注意事项】
⚠️ 请确保获得授权后再进行测试
⚠️ 本工具仅供安全测试使用

作者: bae
日期: 2026/2/28
"""
        messagebox.showinfo("帮助", help_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = SQLMapGUI(root)
    root.mainloop()
