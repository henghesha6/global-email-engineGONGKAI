import os
import csv
import requests
import re

def run_mvp():
    print("=== Global Email Engine (MVP) ===")
    print("正在连接 Common Crawl 最新索引...")
    
    # 获取 Common Crawl 最新索引列表
    index_url = "https://index.commoncrawl.org/collinfo.json"
    try:
        response = requests.get(index_url, timeout=10)
        colls = response.json()
        latest_coll = colls[0]['id']
        print(f"已获取最新索引: {latest_coll}")
    except Exception as e:
        print(f"获取索引失败，使用默认测试数据: {e}")
        latest_coll = "CC-MAIN-2026-10"

    # 模拟在 Common Crawl 中检索印尼机械类目标网站 (以 indotrading 或类似外贸B2B目录为例)
    # 实际生产中会通过 CDX API 查询目标域名
    print("正在检索印尼机械行业公开企业页面...")
    
    # 模拟抓取到的测试结果数据（后续会替换为真实的 Common Crawl 解析流）
    mock_results = [
        {"company": "PT Makmur Abadi Mesin", "domain": "makmurabadi.co.id", "email": "sales@makmurabadi.co.id", "industry": "Machinery", "country": "Indonesia"},
        {"company": "Indo Teknik Perkasa", "domain": "indotehnik.id", "email": "info@indotehnik.id", "industry": "Machinery", "country": "Indonesia"},
        {"company": "Jakarta Heavy Equipment", "domain": "jkt-heavy.com", "email": "contact@jkt-heavy.com", "industry": "Machinery", "country": "Indonesia"}
    ]

    # 创建输出目录
    os.makedirs("output", exist_ok=True)
    output_file = "output/indonesia_machinery.csv"

    # 写入 CSV 文件
    print(f"正在生成结果文件: {output_file}")
    with open(output_file, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["company", "domain", "email", "industry", "country"])
        writer.writeheader()
        for row in mock_results:
            writer.writerow(row)

    print("任务完成！CSV 文件已成功生成。")

if __name__ == "__main__":
    run_mvp()
