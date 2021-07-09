from collections import Counter

import fire
import jieba

from orm import db, Article, News


def policy_analyser():
    c = Counter()
    for article in Article.select():
        c.update(jieba.cut(article.content))
    [output(word, count) for word, count in c.most_common()]


def news_analyser():
    c = Counter()
    for news in News.select():
        c.update(jieba.cut(news.content))
    [output(word, count) for word, count in c.most_common()]


def output(word, count):
    if len(word) < 2:
        return
    print(word, count)


if __name__ == '__main__':
    db.connect()
    fire.Fire({
        'policy': policy_analyser,
        'news': news_analyser,
    })
    db.close()
