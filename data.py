import sqlite3 as sql
import pandas as pd
import config
import requests
import io

SEPARATOR = ' >> '


class Data:
    def __init__(self):
        self.conn = sql.connect('cultobjects.db')
        self.c = self.conn.cursor()
        self.c.execute('DROP TABLE IF EXISTS objects')
        self.objects = dict()
        self.reload()

    def get_objects(self):
        self.c.execute('SELECT DISTINCT `Nozare` FROM objects ')
        objects = [x[0] for x in self.c.fetchall()]
        for obj in objects:
            self.c.execute(f'SELECT DISTINCT`Objekta veids` FROM objects WHERE `Nozare` = "{obj}"')
            categories = [x[0] for x in self.c.fetchall()]
            shortened_categories = []
            for category in categories:
                if category is None:
                    shortened_categories.append('Citi')
                    continue
                if SEPARATOR in category:
                    shortened_categories.append(category.split(SEPARATOR)[1])
            self.objects[obj] = shortened_categories

    def get_objects_by_category(self, obj, category):
        if category == 'Citi':
            self.c.execute(f'SELECT `Nosaukums` FROM objects WHERE `Nozare` = "{obj}" AND `Objekta veids` IS NULL')
        else:
            self.c.execute('SELECT `Objekta nosaukums` FROM objects WHERE `Objekta veids` = ? AND `Nozare` = ?',
                       (category, obj))
        return [x[0] for x in self.c.fetchall()]

    def get_data(self):  # TODO: add error handling
        r = requests.get(config.DATA_URL)
        df = pd.read_csv(io.StringIO(r.content.decode('utf-8')))
        df.to_sql('objects', self.conn)

    def reload(self):
        self.get_data()
        self.get_objects()
