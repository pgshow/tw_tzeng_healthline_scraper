import os
import re

import requests
from bs4 import BeautifulSoup
import time

headers = {
    'authority': 'www.healthline.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5,ja;q=0.4',
    'cache-control': 'max-age=0',
    # 'cookie': 'blab=726a7b64-2d5b-4d14-8638-1ca9ad7f9fc7; tglr_anon_id=672c0176-b248-48d4-aefa-5aa211d653b6; tglr_hash_id=h_7255498a79be78437a0b78e82a03857be7fbebbcb52072dc117e086aac590042; tglr_http_only=672c0176-b248-48d4-aefa-5aa211d653b6; chsn_cnsnt=www.healthline.com%3AC0001%2CC0002%2CC0003%2CC0004%2CC0005; tglr_tenant_id=src_1Tqf7BF96WTbG5QbUndHWIgKoFo; pmpdid=21f47361-2782-46c0-859d-fd60b4344a8f; usprivacy=1YNY; cohsn_xs_id=2234002f-6418-4465-b28d-1cbc384048e8; tglr_sess_id=283e7684-4135-47d0-a524-49882aa98dd3; tglr_ref=; tglr_req=https://www.healthline.com/articles-6.xm; tglr_sess_count=3; tglr_smpl=0; lastContentSeen=/health/restrictions-after-cataract-surgery|cataract',
    'dnt': '1',
    'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54',
}

# 创建输出目录
if not os.path.exists("output"):
    os.makedirs("output")

# 读取所有的文章URL
with open("unique_article_urls.txt", "r") as f:
    all_article_urls = set(f.read().strip().split("\n"))

# 读取已经爬取的文章URL
if os.path.exists("already.txt"):
    with open("already.txt", "r") as f:
        already_crawled = set(f.read().strip().split("\n"))
else:
    already_crawled = set()


# 函数：将文件名中的特殊字符过滤或替换
def sanitize_filename(filename):
    # 过滤不能用作Windows文件名的特殊字符，并用空格替代
    filename = re.sub(r'[\\/:*?"<>|]', ' ', filename)
    # 将连续的空格缩减为一个空格
    filename = re.sub(' +', ' ', filename).strip()
    return filename


def save_article(sanitized_title, content):
    """保存文章到本地，如果文件名已存在，则在文件名后添加数字"""
    count = 1
    original_sanitized_title = sanitized_title
    while os.path.exists(f"output/{sanitized_title}.txt"):
        sanitized_title = f"{original_sanitized_title}_{count}"
        count += 1

    with open(f"output/{sanitized_title}.txt", "w", encoding="utf-8") as f:
        f.write(content.strip())


# 计算尚未爬取的文章URL
to_crawl = all_article_urls - already_crawled

while to_crawl:
    url = to_crawl.pop()  # 取出一个尚未爬取的URL
    retry_count = 0

    print(f"Remaining: {len(to_crawl)}")

    while retry_count < 5:
        try:
            print(f"Crawling article: {url}")

            response = requests.get(url, timeout=10, headers=headers)
            if response.status_code == 404 or response.status_code == 410 or 'assessment: Error: extractChildren: No children found in' in response.text or '/health/video/' in url:
                print("Unavailable page, skipping...")
                # 添加到已经爬过列表
                already_crawled.add(url)
                with open("already.txt", "w") as f:
                    f.write("\n".join(already_crawled))
                to_crawl = all_article_urls - already_crawled
                break

            soup = BeautifulSoup(response.text, "html.parser")

            # 找到并提取标题
            title_tag = soup.find("h1")
            if title_tag:
                title = title_tag.text.strip()
                sanitized_title = sanitize_filename(title)
                print(sanitized_title)

                # 找到并提取内容
                article_body = soup.select_one("article.article-body")
                if article_body:
                    content = ""
                    for tag in article_body.find_all(['p', 'h2', 'li']):
                        if tag.name == 'h2':
                            content += f"\n<h2>{tag.text.strip()}</h2>"  # 修改h2标签的标注方式
                        elif tag.name == 'li':
                            content += f"\n{tag.text.strip()}"  # 在每个<li>前添加换行符并标记
                        else:
                            content += f"\n{tag.text.strip()}"  # 在每个<p>前添加换行符

                    # 保存文章
                    save_article(sanitized_title, content)

                # 添加到已经爬过列表
                already_crawled.add(url)
                with open("already.txt", "w") as f:
                    f.write("\n".join(already_crawled))
                to_crawl = all_article_urls - already_crawled

            else:
                print("No title found, please check...")
                exit()

            # time.sleep(1)
            break  # 成功爬取，跳出重试循环
        except requests.RequestException as e:
            retry_count += 1
            print(f"Failed to crawl {url}, retrying ({retry_count})...")
            time.sleep(5)

print("Completed crawling and extracting articles.")
