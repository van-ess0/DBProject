from hashlib import sha1

from flask import *

app = Flask(__name__)

import psycopg2

try:
    conn = psycopg2.connect("dbname='project' user='Van-ess0' host='localhost' password=''")
    cr = conn.cursor()
except:
    print("I am unable to connect to the database")


class AbstractORM():
    '''Abstact ORM CLASS'''
    table = ''
    id = 0

    def write(self, vals):
        '''gets dict of vals, writes into table'''
        fields = []
        for key in vals.keys():
            fields.append("{key} = {'val'}".format(key, vals.get(key, ''))) # TODO: rewrite
        fields = ', '.join(fields)
        SQL = '''UPDATE {table} SET {fields} WHERE id = {id}'''.format(table=self.table, fields=fields, id=self.id)
        try:
            cr.execute(SQL)
        except Exception as e:
            print(e)
            raise e

    @classmethod
    def create(cls, vals):
        keys = vals.keys()
        fields = ', '.join(keys)
        SQL = '''INSERT INTO {table}({fields}) VALUES (%s)'''.format(table=cls.table, fields=fields)
        try:
            print("HELLO")
            cr.execute(SQL, ([vals.get(key) for key in keys],))
            print(cr.fetchall())
        except Exception as e:
            print(e)
            raise e

        for key in vals.iterkeys():
            statement.append("{key} = {val}".format(key, vlas.get(key, '')))
        statement = ' AND '.join(fields)
        SQL = '''SELECT * FROM {table} WHERE {statement}'''.format(table=cls.table, statement=statement)
        cr.execute(SQL)
        new_obj = cls(cr.fetchone())
        return new_obj


class Product(AbstractORM):
    table = 'product'

    def __init__(self, data):
        self.id, self.type_id, self.name, self.articul, self.color, self.price, self.number_left, self.diller_id, self.shop_id = data
        self.type = '' # TODO: get type from database


class Type(AbstractORM):
    table = 'type'

    def __init__(self, data):
        self.id, self.name = data


class Customer(AbstractORM):
    table = 'customer'

    def __init__(self, data):
        self.id, self.name, self.adress, self.cellphone, self.email, self.pwd_hash, self.login = data


class Diller(AbstractORM):
    table = 'diller'

    def __init__(self, data):
        self.id, self.adress, self.company, self.cellphone, self.email = data


class Order(AbstractORM):
    table = 'order'

    def __init__(self, data):
        self.id, self.date, self.worker_id, self.customer_id = data


class OrderPosition(AbstractORM):
    table = 'order_position'

    def __init__(self, data):
        self.id, self.product_id, self.qty, self.order_id = data


class Shop(AbstractORM):
    table = 'shop'

    def __init__(self, data):
        self.id, self.adress, self.name, self.cellphone, self.email = data


class Worker(AbstractORM):
    table = 'worker'

    def __init__(self, data):
        self.id, self.name, self.shop_id, self.cellphone, self.email = data


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


if __name__ == '__main__':
    SQL = '''SELECT * FROM customer'''
    cr.execute(SQL)
    users = [Customer(line) for line in cr.fetchall()]
    print([user.__dict__ for user in users])
    app.run()
