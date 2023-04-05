import sqlite3


def init_sqlite3():
    return sqlite3.connect("database.db")


def creata_table(_cu):
    with open('sql/init.sql', 'r', encoding='utf-8') as f:
        try:
            _cu.executescript(f.read())
        except sqlite3.OperationalError:
            print("数据库已完成过初始化")
        else:
            print("数据库初始化完毕！")


if __name__ == '__main__':
    cn = init_sqlite3()
    cu = cn.cursor()
    creata_table(cu)
