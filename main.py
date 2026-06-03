import base64
import datetime as dt
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


ROOT = os.path.dirname(os.path.abspath(__file__))
TOPICS_PATH = os.path.join(ROOT, "config", "topics.json")
PROMPT_PATH = os.path.join(ROOT, "prompts", "daily_report.md")
BEIJING_TZ = dt.timezone(dt.timedelta(hours=8))


def read_text(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def read_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def require_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"缺少必填环境变量：{name}")
    return value


def post_json(url, payload, headers=None, timeout=45):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            **(headers or {}),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"请求失败：HTTP {exc.code} {detail}") from exc


def collect_serper_results(topics):
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return [
            {
                "note": "未配置 SERPER_API_KEY，已跳过实时搜索。生成日报时，所有最新事实必须标注“待验证”。"
            }
        ]

    results = []
    for query in topics.get("search_queries", [])[:12]:
        payload = {
            "q": query,
            "num": 5,
            "gl": "sa",
            "hl": "en",
        }
        data = post_json(
            "https://google.serper.dev/search",
            payload,
            headers={"X-API-KEY": api_key},
            timeout=30,
        )
        organic = data.get("organic", [])[:5]
        results.append(
            {
                "query": query,
                "items": [
                    {
                        "title": item.get("title"),
                        "link": item.get("link"),
                        "snippet": item.get("snippet"),
                        "date": item.get("date"),
                    }
                    for item in organic
                ],
            }
        )
        time.sleep(0.2)
    return results


def call_aihubmix(system_prompt, topics, search_results, today):
    api_key = require_env("AIHUBMIX_API_KEY")
    base_url = os.getenv("AIHUBMIX_BASE_URL", "https://aihubmix.com/v1").rstrip("/")
    model = os.getenv("AIHUBMIX_MODEL", "gpt-4o-mini")

    user_payload = {
        "date": today,
        "topics": topics,
        "search_results": search_results,
        "instruction": "请基于以上资料生成今天的钉钉群日报。若资料不足，请明确标注待验证，不要编造事实。",
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt.replace("{{date}}", today)},
            {
                "role": "user",
                "content": json.dumps(user_payload, ensure_ascii=False, indent=2),
            },
        ],
        "temperature": 0.45,
    }

    data = post_json(
        f"{base_url}/chat/completions",
        payload,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=90,
    )
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as exc:
        preview = json.dumps(data, ensure_ascii=False)[:1000]
        raise RuntimeError(f"AIHubMix 返回格式异常：{preview}") from exc


def signed_dingtalk_url(webhook, secret):
    if not secret:
        return webhook
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f"{timestamp}\n{secret}".encode("utf-8")
    secret_bytes = secret.encode("utf-8")
    signature = base64.b64encode(
        hmac.new(secret_bytes, string_to_sign, hashlib.sha256).digest()
    )
    sign = urllib.parse.quote_plus(signature)
    separator = "&" if "?" in webhook else "?"
    return f"{webhook}{separator}timestamp={timestamp}&sign={sign}"


def send_dingtalk(report, today):
    webhook = require_env("DINGTALK_WEBHOOK")
    secret = os.getenv("DINGTALK_SECRET", "")
    url = signed_dingtalk_url(webhook, secret)
    title = f"中东AI角色互动情报 · {today}"

    text = report
    if len(text) > 18000:
        text = text[:17800] + "\n\n（内容过长，已自动截断。）"

    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": text,
        },
    }
    return post_json(url, payload, timeout=45)


def main():
    today = dt.datetime.now(BEIJING_TZ).strftime("%Y年%m月%d日")
    topics = read_json(TOPICS_PATH)
    prompt = read_text(PROMPT_PATH)
    search_results = collect_serper_results(topics)
    report = call_aihubmix(prompt, topics, search_results, today)

    if os.getenv("DRY_RUN") == "true":
        print(report)
        return

    result = send_dingtalk(report, today)
    print(json.dumps({"status": "sent", "dingtalk_result": result}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
