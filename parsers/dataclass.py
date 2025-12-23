from dataclasses import dataclass


@dataclass
class CatalogDataClass():
    id: int
    good_link: str
    name: str
    price: int
    seller_name: str
    seller_link: str
    sizes: list[int]
    totalQuantity: int
    raiting: float
    feedbacks: int


@dataclass
class CardDataClass():
    description: str
    options: list[dict]
    media: list[str]


@dataclass
class FullGoodDataClass(CatalogDataClass, CardDataClass):
    pass
