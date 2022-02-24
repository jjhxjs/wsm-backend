from operator import ne
import re
from app.models.description_wt import Description_Weight
import string
from itertools import count

from app import app, db
from app.models.author_indices import Author_Indices
from app.models.author_wt import Author_Weight
from app.models.book import Book
from app.models.content_indices import Content_Indices
from app.models.content_wt import Content_Weight
from app.models.description_indices import Description_Indices
from app.models.title_indices import Title_Indices
from app.models.title_wt import Title_Weight
from flask import jsonify, request
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sqlalchemy import and_, or_, union_all
from app.func.correct import *
from app import cache

@cache.memoize(timeout=300)
def search_books_in_list(search_list, start=0, end=5000):
    sql = "SELECT id, title, author, year, url_index, description FROM book WHERE year > " + str(start) + " AND year < " + str(end) + " AND id IN ("
    for i, book in enumerate(search_list):
        if i == 0:
            sql += str(book)
        else:
            sql += ("," + str(book))
    sql += ") ORDER BY FIELD(id"
    for book in search_list:
        sql += ("," + str(book))
    sql += ")"
    res = db.session.execute(sql).fetchall()

    return res

@cache.memoize(timeout=300)
def search_by_content(q, t, p):
    ps = PorterStemmer()
    wnl = WordNetLemmatizer()
    terms = {}
    correct_words = ""
    mistake = False

    wildcard_words = []
    if q != None and q != "":
        for words in q.split(" "):
            if "*" in words:
                wildcard_words.append(words.replace("*", "%"))
                continue
            for word in word_tokenize(words):
                if word not in string.punctuation:
                    word = word.encode('UTF-8').decode('UTF-8-sig')
                    word = word.lower()
                    word = wnl.lemmatize(word)
                    word = ps.stem(word) # 首先将query中的term提取出来
                    res = []
                    # print(word)
                    res = db.session.query(Content_Indices.term, Content_Indices.book_id, Content_Indices.indices).filter(Content_Indices.term == word).all()
                    
                    if res.__len__() == 0:
                        # 对单词纠错
                        mistake = True
                        prepare()
                        word = correct_text_generic(word)
                        res = db.session.query(Content_Indices.term, Content_Indices.book_id, Content_Indices.indices).filter(Content_Indices.term == word).all()
                    
                    correct_words += (word + " ")

                    for item in res:
                        if item[0] in terms:
                            if item[1] not in terms[item[0]]:
                                terms[item[0]][item[1]] = item[2].split("+")
                        else:
                            terms[item[0]] = {}
                            terms[item[0]][item[1]] = item[2].split("+")

    # print(terms)
    # terms构建完成
    
    final_list = []
    if terms.__len__() > 0:
        terms_bid = {}
        for term in terms:
            terms_bid[term] = list(terms[term].keys())

        # print(terms_bid)
        
        book_list = terms_bid[list(terms_bid.keys())[0]]
        if t == "SOME" or t == "NONE":
            for term in terms_bid:
                book_list = list(set(book_list) | set(terms_bid[term])) # 求并集
        elif t == "ALL":
            for term in terms_bid:
                book_list = list(set(book_list) & set(terms_bid[term])) # 求交集

            # 这段代码只有ALL的时候才会执行
            # if p == "true": # query中每个单词要相邻
            #     term_list = list(terms.keys())
            #     for book in book_list:
            #         flag1 = False # 这本书是否需要被检索
            #         for index in terms[term_list[0]][book]:
            #             flag2 = True
            #             next_index = index
            #             for term in term_list[1:]:
            #                 next_index = str(int(next_index) + 1)
            #                 if next_index not in terms[term][book]:
            #                     flag2 = False
            #             flag1 = flag1 or flag2
            #         if not flag1:
            #             book_list.remove(book)
        
        search_list = {}
        for book in book_list: # 计算每本书的权重
            search_list[book] = 0
            for term in terms:
                tf_res = db.session.query(Content_Indices.tf_wt).filter(and_(Content_Indices.term == term, Content_Indices.book_id == book)).first()
                df_res = db.session.query(Content_Weight.idf).filter(Content_Weight.term == term).first()
                search_list[book] += (tf_res[0] * df_res[0])
        search_list = sorted(search_list.items(), key=lambda x:x[1], reverse=True)
        for book in search_list:
            final_list.append(book[0])

    for wildcard_word in wildcard_words:
        fuzzy_res = db.session.query(Content_Indices.book_id).filter(Content_Indices.term.like(wildcard_word)).all()
        for i in fuzzy_res:
            if i[0] not in final_list:
                print(i[0])
                final_list.append(i[0])

    return final_list, correct_words, mistake

