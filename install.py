import os
import yaml
from sqlalchemy import create_engine

with open("config.yaml", 'r', encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

db = config["database"]
if db["engine"] == "sqlite":
    db_path = os.path.join(os.path.abspath(
        os.path.dirname(__file__)), f'./{db["sqlite_file"]}')
    if os.name != "nt":
        db_path = f"/{db_path}"
    DATABASE_URI = f'sqlite:///{db_path}'
else:
    DATABASE_URI = f'{db["type"]}://{db["username"]}:{db["password"]}@{db["host"]}/{db["dbname"]}'

try:
    engine = create_engine(DATABASE_URI, echo=False)
    with engine.connect() as conn:
        with open('sql/init.sql', 'r', encoding='utf-8') as f:
            for sql in f.read().split(';'):
                if sql.strip():
                    conn.execute(sql)
except Exception as e:
    print('An error occurred:', e)
else:
    print("初始化完毕")

