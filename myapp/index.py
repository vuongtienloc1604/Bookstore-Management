import math
from flask import render_template, url_for, session, jsonify
from myapp import app, login
from flask_login import login_user, login_required
import cloudinary.uploader


@app.route("/")
def home():
    book_cates = utils.load_book_category()
    book_cate_id = request.args.get('book_category_id')
    kw = request.args.get('keyword')
    page = request.args.get('page', 1)
    books = utils.load_books(book_cate_id=book_cate_id, kw=kw, page=int(page))
    return render_template('index.html', books=books,
                           pages=math.ceil(utils.count_books() / app.config['PAGE_SIZE']))


# @app.route("/user/<id:user_id>")
# @login_required
# def user_info(user_id):
#     user = utils.get_user_by_id(user_id)
#     return render_template('user_detail.html', user=user)


@app.route("/employee_home")
def employee_home():
    return render_template('employee_home.html')


@app.route("/books")
def book_list():
    book_cate_id = request.args.get("book_category_id")
    kw = request.args.get("keyword")
    from_price = request.args.get("from_price")
    to_price = request.args.get("to_price")

    books = utils.load_books(book_cate_id=book_cate_id,
                             kw=kw,
                             from_price=from_price,
                             to_price=to_price)

    return render_template('books.html',
                           books=books)


@app.route("/register", methods=['get', 'post'])
def user_register():
    err_msg = ""
    if request.method.__eq__('POST'):
        name = request.form['name']
        email = request.form.get('email')
        username = request.form['username']
        password = request.form['password']
        confirm = request.form.get('confirm')
        avatar_path = None

        try:
            if password.strip().__eq__(confirm.strip()):
                avatar = request.files.get('avatar')
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_  url']

                utils.add_user(name=name, username=username, password=password, email=email, avatar=avatar_path)
                return redirect('user_signin')
            else:
                err_msg = 'Mat khau khong khop!!'
        except Exception as ex:
            err_msg = 'He thong dang co loi:' + str(ex)

    return render_template('register.html', err_msg=err_msg)


@app.route('/user_signin', methods=['get', 'post'])
def user_signin():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = utils.check_login(username=username, password=password)
        if user:
            login_user(user=user)
            next = request.args.get('next', 'home')
            return redirect(url_for(next))
        else:
            err_msg = 'Username hoac password khong chinh xac!!!'

    return render_template('login.html', err_msg=err_msg)


@app.route('/admin-login', methods=['post'])
def signin_admin():
    username = request.form['username']
    password = request.form['password']

    user = utils.check_login(username=username,
                             password=password,
                             role=UserRole.ADMIN)
    if user:
        login_user(user=user)

    return redirect('/admin')


@app.route('/employee-login', methods=['get', 'post'])
def employee_signin():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user_role = request.form.get('choice')
        user = utils.check_login(username=username, password=password, role=user_role)
        if user and (user.user_role.__eq__('STORE_MANAGER')
                     or user.user_role.__eq__('BOOK_SELLER')
                     or user.user_role.__eq__('MANAGER')):
            login_user(user=user)
            next = request.args.get('next', 'employee_home')
            return redirect(url_for(next))
        else:
            err_msg = 'Username hoac password khong chinh xac!!!'

    return render_template('employee_login.html', err_msg=err_msg)


@app.context_processor
def common_response():
    return {
        'book_category': utils.load_book_category(),
        'cart_stats': utils.count_cart(session.get('cart'))
    }


@app.route("/books/<int:book_id>")
def book_detail(book_id):
    book = utils.get_book_by_id(book_id)
    comments = utils.get_comment(book_id=book_id, page=int(request.args.get('page', 1)))
    return render_template('book_detail.html', comments=comments, book=book,
                           pages=math.ceil(utils.count_commnent(book_id=book_id) / app.config['PAGE_SIZE']))


@app.route('/cart')
def cart():
    return render_template('cart.html', stats=utils.count_cart(session.get('cart')))


@app.route('/employee_selling_book')
def saleform():
    books = Book.query.all()
    book_cates = BookCategory.query.all()

    return render_template('employee_selling_book.html', stats=utils.count_item_saleform(session.get('saleform')),
                           books=books,book_cates=book_cates)


@app.route('/api/add-cart', methods=['post'])
def add_to_cart():
    data = request.json
    id = str(data.get('id'))
    name = data.get('name')
    price = data.get('price')

    cart = session.get('cart')

    if not cart:
        cart = {}
    if id in cart:
        cart[id]['quantity'] = cart[id]['quantity'] + 1
    else:
        cart[id] = {
            'id': id,
            'name': name,
            'price': price,
            'quantity': 1
        }

    session['cart'] = cart
    return jsonify(utils.count_cart(cart))


@app.route('/api/add-saleform', methods=['post'])
def add_to_saleform():
    data = request.json

    name = data.get('name')
    price = data.get('price')
    category = data.get('category')
    number = data.get('number')
    saleform = session.get('saleform')

    if not saleform:
        saleform = {}
    if name in Book.name:
        saleform[id]['quantity'] = saleform[id]['quantity'] + 1
    else:
        saleform[id] = {
            'name': name,
            'category': category,
            'number': number,
            'price': price,
            'quantity': 1
        }

    session['saleform'] = saleform
    return jsonify(utils.count_item_saleform(saleform))


