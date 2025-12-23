import asyncio
import logging
import sys

import pandas as pd

from dataclasses import asdict
from clients.async_clients import AsyncClient, AsyncCardClient
from parsers.jsonParsers import CatalogJsonParser, CardJsonParser
from parsers.dataclass import CatalogDataClass, FullGoodDataClass

from settings import (xls_file_name,
                      headers,
                      catalog_url,
                      condition_url,
                      BASE_CARD_URL,
                      BASE_SELLER_URL,
                      BASE_GOOD_URL,
                      BASE_IMAGE_URL,
                      working_basket_list,
                      PAGE_COUNT,
                      conditions)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs.txt', mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

sem = asyncio.Semaphore(20)


def export_to_xlsx(goods: list[FullGoodDataClass], path=xls_file_name):
    rows = []

    for good in goods:
        try:
            data = asdict(good)
            data["sizes"] = ", ".join(map(str, data["sizes"]))
            data["options"] = str(data["options"])
            data["media"] = ", ".join(data["media"])
            rows.append(data)
        except Exception as e:
            if good is None:
                pass
            else:
                logging.error(f'Не удалось обработать {good}, {e}')
    df = pd.DataFrame(rows)
    df.to_excel(path, index=False)


async def card_worker(client: AsyncCardClient,
                      base_card_url: str,
                      catalog_page:
                      CatalogDataClass,
                      cardparser: CardJsonParser):
    id = str(catalog_page.id)
    async with sem:
        response = await client.get_valid_card_in_basketpool(base_card_url, id)
    if response.get('success'):
        cardpage = cardparser.parse(response.get('success'), BASE_IMAGE_URL)
        fullGood = FullGoodDataClass(
            **asdict(catalog_page),
            **asdict(cardpage)
        )
        logging.info(f'Обработан товар {id}')
        return fullGood
    logging.error(f'ошибка {response}, {id}')
    return None


async def main():
    client = AsyncClient(headers=headers)
    cardclient = AsyncCardClient(headers=headers,
                                 working_basket_list=working_basket_list)
    cardclient.start_session()
    catalogparser = CatalogJsonParser(base_seller_url=BASE_SELLER_URL,
                                      good_base_url=BASE_GOOD_URL,
                                      conditions=conditions)
    cardparser = CardJsonParser()
    card_tasks = []
    try:
        async for result in client.api_response_generator(base_url=catalog_url,
                                                          page_count=PAGE_COUNT):
            catalog_pages = catalogparser.parse(row_data=result)
            if catalog_pages:
                for catalog_page in catalog_pages:
                    card_tasks.append(asyncio.create_task(card_worker(
                        client=cardclient,
                        base_card_url=BASE_CARD_URL,
                        catalog_page=catalog_page,
                        cardparser=cardparser
                    )))
        results = await asyncio.gather(*card_tasks, return_exceptions=True)
    except Exception as e:
        logging.critical(f'{e}')
        raise e
    else:
        export_to_xlsx(results)
    finally:
        await cardclient.close_session()

if __name__ == '__main__':
    asyncio.run(main())
