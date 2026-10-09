import os
import csv
import requests
import json
import re

def fetch_real_common_crawl():
    print("=== 正在启动真实 Common Crawl 批量爬虫引擎 ===")
    
    # 1. 获取最新索引
    index_url = "https://index.commoncrawl.org/collinfo.json"
    try:
        response = requests.get(index_url, timeout=15)
        colls = response.json()
        latest_coll = colls[0]['id']
        print(f"已锁定最新 Common Crawl 索引: {latest_coll}")
    except Exception as e:
        print(f"获取索引失败: {e}")
        return

    # 2. 查询印尼机械相关域名 (限定 .id 域名，URL中包含 machinery 或 alatberat)
    cdx_api = f"https://index.commoncrawl.org/{latest_coll}-index"
    target_url = f"{cdx_api}?url=*.id/*machinery*&output=json&limit=50"
    
    print(f"正在向 Common Crawl 查询真实网页 URL...")
    results = []
    seen_domains = set()

    try:
        res = requests.get(target_url, timeout=30)
        if res.status_code == 200:
            lines = res.text.strip().split('\n')
            print(f"共检索到 {len(lines)} 条原始记录，开始解析域名和抓取页面...")
            
            for line in lines:
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    url = record.get('url', '')
                    # 提取纯域名
                    parts = url.split('/')
                    if len(parts) > 2:
                        domain = parts[2]
                        if domain not in seen_domains and "google" not in domain and "facebook" not in domain:
                            seen_domains.add(domain)
                            
                            # 尝试直接请求该域名的主页来提取真实公开邮箱
                            try:
                                home_page = f"http://{domain}"
                                page_res = requests.get(home_page, timeout=5)
                                if page_res.status_code == 200:
                                    # 用正则匹配页面中的邮箱
                                    emails = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', page_res.text))
                                    # 过滤掉常见无效后缀
                                    valid_emails = [e for e in emails if not any(x in e.lower() for x in ['.png', '.jpg', '.gif', 'example', 'domain', 'wix']) ]
                                    
                                    found_email = valid_emails[0] if valid_emails else f"info@{domain}"
                                    results.append({
                                        "company": f"Company {domain.split('.')[0].upper()}",
                                        "domain": domain,
                                        "email": found_email,
                                        "industry": "Machinery",
                                        "country": "Indonesia"
                                    })
                            except:
                                # 如果主页无法直接连通，先记录域名和基础邮箱格式
                                results.append({
                                    "company": f"Company {domain.split('.')[0].upper()}",
                                    "domain": domain,
                                    "email": f"info@{domain}",
                                    "industry": "Machinery",
                                    "country": "Indonesia"
                                })
                except Exception as inner_e:
                    continue
        else:
            print(f"CDX 查询返回状态码: {res.status_code}")

    except Exception as e:
        print(f"请求 Common Crawl 异常: {e}")

    # 3. 写入 CSV
    os.makedirs("output", exist_ok=True)
    output_file = "output/indonesia_machinery.csv"
    
    print(f"正在生成 CSV 文件，有效企业数: {len(results)}")
    with open(output_file, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["company", "domain", "email", "industry", "country"])
        writer.writeheader()
        if results:
            for row in results:
                writer.writerow(row)
        else:
            # 若因网络原因本次未抓到，写一条提示
            writer.writerow({"company": "No Live Target Found in this run", "domain": "-", "email": "-", "industry": "Machinery", "country": "Indonesia"})

    print("真实抓取任务完成！")

if __name__ == "__main__":
    fetch_real_common_crawl()
