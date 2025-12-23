import asyncio
import json

from typing import AsyncGenerator

import aiohttp
from aiohttp import ClientSession

from .base import AsyncClientBase


class AsyncClient(AsyncClientBase):

    def __init__(self, headers: dict):
        self.conn = aiohttp.TCPConnector(limit=50, limit_per_host=50)
        self.timeout = aiohttp.ClientTimeout(total=100000)
        super().__init__(headers)

    async def api_response_generator(self, base_url: str,
                                     page_count: int) -> AsyncGenerator[dict]:
        url_list = self.create_links(base_url, page_count)
        async with aiohttp.ClientSession(connector=self.conn,
                                         timeout=self.timeout,
                                         headers=self.headers) as session:
            tasks_list = [asyncio.create_task(self.get_api_response(session, url)) for url in url_list]
            for task in asyncio.as_completed(tasks_list):
                result = await task
                yield result

    async def get_api_response(self,
                               session: ClientSession,
                               url: str) -> dict:
        try:
            async with session.get(url=url) as response:
                text = await response.text()
                return json.loads(text)

        except Exception as e:
            return {f'{url}': f'{e}'}

    def create_links(self, base_url, page_count) -> list[str]:
        links = [base_url.format(page_number=number) for number in range(1, page_count+1)]
        return links


class AsyncCardClient(AsyncClient):
    _max_id_len = 9

    def __init__(self, headers, working_basket_list: list):
        self.timeout = aiohttp.ClientTimeout(total=1000)
        self.connector = aiohttp.TCPConnector(
            limit=20,
            limit_per_host=20,
            enable_cleanup_closed=True
        )
        self.session = None
        self.working_basket_list = working_basket_list
        super().__init__(headers)

    def start_session(self):
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=self.timeout,
            headers=self.headers
        )

    async def close_session(self):
        if self.session:
            await self.session.close()

    async def get_api_response(self, url: str) -> dict:
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return {"success": (url, await response.json())}
                return {"notfound": (url, response.status)}
        except asyncio.CancelledError:
            raise
        except Exception as e:
            return {"error": (url, e)}

    async def get_valid_card_in_basketpool(self,
                                           base_card_url: str,
                                           id: int) -> dict:
        "Перебираем все возможные baskets, чтобы получить json карточки"

        if self.session is None:
            raise RuntimeError('Session not started')

        basket_url = {
            self.create_link(base_card_url, id, basket_number): basket_number
            for basket_number in self.working_basket_list
        }

        tasks = [
            asyncio.create_task(self.get_api_response(url))
            for url in basket_url
        ]

        try:
            for finished in asyncio.as_completed(tasks):
                result = await finished
                success = result.get('success')
                if success:
                    url, data = success
                    data["valid_basket"] = basket_url[url]

                    for task in tasks:
                        if task is not finished:
                            task.cancel()
                    await asyncio.gather(*tasks, return_exceptions=True)
                    return {"success": data}
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()
            final = await asyncio.gather(*tasks, return_exceptions=True)

        return {"error": f"No valid basket found {final}"}

    def create_link(self,
                    base_url: str,
                    id: str,
                    basket_number: int) -> str:
        "Создаем ссылку из basket_number, в которой может быть необходимый эндпоинт карточки товара"
        id_cut_shift = self._max_id_len - len(id)
        cut_ends = [4-id_cut_shift, 6-id_cut_shift]
        return base_url.format(
            number=basket_number,
            id=id,
            id_four_first_digits=str(id)[:cut_ends[0]],
            id_six_first_digits=str(id)[:cut_ends[1]],
        )
