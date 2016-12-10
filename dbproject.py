import web_page

if __name__ == '__main__':
    SQL = '''SELECT * FROM customer'''
    cr.execute(SQL)
    users = [Customer(line) for line in cr.fetchall()]
    print([user.__dict__ for user in users])
    # app.run()
