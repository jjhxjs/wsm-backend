from operator import length_hint
import string
from enum import auto
from itertools import count
from math import log10
from warnings import catch_warnings

from app import app, db
from app.models.author_indices import Author_Indices
from app.models.author_wt import Author_Weight
from app.models.book import Book
from app.models.content_indices import Content_Indices
from app.models.content_wt import Content_Weight
from app.models.description_indices import Description_Indices
from app.models.description_wt import Description_Weight
from app.models.title_indices import Title_Indices
from app.models.title_wt import Title_Weight
from flask import jsonify, request
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sqlalchemy import and_, func, or_, union_all, between
from sqlalchemy import text
import sys

# 书本数量是需要修改的，目前是99本


def construct_content_vocabulary(start, end):
    ind = 0
    ps = PorterStemmer()
    wnl = WordNetLemmatizer()

    for i in range(start, end):
        print('epoch', i)
        res = db.session.query(Book.content, Book.id).filter(
            Book.id.between(i*100, i*100+99)).all()
        if len(res) == 0:
            continue
        for data in res:
            tokens = {}
            j = 0
            sqlstr = 'INSERT INTO content_indices VALUES '
            content = data[0]
            id = data[1]
            ind += 1
            if content != None:
                print('processing book id', id, 'length', len(content))
                for word in word_tokenize(content):
                    if word not in string.punctuation:
                        word = word.encode('UTF-8').decode('UTF-8-sig')
                        word = word.lower()
                        word = wnl.lemmatize(word)
                        word = ps.stem(word)
                        if word in tokens:
                            tokens[word] += ("+" + str(j))
                        else:
                            tokens[word] = str(j)
                        j += 1

                adds = []
                for token in tokens:
                    tf = tokens[token].split("+").__len__()
                    tf_wt = 1 + log10(tf)
                    sqlstr += "('{}',{},'{}',{},{}),\n".format(token.replace("'",
                                                                             "\\'").replace(":", ""), id, tokens[token], tf, tf_wt)
                sqlstr = sqlstr[:-2]+'\n'
                sqlstr += 'ON DUPLICATE KEY UPDATE indices=values(indices),tf=values(tf),tf_wt=values(tf_wt)'
                try:
                    db.session.execute(sqlstr)
                except Exception as e:
                    print('err:',id)
                    continue

                # db.session.add_all(adds)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print('err')


def construct_title_vocabulary(start, end):
    ind = 0
    ps = PorterStemmer()
    wnl = WordNetLemmatizer()

    processed_id = db.session.query(Content_Indices.book_id).distinct().all()
    print(processed_id)
    for i in range(start, end):
        print('epoch', i)
        res = db.session.query(Book.content, Book.id).filter(
            Book.id.between(i*100, i*100+99)).all()
        if len(res) == 0:
            continue
        for data in res:
            j = 0
            sqlstr = 'INSERT INTO content_indices VALUES '
            tokens = {}
            content = data[0]
            id = data[1]
            ind += 1
            if content != None and (id,) not in processed_id:
                print('processing book id', id, 'length', len(content))
                for word in word_tokenize(content):
                    if word not in string.punctuation:
                        word = word.encode('UTF-8').decode('UTF-8-sig')
                        word = word.lower()
                        word = wnl.lemmatize(word)
                        word = ps.stem(word)
                        if word in tokens:
                            tokens[word] += ("+" + str(j))
                        else:
                            tokens[word] = str(j)
                        j += 1

                adds = []
                for token in tokens:
                    tf = tokens[token].split("+").__len__()
                    tf_wt = 1 + log10(tf)
                    sqlstr += "('{}',{},'{}',{},{}),\n".format(token.replace("'",
                                                                             "\\'").replace(":", ""), id, tokens[token], tf, tf_wt)
                sqlstr = sqlstr[:-2]+'\n'
                sqlstr += 'ON DUPLICATE KEY UPDATE indices=values(indices),tf=values(tf),tf_wt=values(tf_wt)'
                try:
                    db.session.execute(sqlstr)
                except Exception as e:
                    print('err:',id)
                    continue

                # db.session.add_all(adds)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print('err')
            else:
                print('processed book id', id, 'skip')


