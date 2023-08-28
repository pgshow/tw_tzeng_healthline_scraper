import time

import requests
from bs4 import BeautifulSoup


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

# 保存已经爬取的网址，用于去重
unique_urls = set()

# 抓取sitemapindex的内容，获取所有articles-n.xml的链接
sitemap_index_url = "https://www.healthline.com/hlcms.xml"
response = requests.get(sitemap_index_url, headers=headers)
soup = BeautifulSoup(response.text, "lxml")

# 获取所有的sitemap标签，用于进度显示
all_sitemaps = soup.find_all("sitemap")
total_sitemaps = len(all_sitemaps)
print(f"Total sitemaps to crawl: {total_sitemaps}")

for index, sitemap in enumerate(all_sitemaps):
    time.sleep(1)
    articles_xml_url = sitemap.find("loc").text

    print(f"Crawling sitemap {index+1} of {total_sitemaps}: {articles_xml_url}")

    # 对于每个articles-n.xml，抓取里面的所有文章链接
    response = requests.get(articles_xml_url, headers=headers)
    articles_soup = BeautifulSoup(response.text, "lxml")
    for url in articles_soup.find_all("url"):
        article_url = url.find("loc").text

        # 打印正在爬取的文章链接
        print(f"  Crawling article URL: {article_url}")

        # 保存到集合中进行去重
        unique_urls.add(article_url)

# 将结果写入到txt文件
with open("unique_article_urls.txt", "w") as f:
    for url in unique_urls:
        f.write(f"{url}\n")

print("Crawling completed.")
