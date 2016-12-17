import psycopg2
import psycopg2.extras
from psycopg2.extensions import AsIs

try:
    conn = psycopg2.connect("dbname='project' user='Van-ess0' host='localhost' password=''")
    cr = conn.cursor()
    crd = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    crd.execute("""SELECT * FROM customer""")
    print(crd.fetchall())
except Exception as e:
    print(e)
    print("I am unable to connect to the database")

class AbstractORM():
    '''Abstact ORM CLASS'''
    table = ''
    id = 0

    @classmethod
    def get_all(cls):
        '''returns list of objects'''
        SQL = '''SELECT * FROM {table}'''.format(table=cls.table)
        cr.execute(SQL)
        return [cls(line) for line in cr.fetchall()]


    def get(self, *fields):
        '''Get selected fields for this model,
            Returns dict with {'field_name': value}'''
        to_get = ', '.join(fields)
        SQL = '''SELECT {fields} FROM {table} WHERE id={id}'''.format(fields=to_get, table=self.table, id=self.id)
        crd.execute(SQL)
        return crd.fetchone()

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
        print("HELLOOOO!O!O!O!O!O")
        keys = vals.keys()
        print(keys)
        columns = ', '.join(keys)
        values = [vals.get(key) for key in keys]
        SQL = '''INSERT INTO {table}(%s) VALUES %s;'''.format(table=cls.table)
        try:
            print("HELLO")
            print(cr.mogrify(SQL, (AsIs(columns), tuple(values))))
            SQL = cr.mogrify(SQL, (AsIs(columns), tuple(values)))
            cr.execute(SQL)
            conn.commit()
        except Exception as e:
            print(e)
            raise e
        # TODO: rewrite to avoid SQL injections
        statement = []
        for key in vals.keys():
            statement.append("{key} = '{val}'".format(key=key, val=vals.get(key, '')))
        statement = ' AND '.join(statement)
        SQL = '''SELECT * FROM {table} WHERE {statement}'''.format(table=cls.table, statement=statement)
        print(SQL)
        cr.execute(SQL)
        print(cr.fetchall())
        new_obj = cls(cr.fetchone())
        return new_obj


class Product(AbstractORM):
    table = 'product'

    def __init__(self, data):
        self.id, self.type_id, self.name, self.articul, self.color, self.price, self.number_left, self.diller_id, self.shop_id = data
        self.type = ''   # TODO: get type from database by id


    @classmethod
    def get_by_shop(cls, shop_name):
        SQL = '''
            SELECT {table}.id, {table}.type_id, {table}.name, {table}.articul, {table}.color, {table}.price, {table}.number_left, {table}.diller_id, {table}.shop_id
            FROM {table}
            JOIN shop sh on sh.id = {table}.shop_id
            WHERE sh.name = '{shop_name}' '''.format(table=cls.table, shop_name=shop_name)
        cr.execute(SQL)
        return [cls(line) for line in cr.fetchall()]


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