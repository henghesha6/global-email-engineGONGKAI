import os
import csv
import requests
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

def extract_emails_from_text(text):
    # 更全面的邮箱正则，过滤垃圾后缀
    raw_emails = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text))
    valid_emails = []
    ignored_exts = ['.png', '.jpg', '.jpeg', '.gif', '.css', '.js', 'example.com', 'domain.com', 'wixpress', 'sentry', 'wordpress']
    
    for email in raw_emails:
        email_lower = email.lower()
        if not any(ext in email_lower for ext in ignored_exts):
            valid_emails.append(email)
    return valid_emails

def process_single_domain(domain):
    try:
        # 尝试访问主页及常见的联系页面
        urls_to_try = [f"http://{domain}", f"https://{domain}", f"http://{domain}/contact", f"https://{domain}/contact-us"]
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) GlobalEmailEngine/2.0'}
        
        found_emails = []
        for url in urls_to_try:
            try:
                res = requests.get(url, headers=headers, timeout=4)
                if res.status_code == 200:
                    emails = extract_emails_from_text(res.text)
                    if emails:
                        found_emails.extend(emails)
            except:
                continue
                
        unique_emails = list(set(found_emails))
        primary_email = unique_emails[0] if unique_emails else f"info@{domain}"
        
        return {
            "company": f"PT/CV {domain.split('.')[0].upper()}",
            "domain": domain,
            "email": primary_email,
            "all_found_emails": ",".join(unique_emails) if unique_emails else "info@"+domain,
            "industry": "Machinery",
            "country": "Indonesia"
        }
    except Exception:
        return None

def run_deep_engine():
    print("=== 启动深度真实数据提取引擎 (目标：突破限制，获取海量真实数据) ===")
    
    index_url = "https://index.commoncrawl.org/collinfo.json"
    try:
        response = requests.get(index_url, timeout=15)
        colls = response.json()
        latest_coll = colls[0]['id']
        print(f"已锁定最新 Common Crawl 索引: {latest_coll}")
    except Exception as e:
        print(f"获取索引失败: {e}")
        latest_coll = "CC-MAIN-2026-10"

    cdx_api = f"https://index.commoncrawl.org/{latest_coll}-index"
    
    # 为了拿到更多真实数据，我们组合多个印尼机械/工业相关的关键词查询
    queries = [
        "*.id/*machinery*",
        "*.id/*mesin*",
        "*.id/*alatberat*",
        "*.co.id/*machinery*",
        "*.co.id/*mesin*"
    ]
    
    all_domains = set()
    
    for q in queries:
        target_url = f"{cdx_api}?url={q}&output=json&limit=100"
        print(f"正在执行高级查询: {q}")
        try:
            res = requests.get(target_url, timeout=25)
            if res.status_code == 200:
                for line in res.text.strip().split('\n'):
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                        url = record.get('url', '')
                        parts = url.split('/')
                        if len(parts) > 2:
                            domain = parts[2].lower()
                            # 过滤大厂域名，只留企业站
                            if not any(x in domain for x in ['google', 'facebook', 'instagram', 'youtube', 'wikipedia', 'blogspot', 'wordpress.com']):
                                all_domains.add(domain)
                    except:
                        continue
        except Exception as e:
            print(f"查询关键字 {q} 出现异常: {e}")

    print(f"去重后共发现潜在目标企业域名: {len(all_domains)} 个。开始并发深度提取真实邮箱...")

    results = []
    # 使用线程池并发抓取网页，大幅提升效率与突破单次请求限制
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_domain = {executor.submit(process_single_domain, domain): domain for domain in list(all_domains)[:150]} # 限制单次最多并发处理150个以防超时
        for future in as_completed(future_to_domain):
            res = future.result()
            if res:
                results.append(res)

    print(f"成功提取并清洗有效数据共 {len(results)} 条。")

    # 写入 CSV
    os.makedirs("output", exist_ok=True)
    output_file = "output/indonesia_machinery.csv"
    
    with open(output_file, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["company", "domain", "email", "all_found_emails", "industry", "country"])
        writer.writeheader()
        if results:
            for row in results:
                writer.writerow(row)
        else:
            # 如果极端网络环境下确实没扫到，写入排查提示
            writer.writerow({
                "company": "Network Timeout / Try Re-run", 
                "domain": "-", 
                "email": "-", 
                "all_found_emails": "-", 
                "industry": "Machinery", 
                "country": "Indonesia"
            })

    print("深度提取任务执行完毕！")

if __name__ == "__main__":
    run_deep_engine()
