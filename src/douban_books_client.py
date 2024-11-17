import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from logger import LOG
import time

class DoubanNewBooksClient:
    def __init__(self):
        self.url = 'https://book.douban.com/latest?subcat=%E7%A7%91%E5%AD%A6%E6%96%B0%E7%9F%A5'
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'Referer': 'https://book.douban.com/',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
        }

    def fetch_new_books(self):
        LOG.debug("准备获取豆瓣新书速递。")
        try:
            response = self.session.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            new_books = self.parse_books(response.text)
            return new_books
        except requests.exceptions.HTTPError as e:
            LOG.error(f"HTTP错误: {e}")
        except requests.exceptions.RequestException as e:
            LOG.error(f"请求失败: {e}")
        except Exception as e:
            LOG.error(f"获取豆瓣新书速递失败：{str(e)}")
        return []

    def parse_books(self, html_content):
        LOG.debug("解析豆瓣新书速递的HTML内容。")
        soup = BeautifulSoup(html_content, 'html.parser')
        books = soup.find_all('li', class_='media clearfix')

        new_books = []
        for book in books:
            title_tag = book.find('a', class_='fleft')
            if title_tag:
                title = title_tag.text.strip()
                link = title_tag['href']
            else:
                continue

            image_tag = book.find('img', class_='subject-cover')
            image = image_tag['src'] if image_tag else ""

            abstract_tag = book.find('p', class_='subject-abstract')
            abstract = abstract_tag.text.strip() if abstract_tag else "暂无简介"

            rating_tag = book.find('span', class_='font-small color-red')
            rating = rating_tag.text.strip() if rating_tag else "暂无评分"

            buy_info_tag = book.find('span', class_='buy-info')
            price = buy_info_tag.text.strip() if buy_info_tag else "暂无价格"

            new_books.append({
                'title': title,
                'link': link,
                'image': image,
                'abstract': abstract,
                'rating': rating,
                'price': price
            })
        
        LOG.info(f"成功解析 {len(new_books)} 本豆瓣新书。")
        return new_books

    def export_new_books(self):
        LOG.debug("准备导出豆瓣新书速递。")
        new_books = self.fetch_new_books()

        if not new_books:
            LOG.warning("未找到任何豆瓣新书。")
            return None
        
        date = datetime.now().strftime('%Y-%m-%d')
        hour = datetime.now().strftime('%H')

        dir_path = os.path.join('douban_books', date)
        os.makedirs(dir_path, exist_ok=True)

        file_path = os.path.join(dir_path, f'{hour}.md')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"# 豆瓣新书速递 ({date} {hour}:00)\n\n")
            for idx, book in enumerate(new_books, start=1):
                file.write(f"## {idx}. [{book['title']}]({book['link']})\n")
                file.write(f"**评分**: {book['rating']}\n")
                file.write(f"**价格**: {book['price']}\n")
                file.write(f"**摘要**: {book['abstract']}\n")
                file.write(f"![封面]({book['image']})\n")
                file.write("\n---\n")
        
        LOG.info(f"豆瓣新书速递文件生成：{file_path}")
        return file_path


if __name__ == "__main__":
    client = DoubanNewBooksClient()
    client.export_new_books()
