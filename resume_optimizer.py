import os
import json
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from prompts import SYSTEM_PROMPT

load_dotenv(override=True)


def get_config():
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
    base_url = os.getenv("OPENAI_BASE_URL") or st.secrets.get("OPENAI_BASE_URL", "https://api.deepseek.com")
    model_name = os.getenv("OPENAI_MODEL") or st.secrets.get("OPENAI_MODEL", "deepseek-v4-flash")
    return api_key, base_url, model_name


def extract_json(text):
    text = text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}") + 1

    if start != -1 and end != 0:
        json_text = text[start:end]
        return json.loads(json_text)

    raise ValueError("AI 返回的内容不是有效 JSON。")


def ensure_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def normalize_result(data):
    return {
        "match_score": data.get("match_score", 0),
        "score_reason": data.get("score_reason", "暂无说明"),
        "strengths": ensure_list(data.get("strengths", [])),
        "problems": ensure_list(data.get("problems", [])),
        "suggestions": ensure_list(data.get("suggestions", [])),
        "missing_keywords": ensure_list(data.get("missing_keywords", [])),
        "optimized_resume": data.get("optimized_resume", "")
    }


def optimize_resume(job_description, resume_text, resume_style="正式专业"):
    api_key, base_url, model_name = get_config()

    if not api_key:
        raise ValueError("云端没有读取到 OPENAI_API_KEY。请去 Streamlit 的 Manage app → Settings → Secrets 里检查。")

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=120,
        max_retries=2
    )

    user_prompt = f"""
岗位描述：
{job_description}

简历内容：
{resume_text}

优化风格：
{resume_style}

请根据岗位描述和简历内容，输出一个 JSON 对象。
不要输出解释，不要输出额外文字，不要输出 markdown，只输出 JSON。

JSON 格式必须严格如下：
{{
  "match_score": 80,
  "score_reason": "这里写打分原因",
  "strengths": ["优点1", "优点2", "优点3"],
  "problems": ["问题1", "问题2", "问题3"],
  "suggestions": ["建议1", "建议2", "建议3"],
  "missing_keywords": ["关键词1", "关键词2", "关键词3"],
  "optimized_resume": "这里写优化后的简历全文"
}}
"""

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )

    result_text = response.choices[0].message.content.strip()

    try:
        result_json = extract_json(result_text)
        return normalize_result(result_json)
    except Exception:
        return {
            "match_score": 0,
            "score_reason": "AI 返回结果格式不正确，暂时无法正常解析。",
            "strengths": [],
            "problems": ["返回内容不是标准 JSON 格式。"],
            "suggestions": ["检查 prompts.py 提示词", "检查模型输出格式", "重新点击生成再试一次"],
            "missing_keywords": [],
            "optimized_resume": result_text
        }