@cache.memoize(timeout=300)
def search_by_title(q, t, p):
    print(t)
    ps = PorterStemmer()
    wnl = WordNetLemmatizer()
    terms = {}
    correct_words = ""
    mistake = False

    wildcard_words = []
    if q != None and q != "":
        for words in q.split(" "):
            if "*" in words:
                wildcard_words.append(words.replace("*", "%"))
                continue
            for word in word_tokenize(words):
                if word not in string.punctuation:
                    word = word.encode('UTF-8').decode('UTF-8-sig')
                    word = word.lower()
                    word = wnl.lemmatize(word)
                    word = ps.stem(word) # 首先将query中的term提取出来
                    res = []
                    
                    res = db.session.query(Title_Indices.term, Title_Indices.book_id, Title_Indices.indices).filter(Title_Indices.term == word).all()
                    
                    if res.__len__() == 0:
                        # 对单词纠错
                        mistake = True
                        prepare()
                        word = correct_text_generic(word)
                        res = db.session.query(Title_Indices.term, Title_Indices.book_id, Title_Indices.indices).filter(Title_Indices.term == word).all()
                    
                    correct_words += (word + " ")

                    for item in res:
                        if item[0] in terms:
                            if item[1] not in terms[item[0]]:
                                terms[item[0]][item[1]] = item[2].split("+")
                        else:
                            terms[item[0]] = {}
                            terms[item[0]][item[1]] = item[2].split("+")

    # print(terms)
    # terms构建完成
    
    final_list = []
    if terms.__len__() > 0:
        terms_bid = {}
        for term in terms:
            terms_bid[term] = list(terms[term].keys())

        # print(terms_bid)
        
        book_list = terms_bid[list(terms_bid.keys())[0]]
        if t == "SOME" or t == "NONE":
            for term in terms_bid:
                book_list = list(set(book_list) | set(terms_bid[term])) # 求并集
        elif t == "ALL":
            for term in terms_bid:
                book_list = list(set(book_list) & set(terms_bid[term])) # 求交集

            # 这段代码只有ALL的时候才会执行
            print(p)
            if p == "true": # query中每个单词要相邻
                term_list = list(terms.keys())
                for book in book_list:
                    flag1 = False # 这本书是否需要被检索
                    for index in terms[term_list[0]][book]:
                        flag2 = True
                        next_index = index
                        for term in term_list[1:]:
                            next_index = str(int(next_index) + 1)
                            if next_index not in terms[term][book]:
                                flag2 = False
                        flag1 = flag1 or flag2
                    if not flag1:
                        book_list.remove(book)
        
        search_list = {}
        print(book_list)
        for book in book_list: # 计算每本书的权重
            search_list[book] = 0
            for term in terms:
                tf_res = db.session.query(Title_Indices.tf_wt).filter(and_(Title_Indices.term == term, Title_Indices.book_id == book)).first()
                df_res = db.session.query(Title_Weight.idf).filter(Title_Weight.term == term).first()
                if tf_res:
                    search_list[book] += (tf_res[0] * df_res[0])
        search_list = sorted(search_list.items(), key=lambda x:x[1], reverse=True)
        for book in search_list:
            final_list.append(book[0])

    for wildcard_word in wildcard_words:
        fuzzy_res = db.session.query(Title_Indices.book_id).filter(Title_Indices.term.like(wildcard_word)).all()
        for i in fuzzy_res:
            if i[0] not in final_list:
                print(i[0])
                final_list.append(i[0])

    return final_list, correct_words, mistake
                
@cache.memoize(timeout=300)
def search_by_author(q, t, p):
    ps = PorterStemmer()
    wnl = WordNetLemmatizer()
    terms = {}
    correct_words = ""
    mistake = False

    wildcard_words = []
    if q != None and q != "":
        for words in q.split(" "):
            if "*" in words:
                wildcard_words.append(words.replace("*", "%"))
                continue
            for word in word_tokenize(words):
                if word not in string.punctuation:
                    word = word.encode('UTF-8').decode('UTF-8-sig')
                    word = word.lower()
                    word = wnl.lemmatize(word)
                    word = ps.stem(word) # 首先将query中的term提取出来
                    res = []
                    
                    res = db.session.query(Author_Indices.term, Author_Indices.book_id, Author_Indices.indices).filter(Author_Indices.term == word).all()
                    
                    if res.__len__() == 0:
                        # 对单词纠错
                        mistake = True
                        prepare()
                        word = correct_text_generic(word)
                        res = db.session.query(Author_Indices.term, Author_Indices.book_id, Author_Indices.indices).filter(Author_Indices.term == word).all()
                    
                    correct_words += (word + " ")

                    for item in res:
                        if item[0] in terms:
                            if item[1] not in terms[item[0]]:
                                terms[item[0]][item[1]] = item[2].split("+")
                        else:
                            terms[item[0]] = {}
                            terms[item[0]][item[1]] = item[2].split("+")

    # print(terms)
    # terms构建完成
    
    final_list = []
    if terms.__len__() > 0:
        terms_bid = {}
        for term in terms:
            terms_bid[term] = list(terms[term].keys())

        # print(terms_bid)
        
        book_list = terms_bid[list(terms_bid.keys())[0]]
        if t == "SOME" or t == "NONE":
            for term in terms_bid:
                book_list = list(set(book_list) | set(terms_bid[term])) # 求并集
        elif t == "ALL":
            for term in terms_bid:
                book_list = list(set(book_list) & set(terms_bid[term])) # 求交集

            # 这段代码只有ALL的时候才会执行
            # if p == "true": # query中每个单词要相邻
            #     term_list = list(terms.keys())
            #     for book in book_list:
            #         flag1 = False # 这本书是否需要被检索
            #         for index in terms[term_list[0]][book]:
            #             flag2 = True
            #             next_index = index
            #             for term in term_list[1:]:
            #                 next_index = str(int(next_index) + 1)
            #                 if next_index not in terms[term][book]:
            #                     flag2 = False
            #             flag1 = flag1 or flag2
            #         if not flag1:
            #             book_list.remove(book)
        
        search_list = {}
        for book in book_list: # 计算每本书的权重
            search_list[book] = 0
            for term in terms:
                tf_res = db.session.query(Author_Indices.tf_wt).filter(and_(Author_Indices.term == term, Author_Indices.book_id == book)).first()
                df_res = db.session.query(Author_Weight.idf).filter(Author_Weight.term == term).first()
                search_list[book] += (tf_res[0] * df_res[0])
        search_list = sorted(search_list.items(), key=lambda x:x[1], reverse=True)
        for book in search_list:
            final_list.append(book[0])

    for wildcard_word in wildcard_words:
        fuzzy_res = db.session.query(Author_Indices.book_id).filter(Author_Indices.term.like(wildcard_word)).all()
        for i in fuzzy_res:
            if i[0] not in final_list:
                print(i[0])
                final_list.append(i[0])

    return final_list, correct_words, mistake

