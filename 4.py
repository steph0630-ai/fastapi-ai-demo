import os
from fastapi import FastAPI
import pymysql,requests
#导入 DictCursor 让结果以字典的形式返回
from pymysql.cursors import DictCursor 
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# 新增一个接口：访问 http://127.0.0.1:8000/ai_analysis
@app.get("/ai_analysis")
def ai_analysis():
    # 1. 先调用你刚才写的“查数据”逻辑（直接复制你的代码）
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),   # 你的密码
        database="itheima",
        cursorclass=DictCursor
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM emp LIMIT 5") # 只取5条，省AI费用
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # 2. 如果没数据，直接提示
    if not data:
        return {"msg": "表里没数据呀"}
    
    # 3. 把数据塞进提示词，发给AI
    prompt = f"请用一句幽默的话总结以下员工数据的特点：{data}"

    try:
        ai_response = requests.post(
            "https://api.deepseek.com/chat/completions", # 免费的AI网关
            headers={"Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}"}
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=10
        )
        result = ai_response.json()
        ai_text = result['choices'][0]['message']['content']
    except Exception as e:
        # 如果AI接口调不通，绝不让你卡住！我们走“人工兜底”
        ai_text = f"（AI接口调试中，先看数据）共查到 {len(data)} 条记录，第一条叫 {data[0].get('name', '未知')}"
        print(e)
    # 4. 返回给浏览器
    return {
        "code": 200, 
        "data": data, 
        "ai_comment": ai_text  # 看！这就是AI生成的评论！
    }