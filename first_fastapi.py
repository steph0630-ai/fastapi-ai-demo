import json
import logging
import datetime
from fastapi import FastAPI
import asyncmy
from asyncmy.cursors import DictCursor
import httpx
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="员工AI分析服务", version="1.0.0")

@app.get("/")
async def root():
    return {"msg": "员工AI分析服务已启动，请访问 /ai_analysis"}

@app.get("/ai_analysis")
async def ai_analysis():
    # ---------- 1. 异步查询数据库 ----------
    try:
        async with asyncmy.connect(
            host=settings.DB_HOST,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
        ) as conn:
            async with conn.cursor(cursor=DictCursor) as cursor:
                await cursor.execute("SELECT * FROM emp LIMIT 5")
                data = await cursor.fetchall()
    except asyncmy.errors.Error as e:
        logger.error(f"数据库查询失败: {e}", exc_info=True)
        return {
            "code": 500,
            "msg": "数据库暂时不可用，请稍后重试",
            "data": [],
            "ai_comment": ""
        }

    if not data:
        return {
            "code": 404,
            "msg": "员工表为空",
            "data": [],
            "ai_comment": "暂无数据可分析"
        }

    # ---------- 2. 构造提示词（处理日期类型） ----------
    # 将 data 中的日期字段转为 ISO 字符串
    data_serializable = []
    for row in data:
        row_copy = {}
        for key, value in row.items():
            if isinstance(value, (datetime.date, datetime.datetime)):
                row_copy[key] = value.isoformat()
            else:
                row_copy[key] = value
        data_serializable.append(row_copy)

    prompt = f"请用一句幽默的话总结以下员工数据的特点：{json.dumps(data_serializable, ensure_ascii=False)}"

    # ---------- 3. 异步调用 DeepSeek AI ----------
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://api.deepseek.com/chat/completions",
                headers={"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"},
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            resp.raise_for_status()
            ai_text = resp.json()['choices'][0]['message']['content']

    except httpx.TimeoutException:
        logger.warning("DeepSeek API 超时")
        ai_text = f"（AI 思考超时）当前共 {len(data)} 条记录，第一条是 {data[0].get('name', '未知')}"

    except httpx.HTTPStatusError as e:
        logger.error(f"DeepSeek API 状态码异常: {e.response.status_code} - {e.response.text}")
        if e.response.status_code == 401:
            ai_text = "（API Key 无效，请检查配置）"
        elif e.response.status_code == 429:
            ai_text = "（API 调用频率过高，请稍后再试）"
        else:
            ai_text = f"（AI 服务返回错误 {e.response.status_code}）"

    except Exception as e:
        logger.error(f"AI 调用发生未知错误: {e}", exc_info=True)
        ai_text = f"（AI 服务暂时开小差）当前共 {len(data)} 条数据"

    # ---------- 4. 返回统一响应 ----------
    return {
        "code": 200,
        "msg": "success",
        "data": data,  # 原始数据（包含 date 对象，但 FastAPI 会自动转换）
        "ai_comment": ai_text
    }