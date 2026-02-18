# -*- coding: utf-8 -*-
"""
SQL注入测试靶场 - 用于测试SQLMap GUI
作者: bae
日期: 2026/2/28
"""

from flask import Flask, request, render_template_string
import sqlite3
import os

app = Flask(__name__)

# HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>SQL注入测试靶场</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #333; }
        .section { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 8px; }
        input[type="text"] { width: 300px; padding: 10px; margin: 5px 0; }
        input[type="submit"] { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
        input[type="submit"]:hover { background: #0056b3; }
        .result { background: #e9ecef; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .error { color: red; }
        .success { color: green; }
        table { border-collapse: collapse; width: 100%; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #007bff; color: white; }
    </style>
</head>
<body>
    <h1>🎯 SQL注入测试靶场</h1>
    
    <div class="section">
        <h2>Less-1: 基于错误的GET单引号注入</h2>
        <form action="/less-1" method="get">
            <label>ID: </label>
            <input type="text" name="id" placeholder="输入用户ID，如: 1">
            <input type="submit" value="查询">
        </form>
        {% if result1 %}
        <div class="result">
            <h3>查询结果:</h3>
            {{ result1|safe }}
        </div>
        {% endif %}
    </div>
    
    <div class="section">
        <h2>Less-2: 基于错误的GET整型注入</h2>
        <form action="/less-2" method="get">
            <label>ID: </label>
            <input type="text" name="id" placeholder="输入用户ID，如: 1">
            <input type="submit" value="查询">
        </form>
        {% if result2 %}
        <div class="result">
            <h3>查询结果:</h3>
            {{ result2|safe }}
        </div>
        {% endif %}
    </div>
    
    <div class="section">
        <h2>Less-3: 基于错误的GET单引号变形注入</h2>
        <form action="/less-3" method="get">
            <label>ID: </label>
            <input type="text" name="id" placeholder="输入用户ID，如: 1">
            <input type="submit" value="查询">
        </form>
        {% if result3 %}
        <div class="result">
            <h3>查询结果:</h3>
            {{ result3|safe }}
        </div>
        {% endif %}
    </div>
    
    <div class="section">
        <h2>Less-4: 基于错误的GET双引号注入</h2>
        <form action="/less-4" method="get">
            <label>ID: </label>
            <input type="text" name="id" placeholder="输入用户ID，如: 1">
            <input type="submit" value="查询">
        </form>
        {% if result4 %}
        <div class="result">
            <h3>查询结果:</h3>
            {{ result4|safe }}
        </div>
        {% endif %}
    </div>
    
    <div class="section">
        <h2>Less-5: 基于错误的GET单引号双查询注入</h2>
        <form action="/less-5" method="get">
            <label>ID: </label>
            <input type="text" name="id" placeholder="输入用户ID，如: 1">
            <input type="submit" value="查询">
        </form>
        {% if result5 %}
        <div class="result">
            <h3>查询结果:</h3>
            {{ result5|safe }}
        </div>
        {% endif %}
    </div>
    
    <div class="section">
        <h2>Less-6: 基于错误的GET双引号双查询注入</h2>
        <form action="/less-6" method="get">
            <label>ID: </label>
            <input type="text" name="id" placeholder="输入用户ID，如: 1">
            <input type="submit" value="查询">
        </form>
        {% if result6 %}
        <div class="result">
            <h3>查询结果:</h3>
            {{ result6|safe }}
        </div>
        {% endif %}
    </div>
    
    <div class="section">
        <h2>Less-7: 基于错误的GET单引号变形双查询注入</h2>
        <form action="/less-7" method="get">
            <label>ID: </label>
            <input type="text" name="id" placeholder="输入用户ID，如: 1">
            <input type="submit" value="查询">
        </form>
        {% if result7 %}
        <div class="result">
            <h3>查询结果:</h3>
            {{ result7|safe }}
        </div>
        {% endif %}
    </div>
    
    <div class="section">
        <h2>Less-8: 基于布尔盲注的单引号注入</h2>
        <form action="/less-8" method="get">
            <label>ID: </label>
            <input type="text" name="id" placeholder="输入用户ID，如: 1">
            <input type="submit" value="查询">
        </form>
        {% if result8 %}
        <div class="result">
            <h3>查询结果:</h3>
            {{ result8|safe }}
        </div>
        {% endif %}
    </div>
    
    <div class="section">
        <h2>Less-9: 基于时间盲注的单引号注入</h2>
        <form action="/less-9" method="get">
            <label>ID: </label>
            <input type="text" name="id" placeholder="输入用户ID，如: 1">
            <input type="submit" value="查询">
        </form>
        {% if result9 %}
        <div class="result">
            <h3>查询结果:</h3>
            {{ result9|safe }}
        </div>
        {% endif %}
    </div>
    
    <div class="section">
        <h2>Less-10: 基于时间盲注的双引号注入</h2>
        <form action="/less-10" method="get">
            <label>ID: </label>
            <input type="text" name="id" placeholder="输入用户ID，如: 1">
            <input type="submit" value="查询">
        </form>
        {% if result10 %}
        <div class="result">
            <h3>查询结果:</h3>
            {{ result10|safe }}
        </div>
        {% endif %}
    </div>
    
    <div class="section">
        <h2>Less-11: 基于错误的POST单引号注入</h2>
        <form action="/less-11" method="post">
            <label>用户名: </label>
            <input type="text" name="uname" placeholder="输入用户名"><br><br>
            <label>密码: </label>
            <input type="text" name="passwd" placeholder="输入密码"><br><br>
            <input type="submit" value="登录">
        </form>
        {% if result11 %}
        <div class="result">
            <h3>登录结果:</h3>
            {{ result11|safe }}
        </div>
        {% endif %}
    </div>
    
    <div class="section">
        <h2>Less-12: 基于错误的POST双引号变形注入</h2>
        <form action="/less-12" method="post">
            <label>用户名: </label>
            <input type="text" name="uname" placeholder="输入用户名"><br><br>
            <label>密码: </label>
            <input type="text" name="passwd" placeholder="输入密码"><br><br>
            <input type="submit" value="登录">
        </form>
        {% if result12 %}
        <div class="result">
            <h3>登录结果:</h3>
            {{ result12|safe }}
        </div>
        {% endif %}
    </div>
    
    <div class="section">
        <h2>Less-13: 基于错误的POST单引号变形注入</h2>
        <form action="/less-13" method="post">
            <label>用户名: </label>
            <input type="text" name="uname" placeholder="输入用户名"><br><br>
            <label>密码: </label>
            <input type="text" name="passwd" placeholder="输入密码"><br><br>
            <input type="submit" value="登录">
        </form>
        {% if result13 %}
        <div class="result">
            <h3>登录结果:</h3>
            {{ result13|safe }}
        </div>
        {% endif %}
    </div>
    
    <div class="section">
        <h2>Less-14: 基于错误的POST双引号注入</h2>
        <form action="/less-14" method="post">
            <label>用户名: </label>
            <input type="text" name="uname" placeholder="输入用户名"><br><br>
            <label>密码: </label>
            <input type="text" name="passwd" placeholder="输入密码"><br><br>
            <input type="submit" value="登录">
        </form>
        {% if result14 %}
        <div class="result">
            <h3>登录结果:</h3>
            {{ result14|safe }}
        </div>
        {% endif %}
    </div>
    
    <div class="section">
        <h2>Less-15: 基于布尔盲注的POST单引号注入</h2>
        <form action="/less-15" method="post">
            <label>用户名: </label>
            <input type="text" name="uname" placeholder="输入用户名"><br><br>
            <label>密码: </label>
            <input type="text" name="passwd" placeholder="输入密码"><br><br>
            <input type="submit" value="登录">
        </form>
        {% if result15 %}
        <div class="result">
            <h3>登录结果:</h3>
            {{ result15|safe }}
        </div>
        {% endif %}
    </div>
    
    <div class="section">
        <h2>Less-16: 基于时间盲注的POST双引号变形注入</h2>
        <form action="/less-16" method="post">
            <label>用户名: </label>
            <input type="text" name="uname" placeholder="输入用户名"><br><br>
            <label>密码: </label>
            <input type="text" name="passwd" placeholder="输入密码"><br><br>
            <input type="submit" value="登录">
        </form>
        {% if result16 %}
        <div class="result">
            <h3>登录结果:</h3>
            {{ result16|safe }}
        </div>
        {% endif %}
    </div>
    
    <div class="section">
        <h2>Less-17: 基于错误的UPDATE单引号注入</h2>
        <form action="/less-17" method="post">
            <label>用户名: </label>
            <input type="text" name="username" placeholder="输入用户名"><br><br>
            <label>当前密码: </label>
            <input type="text" name="password" placeholder="输入当前密码"><br><br>
            <label>新密码: </label>
            <input type="text" name="new_password" placeholder="输入新密码"><br><br>
            <input type="submit" value="修改密码">
        </form>
        {% if result17 %}
        <div class="result">
            <h3>修改结果:</h3>
            {{ result17|safe }}
        </div>
        {% endif %}
    </div>
    
    <div class="section">
        <h2>Less-18: 基于错误的User-Agent注入</h2>
        <form action="/less-18" method="post">
            <label>用户名: </label>
            <input type="text" name="uname" placeholder="输入用户名"><br><br>
            <label>密码: </label>
            <input type="text" name="passwd" placeholder="输入密码"><br><br>
            <input type="submit" value="登录并记录UA">
        </form>
        {% if result18 %}
        <div class="result">
            <h3>登录结果:</h3>
            {{ result18|safe }}
        </div>
        {% endif %}
    </div>
    
    <div class="section">
        <h2>Less-19: 基于错误的Referer注入</h2>
        <form action="/less-19" method="post">
            <label>用户名: </label>
            <input type="text" name="uname" placeholder="输入用户名"><br><br>
            <label>密码: </label>
            <input type="text" name="passwd" placeholder="输入密码"><br><br>
            <input type="submit" value="登录并记录Referer">
        </form>
        {% if result19 %}
        <div class="result">
            <h3>登录结果:</h3>
            {{ result19|safe }}
        </div>
        {% endif %}
    </div>
    
    <div class="section">
        <h2>Less-20: 基于错误的Cookie注入</h2>
        <form action="/less-20" method="post">
            <label>用户名: </label>
            <input type="text" name="uname" placeholder="输入用户名"><br><br>
            <label>密码: </label>
            <input type="text" name="passwd" placeholder="输入密码"><br><br>
            <input type="submit" value="登录并设置Cookie">
        </form>
        {% if result20 %}
        <div class="result">
            <h3>登录结果:</h3>
            {{ result20|safe }}
        </div>
        {% endif %}
    </div>
    
    <hr>
    <p style="text-align: center; color: #666;">
        SQL注入测试靶场 | 作者: bae | 日期: 2026/2/28
    </p>
</body>
</html>
'''

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect('sqli_test.db')
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT
        )
    ''')
    
    # 插入测试数据
    test_users = [
        (1, 'admin', 'admin123', 'admin@example.com'),
        (2, 'user1', 'password1', 'user1@example.com'),
        (3, 'user2', 'password2', 'user2@example.com'),
        (4, 'test', 'test123', 'test@example.com'),
        (5, 'guest', 'guest123', 'guest@example.com'),
    ]
    
    cursor.executemany('INSERT OR IGNORE INTO users VALUES (?,?,?,?)', test_users)
    conn.commit()
    conn.close()
    print("[+] 数据库初始化完成")

def get_db_connection():
    """获取数据库连接"""
    return sqlite3.connect('sqli_test.db')

def format_result(cursor, rows):
    """格式化查询结果"""
    if not rows:
        return "<p class='error'>没有找到记录</p>"
    
    columns = [description[0] for description in cursor.description]
    
    html = "<table><tr>"
    for col in columns:
        html += f"<th>{col}</th>"
    html += "</tr>"
    
    for row in rows:
        html += "<tr>"
        for cell in row:
            html += f"<td>{cell}</td>"
        html += "</tr>"
    
    html += "</table>"
    return html

@app.route('/')
def index():
    """主页"""
    return render_template_string(HTML_TEMPLATE)

# Less-1: 基于错误的GET单引号注入
@app.route('/less-1')
def less_1():
    id_param = request.args.get('id', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 有漏洞的代码
        query = f"SELECT * FROM users WHERE id='{id_param}'"
        cursor.execute(query)
        rows = cursor.fetchall()
        result = format_result(cursor, rows)
    except Exception as e:
        result = f"<p class='error'>错误: {str(e)}</p>"
    finally:
        conn.close()
    
    return render_template_string(HTML_TEMPLATE, result1=result)

# Less-2: 基于错误的GET整型注入
@app.route('/less-2')
def less_2():
    id_param = request.args.get('id', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = f"SELECT * FROM users WHERE id={id_param}"
        cursor.execute(query)
        rows = cursor.fetchall()
        result = format_result(cursor, rows)
    except Exception as e:
        result = f"<p class='error'>错误: {str(e)}</p>"
    finally:
        conn.close()
    
    return render_template_string(HTML_TEMPLATE, result2=result)

# Less-3: 基于错误的GET单引号变形注入
@app.route('/less-3')
def less_3():
    id_param = request.args.get('id', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = f"SELECT * FROM users WHERE id=('{id_param}')"
        cursor.execute(query)
        rows = cursor.fetchall()
        result = format_result(cursor, rows)
    except Exception as e:
        result = f"<p class='error'>错误: {str(e)}</p>"
    finally:
        conn.close()
    
    return render_template_string(HTML_TEMPLATE, result3=result)

# Less-4: 基于错误的GET双引号注入
@app.route('/less-4')
def less_4():
    id_param = request.args.get('id', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = f'SELECT * FROM users WHERE id=("{id_param}")'
        cursor.execute(query)
        rows = cursor.fetchall()
        result = format_result(cursor, rows)
    except Exception as e:
        result = f"<p class='error'>错误: {str(e)}</p>"
    finally:
        conn.close()
    
    return render_template_string(HTML_TEMPLATE, result4=result)

# Less-5: 基于错误的GET单引号双查询注入
@app.route('/less-5')
def less_5():
    id_param = request.args.get('id', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = f"SELECT * FROM users WHERE id='{id_param}' LIMIT 0,1"
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            result = format_result(cursor, rows)
        else:
            result = "<p class='error'>You are in...........</p>"
    except Exception as e:
        result = f"<p class='error'>错误: {str(e)}</p>"
    finally:
        conn.close()
    
    return render_template_string(HTML_TEMPLATE, result5=result)

# Less-6: 基于错误的GET双引号双查询注入
@app.route('/less-6')
def less_6():
    id_param = request.args.get('id', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = f'SELECT * FROM users WHERE id="{id_param}" LIMIT 0,1'
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            result = format_result(cursor, rows)
        else:
            result = "<p class='error'>You are in...........</p>"
    except Exception as e:
        result = f"<p class='error'>错误: {str(e)}</p>"
    finally:
        conn.close()
    
    return render_template_string(HTML_TEMPLATE, result6=result)

# Less-7: 基于错误的GET单引号变形双查询注入
@app.route('/less-7')
def less_7():
    id_param = request.args.get('id', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = f"SELECT * FROM users WHERE id=(('{id_param}')) LIMIT 0,1"
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            result = format_result(cursor, rows)
        else:
            result = "<p class='error'>You are in........ Use outfile......</p>"
    except Exception as e:
        result = f"<p class='error'>错误: {str(e)}</p>"
    finally:
        conn.close()
    
    return render_template_string(HTML_TEMPLATE, result7=result)

# Less-8: 基于布尔盲注的单引号注入
@app.route('/less-8')
def less_8():
    id_param = request.args.get('id', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = f"SELECT * FROM users WHERE id='{id_param}' LIMIT 0,1"
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            result = "<p class='success'>You are in...........</p>"
        else:
            result = ""
    except Exception as e:
        result = ""
    finally:
        conn.close()
    
    return render_template_string(HTML_TEMPLATE, result8=result)

# Less-9: 基于时间盲注的单引号注入
@app.route('/less-9')
def less_9():
    id_param = request.args.get('id', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = f"SELECT * FROM users WHERE id='{id_param}' LIMIT 0,1"
        cursor.execute(query)
        rows = cursor.fetchall()
        result = "<p class='success'>You are in...........</p>"
    except Exception as e:
        result = ""
    finally:
        conn.close()
    
    return render_template_string(HTML_TEMPLATE, result9=result)

# Less-10: 基于时间盲注的双引号注入
@app.route('/less-10')
def less_10():
    id_param = request.args.get('id', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = f'SELECT * FROM users WHERE id="{id_param}" LIMIT 0,1'
        cursor.execute(query)
        rows = cursor.fetchall()
        result = "<p class='success'>You are in...........</p>"
    except Exception as e:
        result = ""
    finally:
        conn.close()
    
    return render_template_string(HTML_TEMPLATE, result10=result)

# Less-11: 基于错误的POST单引号注入
@app.route('/less-11', methods=['POST'])
def less_11():
    uname = request.form.get('uname', '')
    passwd = request.form.get('passwd', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = f"SELECT * FROM users WHERE username='{uname}' AND password='{passwd}'"
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            result = f"<p class='success'>登录成功! 欢迎 {rows[0][1]}</p>"
        else:
            result = "<p class='error'>登录失败</p>"
    except Exception as e:
        result = f"<p class='error'>错误: {str(e)}</p>"
    finally:
        conn.close()
    
    return render_template_string(HTML_TEMPLATE, result11=result)

# Less-12: 基于错误的POST双引号变形注入
@app.route('/less-12', methods=['POST'])
def less_12():
    uname = request.form.get('uname', '')
    passwd = request.form.get('passwd', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = f'SELECT * FROM users WHERE username=("{uname}") AND password=("{passwd}")'
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            result = f"<p class='success'>登录成功! 欢迎 {rows[0][1]}</p>"
        else:
            result = "<p class='error'>登录失败</p>"
    except Exception as e:
        result = f"<p class='error'>错误: {str(e)}</p>"
    finally:
        conn.close()
    
    return render_template_string(HTML_TEMPLATE, result12=result)

# Less-13: 基于错误的POST单引号变形注入
@app.route('/less-13', methods=['POST'])
def less_13():
    uname = request.form.get('uname', '')
    passwd = request.form.get('passwd', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = f"SELECT * FROM users WHERE username=('{uname}') AND password=('{passwd}')"
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            result = f"<p class='success'>登录成功! 欢迎 {rows[0][1]}</p>"
        else:
            result = "<p class='error'>登录失败</p>"
    except Exception as e:
        result = f"<p class='error'>错误: {str(e)}</p>"
    finally:
        conn.close()
    
    return render_template_string(HTML_TEMPLATE, result13=result)

# Less-14: 基于错误的POST双引号注入
@app.route('/less-14', methods=['POST'])
def less_14():
    uname = request.form.get('uname', '')
    passwd = request.form.get('passwd', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = f'SELECT * FROM users WHERE username="{uname}" AND password="{passwd}"'
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            result = f"<p class='success'>登录成功! 欢迎 {rows[0][1]}</p>"
        else:
            result = "<p class='error'>登录失败</p>"
    except Exception as e:
        result = f"<p class='error'>错误: {str(e)}</p>"
    finally:
        conn.close()
    
    return render_template_string(HTML_TEMPLATE, result14=result)

# Less-15: 基于布尔盲注的POST单引号注入
@app.route('/less-15', methods=['POST'])
def less_15():
    uname = request.form.get('uname', '')
    passwd = request.form.get('passwd', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = f"SELECT * FROM users WHERE username='{uname}' AND password='{passwd}'"
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            result = "<p class='success'>You are in...........</p>"
        else:
            result = ""
    except Exception as e:
        result = ""
    finally:
        conn.close()
    
    return render_template_string(HTML_TEMPLATE, result15=result)

# Less-16: 基于时间盲注的POST双引号变形注入
@app.route('/less-16', methods=['POST'])
def less_16():
    uname = request.form.get('uname', '')
    passwd = request.form.get('passwd', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = f'SELECT * FROM users WHERE username=("{uname}") AND password=("{passwd}")'
        cursor.execute(query)
        rows = cursor.fetchall()
        result = "<p class='success'>You are in...........</p>"
    except Exception as e:
        result = ""
    finally:
        conn.close()
    
    return render_template_string(HTML_TEMPLATE, result16=result)

# Less-17: 基于错误的UPDATE单引号注入
@app.route('/less-17', methods=['POST'])
def less_17():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    new_password = request.form.get('new_password', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 先验证用户
        check_query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cursor.execute(check_query)
        if cursor.fetchone():
            # 更新密码 - 有漏洞
            update_query = f"UPDATE users SET password='{new_password}' WHERE username='{username}'"
            cursor.execute(update_query)
            conn.commit()
            result = "<p class='success'>密码修改成功!</p>"
        else:
            result = "<p class='error'>用户名或密码错误</p>"
    except Exception as e:
        result = f"<p class='error'>错误: {str(e)}</p>"
    finally:
        conn.close()
    
    return render_template_string(HTML_TEMPLATE, result17=result)

# Less-18: 基于错误的User-Agent注入
@app.route('/less-18', methods=['POST'])
def less_18():
    uname = request.form.get('uname', '')
    passwd = request.form.get('passwd', '')
    ua = request.headers.get('User-Agent', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 验证用户
        query = f"SELECT * FROM users WHERE username='{uname}' AND password='{passwd}'"
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            # 记录User-Agent - 有漏洞
            insert_query = f"INSERT INTO users (username, password, email) VALUES ('UA_LOG', '{ua}', 'log@example.com')"
            try:
                cursor.execute(insert_query)
                conn.commit()
            except:
                pass
            result = f"<p class='success'>登录成功! User-Agent已记录</p><p>你的UA: {ua[:100]}...</p>"
        else:
            result = "<p class='error'>登录失败</p>"
    except Exception as e:
        result = f"<p class='error'>错误: {str(e)}</p>"
    finally:
        conn.close()
    
    return render_template_string(HTML_TEMPLATE, result18=result)

# Less-19: 基于错误的Referer注入
@app.route('/less-19', methods=['POST'])
def less_19():
    uname = request.form.get('uname', '')
    passwd = request.form.get('passwd', '')
    referer = request.headers.get('Referer', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = f"SELECT * FROM users WHERE username='{uname}' AND password='{passwd}'"
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            insert_query = f"INSERT INTO users (username, password, email) VALUES ('REF_LOG', '{referer}', 'log@example.com')"
            try:
                cursor.execute(insert_query)
                conn.commit()
            except:
                pass
            result = f"<p class='success'>登录成功! Referer已记录</p><p>你的Referer: {referer[:100]}...</p>"
        else:
            result = "<p class='error'>登录失败</p>"
    except Exception as e:
        result = f"<p class='error'>错误: {str(e)}</p>"
    finally:
        conn.close()
    
    return render_template_string(HTML_TEMPLATE, result19=result)

# Less-20: 基于错误的Cookie注入
@app.route('/less-20', methods=['POST', 'GET'])
def less_20():
    if request.method == 'POST':
        uname = request.form.get('uname', '')
        passwd = request.form.get('passwd', '')
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            query = f"SELECT * FROM users WHERE username='{uname}' AND password='{passwd}'"
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows:
                from flask import make_response
                resp = make_response(render_template_string(HTML_TEMPLATE, 
                    result20="<p class='success'>登录成功! Cookie已设置</p>"))
                resp.set_cookie('uname', uname)
                return resp
            else:
                result = "<p class='error'>登录失败</p>"
        except Exception as e:
            result = f"<p class='error'>错误: {str(e)}</p>"
        finally:
            conn.close()
        
        return render_template_string(HTML_TEMPLATE, result20=result)
    else:
        # GET请求 - 检查Cookie
        cookie_uname = request.cookies.get('uname', '')
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            query = f"SELECT * FROM users WHERE username='{cookie_uname}'"
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows:
                result = f"<p class='success'>欢迎回来, {rows[0][1]}!</p>"
            else:
                result = "<p>请登录</p>"
        except Exception as e:
            result = f"<p class='error'>错误: {str(e)}</p>"
        finally:
            conn.close()
        
        return render_template_string(HTML_TEMPLATE, result20=result)

if __name__ == '__main__':
    init_db()
    print("[*] 启动SQL注入测试靶场...")
    print("[*] 访问地址: http://127.0.0.1:5000")
    print("[*] 按Ctrl+C停止服务器")
    app.run(host='127.0.0.1', port=5000, debug=False)
