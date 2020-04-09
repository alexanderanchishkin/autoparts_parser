import peewee

db = peewee.MySQLDatabase('autoparts_parser',
                          host="127.0.0.1", port=3306, user="autoparts_parser", passwd="parser123")