def construct_author_vocabulry():
    ps = PorterStemmer()
    wnl = WordNetLemmatizer()

    for i in range(1, 100):
        res = Book.query.filter(Book.id == i).all()
        data = [tmp.to_dict() for tmp in res]
        author = data[0].get('author')
        tokens = {}
        j = 0

        if author != None:
            for word in word_tokenize(author):
                if word not in string.punctuation:
                    word = word.encode('UTF-8').decode('UTF-8-sig')
                    word = word.lower()
                    word = wnl.lemmatize(word)
                    word = ps.stem(word)
                    if word in tokens:
                        tokens[word] += ("+" + str(j))
                    else:
                        tokens[word] = str(j)
                    j += 1

            adds = []
            for token in tokens:
                tf = tokens[token].split("+").__len__()
                tf_wt = 1 + log10(tf)
                indices = Author_Indices(
                    term=token, book_id=i, indices=tokens[token], tf=tf, tf_wt=tf_wt)
                adds.append(indices)
            db.session.add_all(adds)
            db.session.commit()


def construct_description_vocabulary():
    ps = PorterStemmer()
    wnl = WordNetLemmatizer()

    for i in range(1, 100):
        res = Book.query.filter(Book.id == i).all()
        data = [tmp.to_dict() for tmp in res]
        description = data[0].get('description')
        tokens = {}
        j = 0

        if description != None:
            for word in word_tokenize(description):
                if word not in string.punctuation:
                    word = word.encode('UTF-8').decode('UTF-8-sig')
                    word = word.lower()
                    word = wnl.lemmatize(word)
                    word = ps.stem(word)
                    if word in tokens:
                        tokens[word] += ("+" + str(j))
                    else:
                        tokens[word] = str(j)
                    j += 1

            adds = []
            for token in tokens:
                tf = tokens[token].split("+").__len__()
                tf_wt = 1 + log10(tf)
                indices = Description_Indices(
                    term=token, book_id=i, indices=tokens[token], tf=tf, tf_wt=tf_wt)
                adds.append(indices)
            db.session.add_all(adds)
            db.session.commit()


def calculate_content_wt():
    res = db.session.query(Content_Indices.term, func.count(
        '*')).group_by(Content_Indices.term).all()
    for i,data in enumerate(res):
        df = data[1]
        print(i)
        idf = log10(84837 / df)
        db.session.add(Content_Weight(term=data[0], df=df, idf=idf))
        if i%1000==999:
            db.session.commit()


def calculate_title_wt():
    res = db.session.query(Title_Indices.term, func.count(
        '*')).group_by(Title_Indices.term).all()
    for i,data in enumerate(res):
        df = data[1]
        print(i)
        idf = log10(84837 / df)
        db.session.add(Title_Weight(term=data[0], df=df, idf=idf))
        if i%1000==999:
            db.session.commit()


def calculate_author_wt():
    res = db.session.query(Author_Indices.term, func.count('*')
                           ).group_by(Author_Indices.term).all()
    for i,data in enumerate(res):
        df = data[1]
        print(i)
        idf = log10(84837 / df)
        db.session.add(Author_Weight(term=data[0], df=df, idf=idf))
        if i%1000==999:
            db.session.commit()


def calculate_description_wt():
    res = db.session.query(Description_Indices.term, func.count('*')
                           ).group_by(Description_Indices.term).all()
    for i,data in enumerate(res):
        df = data[1]
        print(i)
        idf = log10(84837 / df)
        db.session.add(Description_Weight(term=data[0], df=df, idf=idf))
        if i%1000==999:
            db.session.commit()


def main():
    construct_content_vocabulary()


if __name__ == "__main__":
    main()
