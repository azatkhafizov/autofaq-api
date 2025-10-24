import os
import mimetypes
import aiofiles
import warnings

from base64 import b64encode
from aiohttp import FormData
from requests_toolbelt.multipart.encoder import MultipartEncoder
from pydantic import ValidationError
from .models.kb_external_models import QuestionModel, CloseСonversationModel, GetConversationsModel, PostDelayedDeliveryModel, \
                                       VarModel, ConversationsCountReportModel, OperatorsReportModel
from .http_client import AutoFaqHTTPClient


class AutoFaqExternal(AutoFaqHTTPClient):
    
    def __init__(self, base_url:str, userlogin:str, userpassword:str, service_id:str, timeout: int = 30):
        """
        Инициализация клиента для работы с AutoFAQ External API.
        
        Args:
            base_url (str): Базовый URL API AutoFAQ
            userlogin (str): Логин пользователя для аутентификации
            userpassword (str): Пароль пользователя для аутентификации
            service_id (str): ID сервиса AutoFAQ
            timeout (int, optional): Таймаут запросов в секундах. По умолчанию 30.
        """
        super().__init__(base_url, timeout)
        self.userlogin = userlogin
        self.userpassword = userpassword
        self.service_id = service_id
        self._auth_in_progress = False
        
    def sync_authorization(self):
        """
        Синхронная аутентификация в API AutoFAQ.
        
        Получает Bearer token используя Basic Auth и сохраняет его для последующих запросов.
        
        Raises:
            Exception: Если аутентификация не удалась
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Аутентификация/Authenticate
        """
        basic_auth_data = f'{self.userlogin}:{self.userpassword}'.encode('utf-8')
        headers = { "Authorization": f"Basic {b64encode(basic_auth_data).decode()}"}
        url = self._build_url('/api/ext/v2/login')
        resp = self.sync_session.request('GET', url, headers=headers)
        is_response_json_serialize = False
        try:
            resp.json()
            is_response_json_serialize = True
        except: pass
        if is_response_json_serialize: raise Exception(f'Athorization error in "{url}"')
        auth_token = resp.text
        if auth_token:
            self.update_default_headers({"authorization": f"Bearer {auth_token}"}) 
            
    async def async_authorization(self):
        """
        Асинхронная аутентификация в API AutoFAQ.
        
        Получает Bearer token используя Basic Auth и сохраняет его для последующих запросов.
        
        Raises:
            Exception: Если аутентификация не удалась
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Аутентификация/Authenticate
        """
        basic_auth_data = f'{self.userlogin}:{self.userpassword}'.encode('utf-8')
        headers = {"Authorization": f"Basic {b64encode(basic_auth_data).decode()}"}
        try: 
            url = self._build_url('/api/ext/v2/login')
            async with self.async_session.request('GET', url, headers=headers) as response:
                try:
                    await response.json()
                    raise Exception(f'Athorization error in "{url}"')
                except:
                    auth_token = await response.text()
        except: 
            raise Exception(f'Athorization error in "{url}"')
        if auth_token:
            await self.async_set_default_headers({"authorization": f"Bearer {auth_token}"})
    
    def sync_request(self, method: str, endpoint: str, return_json: bool = True, **kwargs):
        if 'authorization' not in self._default_headers:
            self.sync_authorization()
        url = self._build_url(endpoint)
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        response = self.sync_session.request(method.upper(), url, **kwargs)
        return self._handle_response(response, return_json)
    
    async def async_request(self, method: str, endpoint: str, return_json: bool = True, **kwargs):
        if 'authorization' not in self._default_headers:
            await self.async_authorization()
        url = self._build_url(endpoint)
        async with self.async_session.request(method.upper(), url, **kwargs) as response:
            return await self._handle_async_response(response, return_json)
        
    def sync_set_webhook(self, channel_id: str, webhook_url: str):
        """
        Синхронная установка webhook URL для канала.
        
        Args:
            channel_id (str): ID канала
            webhook_url (str): URL для получения webhook уведомлений
            
        Returns:
            dict: Результат операции
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Переписка/set_webhook
        """
        json = {"webhookUrl": webhook_url}
        return self.sync_request(
            'post',
            f'/api/ext/v2/services/{self.service_id}/{channel_id}/webhook',
            json=json
        ) 
    
    async def async_set_webhook(self, channel_id: str, webhook_url: str):
        """
        Асинхронная установка webhook URL для канала.
        
        Args:
            channel_id (str): ID канала
            webhook_url (str): URL для получения webhook уведомлений
            
        Returns:
            dict: Результат операции
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Переписка/set_webhook
        """
        json = {"webhookUrl": webhook_url}
        return await self.async_request(
            'post',
            f'/api/ext/v2/services/{self.service_id}/{channel_id}/webhook',
            json=json
        ) 
    
    def sync_channel_post_file(self, channel_id: str, file_path: str):
        """
        Синхронная загрузка файла в канал.
        
        Args:
            channel_id (str): ID канала
            file_path (str): Путь к файлу для загрузки
            
        Returns:
            dict: Информация о загруженном файле
            
        Raises:
            FileNotFoundError: Если файл не найден
            Exception: Если загрузка не удалась
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Переписка/post_api_ext_v2_services__serviceId__channels__channelId__files
        """
        file_name = file_path.split(os.path.sep)[-1]
        mime_type, _ = mimetypes.guess_type(file_path)
        data = MultipartEncoder(fields={'file': (file_name, open(file_path, 'rb'), mime_type)})
        headers = self._default_headers.copy()
        headers['Content-Type'] = data.content_type
        self._default_headers.update(headers)
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/services/{self.service_id}/channels/{channel_id}/files',
            data=data,
        ) 
        headers['Content-Type'] = 'application/json'
        self._default_headers.update(headers)
        return resp
    
    async def async_channel_post_file(self, channel_id: str, file_path: str):
        """
        Асинхронная загрузка файла в канал.
        
        Args:
            channel_id (str): ID канала
            file_path (str): Путь к файлу для загрузки
            
        Returns:
            dict: Информация о загруженном файле
            
        Raises:
            FileNotFoundError: Если файл не найден
            Exception: Если загрузка не удалась
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Переписка/post_api_ext_v2_services__serviceId__channels__channelId__files
        """
        file_name = file_path.split(os.path.sep)[-1]
        mime_type, _ = mimetypes.guess_type(file_path)
        async with aiofiles.open(file_path, 'rb') as file:
            file_data = await file.read()
        data = FormData()
        data.add_field(
            'file',
            file_data,
            filename=file_name,
            content_type=mime_type
        )
        original_headers = self._default_headers.copy()
        headers = original_headers.copy()
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/services/{self.service_id}/channels/{channel_id}/files',
            data=data,
            headers=headers 
        )
        return resp
    
    def sync_channel_get_file(self, channel_id: str, file_id: str):
        """
        Синхронное получение файла из канала.
        
        Args:
            channel_id (str): ID канала
            file_id (str): ID файла
            
        Returns:
            dict: Данные файла
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Переписка/get_api_ext_v2_services__serviceId__channels__channelId__files__fileId_
        """
        resp = self.sync_request(
            'get',
            f'/api/ext/v2/services/{self.service_id}/channels/{channel_id}/files/{file_id}',
        ) 
        return resp
    
    async def async_channel_get_file(self, channel_id: str, file_id: str):
        """
        Асинхронное получение файла из канала.
        
        Args:
            channel_id (str): ID канала
            file_id (str): ID файла
            
        Returns:
            dict: Данные файла
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Переписка/get_api_ext_v2_services__serviceId__channels__channelId__files__fileId_
        """
        resp = await self.async_request(
            'get',
            f'/api/ext/v2/services/{self.service_id}/channels/{channel_id}/files/{file_id}',
        )
        return resp

    def sync_channel_question_async(self, channel_id: str, **kwargs):
        """
        Синхронная отправка вопроса в канал (асинхронная обработка).
        
        Args:
            channel_id (str): ID канала
            **kwargs: Параметры вопроса (см. QuestionModel)
            
        Returns:
            dict: Результат с ID вопроса или ошибками валидации
                - id (str): ID созданного вопроса
                - errors (list): Список ошибок валидации
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Переписка/SendQuestionAsync
        """
        try: model = QuestionModel(**kwargs)
        except ValidationError as e:
            return {
                "id": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/services/{self.service_id}/{channel_id}/questionsAsync',
            json=json
        ) 
        return {"id": resp, "errors": None}
    
    async def async_channel_question_async(self, channel_id: str, **kwargs):
        """
        Асинхронная отправка вопроса в канал (асинхронная обработка).
        
        Args:
            channel_id (str): ID канала
            **kwargs: Параметры вопроса (см. QuestionModel)
            
        Returns:
            dict: Результат с ID вопроса или ошибками валидации
                - id (str): ID созданного вопроса
                - errors (list): Список ошибок валидации
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Переписка/SendQuestionAsync
        """
        try: model = QuestionModel(**kwargs)
        except ValidationError as e:
            return {
                "id": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/services/{self.service_id}/{channel_id}/questionsAsync',
            json=json
        )
        return {"id": resp, "errors": None}
    
    def sync_close_conversation(self, conversation_id: str, **kwargs):
        """
        Синхронное закрытие диалога.
        
        Args:
            conversation_id (str): ID диалога
            **kwargs: Параметры закрытия (см. CloseConversationModel)
            
        Returns:
            dict: Результат операции или ошибки валидации
                - result: Результат закрытия
                - errors (list): Список ошибок валидации
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Переписка/CloseConversation
        """
        try: model = CloseСonversationModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/services/{self.service_id}/conversations/{conversation_id}/close',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_close_conversation(self, conversation_id: str, **kwargs):
        """
        Асинхронное закрытие диалога.
        
        Args:
            conversation_id (str): ID диалога
            **kwargs: Параметры закрытия (см. CloseConversationModel)
            
        Returns:
            dict: Результат операции или ошибки валидации
                - result: Результат закрытия
                - errors (list): Список ошибок валидации
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Переписка/CloseConversation
        """
        try: model = CloseСonversationModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/services/{self.service_id}/conversations/{conversation_id}/close',
            json=json
        )
        return {"result": resp, "errors": None}
    
    def sync_get_conversation_suggestions(self, conversation_id: str):
        """
        Синхронное получение предложений для диалога.
        
        Args:
            conversation_id (str): ID диалога
            
        Returns:
            dict: Список предложений и ошибки
                - result: Список предложений
                - errors (list): Список ошибок
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Переписка/GetSuggestions
        """
        resp = self.sync_request(
            'get',
            f'/api/ext/v2/services/{self.service_id}/conversations/{conversation_id}/suggestions',
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_conversation_suggestions(self, conversation_id: str):
        """
        Асинхронное получение предложений для диалога.
        
        Args:
            conversation_id (str): ID диалога
            
        Returns:
            dict: Список предложений и ошибки
                - result: Список предложений
                - errors (list): Список ошибок
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Переписка/GetSuggestions
        """
        resp = await self.async_request(
            'get',
            f'/api/ext/v2/services/{self.service_id}/conversations/{conversation_id}/suggestions',
        )
        return {"result": resp, "errors": None}
    
    def sync_get_conversations(self, **kwargs):
        """
        Синхронное получение списка диалогов с фильтрацией.
        
        Args:
            **kwargs: Параметры фильтрации (см. GetConversationsModel)
                - tsFrom (datetime): Начало периода
                - tsTo (datetime): Конец периода
                - limit (int): Лимит записей
                - page (int): Номер страницы
                - conversationStatusList (list): Список статусов
                - channelUserQuery (str): Поиск по пользователю
                - и другие...
            
        Returns:
            dict: Результат с данными диалогов или ошибками
                - result: Список диалогов
                - errors (list): Список ошибок валидации
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Переписка/GetConversations
        """
        try: model = GetConversationsModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/services/{self.service_id}/conversations',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_conversations(self, **kwargs):
        """
        Асинхронное получение списка диалогов с фильтрацией.
        
        Args:
            **kwargs: Параметры фильтрации (см. GetConversationsModel)
                - tsFrom (datetime): Начало периода
                - tsTo (datetime): Конец периода
                - limit (int): Лимит записей
                - page (int): Номер страницы
                - conversationStatusList (list): Список статусов
                - channelUserQuery (str): Поиск по пользователю
                - и другие...
            
        Returns:
            dict: Результат с данными диалогов или ошибками
                - result: Список диалогов
                - errors (list): Список ошибок валидации
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Переписка/GetConversations
        """
        try: model = GetConversationsModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/services/{self.service_id}/conversations',
            json=json
        )
        return {"result": resp, "errors": None}
    
    def sync_get_conversation(self, conversation_id):
        """
        Синхронное получение информации о конкретном диалоге.
        
        Args:
            conversation_id (str): ID диалога
            
        Returns:
            dict: Данные диалога и ошибки
                - result: Информация о диалоге
                - errors (list): Список ошибок
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Переписка/GetConversation
        """
        resp = self.sync_request(
            'get',
            f'/api/ext/v2/services/{self.service_id}/conversations/{conversation_id}',
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_conversation(self, conversation_id):
        """
        Асинхронное получение информации о конкретном диалоге.
        
        Args:
            conversation_id (str): ID диалога
            
        Returns:
            dict: Данные диалога и ошибки
                - result: Информация о диалоге
                - errors (list): Список ошибок
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Переписка/GetConversation
        """
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/services/{self.service_id}/conversations/{conversation_id}',
        )
        return {"result": resp, "errors": None}
    
    def sync_create_delayed_delivery(self, **kwargs):
        """
        Синхронное создание отложенной рассылки сообщения.
        
        Args:
            **kwargs: Параметры рассылки (см. PostDelayedDeliveryModel)
                - serviceId (str): ID сервиса (автоподстановка)
                - message (str): Текст сообщения
                - scheduleTime (datetime): Время отправки
                - recipient (dict): Информация о получателе
                - и другие...
            
        Returns:
            dict: Результат создания рассылки или ошибки
                - result: Данные созданной рассылки
                - errors (list): Список ошибок валидации
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Рассылки/CreateDelivery
        """
        if 'serviceId' not in kwargs.keys(): kwargs['serviceId'] = self.service_id
        try: model = PostDelayedDeliveryModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/delayedDelivery',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_create_delayed_delivery(self, **kwargs):
        """
        Асинхронное создание отложенной рассылки сообщения.
        
        Args:
            **kwargs: Параметры рассылки (см. PostDelayedDeliveryModel)
                - serviceId (str): ID сервиса (автоподстановка)
                - message (str): Текст сообщения
                - scheduleTime (datetime): Время отправки
                - recipient (dict): Информация о получателе
                - и другие...
            
        Returns:
            dict: Результат создания рассылки или ошибки
                - result: Данные созданной рассылки
                - errors (list): Список ошибок валидации
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Рассылки/CreateDelivery
        """
        try: model = PostDelayedDeliveryModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/delayedDelivery',
            json=json
        )
        return {"result": resp, "errors": None}
    
    def sync_get_delayed_delivery_status(self, delayed_delivery_id):
        """
        Синхронная проверка статуса отложенной рассылки.
        
        Args:
            delayed_delivery_id (str): ID отложенной рассылки
            
        Returns:
            dict: Статус рассылки и ошибки
                - result: Статус рассылки
                - errors (list): Список ошибок
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Рассылки/get_api_ext_v2_delayedDelivery_status
        """
        resp = self.sync_request(
            'get',
            f'/api/ext/v2/delayedDelivery',
            params={'delayedDeliveryId': delayed_delivery_id}
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_delayed_delivery_status(self, delayed_delivery_id):
        """
        Асинхронная проверка статуса отложенной рассылки.
        
        Args:
            delayed_delivery_id (str): ID отложенной рассылки
            
        Returns:
            dict: Статус рассылки и ошибки
                - result: Статус рассылки
                - errors (list): Список ошибок
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Рассылки/get_api_ext_v2_delayedDelivery_status
        """
        resp = await self.async_request(
            'get',
            f'/api/ext/v2/delayedDelivery',
            params={'delayedDeliveryId': delayed_delivery_id}
        )
        return {"result": resp, "errors": None}
    
    def sync_get_delayed_delivery(self, delayed_delivery_id):
        """
        Синхронное получение информации об отложенной рассылки.
        
        Args:
            delayed_delivery_id (str): ID отложенной рассылки
            
        Returns:
            dict: Данные рассылки и ошибки
                - result: Информация о доставке
                - errors (list): Список ошибок
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Рассылки/GetDelivery
        """
        resp = self.sync_request(
            'get',
            f'/api/ext/v2/delayedDelivery/{delayed_delivery_id}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_delayed_delivery(self, delayed_delivery_id):
        """
        Асинхронное получение информации об отложенной рассылки.
        
        Args:
            delayed_delivery_id (str): ID отложенной рассылки
            
        Returns:
            dict: Данные рассылки и ошибки
                - result: Информация о доставке
                - errors (list): Список ошибок
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Рассылки/GetDelivery
        """
        resp = await self.async_request(
            'get',
            f'/api/ext/v2/delayedDelivery/{delayed_delivery_id}'
        )
        return {"result": resp, "errors": None}
    
    def sync_delete_delayed_delivery(self, delayed_delivery_id):
        """
        Синхронное удаление отложенной рассылки.
        
        Args:
            delayed_delivery_id (str): ID отложенной рассылки
            
        Returns:
            dict: Результат удаления и ошибки
                - result: Результат операции
                - errors (list): Список ошибок
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Рассылки/DeleteDelivery
        """
        resp = self.sync_request(
            'delete',
            f'/api/ext/v2/delayedDelivery/{delayed_delivery_id}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_delete_delayed_delivery(self, delayed_delivery_id):
        """
        Асинхронное удаление отложенной рассылки.
        
        Args:
            delayed_delivery_id (str): ID отложенной рассылки
            
        Returns:
            dict: Результат удаления и ошибки
                - result: Результат операции
                - errors (list): Список ошибок
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Рассылки/DeleteDelivery
        """
        resp = await self.async_request(
            'delete',
            f'/api/ext/v2/delayedDelivery/{delayed_delivery_id}'
        )
        return {"result": resp, "errors": None}
    
    def sync_edit_vars(self, vars: list):
        """
        Синхронное редактирование переменных сервиса.
        
        Args:
            vars (list): Список переменных для обновления
                Каждый элемент должен содержать:
                - name (str): Имя переменной
                - value (str): Значение переменной
            
        Returns:
            dict: Результат обновления или ошибки
                - result: Результат операции
                - errors (list): Список ошибок валидации
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Переменные%20сервиса/EditServiceVars
        """
        try: model = [VarModel(**item) for item in vars]
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = [m.model_dump() for m in model]
        resp = self.sync_request(
            'put',
            f'/api/ext/v2/services/{self.service_id}/vars',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_edit_vars(self, vars: list):
        """
        Асинхронное редактирование переменных сервиса.
        
        Args:
            vars (list): Список переменных для обновления
                Каждый элемент должен содержать:
                - name (str): Имя переменной
                - value (str): Значение переменной
            
        Returns:
            dict: Результат обновления или ошибки
                - result: Результат операции
                - errors (list): Список ошибок валидации
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Переменные%20сервиса/EditServiceVars
        """
        try: model = [VarModel(**item) for item in vars]
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = [m.model_dump() for m in model]
        resp = await self.async_request(
            'put',
            f'/api/ext/v2/services/{self.service_id}/vars',
            json=json
        )
        return {"result": resp, "errors": None}
    
    def sync_closed_conversations_count_report(self, **kwargs):
        """
        Синхронное получение отчета по количеству закрытых диалогов.
        
        Args:
            **kwargs: Параметры отчета (см. ConversationsCountReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "ByOperator" - по операторам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
                - documentTags (list, optional): Список тегов документов для фильтрации
                - groups (list, optional): Список ID групп для фильтрации
                - filters (list, optional): Дополнительные фильтры
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета об уровне автоматизации
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_conversations_automation_level_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     dateGrouping="ByWeek",
            ...     additionalGrouping="ByGroup"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20диалогам/post_api_ext_v2_reports_operators_status
        """
        try: model = ConversationsCountReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/reports/conversations/number',
            json=json
        )
        return {"result": resp, "errors": None}
    
    async def async_closed_conversations_count_report(self, **kwargs):
        """
        Асинхронное получение отчета по количеству закрытых диалогов.
        
        Args:
            **kwargs: Параметры отчета (см. ConversationsCountReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "ByOperator" - по операторам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
                - documentTags (list, optional): Список тегов документов для фильтрации
                - groups (list, optional): Список ID групп для фильтрации
                - filters (list, optional): Дополнительные фильтры
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета об уровне автоматизации
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_conversations_automation_level_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     dateGrouping="ByWeek",
            ...     additionalGrouping="ByGroup"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20диалогам/post_api_ext_v2_reports_operators_status
        """
        try: model = ConversationsCountReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/reports/conversations/number',
            json=json
        )
        return {"result": resp, "errors": None}
    
    def sync_conversations_automation_level_report(self, **kwargs):
        """
        Синхронное получение отчета по уровню автоматизации диалогов.
        
        Отчет показывает статистику по автоматизации обработки диалогов,
        включая процент автоматически закрытых диалогов и распределение
        по уровням автоматизации.
        
        Args:
            **kwargs: Параметры отчета (см. ConversationsCountReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "ByOperator" - по операторам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
                - documentTags (list, optional): Список тегов документов для фильтрации
                - groups (list, optional): Список ID групп для фильтрации
                - filters (list, optional): Дополнительные фильтры
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета об уровне автоматизации
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_conversations_automation_level_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     dateGrouping="ByWeek",
            ...     additionalGrouping="ByGroup"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20диалогам/post_api_ext_v2_reports_conversations_automation_level
        """
        try: model = ConversationsCountReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/reports/conversations/automation-level',
            json=json
        )
        return {"result": resp, "errors": None}
    
    async def async_conversations_automation_level_report(self, **kwargs):
        """
        Асинхронное получение отчета по уровню автоматизации диалогов.
        
        Отчет показывает статистику по автоматизации обработки диалогов,
        включая процент автоматически закрытых диалогов и распределение
        по уровням автоматизации.
        
        Args:
            **kwargs: Параметры отчета (см. ConversationsCountReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "ByOperator" - по операторам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
                - documentTags (list, optional): Список тегов документов для фильтрации
                - groups (list, optional): Список ID групп для фильтрации
                - filters (list, optional): Дополнительные фильтры
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета об уровне автоматизации
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_conversations_automation_level_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     dateGrouping="ByWeek",
            ...     additionalGrouping="ByGroup"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20диалогам/post_api_ext_v2_reports_conversations_automation_level
        """
        try: model = ConversationsCountReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/reports/conversations/automation-level',
            json=json
        )
        return {"result": resp, "errors": None}
    
    def sync_conversations_kb_usage_report(self, **kwargs):
        """
        Синхронное получение отчета об абсолютные и относительные данные об использовании 
        баз знаний в автоматических ответах бот и рекомендациях операторам.
        
        Args:
            **kwargs: Параметры отчета (см. ConversationsCountReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "ByOperator" - по операторам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
                - documentTags (list, optional): Список тегов документов для фильтрации
                - groups (list, optional): Список ID групп для фильтрации
                - filters (list, optional): Дополнительные фильтры
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по CSAT/DSAT
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_conversations_rate_csat_dsat_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     additionalGrouping="ByOperator"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20диалогам/post_api_ext_v2_reports_conversations_knowledge_base_usage
        """
        try: model = ConversationsCountReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/reports/conversations/knowledge-base-usage',
            json=json
        )
        return {"result": resp, "errors": None}
    
    async def async_conversations_kb_usage_report(self, **kwargs):
        """
        Синхронное получение отчета об абсолютные и относительные данные об использовании 
        баз знаний в автоматических ответах бот и рекомендациях операторам.
        
        Args:
            **kwargs: Параметры отчета (см. ConversationsCountReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "ByOperator" - по операторам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
                - documentTags (list, optional): Список тегов документов для фильтрации
                - groups (list, optional): Список ID групп для фильтрации
                - filters (list, optional): Дополнительные фильтры
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по CSAT/DSAT
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_conversations_rate_csat_dsat_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     additionalGrouping="ByOperator"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20диалогам/post_api_ext_v2_reports_conversations_knowledge_base_usage
        """
        try: model = ConversationsCountReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/reports/conversations/knowledge-base-usage',
            json=json
        )
        return {"result": resp, "errors": None}
    
    def sync_conversations_rate_csat_dsat_report(self, **kwargs):
        """
        Синхронное получение отчета по CSAT (Customer Satisfaction) и DSAT (Customer Dissatisfaction).
        
        Отчет показывает уровень удовлетворенности клиентов на основе оценок,
        полученных после закрытия диалогов. CSAT - процент положительных оценок,
        DSAT - процент отрицательных оценок.
        
        Args:
            **kwargs: Параметры отчета (см. ConversationsCountReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "ByOperator" - по операторам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
                - documentTags (list, optional): Список тегов документов для фильтрации
                - groups (list, optional): Список ID групп для фильтрации
                - filters (list, optional): Дополнительные фильтры
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по CSAT/DSAT
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_conversations_rate_csat_dsat_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     additionalGrouping="ByOperator"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20диалогам/post_api_ext_v2_reports_conversations_rate_csat_dsat
        """
        try: model = ConversationsCountReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/reports/conversations/rate-csat-dsat',
            json=json
        )
        return {"result": resp, "errors": None}
    
    async def async_conversations_rate_csat_dsat_report(self, **kwargs):
        """
        Асинхронное получение отчета по CSAT (Customer Satisfaction) и DSAT (Customer Dissatisfaction).
        
        Отчет показывает уровень удовлетворенности клиентов на основе оценок,
        полученных после закрытия диалогов. CSAT - процент положительных оценок,
        DSAT - процент отрицательных оценок.
        
        Args:
            **kwargs: Параметры отчета (см. ConversationsCountReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "ByOperator" - по операторам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
                - documentTags (list, optional): Список тегов документов для фильтрации
                - groups (list, optional): Список ID групп для фильтрации
                - filters (list, optional): Дополнительные фильтры
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по CSAT/DSAT
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_conversations_rate_csat_dsat_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     additionalGrouping="ByOperator"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20диалогам/post_api_ext_v2_reports_conversations_rate_csat_dsat
        """
        try: model = ConversationsCountReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/reports/conversations/rate-csat-dsat',
            json=json
        )
        return {"result": resp, "errors": None}
    
    def sync_conversations_rate_distribution_report(self, **kwargs):
        """
        Синхронное получение отчета по распределению оценок диалогов.
        
        Отчет показывает детальное распределение всех полученных оценок
        (например, 1-5 звезд или другую шкалу оценок) с разбивкой по
        выбранным параметрам группировки.
        
        Args:
            **kwargs: Параметры отчета (см. ConversationsCountReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "ByOperator" - по операторам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
                - documentTags (list, optional): Список тегов документов для фильтрации
                - groups (list, optional): Список ID групп для фильтрации
                - filters (list, optional): Дополнительные фильтры
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по распределению оценок
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_conversations_rate_distribution_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     dateGrouping="ByMonth"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20диалогам/post_api_ext_v2_reports_conversations_rate_distribution
        """
        try: model = ConversationsCountReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/reports/conversations/rate-distribution',
            json=json
        )
        return {"result": resp, "errors": None}
    
    async def async_conversations_rate_distribution_report(self, **kwargs):
        """
        Асинхронное получение отчета по распределению оценок диалогов.
        
        Отчет показывает детальное распределение всех полученных оценок
        (например, 1-5 звезд или другую шкалу оценок) с разбивкой по
        выбранным параметрам группировки.
        
        Args:
            **kwargs: Параметры отчета (см. ConversationsCountReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "ByOperator" - по операторам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
                - documentTags (list, optional): Список тегов документов для фильтрации
                - groups (list, optional): Список ID групп для фильтрации
                - filters (list, optional): Дополнительные фильтры
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по распределению оценок
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_conversations_rate_distribution_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     dateGrouping="ByMonth"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20диалогам/post_api_ext_v2_reports_conversations_rate_distribution
        """
        try: model = ConversationsCountReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/reports/conversations/rate-distribution',
            json=json
        )
        return {"result": resp, "errors": None}
    
    def sync_conversations_rate_coverage_report(self, **kwargs):
        """
        Синхронное получение отчета по покрытию оценками.
        
        Отчет показывает процент диалогов, которые получили оценку
        от клиентов, от общего количества закрытых диалогов.
        Помогает анализировать вовлеченность клиентов в процесс оценки.
        
        Args:
            **kwargs: Параметры отчета (см. ConversationsCountReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "ByOperator" - по операторам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
                - documentTags (list, optional): Список тегов документов для фильтрации
                - groups (list, optional): Список ID групп для фильтрации
                - filters (list, optional): Дополнительные фильтры
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по покрытию оценками
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_conversations_rate_coverage_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     additionalGrouping="ByChannel"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20диалогам/post_api_ext_v2_reports_conversations_rate_coverage
        """
        try: model = ConversationsCountReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/reports/conversations/rate-coverage',
            json=json
        )
        return {"result": resp, "errors": None}
    
    async def async_conversations_rate_coverage_report(self, **kwargs):
        """
        Асинхронное получение отчета по покрытию оценками.
        
        Отчет показывает процент диалогов, которые получили оценку
        от клиентов, от общего количества закрытых диалогов.
        Помогает анализировать вовлеченность клиентов в процесс оценки.
        
        Args:
            **kwargs: Параметры отчета (см. ConversationsCountReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "ByOperator" - по операторам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
                - documentTags (list, optional): Список тегов документов для фильтрации
                - groups (list, optional): Список ID групп для фильтрации
                - filters (list, optional): Дополнительные фильтры
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по покрытию оценками
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_conversations_rate_coverage_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     additionalGrouping="ByChannel"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20диалогам/post_api_ext_v2_reports_conversations_rate_coverage
        """
        try: model = ConversationsCountReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/reports/conversations/rate-coverage',
            json=json
        )
        return {"result": resp, "errors": None}
    
    def sync_conversations_afrt_timing_report(self, **kwargs):
        """
        Синхронное получение отчета по времени ответа AutoFAQ (AFRT - AutoFAQ Response Time).
        
        Отчет показывает статистику по времени, которое требуется системе AutoFAQ
        для генерации ответов на вопросы пользователей. Включает среднее время
        ответа, медиану, процентили и другие метрики.
        
        Args:
            **kwargs: Параметры отчета (см. ConversationsCountReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "ByOperator" - по операторам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
                - documentTags (list, optional): Список тегов документов для фильтрации
                - groups (list, optional): Список ID групп для фильтрации
                - filters (list, optional): Дополнительные фильтры
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по времени ответа AutoFAQ
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_conversations_afrt_timing_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     dateGrouping="ByDay"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20диалогам/post_api_ext_v2_reports_conversations_afrt_timing
        """
        try: model = ConversationsCountReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/reports/conversations/afrt-timing',
            json=json
        )
        return {"result": resp, "errors": None}
    
    async def async_conversations_afrt_timing_report(self, **kwargs):
        """
        Асинхронное получение отчета по времени ответа AutoFAQ (AFRT - AutoFAQ Response Time).
        
        Отчет показывает статистику по времени, которое требуется системе AutoFAQ
        для генерации ответов на вопросы пользователей. Включает среднее время
        ответа, медиану, процентили и другие метрики.
        
        Args:
            **kwargs: Параметры отчета (см. ConversationsCountReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "ByOperator" - по операторам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
                - documentTags (list, optional): Список тегов документов для фильтрации
                - groups (list, optional): Список ID групп для фильтрации
                - filters (list, optional): Дополнительные фильтры
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по времени ответа AutoFAQ
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_conversations_afrt_timing_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     dateGrouping="ByDay"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20диалогам/post_api_ext_v2_reports_conversations_afrt_timing
        """
        try: model = ConversationsCountReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/reports/conversations/afrt-timing',
            json=json
        )
        return {"result": resp, "errors": None}

    def sync_conversations_art_timing_report(self, **kwargs):
        """
        Синхронное получение отчета по времени ответа операторов (ART - Agent Response Time).
        
        Отчет показывает статистику по времени, которое требуется операторам
        для ответа на сообщения пользователей. Включает среднее время ответа,
        медиану, процентили и распределение по операторам или группам.
        
        Args:
            **kwargs: Параметры отчета (см. ConversationsCountReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "ByOperator" - по операторам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
                - documentTags (list, optional): Список тегов документов для фильтрации
                - groups (list, optional): Список ID групп для фильтрации
                - filters (list, optional): Дополнительные фильтры
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по времени ответа операторов
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_conversations_art_timing_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     additionalGrouping="ByOperator"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20диалогам/post_api_ext_v2_reports_conversations_art_timing
        """
        try: model = ConversationsCountReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/reports/conversations/art-timing',
            json=json
        )
        return {"result": resp, "errors": None}
    
    async def async_conversations_art_timing_report(self, **kwargs):
        """
        Асинхронное получение отчета по времени ответа операторов (ART - Agent Response Time).
        
        Отчет показывает статистику по времени, которое требуется операторам
        для ответа на сообщения пользователей. Включает среднее время ответа,
        медиану, процентили и распределение по операторам или группам.
        
        Args:
            **kwargs: Параметры отчета (см. ConversationsCountReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "ByOperator" - по операторам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
                - documentTags (list, optional): Список тегов документов для фильтрации
                - groups (list, optional): Список ID групп для фильтрации
                - filters (list, optional): Дополнительные фильтры
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по времени ответа операторов
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_conversations_art_timing_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     additionalGrouping="ByOperator"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20диалогам/post_api_ext_v2_reports_conversations_art_timing
        """
        try: model = ConversationsCountReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/reports/conversations/art-timing',
            json=json
        )
        return {"result": resp, "errors": None}
    
    def sync_operators_status_report(self, **kwargs):
        """
        Синхронное получение отчета по статусам операторов.
        
        Отчет показывает распределение операторов по статусам (онлайн, офлайн, перерыв и т.д.)
        за выбранный период времени с возможностью группировки по различным параметрам.
        
        Args:
            **kwargs: Параметры отчета (см. OperatorsReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - operators (list, optional): Список UUID операторов для фильтрации
                - groups (list, optional): Список UUID групп для фильтрации
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByOperator" - по операторам
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по статусам операторов
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_operators_status_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     dateGrouping="ByDay",
            ...     additionalGrouping="ByOperator"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20операторам/post_api_ext_v2_reports_operators_status
        """
        try: model = OperatorsReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/reports/operators/status',
            json=json
        )
        return {"result": resp, "errors": None}
    
    async def async_operators_status_report(self, **kwargs):
        """
        Асинхронное получение отчета по статусам операторов.
        
        Отчет показывает распределение операторов по статусам (онлайн, офлайн, перерыв и т.д.)
        за выбранный период времени с возможностью группировки по различным параметрам.
        
        Args:
            **kwargs: Параметры отчета (см. OperatorsReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - operators (list, optional): Список UUID операторов для фильтрации
                - groups (list, optional): Список UUID групп для фильтрации
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByOperator" - по операторам
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по статусам операторов
                - errors (list): Список ошибок валидации или None
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20операторам/post_api_ext_v2_reports_operators_status
        """
        try: model = OperatorsReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/reports/operators/status',
            json=json
        )
        return {"result": resp, "errors": None}
    
    def sync_operators_productivity_absolute_report(self, **kwargs):
        """
        Синхронное получение отчета по абсолютной продуктивности операторов.
        
        Отчет показывает абсолютные показатели продуктивности операторов:
        количество обработанных диалогов, закрытых диалогов, отправленных сообщений
        и другие количественные метрики за выбранный период.
        
        Args:
            **kwargs: Параметры отчета (см. OperatorsReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - operators (list, optional): Список UUID операторов для фильтрации
                - groups (list, optional): Список UUID групп для фильтрации
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByOperator" - по операторам
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по абсолютной продуктивности
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_operators_productivity_absolute_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     additionalGrouping="ByOperator"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20операторам/post_api_ext_v2_reports_operators_productivity_absolute
        """
        try: model = OperatorsReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/reports/operators/productivity/absolute',
            json=json
        )
        return {"result": resp, "errors": None}
    
    async def async_operators_productivity_absolute_report(self, **kwargs):
        """
        Асинхронное получение отчета по абсолютной продуктивности операторов.
        
        Отчет показывает абсолютные показатели продуктивности операторов:
        количество обработанных диалогов, закрытых диалогов, отправленных сообщений
        и другие количественные метрики за выбранный период.
        
        Args:
            **kwargs: Параметры отчета (см. OperatorsReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - operators (list, optional): Список UUID операторов для фильтрации
                - groups (list, optional): Список UUID групп для фильтрации
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByOperator" - по операторам
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по абсолютной продуктивности
                - errors (list): Список ошибок валидации или None
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20операторам/post_api_ext_v2_reports_operators_productivity_absolute
        """
        try: model = OperatorsReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/reports/operators/productivity/absolute',
            json=json
        )
        return {"result": resp, "errors": None}
    
    def sync_operators_productivity_relative_report(self, **kwargs):
        """
        Синхронное получение отчета по относительной продуктивности операторов.
        
        Отчет показывает относительные показатели продуктивности операторов:
        среднее время обработки диалога, процент автоматизации, эффективность
        и другие относительные метрики в сравнении между операторами или группами.
        
        Args:
            **kwargs: Параметры отчета (см. OperatorsReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - operators (list, optional): Список UUID операторов для фильтрации
                - groups (list, optional): Список UUID групп для фильтрации
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByOperator" - по операторам
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по относительной продуктивности
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_operators_productivity_relative_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     dateGrouping="ByWeek"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20операторам/post_api_ext_v2_reports_operators_productivity_relative
        """
        try: model = OperatorsReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/reports/operators/productivity/relative',
            json=json
        )
        return {"result": resp, "errors": None}
    
    async def async_operators_productivity_relative_report(self, **kwargs):
        """
        Асинхронное получение отчета по относительной продуктивности операторов.
        
        Отчет показывает относительные показатели продуктивности операторов:
        среднее время обработки диалога, процент автоматизации, эффективность
        и другие относительные метрики в сравнении между операторами или группами.
        
        Args:
            **kwargs: Параметры отчета (см. OperatorsReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - operators (list, optional): Список UUID операторов для фильтрации
                - groups (list, optional): Список UUID групп для фильтрации
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByOperator" - по операторам
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по относительной продуктивности
                - errors (list): Список ошибок валидации или None
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20операторам/post_api_ext_v2_reports_operators_productivity_relative
        """
        try: model = OperatorsReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/reports/operators/productivity/relative',
            json=json
        )
        return {"result": resp, "errors": None}
    
    def sync_operators_occupancy_report(self, **kwargs):
        """
        Синхронное получение отчета по загрузке (occupancy) операторов.
        
        Отчет показывает уровень загрузки операторов - процент времени,
        который операторы фактически работали с диалогами от общего
        рабочего времени за выбранный период.
        
        Args:
            **kwargs: Параметры отчета (см. OperatorsReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - operators (list, optional): Список UUID операторов для фильтрации
                - groups (list, optional): Список UUID групп для фильтрации
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByOperator" - по операторам
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по загрузке операторов
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_operators_occupancy_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     additionalGrouping="ByGroup"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20операторам/post_api_ext_v2_reports_operators_occupancy
        """
        try: model = OperatorsReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/reports/operators/occupancy',
            json=json
        )
        return {"result": resp, "errors": None}
    
    async def async_operators_occupancy_report(self, **kwargs):
        """
        Асинхронное получение отчета по загрузке (occupancy) операторов.
        
        Отчет показывает уровень загрузки операторов - процент времени,
        который операторы фактически работали с диалогами от общего
        рабочего времени за выбранный период.
        
        Args:
            **kwargs: Параметры отчета (см. OperatorsReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - operators (list, optional): Список UUID операторов для фильтрации
                - groups (list, optional): Список UUID групп для фильтрации
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByOperator" - по операторам
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по загрузке операторов
                - errors (list): Список ошибок валидации или None
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20операторам/post_api_ext_v2_reports_operators_occupancy
        """
        try: model = OperatorsReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/reports/operators/occupancy',
            json=json
        )
        return {"result": resp, "errors": None}
    
    def sync_operators_concurrency_report(self, **kwargs):
        """
        Синхронное получение отчета по параллельности работы операторов.
        
        Отчет показывает среднее количество одновременных диалогов, которые 
        операторы ведут параллельно, а также максимальные значения параллельности 
        для анализа нагрузки и эффективности работы операторов.
        
        Args:
            **kwargs: Параметры отчета (см. OperatorsReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - operators (list, optional): Список UUID операторов для фильтрации
                - groups (list, optional): Список UUID групп для фильтрации
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByOperator" - по операторам
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по параллельности работы операторов
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_operators_concurrency_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     dateGrouping="ByDay"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20операторам/post_api_ext_v2_reports_operators_concurrency
        """
        try: model = OperatorsReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/reports/operators/concurrency',
            json=json
        )
        return {"result": resp, "errors": None}
    
    async def async_operators_concurrency_report(self, **kwargs):
        """
        Асинхронное получение отчета по параллельности работы операторов.
        
        Отчет показывает среднее количество одновременных диалогов, которые 
        операторы ведут параллельно, а также максимальные значения параллельности 
        для анализа нагрузки и эффективности работы операторов.
        
        Args:
            **kwargs: Параметры отчета (см. OperatorsReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - operators (list, optional): Список UUID операторов для фильтрации
                - groups (list, optional): Список UUID групп для фильтрации
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByOperator" - по операторам
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по параллельности работы операторов
                - errors (list): Список ошибок валидации или None
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20операторам/post_api_ext_v2_reports_operators_concurrency
        """
        try: model = OperatorsReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/reports/operators/concurrency',
            json=json
        )
        return {"result": resp, "errors": None}
    
    def sync_operators_afrt_timing_report(self, **kwargs):
        """
        Синхронное получение отчета по времени ответа AutoFAQ для операторов (AFRT).
        
        Отчет показывает статистику по времени, которое требуется системе AutoFAQ
        для генерации ответов на вопросы пользователей в диалогах, которые 
        обрабатываются конкретными операторами или группами операторов.
        
        Args:
            **kwargs: Параметры отчета (см. OperatorsReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - operators (list, optional): Список UUID операторов для фильтрации
                - groups (list, optional): Список UUID групп для фильтрации
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByOperator" - по операторам
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по времени ответа AutoFAQ для операторов
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_operators_afrt_timing_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     additionalGrouping="ByOperator"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20операторам/post_api_ext_v2_reports_operators_afrt_operator_timing
        """
        try: model = OperatorsReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/reports/operators/afrt-operator-timing',
            json=json
        )
        return {"result": resp, "errors": None}
    
    async def async_operators_afrt_timing_report(self, **kwargs):
        """
        Асинхронное получение отчета по времени ответа AutoFAQ для операторов (AFRT).
        
        Отчет показывает статистику по времени, которое требуется системе AutoFAQ
        для генерации ответов на вопросы пользователей в диалогах, которые 
        обрабатываются конкретными операторами или группами операторов.
        
        Args:
            **kwargs: Параметры отчета (см. OperatorsReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - operators (list, optional): Список UUID операторов для фильтрации
                - groups (list, optional): Список UUID групп для фильтрации
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByOperator" - по операторам
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по времени ответа AutoFAQ для операторов
                - errors (list): Список ошибок валидации или None
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20операторам/post_api_ext_v2_reports_operators_afrt_operator_timing
        """
        try: model = OperatorsReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/reports/operators/afrt-operator-timing',
            json=json
        )
        return {"result": resp, "errors": None}
    
    def sync_operators_art_timing_report(self, **kwargs):
        """
        Синхронное получение отчета по времени ответа операторов (ART).
        
        Отчет показывает статистику по времени, которое требуется операторам
        для ответа на сообщения пользователей. Включает среднее время ответа,
        медиану, процентили и распределение по операторам или группам.
        
        Args:
            **kwargs: Параметры отчета (см. OperatorsReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - operators (list, optional): Список UUID операторов для фильтрации
                - groups (list, optional): Список UUID групп для фильтрации
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByOperator" - по операторам
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по времени ответа операторов
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_operators_art_timing_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     additionalGrouping="ByGroup"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20операторам/post_api_ext_v2_reports_operators_art_operator_timing
        """
        try: model = OperatorsReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/reports/operators/art-operator-timing',
            json=json
        )
        return {"result": resp, "errors": None}
    
    async def async_operators_art_timing_report(self, **kwargs):
        """
        Асинхронное получение отчета по времени ответа операторов (ART).
        
        Отчет показывает статистику по времени, которое требуется операторам
        для ответа на сообщения пользователей. Включает среднее время ответа,
        медиану, процентили и распределение по операторам или группам.
        
        Args:
            **kwargs: Параметры отчета (см. OperatorsReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - operators (list, optional): Список UUID операторов для фильтрации
                - groups (list, optional): Список UUID групп для фильтрации
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByOperator" - по операторам
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по времени ответа операторов
                - errors (list): Список ошибок валидации или None
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20операторам/post_api_ext_v2_reports_operators_art_operator_timing
        """
        try: model = OperatorsReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/reports/operators/art-operator-timing',
            json=json
        )
        return {"result": resp, "errors": None}
    
    def sync_operators_aht_timing_report(self, **kwargs):
        """
        Синхронное получение отчета по среднему времени обработки диалогов (AHT).
        
        Отчет показывает Average Handling Time - среднее время, которое операторы
        затрачивают на полную обработку одного диалога от первого сообщения 
        до закрытия, включая все этапы работы с клиентом.
        
        Args:
            **kwargs: Параметры отчета (см. OperatorsReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - operators (list, optional): Список UUID операторов для фильтрации
                - groups (list, optional): Список UUID групп для фильтрации
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByOperator" - по операторам
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по среднему времени обработки диалогов
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_operators_aht_timing_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     dateGrouping="ByWeek"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20операторам/post_api_ext_v2_reports_operators_aht_operator_timing
        """
        try: model = OperatorsReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/reports/operators/aht-operator-timing',
            json=json
        )
        return {"result": resp, "errors": None}
    
    async def async_operators_aht_timing_report(self, **kwargs):
        """
        Асинхронное получение отчета по среднему времени обработки диалогов (AHT).
        
        Отчет показывает Average Handling Time - среднее время, которое операторы
        затрачивают на полную обработку одного диалога от первого сообщения 
        до закрытия, включая все этапы работы с клиентом.
        
        Args:
            **kwargs: Параметры отчета (см. OperatorsReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - operators (list, optional): Список UUID операторов для фильтрации
                - groups (list, optional): Список UUID групп для фильтрации
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByOperator" - по операторам
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по среднему времени обработки диалогов
                - errors (list): Список ошибок валидации или None
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20операторам/post_api_ext_v2_reports_operators_aht_operator_timing
        """
        try: model = OperatorsReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/reports/operators/aht-operator-timing',
            json=json
        )
        return {"result": resp, "errors": None}
    
    def sync_operators_afrt_sla_report(self, **kwargs):
        """
        Синхронное получение отчета по соблюдению SLA для времени ответа AutoFAQ.
        
        Отчет показывает процент диалогов, в которых время ответа системы AutoFAQ
        укладывается в установленные Service Level Agreement (SLA) нормы.
        Помогает оценить соответствие скорости работы бота требуемым стандартам.
        
        Args:
            **kwargs: Параметры отчета (см. OperatorsReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - operators (list, optional): Список UUID операторов для фильтрации
                - groups (list, optional): Список UUID групп для фильтрации
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByOperator" - по операторам
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по соблюдению SLA для времени ответа AutoFAQ
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_operators_afrt_sla_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     additionalGrouping="ByChannel"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20операторам/post_api_ext_v2_reports_operators_afrt_sla
        """
        try: model = OperatorsReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/reports/operators/afrt-sla',
            json=json
        )
        return {"result": resp, "errors": None}
    
    async def async_operators_afrt_sla_report(self, **kwargs):
        """
        Асинхронное получение отчета по соблюдению SLA для времени ответа AutoFAQ.
        
        Отчет показывает процент диалогов, в которых время ответа системы AutoFAQ
        укладывается в установленные Service Level Agreement (SLA) нормы.
        Помогает оценить соответствие скорости работы бота требуемым стандартам.
        
        Args:
            **kwargs: Параметры отчета (см. OperatorsReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - operators (list, optional): Список UUID операторов для фильтрации
                - groups (list, optional): Список UUID групп для фильтрации
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByOperator" - по операторам
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по соблюдению SLA для времени ответа AutoFAQ
                - errors (list): Список ошибок валидации или None
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20операторам/post_api_ext_v2_reports_operators_afrt_sla
        """
        try: model = OperatorsReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/reports/operators/afrt-sla',
            json=json
        )
        return {"result": resp, "errors": None}
    
    def sync_operators_art_sla_report(self, **kwargs):
        """
        Синхронное получение отчета по соблюдению SLA для времени ответа операторов.
        
        Отчет показывает процент диалогов, в которых время ответа операторов
        укладывается в установленные Service Level Agreement (SLA) нормы.
        Помогает оценить соответствие скорости работы операторов требуемым стандартам.
        
        Args:
            **kwargs: Параметры отчета (см. OperatorsReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - operators (list, optional): Список UUID операторов для фильтрации
                - groups (list, optional): Список UUID групп для фильтрации
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByOperator" - по операторам
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по соблюдению SLA для времени ответа операторов
                - errors (list): Список ошибок валидации или None
            
        Example:
            >>> report = client.sync_operators_art_sla_report(
            ...     dateRange={
            ...         "from": "2024-01-01T00:00:00Z",
            ...         "to": "2024-01-31T23:59:59Z"
            ...     },
            ...     dateGrouping="ByMonth"
            ... )
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20операторам/post_api_ext_v2_reports_operators_art_sla
        """
        try: model = OperatorsReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = self.sync_request(
            'post',
            f'/api/ext/v2/reports/operators/art-sla',
            json=json
        )
        return {"result": resp, "errors": None}
    
    async def async_operators_art_sla_report(self, **kwargs):
        """
        Асинхронное получение отчета по соблюдению SLA для времени ответа операторов.
        
        Отчет показывает процент диалогов, в которых время ответа операторов
        укладывается в установленные Service Level Agreement (SLA) нормы.
        Помогает оценить соответствие скорости работы операторов требуемым стандартам.
        
        Args:
            **kwargs: Параметры отчета (см. OperatorsReportModel)
                - dateRange (dict): Временной диапазон отчета
                    - from (datetime): Начало периода
                    - to (datetime): Конец периода
                - operators (list, optional): Список UUID операторов для фильтрации
                - groups (list, optional): Список UUID групп для фильтрации
                - dateGrouping (str): Группировка по дате. Варианты:
                    - "ByDay" - по дням
                    - "ByWeek" - по неделям  
                    - "ByMonth" - по месяцам
                    - "ByYear" - по годам
                - additionalGrouping (str): Дополнительная группировка. Варианты:
                    - "ByOperator" - по операторам
                    - "ByGroup" - по группам
                    - "ByChannel" - по каналам
                    - "None" - без группировки
                - knowledgeBases (list, optional): Список ID баз знаний для фильтрации
            
        Returns:
            dict: Результат с данными отчета или ошибками валидации
                - result: Данные отчета по соблюдению SLA для времени ответа операторов
                - errors (list): Список ошибок валидации или None
                
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/external-api/2.1.4#/Отчеты%20по%20операторам/post_api_ext_v2_reports_operators_art_sla
        """
        try: model = OperatorsReportModel(**kwargs)
        except ValidationError as e:
            return {
                "results": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            if 'dateRange' in json:
                if json['dateRange']:
                    if 'from_' in json['dateRange']:
                        json['dateRange']['from'] = json['dateRange']['from_']
                        del json['dateRange']['from_']
        resp = await self.async_request(
            'post',
            f'/api/ext/v2/reports/operators/art-sla',
            json=json
        )
        return {"result": resp, "errors": None}