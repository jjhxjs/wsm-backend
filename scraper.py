from flask import jsonify

from app import app, db
from app.models.book import Book


def update_book_list_archive_my(begin_index, end_index):
    import sys
    import time
    from bs4 import BeautifulSoup
    import json
    SLEEP_SEC = 0.01
    RETRY_SLEEP_SEC = 0.1
    MAX_OPEN_COUNT = 3
    index_url_pt = 'https://archive.org/details/{}'
    txt_url_pt = 'https://archive.org/stream/{}/{}_djvu.txt'
    epub_url_pt = 'https://archive.org/download/{}/{}.epub'

    def get_archive_txt_from_url(txt_url):
        for try_count in range(MAX_OPEN_COUNT):
            try:
                user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
                headers = {'User-Agent': user_agent}
                request = urllib.request.Request(txt_url, headers=headers)
                response = opener.open(request)
                if try_count >= 1:
                    sys.stderr.write('Succeeded in opening {}\n'.format(txt_url))
                break  # success
            except Exception as e:
                sys.stderr.write('Failed to open {}\n'.format(txt_url))
                sys.stderr.write('{}: {}\n'.format(type(e).__name__, str(e)))
                time.sleep(RETRY_SLEEP_SEC)
        else:
            sys.stderr.write(' Gave up to open {}\n'.format(txt_url))
            return None
        body = response.read()
        soup = BeautifulSoup(body, 'lxml')
        txt_soup = soup.find('pre')
        return txt_soup.text if txt_soup else None

    try:
        from cookielib import CookieJar
        cj = CookieJar()
        import urllib2
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    except ImportError:
        import http.cookiejar
        cj = http.cookiejar.CookieJar()
        import urllib
        opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(cj))

    cursor = ''
    LOOP = 40
    BASE_ID = 70000
    COUNT = 500
    BEGIN = begin_index
    END = end_index
    scrape_url_header = 'https://archive.org/services/search/v1/scrape?q=collection%3A%22cdl%22&count=500&fields=title,creator,year,language,subject'
    # 每个loop有500本书
    for loop_index in range(LOOP):
        print('loop_index: ', loop_index)
        scrape_url = scrape_url_header + '&cursor=' + cursor if loop_index > 0 else scrape_url_header
        if loop_index >= END:
            break
        for try_count in range(MAX_OPEN_COUNT):
            try:
                user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
                headers = {'User-Agent': user_agent}
                request = urllib.request.Request(scrape_url, headers=headers)
                response = opener.open(request)
                if try_count >= 1:
                    sys.stderr.write('Succeeded in opening {}\n'.format(scrape_url))
                break  # success
            except Exception as e:
                sys.stderr.write('Failed to open {}\n'.format(scrape_url))
                sys.stderr.write('{}: {}\n'.format(type(e).__name__, str(e)))
                time.sleep(RETRY_SLEEP_SEC)
        else:
            sys.stderr.write(' Gave up to open {}\n'.format(scrape_url))
            break
        json_txt = response.read()
        dct = json.loads(json_txt)
        cursor = dct.get('cursor')
        if loop_index < BEGIN:
            continue

        for index, item in enumerate(dct['items']):
            id = BASE_ID + loop_index * COUNT + index
            identifier = item.get('identifier')
            title = item.get('title')
            if title and len(title) > 255:
                title = title[:250]
                title = title + '...'
            authors = item.get('creator')
            author = ', '.join(authors) if isinstance(authors, list) else authors
            if isinstance(authors, list) and len(author) > 255 and len(authors) > 0:
                author = authors[0]
            language = item.get('language')
            year = int(item.get('year')) if item.get('year') else None
            subjects = item.get('subject')
            description = ', '.join(subjects) if isinstance(subjects, list) else subjects
            url_index = index_url_pt.format(identifier)
            url_epub = epub_url_pt.format(identifier, identifier)
            url_txt = txt_url_pt.format(identifier, identifier)
            book = Book()
            book.id = id
            book.author = author
            book.title = title
            book.language = language
            book.description = description
            book.year = year
            book.url_epub = url_epub
            book.url_txt = url_txt
            book.url_index = url_index
            if url_txt != None:
                book.content = get_archive_txt_from_url(url_txt)
            try:
                db.session.add(book)
                db.session.commit()
                print(id)
            except Exception as e:
                sys.stderr.write('Failed to save book {} in mysql.\n'.format(id))
                sys.stderr.write('{}: {}\n'.format(type(e).__name__, str(e)))
                db.session.rollback()

    return 1

if __name__ == '__main__':
    import sys
    start = int(sys.argv[1])
    end = int(sys.argv[2])
    print(update_book_list_archive_my(start, end))
