#!/usr/bin/env python3
"""生成投放日报可视化看板 HTML"""
import json
import os
from datetime import datetime

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
TPL_FILE = os.path.join(os.path.dirname(__file__), "dashboard_tpl.html")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "dashboard.html")


def safe_val(v):
    """获取文本或数值"""
    if isinstance(v, list) and v:
        return v[0].get('text', '') if isinstance(v[0], dict) else str(v[0])
    return str(v) if v else ""


def safe_num(v):
    if isinstance(v, list) and v:
        v = v[0].get('text', '') if isinstance(v[0], dict) else str(v[0])
    try:
        return float(v) if v else 0
    except:
        return 0


def load_data():
    with open(os.path.join(CACHE_DIR, "all_data.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def process_monthly_channel(data):
    records = data.get("线上整体分渠道ByMonth", [])
    items = []
    for r in records:
        f = r.get("fields", {})
        name = safe_val(f.get("名称"))
        month = safe_val(f.get("月份"))
        channel = safe_val(f.get("渠道"))
        items.append({
            "name": name,
            "month": month,
            "channel": channel,
            "消费": safe_num(f.get("实际消费")),
            "线索数": safe_num(f.get("线索数")),
            "有效线索": safe_num(f.get("有效线索")),
            "线索成本": safe_num(f.get("线索成本")),
            "当前有效线索成本": safe_num(f.get("当前有效线索成本")),
        })
    return items


def process_city_monthly(data):
    records = data.get("线上整体分城市数据ByMonth", [])
    items = []
    for r in records:
        f = r.get("fields", {})
        name = safe_val(f.get("名称"))
        month = safe_val(f.get("月份"))
        city = safe_val(f.get("城市"))
        items.append({
            "name": name,
            "month": month,
            "city": city,
            "消费": safe_num(f.get("实际消费")),
            "线索数": safe_num(f.get("线索数")),
            "有效线索": safe_num(f.get("有效线索")),
        })
    return items


def get_months(items):
    return sorted(set(i["month"] for i in items if i["month"]))


def get_channels(items):
    return sorted(set(i["channel"] for i in items if i.get("channel")))


def get_cities(items):
    return sorted(set(i["city"] for i in items if i.get("city")))


def main():
    print("正在生成看板...")
    data = load_data()

    monthly_channel = process_monthly_channel(data)
    city_monthly = process_city_monthly(data)

    months = get_months(monthly_channel)
    channels = get_channels(monthly_channel)
    cities = get_cities(city_monthly)

    q1_months = ["1月", "2月", "3月"]
    q2_months = ["4月", "5月", "6月"]

    # 读取模板
    with open(TPL_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # 替换占位符
    html = html.replace("__UPDATE_TIME__", datetime.now().strftime('%Y-%m-%d %H:%M'))
    html = html.replace("__CHANNEL_OPTIONS__", "\n".join(f'<option value="{c}">{c}</option>' for c in channels))
    html = html.replace("__CITY_OPTIONS__", "\n".join(f'<option value="{c}">{c}</option>' for c in cities))
    html = html.replace("__MONTHLY_DATA__", json.dumps(monthly_channel))
    html = html.replace("__CITY_MONTHLY_DATA__", json.dumps(city_monthly))
    html = html.replace("__Q1_MONTHS__", json.dumps(q1_months))
    html = html.replace("__Q2_MONTHS__", json.dumps(q2_months))
    html = html.replace("__ALL_MONTHS__", json.dumps(months))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ 看板已生成: {OUTPUT_FILE}")
    print(f"   月份范围: {months}")


if __name__ == "__main__":
    main()
