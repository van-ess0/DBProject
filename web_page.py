import db_orm

from hashlib import sha1
import datetime
import os

from flask import *

app = Flask(__name__)
app.debug = True

current_order = None
current_user = None

def add_to_cart(id):
    global current_order, current_user
    if not current_order:
        current_order = db_orm.Order.create({
            'date': datetime.date.today(),
            'customer_id': current_user.id,
        })
        current_order.order_lines = {}
    order_line = db_orm.OrderPosition.get_by_order_and_product(current_order.id, id)
    if not order_line:
        order_line = db_orm.OrderPosition.create({
            'product_id': id,
            'order_id': current_order.id,
            'qty': 1,
        })
    else:
        order_line.write({'qty': order_line.qty + 1})
    current_order.order_lines[id] = current_order.order_lines.get(id, 0) + 1
    print(current_order.__dict__)


@app.route('/')
def index():
    username = request.cookies.get('username')
    app.logger.info('Login from cookies: {}'.format(username))
    if username in session.get('logged_users', []):
        return redirect(url_for('shop_select_page'))
    return redirect(url_for('login_page'))


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    global current_user
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
                current_user = new_user
                return redirect(url_for('shop_select_page'))
            except Exception as e:
                error = e
                return render_template('login_page.html', error=error, register=register)
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
    global current_user
    error = None
    register = False
    users = db_orm.Customer.get_all()
    if request.method == 'POST':
        if request.form['username'] and request.form['password']:
            flag = False
            for user in users:
                if request.form['username'] == user.login and sha1(
                        request.form['password'].encode('utf-8')).hexdigest() == user.pwd_hash:
                    current_user = user
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
        ids = [product.id for product in products]
        for id in ids:
            if request.form.get(str(id)):
                add_to_cart(id)
            pass
        print('hello', request.form)
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


@app.route('/order', methods=['POST', "GET"])
def order_page():
    global current_order
    if not current_order:
        return render_template('shop_select_page.html')
    lines = []
    for id in current_order.order_lines.keys():
        new_line = db_orm.OrderPosition.get_by_order_and_product(current_order.id, id)
        new_line.product_id = db_orm.Product.get_by_id(new_line.product_id)
        lines.append(new_line)
    return render_template('order_page.html', order=current_order, lines=lines)


app.secret_key = "\xa80\xe7g\xac<>\xb1$\xfa0\x1bK\x02\xb1aeKQ\x9f\xfa\xfb\xc1\xa4"
app.run()
