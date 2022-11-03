import pandas as pd
import config
import aiohttp
import io
import sqlite3 as sql  # TODO: migrate to async sqlalchemy core

from cultobject import CultObject


class Data:
    def __init__(self):
        self.db = None
        self.c = None
        self.objects = dict()

    async def init(self):
        self.db = sql.connect(config.SQLITE_FILE)
        self.c = self.db.cursor()
        await self.reload()

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
            self.c.execute('SELECT * FROM objects WHERE `Objekta veids` = ? AND `Nozare` = ?',
                           (category, obj))

        result = []
        for row in self.c:
            result.append(CultObject(list(row)))
        return result

    async def get_data(self):  # TODO: add error handling
        async with aiohttp.ClientSession() as session:
            async with session.get(config.DATA_URL) as response:
                content = await response.text()
                df = pd.read_csv(io.StringIO(content))
        df.to_sql('objects', self.db)

    async def reload(self):
        self.c.execute('DROP TABLE IF EXISTS objects')
        await self.get_data()
        self.get_objects()
