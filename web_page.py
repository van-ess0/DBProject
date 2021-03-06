import db_orm

from hashlib import sha1
import datetime
import random
import tempfile

from flask import *

app = Flask(__name__)
app.debug = True

def export_order_to_xml():
    order_obj = db_orm.Order.get_by_id(session['order_id'])
    if isinstance(order_obj.worker_id, int):
        order_obj.worker_id = db_orm.Worker.get_by_id(order_obj.worker_id)
    if isinstance(order_obj.customer_id, int):
        order_obj.customer_id = db_orm.Customer.get_by_id(order_obj.customer_id)

    from lxml import etree
    order = etree.Element("order")

    def fill_tag(parent, vals):
        for val in vals:
            child = etree.Element(val[0])
            child.text = str(val[1])
            parent.append(child)

    children = [
        ('id', order_obj.id),
        ('date', order_obj.date),
    ]

    fill_tag(order, children)

    worker = etree.Element("worker")
    order.append(worker)

    children = [
        ('id', order_obj.worker_id.id),
        ('name', order_obj.worker_id.name),
        ('cellphone', order_obj.worker_id.cellphone),
        ('email', order_obj.worker_id.email),
    ]

    fill_tag(worker, children)

    customer = etree.Element("customer")
    order.append(customer)

    children = [
        ('id', order_obj.customer_id.id),
        ('name', order_obj.customer_id.name),
        ('adress', order_obj.customer_id.adress),
        ('cellphone', order_obj.customer_id.cellphone),
        ('email', order_obj.customer_id.email),
        ('login', order_obj.customer_id.login),
    ]

    fill_tag(customer, children)

    positions = etree.Element("order_positions")
    order.append(positions)

    for line in order_obj.get_positions():
        line.product_id = db_orm.Product.get_by_id(line.product_id)
        line.product_id.type_id = db_orm.Type.get_by_id(line.product_id.type_id)
        line.product_id.diller_id = db_orm.Diller.get_by_id(line.product_id.diller_id)
        line.product_id.shop_id = db_orm.Shop.get_by_id(line.product_id.shop_id)

        position = etree.Element("order_position")
        positions.append(position)

        children = [
            ('id', line.id),
            ('qty', line.qty),
        ]

        fill_tag(position, children)

        product = etree.Element("product")
        position.append(product)

        children = [
            ('id', line.product_id.id),
            ('name', line.product_id.name),
            ('articul', line.product_id.articul),
            ('color', line.product_id.color),
            ('price', line.product_id.price),
            ('number_left', line.product_id.number_left),
        ]

        fill_tag(product, children)

        product_type = etree.Element("type")
        product.append(product_type)

        children = [
            ('id', line.product_id.type_id.id),
            ('name', line.product_id.type_id.name),
        ]

        fill_tag(product_type, children)

        product_diller = etree.Element("diller")
        product.append(product_diller)

        children = [
            ('id', line.product_id.diller_id.id),
            ('adress', line.product_id.diller_id.adress),
            ('company', line.product_id.diller_id.company),
            ('cellphone', line.product_id.diller_id.cellphone),
            ('email', line.product_id.diller_id.email),
        ]

        fill_tag(product_diller, children)

        product_shop = etree.Element("shop")
        product.append(product_shop)

        children = [
            ('id', line.product_id.shop_id.id),
            ('adress', line.product_id.shop_id.adress),
            ('name', line.product_id.shop_id.name),
            ('cellphone', line.product_id.shop_id.cellphone),
            ('email', line.product_id.shop_id.email),
        ]

        fill_tag(product_shop, children)

    return etree.tostring(order, pretty_print=True)

def add_to_cart(id):
    if session['order_id']:
        order_obj = db_orm.Order.get_by_id(session['order_id'])
    else:
        order_obj = db_orm.Order.create({
            'date': datetime.date.today(),
            'customer_id': db_orm.Customer.get_by_id(session['user_obj']).id,
            'worker_id': random.randrange(1, 5)
        })
        session['order_id'] = order_obj.id
    order_line = db_orm.OrderPosition.get_by_order_and_product(order_obj.id, id)
    if not order_line:
        order_line = db_orm.OrderPosition.create({
            'product_id': id,
            'order_id': order_obj.id,
            'qty': 1,
        })
    else:
        order_line.product_id = db_orm.Product.get_by_id(order_line.product_id)
        if order_line.product_id.number_left >= order_line.qty + 1:
            order_line.write({'qty': order_line.qty + 1})
        else:
            flash('Вы пытаетесь добавить больше товаров, чем есть на складе', 'error')
    return None


