
from flask import Flask, render_template, redirect, url_for, request
from pymongo import MongoClient
from bson.objectid import ObjectId
from functools import reduce
import os

app = Flask(__name__)

host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/my_app_db')
client = MongoClient(host=f"{host}?retryWrites=false")
db = client.get_default_database()

books_collection = db.books

@app.route('/') 
def index():
    """Return homepage."""
    return render_template('index.html', books=books_collection.find())

@app.route('/new')
def new_book():
    """Return new book creation page."""
    return render_template('new_book.html')

@app.route('/new', methods=['POST'])
def create_book():
    """Make a new book according to user's specifications."""
    book = {
        'name': request.form.get('name'),
        'pages': request.form.get('pages'),
        'length': request.form.get('length'),
        'img_url': request.form.get('img_url')
    }
    book_id = books_collection.insert_one(book).inserted_id
    page = book.get("pages", None)
    length = book.get("length", None)
    total = (int(page) / int(length))
    return redirect(url_for('show_book', book_id=book_id, total=total))

@app.route('/book/<book_id>/<total>')
def show_book(book_id, total):
    """Show a single book."""
    book = books_collection.find_one({'_id': ObjectId(book_id)})
    total = total
    return render_template('show_book.html', book=book, total=total)

@app.route('/edit/<book_id>', methods=['POST'])
def update_book(book_id):
    """Edit page for a book."""
    new_book = {
        'name': request.form.get('name'),
        'price': request.form.get('price'),
        'img_url': request.form.get('img_url')
    }
    books_collection.update_one(
        {'_id': ObjectId(book_id)},
        {'$set': new_book}
    )
    return redirect(url_for('show_book', book_id=book_id))

@app.route('/edit/<book_id>', methods=['GET'])
def edit_book(book_id):
    """Page to submit an edit on a book."""
    book = books_collection.find_one({'_id': ObjectId(book_id)})
    return render_template('edit_book.html', book=book)

@app.route('/delete/<book_id>', methods=['POST'])
def delete_book(book_id):
    """Delete a book."""
    books_collection.delete_one({'_id': ObjectId(book_id)})
    return redirect(url_for('index'))


if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))