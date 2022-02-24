
from app import app
from app.models.book import Book

@app.route('/test')
def test():
    return 'Test!'

@app.route('/test_sql')
def test_sql():
    book1 = Book.query.filter_by(id = 1).first()
    return book1.title