def check_if_possible(line):
    product = db_orm.Product.get_by_id(line.product_id.id)
    if product.number_left >= line.qty:
        return True
    else:
        return False


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
                session['user_obj'] = new_user.id
                session['order_id'] = None
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
    show_order_link = False
    order_obj = None
    if session['order_id']:
        order_obj = db_orm.Order.get_by_id(session['order_id'])
    if order_obj:
        show_order_link = True
    if request.method == 'POST':
        pass
    return render_template(
        'shop_select_page.html',
        shops=db_orm.Shop.get_all(),
        show_order_link=show_order_link,
        show_admin_buttons=db_orm.Customer.get_by_id(session['user_obj']).id == 1,
    )


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
                    session['user_obj'] = user.id
                    session['order_id'] = None
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
    show_order_link = False
    products = db_orm.Product.get_by_shop(shop_name)
    products = list(filter(lambda p: p.number_left > 0, products))
    if request.method == 'POST':
        ids = [product.id for product in products]
        for id in ids:
            if request.form.get(str(id)):
                add_to_cart(id)
    order_obj = None
    if session['order_id']:
        order_obj = db_orm.Order.get_by_id(session['order_id'])
    if order_obj:
        show_order_link = True
    return render_template(
        'shop_page.html',
        products=products,
        show_order_link=show_order_link,
    )


@app.route('/product/<product_id>')
def product_page(product_id=None):
    if product_id is None:
        abort(404)
    show_order_link = False
    order_obj = None
    if session['order_id']:
        order_obj = db_orm.Order.get_by_id(session['order_id'])
    if order_obj:
        show_order_link = True
    product = db_orm.Product.get_by_id(product_id)
    product.type_id = db_orm.Type.get_by_id(product.type_id)
    product.diller_id = db_orm.Diller.get_by_id(product.diller_id)
    product.shop_id = db_orm.Shop.get_by_id(product.shop_id)
    return render_template(
        'product_page.html',
        product=product,
        show_order_link=show_order_link,
    )


@app.route('/order', methods=['POST', "GET", 'PUT'])
def order_page():
    order_obj = None
    if session['order_id']:
        order_obj = db_orm.Order.get_by_id(session['order_id'])
    if not order_obj:
        return render_template('shop_select_page.html')
    lines = order_obj.get_positions()
    for line in lines:
        line.product_id = db_orm.Product.get_by_id(line.product_id)
        line.product_id.shop_id = db_orm.Shop.get_by_id(line.product_id.shop_id)
    total = sum((line.product_id.price * line.qty) for line in lines)
    if request.method == 'POST':
        if request.form.get('export_to_xml'):
            tf = tempfile.NamedTemporaryFile()
            tf.write(export_order_to_xml())
            tf.seek(0)
            return send_file(
                tf.name,
                mimetype="text/xml",
                as_attachment=True,
                attachment_filename='Order #{}.xml'.format(order_obj.id),
            )
        elif request.form.get('ok'):
            for line in lines:
                if not check_if_possible(line):
                    flash('Просим прощения, но товара {0} осталось только {1}шт'.format(
                        line.product_id.name,
                        line.porduct_id.number_left,
                    ))
                    return render_template('order_page.html', order=order_obj, lines=lines, total=total)
            for line in lines:
                line.product_id.write({
                    'number_left': line.product_id.number_left - line.qty,
                })
                order_obj = None
                session['order_id'] = None
            #current_user = None
            return redirect(url_for('login_page'))
        for line in lines:
            if request.form.get(str(line.id)):
                if int(request.form.get(str(line.id))) <= 0:
                    line.delete()
                    continue
                if int(request.form.get(str(line.id))) <= line.product_id.number_left:
                    line.write({
                        'qty': int(request.form.get(str(line.id))),
                    })
                else:
                    flash('Вы пытаетесь добавить больше товаров, чем есть на складе', 'error')
        return redirect(url_for('order_page'))
    return render_template('order_page.html', order=order_obj, lines=lines, total=total)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback_page():
    if request.method == 'POST':
        feedback = request.form['feedback']
        if feedback:
            fb = db_orm.Feedback.create({
                'body': feedback,
                'order_id': session['order_id'],
            })
            return redirect(url_for('order_page'))
    return render_template('feedback_page.html')

@app.route('/new_product', methods=['GET', 'POST'])
def new_product_page():
    if db_orm.Customer.get_by_id(session['user_obj']).id != 1:
        abort(404)
    types = db_orm.Type.get_all()
    dillers = db_orm.Diller.get_all()
    shops = db_orm.Shop.get_all()
    if request.method == 'POST':
        new_product = db_orm.Product.create({
            'type_id': request.form.get('type'),
            'diller_id': request.form.get('diller'),
            'shop_id': request.form.get('shop'),
            'name': request.form.get('name'),
            'articul': request.form.get('diller'),
            'color': request.form.get('color'),
            'price': float(request.form.get('price')),
            'number_left': int(request.form.get('number_left')),
        })
        return redirect(url_for('shop_select_page'))
    return render_template(
        'new_product_page.html',
        types=types,
        dillers=dillers,
        shops = shops,
    )


app.secret_key = "\xa80\xe7g\xac<>\xb1$\xfa0\x1bK\x02\xb1aeKQ\x9f\xfa\xfb\xc1\xa4"
app.run(host='0.0.0.0', threaded=True)
