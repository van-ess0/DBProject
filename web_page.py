import db_orm

from hashlib import sha1
import os

from flask import *

app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    username = request.cookies.get('username')
    app.logger.info('Login from cookies: {}'.format(username))
    if username in session.get('logged_users', []):
        return redirect(url_for('shop_select_page'))
    return redirect(url_for('login_page'))


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    error = None
    register = True
    if 'POST' == request.method:
        # Check data
        rule = len(request.form['username']) > 4 and \
               len(request.form['password']) > 4 and \
               request.form['name'] and \
               request.form['cellphone'] and \
               request.form['address']
        if rule:
            app.logger.info("Creating new user")
            try:
                new_user = db_orm.Customer.create({
                    'login': request.form['username'],
                    'pwd_hash': sha1(request.form['password'].encode('utf-8')).hexdigest(),
                    'name': request.form['name'],
                    'cellphone': request.form['cellphone'],
                    'adress': request.form['address'],
                    'email': request.form['email'],
                })
                app.logger.info("Created new user with id {}".format(new_user.id))
            except Exception as e:
                error = e
                return render_template('login_page.html', error=error, register=register)
            return redirect(url_for('shop_select_page'))
        else:
            error = "Не все обязательные поля заполнены"
            return render_template('login_page.html', error=error, register=register)
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
        if request.form['username'] and request.form['password']:
            flag = False
            for user in users:
                if request.form['username'] == user.login and sha1(
                        request.form['password'].encode('utf-8')).hexdigest() == user.pwd_hash:
                    flag = True
                    resp = make_response(render_template('login_page.html'))
                    resp.set_cookie('username', request.form['username'])
                    session['logged_uses'] = session.get('logged_users', []).append(request.form['username'])
                    return redirect(url_for('shop_select_page'))
            if not flag:
                error = 'Invalid Credentials. Please try again.'
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login_page.html', error=error, register=register)


@app.route('/shop/<shop_name>', methods=['POST', 'GET'])
def shop_page(shop_name=None):
    if shop_name is None:
        abort(404)
    products = db_orm.Product.get_by_shop(shop_name)
    if request.method == 'POST':
        print('helo', request.form)
    return render_template('shop_page.html', products=products)


@app.route('/product/<product_id>')
def product_page(product_id=None):
    if product_id is None:
        abort(404)
    product = db_orm.Product.get_by_id(product_id)
    product.type_id = db_orm.Type.get_by_id(product.type_id)
    product.diller_id = db_orm.Diller.get_by_id(product.diller_id)
    product.shop_id = db_orm.Shop.get_by_id(product.shop_id)
    print(product.diller_id.company)
    return render_template('product_page.html', product=product)


app.secret_key = "\xa80\xe7g\xac<>\xb1$\xfa0\x1bK\x02\xb1aeKQ\x9f\xfa\xfb\xc1\xa4"
app.run()
