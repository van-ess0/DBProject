import db_orm

from hashlib import sha1

from flask import *

app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    return redirect(url_for('login_page'))


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    error = None
    register = True
    if 'POST' == request.method:
        if request.form['username'] and request.form['password']:
            # print("Creating new user")
            a = db_orm.Customer.create({
                'login': request.form['username'],
                'pwd_hash': sha1(request.form['password'].encode('utf-8')).hexdigest(),
                'name': request.form['name'],
                'cellphone': request.form['cellphone'],
                'adress': request.form['address'],
                'email': request.form['email'],
            })
            return redirect(url_for('shop_page'))
    return render_template('login_page.html', error=error, register=register)


@app.route('/shop_select', methods=['GET', 'POST'])
def shop_select_page():
    if request.method == 'POST':
        pass
    return render_template('shop_select_page.html', shops=db_orm.Shop.get_all())


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    error = None
    register = False
    users = db_orm.Customer.get_all()
    if request.method == 'POST':
        # if request.form['username'] == 'admin' and request.form['password'] == 'admin':
        #     return redirect(url_for('shop_page'))
        if request.form['username'] and request.form['password']:
            flag = False
            for user in users:
                if request.form['username'] == user.login and sha1(request.form['password'].encode('utf-8')).hexdigest() == user.pwd_hash:
                    flag = True
                    return redirect(url_for('shop_select_page'))
            if not flag:
                error = 'Invalid Credentials. Please try again.'
        else:
            error = 'Invalid Credentials. Please try again.'
    # elif request.method == 'GET':
    #     return redirect(url_for('register_page'))

    return render_template('login_page.html', error=error, register=register)


@app.route('/shop/<shop_name>')
def shop_page(shop_name=None):
    if request.method == 'POST':
        # Return filtered products
        pass
    products = db_orm.Product.get_by_shop(shop_name)
    # TODO: get products by shop
    return render_template('shop_page.html', products=products)

app.run()