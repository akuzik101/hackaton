import sqlite3 as sql  # TODO: migrate to aiosqlite
import pandas as pd
import config
import requests
import io
from cultobject import CultObject


class Data:
    def __init__(self):
        self.conn = sql.connect(config.SQLITE_FILE)
        self.c = self.conn.cursor()
        self.objects = dict()
        self.reload()

    def get_objects(self):
        self.c.execute('SELECT DISTINCT `Nozare` FROM objects ')
        objects = [x[0] for x in self.c.fetchall()]
        for obj in objects:
            self.c.execute('SELECT DISTINCT `Objekta veids` FROM objects WHERE `Nozare` = ?', (obj,))
            categories = [x[0] for x in self.c.fetchall()]
            shortened_categories = []
            for category in categories:
                if category is None:
                    category = 'Citi'
                elif config.SEPARATOR in category:
                    category = category.split(config.SEPARATOR)[1]
                if not self.get_objects_by_category(obj, category):
                    continue
                shortened_categories.append(category)
            if not shortened_categories:
                continue
            self.objects[obj] = shortened_categories

    def get_objects_by_category(self, obj: str, category: str) -> list[CultObject]:
        if category == 'Citi':
            self.c.execute('SELECT * FROM objects WHERE `Nozare` = ? AND `Objekta veids` IS NULL',
                           (obj,))
        else:
            self.c.execute('SELECT * FROM objects WHERE `Objekta veids` LIKE ? AND `Nozare` = ?',
                           (category, obj))

        result = []
        for row in self.c:
            result.append(CultObject(row))
        return result

    def get_data(self):  # TODO: add error handling
        r = requests.get(config.DATA_URL)
        df = pd.read_csv(io.StringIO(r.content.decode('utf-8')))
        df.to_sql('objects', self.conn)

    def reload(self):
        self.c.execute('DROP TABLE IF EXISTS objects')
        self.get_data()
        self.get_objects()
