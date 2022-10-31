from config import Fields


class CultObject:
    def __init__(self, query_res: list):
        self.id = query_res[Fields.ID]
        self.obj = query_res[Fields.OBJ]
        self.name = query_res[Fields.NAME]
        # ISIL
        self.address = query_res[Fields.ADDRESS]
        self.lat = query_res[Fields.LAT]
        self.lon = query_res[Fields.LON]
        # LKS-92 X
        # LKS-92 Y
        self.category = query_res[Fields.CATEGORY]
        self.phone = query_res[Fields.PHONE]
        self.email = query_res[Fields.EMAIL]
        # ATVK
        self.url = query_res[Fields.URL]
        self.image_url = query_res[Fields.IMG_URL]
