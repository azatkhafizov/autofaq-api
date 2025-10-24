# Модуль работы с AutoFAQ API

## Общие сведения

Установка

```
pip install autofaq-api
```

Данный модуль умеет работать со всеми 3-мя API AutoFAD:

- External API
- CRUD API
- QUERY API

Методы для каждого из классов валидируются через модуль Pydantic. Каждый метод подробно расписан и задокументирован в docstring.
В модуле поддерживаются как синхронные запросы так и асинхронные, каждый синхронный метод начинается с *sync_*, а асинхронный с *sync_*:

```python
import asyncio
from autofaq_api import AutoFaqCrud

af_client = AutoFaqCrud('https://chat.autofaq.ai', 'user_token')
result = af_conn.sync_get_services()
print(result)

async def main():
    result = await af_conn.async_get_services()
    print(result)

asyncio.run(main())

...

import asyncio
from autofaq_api import AutoFaqExternal

af_client = AutoFaqExternal('https://chat.autofaq.ai', 'user_login', 'password', 'service_id')
result = af_conn.sync_channel_get_file(channel_id, file_id)
print(result)

async def main():
    result = await af_conn.async_channel_get_file(channel_id, file_id)
    print(result)

asyncio.run(main())

...

import asyncio
from autofaq_api import AutoFaqQuery

af_conn = AutoFaqQuery('https://chat.autofaq.ai')
result = af_conn.sync_kb_query(service_id, service_token, query)
print(result)

async def main():
    result = await af_conn.async_kb_query(service_id, service_token, query)
    print(result)

asyncio.run(main())

```
