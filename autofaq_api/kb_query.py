from pydantic import ValidationError
from .models.kb_query_models import QueryModel, BatchQueryModel
from .http_client import AutoFaqHTTPClient


class AutoFaqQuery(AutoFaqHTTPClient):
    """
    Клиент для выполнения запросов к базе знаний AutoFAQ.
    
    Предоставляет синхронные и асинхронные методы для взаимодействия
    с API запросов к базе знаний, включая одиночные и пакетные запросы.
    """
    
    def __init__(self, base_url: str, timeout: int = 30):
        super().__init__(base_url, timeout)
        
    def sync_kb_query(self, service_id, service_token, query, **kwargs):
        """
        Синхронный запрос к базе знаний.
        
        Выполняет синхронный поиск по базе знаний с использованием
        естественного языка. Возвращает релевантные ответы из базы знаний
        на основе заданного запроса.
        
        Args:
            service_id (str): Идентификатор сервиса
            service_token (str): Токен доступа к сервису
            query (str): Текст запроса на естественном языке
            **kwargs: Дополнительные параметры запроса (см. QueryModel)
                - conversation_id (str, optional): ID диалога для контекста
                - user_id (str, optional): ID пользователя
                - channel_id (str, optional): ID канала коммуникации
                - group_id (str, optional): ID группы
                - limit (int, optional): Лимит результатов (по умолчанию 10)
                - threshold (float, optional): Порог релевантности (0.0-1.0)
                - filters (dict, optional): Дополнительные фильтры поиска
        
        Returns:
            dict: Результат запроса с найденными ответами или ошибками валидации
                - results: Список релевантных ответов из базы знаний
                - errors: Список ошибок валидации или None
            
        Raises:
            ValidationError: При некорректных параметрах запроса
            
        Example:
            >>> client = AutoFaqQuery("https://api.example.com")
            >>> result = client.sync_kb_query(
            ...     service_id="12345",
            ...     service_token="token_here",
            ...     query="Как сбросить пароль?",
            ...     limit=5,
            ...     threshold=0.7
            ... )
            >>> print(result["results"])
            
        Link:
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_query/1.0#/Query%20API/post_query
        """
        try:
            kwargs['service_id'] = service_id
            kwargs['service_token'] = service_token
            kwargs['query'] = query
            model = QueryModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        resp = self.sync_request('post', '/core-api/query/api/v1/query', json=model.model_dump())
        resp["errors"] = None
        return resp
    
    async def async_kb_query(self, service_id, service_token, query, **kwargs):
        """
        Асинхронный запрос к базе знаний.
        
        Выполняет асинхронный поиск по базе знаний с использованием
        естественного языка. Подходит для использования в асинхронных приложениях.
        
        Args:
            service_id (str): Идентификатор сервиса
            service_token (str): Токен доступа к сервису
            query (str): Текст запроса на естественном языке
            **kwargs: Дополнительные параметры запроса (см. QueryModel)
                - conversation_id (str, optional): ID диалога для контекста
                - user_id (str, optional): ID пользователя
                - channel_id (str, optional): ID канала коммуникации
                - group_id (str, optional): ID группы
                - limit (int, optional): Лимит результатов (по умолчанию 10)
                - threshold (float, optional): Порог релевантности (0.0-1.0)
                - filters (dict, optional): Дополнительные фильтры поиска
        
        Returns:
            dict: Результат запроса с найденными ответами или ошибками валидации
                - results: Список релевантных ответов из базы знаний
                - errors: Список ошибок валидации или None
            
        Example:
            >>> import asyncio
            >>> client = AutoFaqQuery("https://api.example.com")
            >>> async def example():
            ...     result = await client.async_kb_query(
            ...         service_id="12345",
            ...         service_token="token_here",
            ...         query="Часы работы поддержки",
            ...         limit=3
            ...     )
            ...     return result
            >>> asyncio.run(example())
            
        Link:
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_query/1.0#/Query%20API/post_query
        """
        try:
            kwargs['service_id'] = service_id
            kwargs['service_token'] = service_token
            kwargs['query'] = query
            model = QueryModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        resp = await self.async_request('post', '/core-api/query/api/v1/query', json=model.model_dump())
        resp["errors"] = None
        return resp
    
    def sync_kb_batch(self, payload):
        """
        Синхронный пакетный запрос к базе знаний.
        
        Выполняет несколько запросов к базе знаний в одном вызове.
        Эффективен при необходимости обработки большого количества запросов.
        
        Args:
            payload (list): Список словарей с параметрами запросов
                Каждый элемент должен содержать:
                - service_id (str): Идентификатор сервиса
                - service_token (str): Токен доступа к сервису  
                - query (str): Текст запроса на естественном языке
                - Дополнительные параметры как в kb_sync_query
        
        Returns:
            dict: Результат пакетной обработки запросов
                - results: Список результатов для каждого запроса или ошибки валидации
            
        Example:
            >>> client = AutoFaqQuery("https://api.example.com")
            >>> batch_payload = [
            ...     {
            ...         "service_id": "12345",
            ...         "service_token": "token_here", 
            ...         "query": "Как восстановить аккаунт?"
            ...     },
            ...     {
            ...         "service_id": "12345",
            ...         "service_token": "token_here",
            ...         "query": "Способы оплаты"
            ...     }
            ... ]
            >>> results = client.sync_kb_batch(batch_payload)
            >>> for result in results["results"]:
            ...     print(result["query"], result["answers"])
            
        Link:
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_query/1.0#/Query%20API/post_query_batch
        """
        try:
            payload = {'payload': payload}
            model = BatchQueryModel(**payload)
        except ValidationError as e:
            return {
                "results":  e.errors()
            }
        resp = self.sync_request('post', '/core-api/query/api/v1/query/batch', json=model.model_dump()['payload'])
        return resp
    
    async def async_kb_batch(self, payload):
        """
        Асинхронный пакетный запрос к базе знаний.
        
        Выполняет несколько асинхронных запросов к базе знаний в одном вызове.
        Оптимален для асинхронных приложений с большим объемом запросов.
        
        Args:
            payload (list): Список словарей с параметрами запросов
                Каждый элемент должен содержать:
                - service_id (str): Идентификатор сервиса
                - service_token (str): Токен доступа к сервису
                - query (str): Текст запроса на естественном языке
                - Дополнительные параметры как в kb_async_query
        
        Returns:
            dict: Результат пакетной обработки запросов
                - result: Список результатов для каждого запроса или ошибки валидации
            
        Example:
            >>> import asyncio
            >>> client = AutoFaqQuery("https://api.example.com")
            >>> batch_payload = [
            ...     {
            ...         "service_id": "12345",
            ...         "service_token": "token_here",
            ...         "query": "Технические требования"
            ...     },
            ...     {
            ...         "service_id": "12345", 
            ...         "service_token": "token_here",
            ...         "query": "Документация API"
            ...     }
            ... ]
            >>> async def example():
            ...     return await client.async_kb_batch(batch_payload)
            >>> asyncio.run(example())
            
        Link:
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_query/1.0#/Query%20API/post_query_batch
        """
        try:
            payload = {'payload': payload}
            model = BatchQueryModel(**payload)
        except ValidationError as e:
            return {
                "result": e.errors()
            }
        resp = await self.async_request('post', '/core-api/query/api/v1/query/batch', json=model.model_dump()['payload'])
        return resp
    
