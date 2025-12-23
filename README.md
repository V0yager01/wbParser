# WbParser

Упрощенный асинхронный парсер каталога и карточек для сайта wildberries.ru
Логика заключается в поиске двух ключевых точек - эндпоинта каталогов и эндпоинта самих карточек.

## Установка и запуск

1. **Клонирование**

   ```
   git clone git@github.com:V0yager01/wbParser.git
   cd wbParser
   ```

2. **Виртуальное окружение**

   ```
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Зависимости**

   ```
   pip install -r requirements.txt
   ```

4. **Настройка параметров**
   ```python
   #Используем готовые или свои заголовки
   headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Referer': 'https://www.wildberries.ru/catalog/0/search.aspx?page=1&sort=popular&search=%D0%BF%D0%B0%D0%BB%D1%8C%D1%82%D0%BE+%D0%B8%D0%B7+%D0%BD%D0%B0%D1%82%D1%83%D1%80%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE%D0%B9+%D1%88%D0%B5%D1%80%D1%81%D1%82%D0%B8&f14177451=15000203',
    'deviceid': 'site_ad8f6168a4f0442dbfa04cd0b9028e08',
    'x-queryid': 'qid359079191176618243120251219222131',
    'x-requested-with': 'XMLHttpRequest',
    'x-spa-version': '13.17.4',
    'x-userid': '0',
    'Sec-GPC': '1',
    'Connection': 'keep-alive',
    'Cookie': 'x_wbaas_token=1.1000.831540e4b44942fbb836f9228f4b3115.MHw3Ny43OS4xNDYuOTF8TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NDsgcnY6MTQ2LjApIEdlY2tvLzIwMTAwMTAxIEZpcmVmb3gvMTQ2LjB8MTc2NzM5MDQ1MHxyZXVzYWJsZXwyfGV5Sm9ZWE5vSWpvaUluMD18MHwzfDE3NjY3ODU2NTB8MQ==.MEUCIQC+gTjzmiUhGEGkHtqWkUVUzxDzMm52iBb+cwScptFUXAIgGuoSfYMZDViTBNCYhanWC55GCvyQ4sVcW+N7+PWBEFc=; _wbauid=3590791911766182431',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Priority': 'u=4',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    # Requests doesn't support trailers
    # 'TE': 'trailers',
    }

   #Эндпоинт каталога "пальто из натуральной шерсти" 
   catalog_url = 'https://www.wildberries.ru/__internal/u-search/exactmatch/ru/common/v18/search?ab_testing=false&ab_testing=false&appType=1&curr=rub&dest=-1257786&hide_dtype=9;11&hide_vflags=4294967296&inheritFilters=false&lang=ru&page={page_number}&query=пальто из натуральной шерсти&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false'
   #Эдпоинт с условием: стоимость до 10000 и страной производства Россия
   condition_url = 'https://www.wildberries.ru/__internal/u-search/exactmatch/ru/common/v18/search?ab_testing=false&ab_testing=false&appType=1&curr=rub&dest=-1257786&f14177451=15000203&hide_dtype=9;11&hide_vflags=4294967296&inheritFilters=false&lang=ru&page={page_number}&priceU=87800;1000000&query=%D0%BF%D0%B0%D0%BB%D1%8C%D1%82%D0%BE%20%D0%B8%D0%B7%20%D0%BD%D0%B0%D1%82%D1%83%D1%80%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE%D0%B9%20%D1%88%D0%B5%D1%80%D1%81%D1%82%D0%B8&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false'

   #Ставим количество страниц
    PAGE_COUNT = 50
   
   #Шаблонные запросы
    BASE_CARD_URL = 'https://basket-{number}.wbbasket.ru/vol{id_four_first_digits}/part{id_six_first_digits}/{id}/info/ru/card.json'
    BASE_IMAGE_URL = 'https://basket-{number}.wbbasket.ru/vol{id_four_first_digits}/part{id_six_first_digits}/{id}/images/c516x688/{photo_number}.webp'
    BASE_SELLER_URL = 'https://www.wildberries.ru/seller/{id}'
    BASE_GOOD_URL = 'https://www.wildberries.ru/catalog/{id}/detail.aspx'
   
   #Доступные баскеты, работающие на текущий момент, где может быть эндпоинт для получения json карточки 
    working_basket_list = [
        '01', '02', '03', '04', '05', '06', '07', '08', '09',
        '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
        '20', '21', '22', '23', '24', '25', '26', '27', '28', '29',
        '30', '31', '32', '33', '34', '35', '36', '37'
    ]
    
    #Условия для json парсера
    # conditions = [
    #     lambda p: p.get("supplierRating", 0) >= 4.5,
    # ]
   
    #Или
   
    conditions = None
    
    #Путь сохранения .xlsx
    xls_file_name='xlsx_goods.xlsx'
   
   ```
5. **Запуск**

   ```
   python main.py
   ```


### 
Готовые результаты находятся в .xlsx файлах



