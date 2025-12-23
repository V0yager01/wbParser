from .base import ParserBase
from .dataclass import CardDataClass, CatalogDataClass


class CatalogJsonParser(ParserBase):

    def __init__(self,
                 base_seller_url: str,
                 good_base_url: str,
                 conditions: dict|None = None):
        self.base_seller_url = base_seller_url
        self.good_base_url = good_base_url
        self.conditions = conditions

    def parse(self, row_data: list[dict]) -> list[CatalogDataClass]:
        parsed_data = []
        row_products: list[dict] = row_data.get('products', False)
        if row_products:
            for product in row_products:
                if self.conditions and not self._match_conditions(product):
                    continue
                parsed_data.append(CatalogDataClass(
                      id=product.get('id'),
                      name=product.get('name'),
                      good_link=self._create_link(self.good_base_url, product.get('id')),
                      price=product.get('sizes')[0].get('price').get('product') / 100,
                      seller_name=product.get('supplier'),
                      seller_link=self._create_link(self.base_seller_url, product.get('supplierId')),
                      sizes=[size.get('name') for size in product.get('sizes')],
                      totalQuantity=product.get('totalQuantity'),
                      raiting=product.get('supplierRating'),
                      feedbacks=product.get('feedbacks'))
                )
            return parsed_data
        return None

    def _create_link(self, base_url: str, id: str|int) -> str:
        return base_url.format(id=id)

    def _match_conditions(self, product: dict) -> bool:
        return all(condition(product) for condition in self.conditions)


class CardJsonParser(ParserBase):
    def parse(self, row_data: list, base_image_url: str) -> CardDataClass:
        if row_data:
            id = str(row_data.get('nm_id'))
            parsed_data = CardDataClass(
                    description=row_data.get('description'),
                    options=[{characteristics.get('name'): characteristics.get('value')} for characteristics in row_data.get('options')],
                    media=[base_image_url.format(number=row_data.get('valid_basket'), id_four_first_digits=id[0:4], id_six_first_digits=id[0:6], id=id, photo_number=photo_number) for photo_number in range(0, 1 + int(row_data.get('media', 0).get('photo_count', 0)))]
                )
        return parsed_data
