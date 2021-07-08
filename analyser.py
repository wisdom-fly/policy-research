from collections import Counter

import jieba

from orm import db, Article


def output(word, count):
    if len(word) < 2:
        return
    print(word, count)


if __name__ == '__main__':
    db.connect()
    c = Counter()
    for article in Article.select():
        c.update(jieba.cut(article.content))
    [output(word, count) for word, count in c.most_common()]
    db.close()
