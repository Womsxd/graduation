import sqlite3


class Sql:
    def __init__(self, database):
        self.cn = self.init_connect(database)

    def init_connect(self, database):
        def sqlite(db):
            return sqlite3.connect(db)

        dbc = locals().get(database[0])
        return dbc(database[1])

    def query(self, table, sql):
        cu = self.cn.cursor()
        cu.execute(f'select * from {table} {sql}')
        _r = cu.fetchall()
        cu.close()
        self.cn.commit()
        return _r

    def add(self, table, field: tuple, value: tuple):
        cu = self.cn.cursor()
        ff = str(field).replace("'", "")
        cu.execute(f"insert into {table} {ff} values {value}")
        _r = cu.fetchall()
        cu.close()
        self.cn.commit()
        return _r

    def edit(self, table, sets: list, where):
        cu = self.cn.cursor()
        ups = ''
        for i in sets:
            if ups != '':
                ups += ', '
            ups += i
        cu.execute(f"update {table} set {ups} where {where}")
        _r = cu.fetchall()
        cu.close()
        self.cn.commit()
        return _r

    def delete(self, table, sql):
        cu = self.cn.cursor()
        cu.execute(f'delete from {table} where {sql}')
        _r = cu.fetchall()
        cu.close()
        self.cn.commit()
        return _r

    def anysql(self, sql):
        cu = self.cn.cursor()
        cu.execute(sql)
        _r = cu.fetchall()
        cu.close()
        self.cn.commit()
        return _r

    def anysqls(self, sqls):
        cu = self.cn.cursor()
        cu.executescript(sqls)
        _r = cu.fetchall()
        cu.close()
        self.cn.commit()
        return _r


if __name__ == '__main__':
    database = Sql(("sqlite", "data.db"))
    print(database.add("user", ("account", "password"), ("user4", "114514")))
    print(database.query("user", ""))
