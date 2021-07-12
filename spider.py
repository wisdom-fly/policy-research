import os
import random
import re
import time
from datetime import date, timedelta

import fire
import peewee
import requests
import tushare
from bs4 import BeautifulSoup

from orm import db, Article, News


def policy_spider(start=1):
    db.create_tables([Article])

    def handle_index_loop(index):
        for url in index:
            print(url)
            try:
                Article.get(Article.url == url)
                print('(stored & skipped)')
            except peewee.DoesNotExist:
                article = extract_article(url)
                Article.get_or_create(url=url, defaults={
                    'index_code': article['meta']['索引号'],
                    'document_code': article['meta']['文号'],
                    'categories': article['meta']['分类'],
                    'title': article['meta']['标题'],
                    'author': article['meta']['发布机构'],
                    'content': article['content'],
                    'url': url,
                    'created_at': article['meta']['成文日期'],
                    'published_at': article['meta']['发布日期'],
                })
                time.sleep(random.randint(5, 30))
        time.sleep(1)

    def extract_index(url):
        r = requests.get(url)
        if r.status_code == 404:
            r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html5lib')
        return [a.get('href') for a in soup.find('div', 'viewList').find('ul').find_all('a')]

    def extract_article(url):
        if 'www.gd.gov.cn/gkml/content' in url:
            id = re.search(r'post_(\d+).', url).group(1)
            dir1 = int(int(id) / 1000000)
            dir2 = int(int(id) / 1000)
            url = f'http://www.gd.gov.cn/gkmlpt/content/{dir1}/{dir2}/post_{id}.html'
        while True:
            r = requests.get(url)
            if r.status_code == 500:
                print('Server Error 500, retrying...')
                time.sleep(60)
            else:
                break
        soup = BeautifulSoup(r.text, 'html5lib')

        def extract_wjk():
            meta = {}
            for meta_item in soup.find('div', 'introduce').find_all('div', 'col'):
                key = meta_item.find('label').string.replace('：', '')
                val = meta_item.find('span').string
                meta[key] = val
            content = soup.find('div', 'zw').get_text()
            return meta, content

        def extract_gkml():
            meta = {}
            cells = [td.get_text().strip() for td in soup.find('div', 'classify').find_all('td')]
            for i in range(0, len(cells), 2):
                k = cells[i].rstrip('：').replace('名称', '标题')
                v = cells[i + 1]
                meta[k] = v
            content = soup.find('div', 'article-content').get_text()
            return meta, content

        if 'www.gd.gov.cn/zwgk/wjk' in url:
            meta, content = extract_wjk()
        elif 'www.gd.gov.cn/gkmlpt' in url:
            meta, content = extract_gkml()
        else:
            raise NotImplementedError()
        return {'meta': meta, 'content': content}

    if start == 1:
        print('P1')
        handle_index_loop(extract_index('http://www.gd.gov.cn/zwgk/wjk/qbwj/index.html'))
    i = start if start > 1 else 2
    while True:
        try:
            print('\nP%s' % i)
            handle_index_loop(extract_index(f'http://www.gd.gov.cn/zwgk/wjk/qbwj/index_{i}.html'))
            i += 1
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print('All done.')
                break
            raise e


def news_spider():
    db.create_tables([News])

    tspro = tushare.pro_api(os.getenv('TUSHARE_TOKEN'))
    latest = News.select().order_by(News.date.desc()).first()
    d = latest.date if latest else date(2010, 1, 1)
    while True:
        ds = d.strftime('%Y%m%d')
        print('\n' + ds)
        for news in tspro.cctv_news(date=ds).itertuples():
            print(news.title)
            News.get_or_create(title=news.title, date=news.date, defaults={'content': news.content})
        d = d + timedelta(days=1)
        if d >= date.today():
            break
        else:
            time.sleep(35)


if __name__ == '__main__':
    db.connect()
    fire.Fire({
        'policy': policy_spider,
        'news': news_spider,
    })
    db.close()
