import db_orm

from hashlib import sha1
import datetime
import random
import tempfile

from flask import *

app = Flask(__name__)
app.debug = True

current_order = None
current_user = None

def export_order_to_xml():
    if isinstance(current_order.worker_id, int):
        current_order.worker_id = db_orm.Worker.get_by_id(current_order.worker_id)
    if isinstance(current_order.worker_id.shop_id, int):
        current_order.worker_id.shop_id = db_orm.Shop.get_by_id(current_order.worker_id.shop_id)
    if isinstance(current_order.customer_id, int):
        current_order.customer_id = db_orm.Customer.get_by_id(current_order.customer_id)

    from lxml import etree
    order = etree.Element("order")

    def fill_tag(parent, vals):
        for val in vals:
            child = etree.Element(val[0])
            child.text = str(val[1])
            parent.append(child)

    children = [
        ('id', current_order.id),
        ('date', current_order.date),
    ]

    fill_tag(order, children)

    worker = etree.Element("worker")
    order.append(worker)

    children = [
        ('id', current_order.worker_id.id),
        ('name', current_order.worker_id.name),
        ('cellphone', current_order.worker_id.cellphone),
        ('email', current_order.worker_id.email),
    ]

    fill_tag(worker, children)

    worker_shop = etree.Element("shop")
    worker.append(worker_shop)

    children = [
        ('id', current_order.worker_id.shop_id.id),
        ('adress', current_order.worker_id.shop_id.adress),
        ('name', current_order.worker_id.shop_id.name),
        ('cellphone', current_order.worker_id.shop_id.cellphone),
        ('email', current_order.worker_id.shop_id.email),
    ]

    fill_tag(worker_shop, children)

    customer = etree.Element("customer")
    order.append(customer)

    children = [
        ('id', current_order.customer_id.id),
        ('name', current_order.customer_id.name),
        ('adress', current_order.customer_id.adress),
        ('cellphone', current_order.customer_id.cellphone),
        ('email', current_order.customer_id.email),
        ('login', current_order.customer_id.login),
    ]

    fill_tag(customer, children)

    positions = etree.Element("order_positions")
    order.append(positions)

    for line in current_order.get_positions():
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
            ('id', current_order.worker_id.shop_id.id),
            ('adress', current_order.worker_id.shop_id.adress),
            ('name', current_order.worker_id.shop_id.name),
            ('cellphone', current_order.worker_id.shop_id.cellphone),
            ('email', current_order.worker_id.shop_id.email),
        ]

        fill_tag(product_shop, children)

    return etree.tostring(order, pretty_print=True)

def add_to_cart(id):
    global current_order, current_user
    if not current_order:
        current_order = db_orm.Order.create({
            'date': datetime.date.today(),
            'customer_id': current_user.id,
            'worker_id': random.randrange(1, 5)
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
    global current_order
    show_order_link = False
    if current_order:
        show_order_link = True
    if request.method == 'POST':
        pass
    return render_template(
        'shop_select_page.html',
        shops=db_orm.Shop.get_all(),
        show_order_link=show_order_link,
    )


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
    return render_template('shop_page.html', products=products)


@app.route('/product/<product_id>')
def product_page(product_id=None):
    if product_id is None:
        abort(404)
    product = db_orm.Product.get_by_id(product_id)
    product.type_id = db_orm.Type.get_by_id(product.type_id)
    product.diller_id = db_orm.Diller.get_by_id(product.diller_id)
    product.shop_id = db_orm.Shop.get_by_id(product.shop_id)
    return render_template('product_page.html', product=product)


@app.route('/order', methods=['POST', "GET", 'PUT'])
def order_page():
    global current_order
    if not current_order:
        return render_template('shop_select_page.html')
    lines = current_order.get_positions()
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
                attachment_filename='Order #{}.xml'.format(current_order.id),
            )
        for line in lines:
            if request.form.get(str(line.id)):
                if int(request.form.get(str(line.id))) <= 0:
                    line.delete()
                    continue
                line.write({
                    'qty': int(request.form.get(str(line.id))),
                })
        return redirect(url_for('order_page'))

    return render_template('order_page.html', order=current_order, lines=lines, total=total)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback_page():
    if request.method == 'POST':
        feedback = request.form['feedback']
        if feedback:
            fb = db_orm.Feedback.create({
                'body': feedback,
                'order_id': current_order.id,
            })
            return redirect(url_for('order_page'))
    return render_template('feedback_page.html')


app.secret_key = "\xa80\xe7g\xac<>\xb1$\xfa0\x1bK\x02\xb1aeKQ\x9f\xfa\xfb\xc1\xa4"
app.run()
