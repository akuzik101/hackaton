from config import Fields
from typing import Any


class Field:
    value: Any

    def __init__(self, table_number: int, display_name: str | None = None):
        self.table_number = table_number
        self.display_name = display_name

    def set_value(self, data: list):
        self.value = data[self.table_number]

    def __str__(self):
        if self.value is None or self.display_name is None:
            return ''
        return f'{self.display_name}: {self.value}'


class CultObject:
    def __init__(self, query_res: list):
        self.data = {

            'id': Field(Fields.ID, None),
            'obj': Field(Fields.OBJ, None),
            'name': Field(Fields.NAME, 'Nosaukums'),
            # ISIL
            'address': Field(Fields.ADDRESS, 'Adrese'),
            'lat': Field(Fields.LAT, None),
            'lon': Field(Fields.LON, None),
            # LKS-92 X
            # LKS-92 Y
            'category': Field(Fields.CATEGORY, None),
            'phone': Field(Fields.PHONE, 'Tālrunis'),
            'email': Field(Fields.EMAIL, 'E-pasts'),
            # ATVK
            'url': Field(Fields.URL, 'Mājaslapa'),
            'image_url': Field(Fields.IMG_URL, None)
        }
        for field in self.data.values():
            field.set_value(query_res)

    def get_real_url(self):
        pass

    def __str__(self):
        result = ''
        for field in self.data.values():
            if field.display_name:
                result += str(field) + '\n'
        return result


if __name__ == '__main__':
    co = CultObject([x for x in range(40)])
    print(co.data['lat'].value)
