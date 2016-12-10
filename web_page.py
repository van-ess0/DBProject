import db_orm

from hashlib import sha1

from flask import *

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('login_page'))


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    error = None
    register = True
    if 'POST' == request.method:
        if request.form['username'] and request.form['password']:
            users.append(Customer.create({
                'login': request.form['username'],
                'pwd_hash': sha1(request.form['password'].encode('utf-8')).hexdigest(),
                'name': request.form['name'],
                'cellphone': request.form['cellphone'],
                'address': request.form['adress'],
                'email': request.form.get('email', None),
            }))
            return redirect(url_for('shop_page'))
    return render_template('login_page.html', error=error, register=register)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    error = None
    register = False
    users = db_orm.Customer.get_all()
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            return redirect(url_for('shop_page'))
        elif request.form['username'] and request.form['password']:
            for user in users:
                if request.form['username'] == user.login and sha1(request.form['password'].encode('utf-8')).hexdigest() == user.pwd_hash:
                    return redirect(url_for('shop_page'))
                else:
                    error = 'Invalid Credentials. Please try again.'
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login_page.html', error=error, register=register)


@app.route('/shop')
def shop_page():
    if request.method == 'POST':
        # Return filtered products
        pass
    products = []
    return render_template('shop_page.html', products=products)

app.run()