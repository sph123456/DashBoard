#!/usr/bin/env python3
"""从飞书多维表格获取投放日报数据"""
import json
import os
import urllib3
from urllib.request import Request, urlopen

# 飞书应用凭证
APP_ID = "cli_a936216e1879dbdd"
APP_SECRET = "jUrnoQKrWBdy119W06VeAfMFY40agnUv"

# 多维表格信息
APP_TOKEN = "Trf1b2Ou9aEyjPssOIOcFh57nac"
TABLES = {
    "线上整体汇总ByDay": "tblQUu7osfaj8xnI",
    "线上整体分渠道ByMonth": "tbllWFyN1MFSGYu4",
    "线上整体分城市数据ByDay": "tblDmqtkRB7FFtdP",
    "线上整体分城市数据ByMonth": "tblbWqKXFwVmGhUp",
    "线上整体分城市分渠道ByDay": "tbldT0EsjVAFxVNm",
}

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def get_token():
    """获取 tenant_access_token"""
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
    r = http.request('POST', url, body=data, headers={'Content-Type': 'application/json'})
    result = json.loads(r.data)
    return result.get("tenant_access_token", "")


def get_records(table_id, token, page_size=500):
    """获取多维表格记录"""
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    all_records = []
    page_token = None

    while True:
        params = f"page_size={page_size}"
        if page_token:
            params += f"&page_token={page_token}"
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/records?{params}"
        r = http.request('GET', url, headers=headers)
        result = json.loads(r.data)

        if result.get("code") != 0:
            print(f"获取记录失败: {result}")
            break

        items = result.get("data", {}).get("items", [])
        all_records.extend(items)

        has_more = result.get("data", {}).get("has_more", False)
        if not has_more:
            break
        page_token = result.get("data", {}).get("page_token")

    return all_records


def main():
    print("正在获取飞书数据...")
    token = get_token()
    if not token:
        print("获取 token 失败")
        return

    summary = {}
    all_data = {}

    for name, table_id in TABLES.items():
        print(f"获取 {name}...")
        records = get_records(table_id, token)
        # 保存单个表数据
        with open(os.path.join(CACHE_DIR, f"{table_id}.json"), "w", encoding="utf-8") as f:
            json.dump({"records": records, "total": len(records)}, f, ensure_ascii=False, indent=2)
        # 汇总
        summary[name] = len(records)
        # 合并到 all_data
        all_data[name] = records
        print(f"  ✓ {len(records)} 条记录")

    # 保存所有数据
    with open(os.path.join(CACHE_DIR, "all_data.json"), "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    # 保存摘要
    with open(os.path.join(CACHE_DIR, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("\n数据更新成功!")
    print("=" * 40)
    for name, count in summary.items():
        print(f"  {name}: {count} 条")
    print("=" * 40)


if __name__ == "__main__":
    main()