@app.route('/api/comments', methods=['post'])
@login_required
def add_comment():
    data = request.json
    content = data.get('content')
    book_id = data.get('book_id')

    try:
        c = utils.add_comment(content=content, book_id=book_id)
    except:
        return {'status': 404, 'err_msg': 'Chuong trinh dang bi loi'}

    return {'status': 201, 'comment': {
        'id': c.id,
        'content': c.content,
        'created_date': c.created_date,
        'user': {
            'username': current_user.username,
            'avatar': current_user.avatar
        }
    }}


@app.route('/api/pay', methods=['post'])
def pay():
    try:
        utils.add_receipt(session.get('cart'))
        del session['cart']
    except:
        return jsonify({'code': 400})

    return jsonify({'code': 200})


@app.route('/api/saleform_pay', methods=['post'])
def pay_saleform():
    try:
        utils.add_offline_receipt(session.get('saleform'))
        del session['saleform']
    except:
        return jsonify({'code': 400})

    return jsonify({'code': 200})


@app.route('/user_signout')
def user_signout():
    logout_user()
    return redirect(url_for('user_signin'))


@app.route('/employee_signout')
def employee_signout():
    logout_user()
    return redirect(url_for('employee_signin'))


@login.user_loader
def load_user(user_id):
    return utils.get_user_by_id(user_id=user_id)


@app.route('/employee_importing_book')
def book_importing():
    books = Book.query.all()
    book_cates = BookCategory.query.all()
    authors = Author.query.all()
    return render_template('employee_importing_book.html', books=books, book_cates=book_cates, authors=authors)


@app.route('/employee_administrate_books')
def book_administration():
    page = request.args.get('page', 1)
    books = utils.load_books(book_cate_id=None, page=int(page))
    return render_template('employee_book_administration.html', books=books,
                           page=math.ceil(utils.count_books() / app.config['PAGE_SIZE']))


@app.route('/api/delete-cart/<book_id>', methods=['delete'])
def delete_cart(book_id):
    cart = session.get('cart')

    if cart and book_id in cart:
        del cart[book_id]
        session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/api/delete-saleform/<book_id>', methods=['delete'])
def delete_saleform(book_id):
    saleform = session.get('saleform')

    if saleform and book_id in saleform:
        del saleform[book_id]
        session['saleform'] = saleform

    return jsonify(utils.count_item_saleform(saleform))


@app.route('/api/update-cart', methods=['put'])
def update_cart():
    data = request.json
    id = str(data.get('id'))
    quantity = data.get('quantity')

    cart = session.get('cart')
    if cart and id in cart:
        cart[id]['quantity'] = quantity
        session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/api/update-saleform', methods=['put'])
def update_saleform():
    data = request.json
    id = str(data.get('id'))
    quantity = data.get('quantity')

    saleform = session.get('saleform')
    if saleform and id in saleform:
        saleform[id]['quantity'] = quantity
        session['saleform'] = saleform

    return jsonify(utils.count_item_saleform(saleform))


@app.route('/employee_administrate_books/add', methods=['get', 'post'])
def add_book():
    err = ""
    if request.method.lower() == "post":
        name = request.form.get("name")
        price = request.form.get("price", 0)
        publisher_id = request.form.get("publisher_id")
        image = request.form.get("image")
        type = request.form.get("type")
        publish_date = request.form.get("publish_date")
        in_stock = request.form.get("in_stock")
        book_category_id = request.form.get("book_cate_id")
        if utils.add_book(name=name, price=price, image=image, type=type,
                          publish_date=publish_date,
                          in_stock=in_stock,
                          book_category_id=book_category_id, publisher_id=publisher_id):
            return redirect(url_for("book_administration"))
        err = "something wrong!!"
    book = None
    book_id = request.args.get("book_id")
    if book_id:
        book = utils.get_book_by_id(book_id=int(book_id))

    return render_template('book_add.html', categories=utils.load_book_category(), err=err, author=utils.load_author(),
                           publisher=utils.load_publisher(), book=book)


@app.route('/api/delete-book/<book_id>', methods=['delete'])
def delete_book(book_id):
    # utils.delete_comment(book_id)
    # utils.delete_receipt_detail(book_id)
    try:
        utils.delete_book(book_id)
    except:
        return jsonify({'code': 400})

    return jsonify({'code': 200})


@app.route('/employee_administrate_books/update', methods=['get', 'post'])
def update_book():
    err = ""
    book_id = request.args.get("book_id")
    if request.method.lower() == "post":
        name = request.form.get("name")
        price = request.form.get("price", 0)
        publisher_id = request.form.get("publisher_id")
        image = request.form.get("image")
        type = request.form.get("type")
        publish_date = request.form.get("publish_date")
        in_stock = request.form.get("in_stock")
        book_category_id = request.form.get("book_cate_id", 1)
        if utils.update_book(book_id=book_id, name=name, price=price, image=image, type=type,
                             publish_date=publish_date,
                             in_stock=in_stock,
                             book_category_id=book_category_id, publisher_id=publisher_id):
            return redirect(url_for("book_administration"))
        err = "something wrong!!"
    book = None

    if book_id:
        book = utils.get_book_by_id(book_id=int(book_id))

    return render_template('book_update.html', categories=utils.load_book_category(), err=err,
                           author=utils.load_author(),
                           publisher=utils.load_publisher(), book=book)


if __name__ == '__main__':
    from myapp.admin import *

    app.run(debug=True)
