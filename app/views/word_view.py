from operator import countOf
from flask import jsonify, request

from app import app, db
from app.models.book import Book
from sqlalchemy import union_all,or_,and_
from itertools import count
from app.models.book import Book
from app.func.construct import *
from app.func.search import *

#http://localhost:8080/#/query?mode=2&
# field0=title
# value0=%E7%9A%84%E9%98%BF%E8%BE%BE
# type0=AND
# precise0=true
# field1=author
# value1=111
# type1=AND
# precise1=true

@app.route('/search', methods=['GET'])
def search_books():
    params = request.args
    page = int(params.get('page'))
    if params.get('mode') == '1':
        data = []
        total_num = 0
        mistake = False
        correct_words = ""
        if params.get('field') == 'title':
            search_list, correct_words, mistake = search_by_title(params.get('content'), 'ALL', 'true')
            total_num = search_list.__len__()
            res = search_books_in_list(search_list[10 * (page - 1):10 * page])
            data = [{column: value for column, value in rowproxy.items()} for rowproxy in res]
        elif params.get('field') == 'author':
            search_list, correct_words, mistake = search_by_author(params.get('content'), 'ALL', 'true')
            total_num = search_list.__len__()
            res = search_books_in_list(search_list[10 * (page - 1):10 * page])
            data = [{column: value for column, value in rowproxy.items()} for rowproxy in res]
        elif params.get('field') == 'content':
            search_list, correct_words, mistake = search_by_content(params.get('content'), 'ALL', 'true')
            total_num = search_list.__len__()
            res = search_books_in_list(search_list[10 * (page - 1):10 * page])
            data = [{column: value for column, value in rowproxy.items()} for rowproxy in res]
        elif params.get('field') == 'description':
            search_list, correct_words, mistake = search_by_description(params.get('content'), 'ALL', 'true')
            total_num = search_list.__len__()
            res = search_books_in_list(search_list[10 * (page - 1):10 * page])
            data = [{column: value for column, value in rowproxy.items()} for rowproxy in res]
        if not mistake:
            return jsonify({'data':data, 'num': total_num, 'check': ''})
        else:
            return jsonify({'data':data, 'num': total_num, 'check': correct_words})
    else:
        search_list = [] # 搜索列表
        none_list = [] # 排除的book id
        start = int(params.get('start'))
        end = int(params.get('end'))
        total_num = 0
        for i in count():
            type=params.get('type{}'.format(i))
            field = params.get('field{}'.format(i))
            pricise = params.get('precise{}'.format(i))
            if type is None or field is None:
                break
            words = params.get('value{}'.format(i))
            if field == "title":
                title_list,_,__ = search_by_title(words, type, pricise)
                if type == "ALL" or type == "SOME":
                    if search_list.__len__() == 0:
                        search_list = title_list
                    else:
                        search_list = list(set(search_list) & set(title_list))
                else:
                    if none_list.__len__() == 0:
                        none_list = title_list
                    else:
                        none_list = list(set(none_list) | set(title_list))
            elif field == "author":
                author_list,_,__ = search_by_author(words, type, pricise)
                if type == "ALL" or type == "SOME":
                    if search_list.__len__() == 0:
                        search_list = author_list
                    else:
                        search_list = list(set(search_list) & set(author_list))
                else:
                    if none_list.__len__() == 0:
                        none_list = author_list
                    else:
                        none_list = list(set(none_list) | set(author_list))
            elif field == "content":
                content_list,_,__ = search_by_content(words, type, pricise)
                if type == "ALL" or type == "SOME":
                    if search_list.__len__() == 0:
                        search_list = content_list
                    else:
                        search_list = list(set(search_list) & set(content_list))
                else:
                    if none_list.__len__() == 0:
                        none_list = content_list
                    else:
                        none_list = list(set(none_list) | set(content_list))
            elif field == "description":
                description_list,_,__ = search_by_description(words, type, pricise)
                if type == "ALL" or type == "SOME":
                    if search_list.__len__() == 0:
                        search_list = description_list
                    else:
                        search_list = list(set(search_list) & set(description_list))
                else:
                    if none_list.__len__() == 0:
                        none_list = description_list
                    else:
                        none_list = list(set(none_list) | set(description_list))
        search_list = list(set(search_list) - set(none_list))
        print(search_list)
        total_num = search_list.__len__()
        res = search_books_in_list(search_list[10 * (page - 1):10 * page], start, end)
        data = [{column: value for column, value in rowproxy.items()} for rowproxy in res]
        return jsonify({'data':data, 'num':total_num,'check':''})


@app.route('/search/<int:start>/<int:end>', methods=['GET'])
def search(start,end):
    # construct_author_vocabulry()
    # construct_title_vocabulary()
    # construct_description_vocabulary()
    print(111)
    # construct_title_vocabulary(start,end)
    # calculate_title_wt()
    calculate_author_wt()
    calculate_description_wt()
    calculate_content_wt()
    return jsonify({'message': 'OK'})


def get_books_by_content(content):
    return Book.query.filter(Book.content.contains(content))


@app.route('/book', methods=['GET'])
def book():
    params = request.args
    res = Book.query.filter(Book.id == params.get('id')).first()
    return jsonify(res.to_dict())