@cache.memoize(timeout=300)          
def search_by_description(q, t, p):
    ps = PorterStemmer()
    wnl = WordNetLemmatizer()
    terms = {}
    correct_words = ""
    mistake = False

    wildcard_words = []
    if q != None and q != "":
        for words in q.split(" "):
            if "*" in words:
                wildcard_words.append(words.replace("*", "%"))
                continue
            for word in word_tokenize(words):
                if word not in string.punctuation:
                    word = word.encode('UTF-8').decode('UTF-8-sig')
                    word = word.lower()
                    word = wnl.lemmatize(word)
                    word = ps.stem(word) # 首先将query中的term提取出来
                    res = []
                    
                    res = db.session.query(Description_Indices.term, Description_Indices.book_id, Description_Indices.indices).filter(Description_Indices.term == word).all()
                    
                    if res.__len__() == 0:
                        # 对单词纠错
                        mistake = True
                        prepare()
                        word = correct_text_generic(word)
                        res = db.session.query(Description_Indices.term, Description_Indices.book_id, Description_Indices.indices).filter(Description_Indices.term == word).all()
                    
                    correct_words += (word + " ")

                    for item in res:
                        if item[0] in terms:
                            if item[1] not in terms[item[0]]:
                                terms[item[0]][item[1]] = item[2].split("+")
                        else:
                            terms[item[0]] = {}
                            terms[item[0]][item[1]] = item[2].split("+")

    # print(terms)
    # terms构建完成
    
    final_list = []
    if terms.__len__() > 0:
        terms_bid = {}
        for term in terms:
            terms_bid[term] = list(terms[term].keys())

        # print(terms_bid)
        
        book_list = terms_bid[list(terms_bid.keys())[0]]
        if t == "SOME" or t == "NONE":
            for term in terms_bid:
                book_list = list(set(book_list) | set(terms_bid[term])) # 求并集
        elif t == "ALL":
            for term in terms_bid:
                book_list = list(set(book_list) & set(terms_bid[term])) # 求交集

            # 这段代码只有ALL的时候才会执行
            # if p == "true": # query中每个单词要相邻
            #     term_list = list(terms.keys())
            #     for book in book_list:
            #         flag1 = False # 这本书是否需要被检索
            #         for index in terms[term_list[0]][book]:
            #             flag2 = True
            #             next_index = index
            #             for term in term_list[1:]:
            #                 next_index = str(int(next_index) + 1)
            #                 if next_index not in terms[term][book]:
            #                     flag2 = False
            #             flag1 = flag1 or flag2
            #         if not flag1:
            #             book_list.remove(book)
        
        search_list = {}
        for book in book_list: # 计算每本书的权重
            search_list[book] = 0
            for term in terms:
                tf_res = db.session.query(Description_Indices.tf_wt).filter(and_(Description_Indices.term == term, Description_Indices.book_id == book)).first()
                df_res = db.session.query(Description_Weight.idf).filter(Description_Weight.term == term).first()
                search_list[book] += (tf_res[0] * df_res[0])
        search_list = sorted(search_list.items(), key=lambda x:x[1], reverse=True)
        for book in search_list:
            final_list.append(book[0])

    for wildcard_word in wildcard_words:
        fuzzy_res = db.session.query(Description_Indices.book_id).filter(Description_Indices.term.like(wildcard_word)).all()
        for i in fuzzy_res:
            if i[0] not in final_list:
                print(i[0])
                final_list.append(i[0])

    return final_list, correct_words, mistake

