import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, date, timedelta  # 导入日期处理模块
from logger import LOG  # 导入日志模块


class HackernewsClient:
    def __init__(self):
        self.url = 'https://news.ycombinator.com/'

    def fetch_hackernews_top_stories(self):
        response = requests.get(self.url)
        response.raise_for_status()  # 检查请求是否成功

        soup = BeautifulSoup(response.text, 'html.parser')
        # 查找包含新闻的所有 <tr> 标签
        stories = soup.find_all('tr', class_='athing')

        top_stories = []
        for story in stories:
            title_tag = story.find('span', class_='titleline').find('a')
            if title_tag:
                title = title_tag.text
                link = title_tag['href']
                top_stories.append({'title': title, 'link': link})

        return top_stories
    
    def export_daily_progress(self):
        LOG.debug(f"[准备导出项目进度]")
        today = datetime.now().date().isoformat()  # 获取今天的日期
        stories = self.fetch_hackernews_top_stories()  # 获取今天的更新数据
        
        repo_dir = os.path.join('daily_progress', 'harkernews')  # 构建存储路径
        os.makedirs(repo_dir, exist_ok=True)  # 确保目录存在
        
        file_path = os.path.join(repo_dir, f'{today}.md')  # 构建文件路径
        with open(file_path, 'w') as file:
            file.write(f"# Daily Progress for  ({today})\n\n")
            file.write("\n## Top News Today\n")
            if stories:
                for idx, story in enumerate(stories, start=1):
                    file.write(f"{idx}. {story['title']}")
                    file.write(f"   Link: {story['link']}\n")
                else:
                    file.write("No stories found.")
        
        LOG.info(f"项目每日进展文件生成： {file_path}")  # 记录日志
        return file_path

if __name__ == "__main__":
    client = HackernewsClient()
    stories = client.fetch_hackernews_top_stories()
    if stories:
        for idx, story in enumerate(stories, start=1):
            print(f"{idx}. {story['title']}")
            print(f"   Link: {story['link']}\n")
    else:
        print("No stories found.")