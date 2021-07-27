import glob
import json
import re
from collections import Counter
from itertools import groupby
from operator import itemgetter

import fire
import jieba

from orm import db, Article, News


def policy_analyser():
    c = Counter()
    for article in Article.select():
        c.update(jieba.cut(article.content))
    [output(word, count) for word, count in c.most_common()]


def news_analyser(trend=None):
    newslist = News.select().order_by(News.date)
    jieba.load_userdict('dict.txt')

    def analyse_all():
        c = Counter()
        for news in newslist:
            c.update(jieba.cut(news.content))
        [output(word, count) for word, count in c.most_common()]

    def analyse_word():
        c = Counter()
        r = {}
        for date, items in groupby(newslist.dicts(), key=itemgetter('date')):
            for news in items:
                c.update(jieba.cut(news['content']))
            r[str(date)] = c[trend]
        with open(f'output/{trend}.json', 'w') as f:
            json.dump(r, f)

    if trend:
        analyse_word()
    else:
        analyse_all()


def news_compiler():
    data = {}
    for path in glob.glob('output/*.json'):
        word = re.search(r'/(.+).json', path).group(1)
        with open(path, 'r') as f:
            data[word] = json.load(f)
    with open(f'output/data.js', 'w') as f:
        f.write('json=' + json.dumps(data))


def output(word, count):
    if len(word) < 2:
        return
    print(word, count)


if __name__ == '__main__':
    db.connect()
    fire.Fire({
        'policy': policy_analyser,
        'news': news_analyser,
        'news:compile': news_compiler,
    })
    db.close()
