import os
import mimetypes
import aiofiles
import warnings

from aiohttp import FormData
from pydantic import ValidationError
from requests_toolbelt.multipart.encoder import MultipartEncoder
from .models.kb_crud_models import UserCreateModel, UserUpdateModel, ServiceCreateModel, ServicesGetModel, \
                                   ServiceIdsModel, ServiceGetModel, ServiceDocumentsGetModel, SuggestedDocumentsParamsModel, \
                                   SuggestedDocumentsCountParamsModel, SuggestedParaphrasesParamsModel, SuggestedParaphrasesCountParamsModel, \
                                   SuggestedDocumentsValidateModel, SearchDocumentsContentModel, ServicesValidationsModel, UpdateServiceAttachmentModel, \
                                   ServicePromptModel, ServicePromptQAModel, CreateDocumentRequest, UpdateDocumentRequest, DocumentAttachmentModel, \
                                   DocumentContextModel, DocumentTagsModel, CreateParaphraseModel, GetParaphrasesyParamsModel, MassUpdateParaphrasesModel, \
                                   MassMoveParaphrasesModel, UpdateParaphraseItemModel, GroupsListModel, CreateServiceTermModel, CreateUserTermModel
from .http_client import AutoFaqHTTPClient


class AutoFaqCrud(AutoFaqHTTPClient):
    """
    Клиент для работы с AutoFAQ Knowledge Base CRUD API.
    
    Предоставляет синхронные и асинхронные методы для управления пользователями, 
    сервисами, документами, парафразами, группами и другими сущностями системы.
    
    Attributes:
        base_url (str): Базовый URL API
        user_token (str): Токен аутентификации пользователя
        timeout (int): Таймаут запросов в секундах (по умолчанию 30)
    
    Examples:
        >>> # Создание клиента
        >>> client = AutoFaqCrud("https://api.example.com", "user_token_123")
        >>> 
        >>> # Синхронное создание пользователя
        >>> result = client.sync_create_user(name="John Doe", email="john@example.com")
        >>> 
        >>> # Асинхронное получение сервиса
        >>> result = await client.async_get_service(service_id=123)
        
    Link: 
        https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/
    """
    
    def __init__(self, base_url: str, user_token: str, timeout: int = 30):
        super().__init__(base_url, timeout)
        self.user_token = user_token
        
    def sync_request(self, method: str, endpoint: str, return_json: bool = True, **kwargs):
        """
        Выполняет синхронный HTTP запрос к API.
        
        Args:
            method (str): HTTP метод (GET, POST, PUT, DELETE, etc.)
            endpoint (str): Конечная точка API
            return_json (bool): Возвращать ответ как JSON (по умолчанию True)
            **kwargs: Дополнительные параметры для requests
        
        Returns:
            dict or Response: Ответ от API в формате JSON или сырой ответ
        """
        if 'AUTOFAQ-User-Token' not in self._default_headers:
            self.update_default_headers({"AUTOFAQ-User-Token": f"{self.user_token}"})
        url = self._build_url(endpoint)
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        response = self.sync_session.request(method.upper(), url, **kwargs)
        return self._handle_response(response, return_json)
    
    async def async_request(self, method: str, endpoint: str, return_json: bool = True, **kwargs):
        """
        Выполняет асинхронный HTTP запрос к API.
        
        Args:
            method (str): HTTP метод (GET, POST, PUT, DELETE, etc.)
            endpoint (str): Конечная точка API
            return_json (bool): Возвращать ответ как JSON (по умолчанию True)
            **kwargs: Дополнительные параметры для aiohttp
        
        Returns:
            dict or Response: Ответ от API в формате JSON или сырой ответ
        """
        if 'AUTOFAQ-User-Token' not in self._default_headers:
            await self.async_set_default_headers({"AUTOFAQ-User-Token": f"{self.user_token}"})
        url = self._build_url(endpoint)
        async with self.async_session.request(method.upper(), url, **kwargs) as response:
            return await self._handle_async_response(response, return_json)
        
    def sync_create_user(self, **kwargs):
        """
        Создает нового пользователя (синхронно).
        
        Args:
            email (str): Email пользователя
            name (str): Имя пользователя
            password (str): Пароль пользователя для аутентификации
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Users%20CRUD%20API/post_users
        """
        try: model = UserCreateModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'post',
            '/core-api/crud/api/v1/users',
            json=json
        ) 
        return {"result": resp, "errors": None}
        
    async def async_create_user(self, **kwargs):
        """
        Создает нового пользователя (асинхронно).
        
        Args:
            email (str): Email пользователя
            name (str): Имя пользователя
            password (str): Пароль пользователя для аутентификации
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Users%20CRUD%20API/post_users
        """
        try: model = UserCreateModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'post',
            '/core-api/crud/api/v1/users',
            json=json
        ) 
        return {"result": resp, "errors": None}
        
    def sync_get_user(self, user_id: int):
        """
        Получает информацию о пользователе по ID (синхронно).
        
        Args:
            user_id (int): ID пользователя
        
        Returns:
            dict: Результат операции {"result": user_data, "errors": None}
        
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Users%20CRUD%20API/get_users__id_
        """
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/users/{user_id}',
        ) 
        return {"result": resp, "errors": None}
        
    async def async_get_user(self, user_id: int):
        """
        Получает информацию о пользователе по ID (асинхронно).
        
        Args:
            user_id (int): ID пользователя
        
        Returns:
            dict: Результат операции {"result": user_data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Users%20CRUD%20API/get_users__id_
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/users/{user_id}',
        ) 
        return {"result": resp, "errors": None}
        
    def sync_update_user(self, user_id: int, **kwargs):
        """
        Обновляет информацию о пользователе (синхронно).
        
        Args:
            token (int): Token пользователя
            name (str): Имя пользователя
            password (str): Пароль пользователя для аутентификации
            max_services_count (int): Максимальное количество сервисов

        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Users%20CRUD%20API/put_users__id_
        """
        try: model = UserUpdateModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'put',
            f'/core-api/crud/api/v1/users/{user_id}',
            json=json
        ) 
        return {"result": resp, "errors": None}
        
    async def async_update_user(self, user_id: int, **kwargs):
        """
        Обновляет информацию о пользователе (асинхронно).
        
        Args:
            token (int): Token пользователя
            name (str): Имя пользователя
            password (str): Пароль пользователя для аутентификации
            max_services_count (int): Максимальное количество сервисов

        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Users%20CRUD%20API/put_users__id_
        """
        try: model = UserUpdateModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'put',
            f'/core-api/crud/api/v1/users/{user_id}',
            json=json
        ) 
        return {"result": resp, "errors": None}
        
    def sync_delete_user(self, user_id: int):
        """
        Удаляет пользователя (синхронно).
        
        Args:
            user_id (int): ID пользователя
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Users%20CRUD%20API/delete_users__id_
        """
        resp = self.sync_request(
            'delete',
            f'/core-api/crud/api/v1/users/{user_id}',
        ) 
        return {"result": resp, "errors": None}
        
    async def async_delete_user(self, user_id: int):
        """
        Удаляет пользователя (асинхронно).
        
        Args:
            user_id (int): ID пользователя
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Users%20CRUD%20API/delete_users__id_
        """
        resp = await self.async_request(
            'delete',
            f'/core-api/crud/api/v1/users/{user_id}',
        )
        return {"result": resp, "errors": None}
        
    def sync_create_service(self, **kwargs):
        """
        Создает новую базу знаний (синхронно).
        
        Args:
            name (str): Название базы знания
            preset (_LanguagePreset): Языковой пресет для обработки текста
            trainable (bool): Возможность обучения модели на данных базы знания
            max_trainable_score (float): Максимальный порог обучаемости модели (0.0-1.0)
            min_levenstein_distance (int): Минимальное расстояние Левенштейна для схожести фраз
            max_conf_mode_for_ident_phs (bool): Максимальный режим уверенности для идентичных фраз
            method Literal["auto", "manual", "hybrid"]: Метод обработки запросов
            split_by_linguistic_conjunctions (bool) Разделение запросов по лингвистическим союзам
            enable_tokenization (bool): Включение токенизации текста
            query_length (_QueryLength): Длина обрабатываемых запросов
            inequal_lang_penalty (float): Штраф за разные языки в запросе и ответе (0.0-1.0)
            without_validation (bool): Создание базы знания без валидации данных
            with_layout_correction (bool): Коррекция layout'а текста
            ext (Dict[str, Any]): Дополнительные параметры базы знания в формате ключ-значение 
            documents (List[DocumentModel]): Список документов базы знания
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services
        """
        try: model = ServiceCreateModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'post',
            '/core-api/crud/api/v1/services',
            json=json
        ) 
        return {"result": resp, "errors": None}
        
    async def async_create_service(self, **kwargs):
        """
        Создает новый базу знаний (асинхронно).
        
        Args:
            name (str): Название базы знания
            preset (_LanguagePreset): Языковой пресет для обработки текста
            trainable (bool): Возможность обучения модели на данных базы знания
            max_trainable_score (float): Максимальный порог обучаемости модели (0.0-1.0)
            min_levenstein_distance (int): Минимальное расстояние Левенштейна для схожести фраз
            max_conf_mode_for_ident_phs (bool): Максимальный режим уверенности для идентичных фраз
            method Literal["auto", "manual", "hybrid"]: Метод обработки запросов
            split_by_linguistic_conjunctions (bool) Разделение запросов по лингвистическим союзам
            enable_tokenization (bool): Включение токенизации текста
            query_length (_QueryLength): Длина обрабатываемых запросов
            inequal_lang_penalty (float): Штраф за разные языки в запросе и ответе (0.0-1.0)
            without_validation (bool): Создание базы знания без валидации данных
            with_layout_correction (bool): Коррекция layout'а текста
            ext (Dict[str, Any]): Дополнительные параметры базы знания в формате ключ-значение 
            documents (List[DocumentModel]): Список документов базы знания
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services
        """
        try: model = ServiceCreateModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'post',
            '/core-api/crud/api/v1/service',
            json=json
        ) 
        return {"result": resp, "errors": None}
        
    def sync_get_services(self, **kwargs):
        """
        Получение списка баз знаний в учетной записи (синхронно).
        
        Args:
            offset (int): pagination offset (default 0)
            count (int): (int):pagination count (default 9999)
            sort_by (str): sort by 'id' or 'modified_at' (default is 'id')
            sort_order (str): sorting order 'asc' or 'desc' (default is 'asc')
        
        Returns:
            dict: Результат операции {"result": services_data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services
        """
        try: model = ServicesGetModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'get',
            '/core-api/crud/api/v1/services',
            params=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_services(self, **kwargs):
        """
        Получение списка баз знаний в учетной записи (асинхронно).
        
        Args:
            offset (int): pagination offset (default 0)
            count (int): (int):pagination count (default 9999)
            sort_by (str): sort by 'id' or 'modified_at' (default is 'id')
            sort_order (str): sorting order 'asc' or 'desc' (default is 'asc')
        
        Returns:
            dict: Результат операции {"result": services_data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services
        """
        try: model = ServicesGetModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'get',
            '/core-api/crud/api/v1/services',
            params=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_services_xls(self, service_ids:list):
        """
        Экспортирует базу знаний в XLS формат (синхронно).
        
        Args:
            service_ids (list): Список ID баз знаний для экспорта
        
        Returns:
            dict or bytes: XLS файл с данными базой знаний или ошибки валидации
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_xls
        """
        service_ids = {'service_ids': service_ids}
        try: model = ServiceIdsModel(**service_ids)
        except ValidationError as e: return {"errors": e.errors()}
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            json['service_ids'] = ','.join(map(str,json['service_ids']))
        resp = self.sync_request(
            'get',
            '/core-api/crud/api/v1/services/xls',
            params=json
        ) 
        return resp
    
    async def async_get_services_xls(self, service_ids:list):
        """
        Экспортирует базу знаний в XLS формат (асинхронно).
        
        Args:
            service_ids (list): Список ID баз знаний для экспорта
        
        Returns:
            dict or bytes: XLS файл с данными базой знаний или ошибки валидации
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_xls
        """
        service_ids = {'service_ids': service_ids}
        try: model = ServiceIdsModel(**service_ids)
        except ValidationError as e: return {"errors": e.errors()}
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            json['service_ids'] = ','.join(map(str,json['service_ids']))
        resp = await self.async_request(
            'get',
            '/core-api/crud/api/v1/services/xls',
            params=json
        ) 
        return resp
    
    def sync_post_service_prediction_xls(self, service_ids: list, file_path: str):
        """
        Пакетное тестирование баз знаний (синхронно).
        
        Args:
            service_ids (list): Список ID баз знаний
            file_path (str): Путь к XLS файлу
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services_prediction_xls
        """
        file_name = file_path.split(os.path.sep)[-1]
        file_ext = file_name.split('.')[-1]
        if file_ext != 'xls': return {"result": None, "errors": "Файл должен быть формата .xls"}
        mime_type, _ = mimetypes.guess_type(file_path)
        data = MultipartEncoder(fields={'file': (file_name, open(file_path, 'rb'), mime_type), 'service_ids': service_ids})
        headers = self._default_headers.copy()
        headers['Content-Type'] = data.content_type
        self._default_headers.update(headers)
        resp = self.sync_request(
            'post',
            '/core-api/crud/api/v1/services/prediction/xls',
            data=data,
        ) 
        headers['Content-Type'] = 'application/json'
        self._default_headers.update(headers)
        return {"result": resp, "errors": None}
    
    async def async_post_service_prediction_xls(self, service_ids: list, file_path: str):
        """
        Пакетное тестирование баз знаний (асинхронно).
        
        Args:
            service_ids (list): Список ID баз знаний
            file_path (str): Путь к XLS файлу
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services_prediction_xls
        """
        file_name = file_path.split(os.path.sep)[-1]
        file_ext = file_name.split('.')[-1]
        if file_ext != 'xls': return {"result": None, "errors": "Файл должен быть формата .xls"}
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
        data.add_field('service_ids',service_ids)
        original_headers = self._default_headers.copy()
        headers = original_headers.copy()
        resp = await self.async_request(
            'post',
            '/core-api/crud/api/v1/services/prediction/xls',
            data=data,
            headers=headers 
        )
        return {"result": resp, "errors": None}
    
    def sync_get_services_prediction_xls(self, service_ids: list):
        """
        Получает результаты пакетного тестирования баз знаний в XLS формате (синхронно).
        
        Args:
            service_ids (list): Список ID баз знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_prediction_xls
        """
        service_ids = {'service_ids': service_ids}
        try: model = ServiceIdsModel(**service_ids)
        except ValidationError as e: return {"result": None, "errors": e.errors()}
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            json['service_ids'] = ','.join(map(str,json['service_ids']))
        resp = self.sync_request(
            'get',
            '/core-api/crud/api/v1/services/prediction/xls',
            params=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_services_prediction_xls(self, service_ids: list):
        """
        Получает результаты пакетного тестирования баз знаний в XLS формате (асинхронно).
        
        Args:
            service_ids (list): Список ID баз знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_prediction_xls
        """
        service_ids = {'service_ids': service_ids}
        try: model = ServiceIdsModel(**service_ids)
        except ValidationError as e: return {"result": None, "errors": e.errors()}
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
            json['service_ids'] = ','.join(map(str,json['service_ids']))
        resp = await self.async_request(
            'get',
            '/core-api/crud/api/v1/services/prediction/xls',
            params=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_services_prediction_status(self):
        """
        Получает статус пакетного тестирования баз знаний (синхронно).
        
        Returns:
            dict: Результат операции {"result": status_data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_prediction_status
        """
        resp = self.sync_request(
            'get',
            '/core-api/crud/api/v1/services/prediction/status',
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_services_prediction_status(self):
        """
        Получает статус пакетного тестирования баз знаний (асинхронно).
        
        Returns:
            dict: Результат операции {"result": status_data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_prediction_status
        """
        resp = await self.async_request(
            'get',
            '/core-api/crud/api/v1/services/prediction/status'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_service(self, service_id: int, **kwargs):
        """
        Получает информацию о базе знаний по ID (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            include_documents (int): Возвращать список документов (default - 0)
            include_suggested (int): DEPRECATED Включать в список документы со статусом рекомендации ((1 - да либо 0 - нет, default 0))
            limit_paraphrases (int): limit number of paraphrases per document (default - 500000)
            limit_history (int): limit document's history changelog size (default - 100)
        
        Returns:
            dict: Результат операции {"result": service_data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_prediction_status
        """
        try: model = ServiceGetModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}',
            params=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_service(self, service_id: int, **kwargs):
        """
        Получает информацию о базе знаний по ID (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            include_documents (int): Возвращать список документов (default - 0)
            include_suggested (int): DEPRECATED Включать в список документы со статусом рекомендации ((1 - да либо 0 - нет, default 0))
            limit_paraphrases (int): limit number of paraphrases per document (default - 500000)
            limit_history (int): limit document's history changelog size (default - 100)
        
        Returns:
            dict: Результат операции {"result": service_data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_prediction_status
        """
        try: model = ServiceGetModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}',
            params=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_update_service(self, service_id: int, **kwargs):
        """
        Обновляет информацию о базе знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            name (str): Название сервиса")
            preset (_LanguagePreset): Языковой пресет для обработки текста
            trainable (bool): Возможность обучения модели на данных сервиса
            max_trainable_score (float): Максимальный порог обучаемости модели (0.0-1.0)
            min_levenstein_distance (int): Минимальное расстояние Левенштейна для схожести фраз
            max_conf_mode_for_ident_phs (bool): Максимальный режим уверенности для идентичных фраз
            method (Literal["auto", "manual", "hybrid"]): Метод обработки запросов
            split_by_linguistic_conjunctions (bool): Разделение запросов по лингвистическим союзам
            enable_tokenization (bool): Включение токенизации текста
            query_length (_QueryLength): Длина обрабатываемых запросов
            inequal_lang_penalty (float): Штраф за разные языки в запросе и ответе (0.0-1.0)
            without_validation (bool): Создание сервиса без валидации данных
            with_layout_correction (bool): Коррекция layout'а текста
            ext (Dict[str, Any]): Дополнительные параметры сервиса в формате ключ-значение
            documents (List[DocumentModel]): Список документов сервиса
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
        
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/put_services__service_id_   
        """
        try: model = ServiceCreateModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'put',
            f'/core-api/crud/api/v1/services/{service_id}',
            json=json
        ) 
        return {"result": resp, "errors": None}
        
    async def async_update_service(self, service_id:int, **kwargs):
        """
        Обновляет информацию о базе знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            name (str): Название сервиса")
            preset (_LanguagePreset): Языковой пресет для обработки текста
            trainable (bool): Возможность обучения модели на данных сервиса
            max_trainable_score (float): Максимальный порог обучаемости модели (0.0-1.0)
            min_levenstein_distance (int): Минимальное расстояние Левенштейна для схожести фраз
            max_conf_mode_for_ident_phs (bool): Максимальный режим уверенности для идентичных фраз
            method (Literal["auto", "manual", "hybrid"]): Метод обработки запросов
            split_by_linguistic_conjunctions (bool): Разделение запросов по лингвистическим союзам
            enable_tokenization (bool): Включение токенизации текста
            query_length (_QueryLength): Длина обрабатываемых запросов
            inequal_lang_penalty (float): Штраф за разные языки в запросе и ответе (0.0-1.0)
            without_validation (bool): Создание сервиса без валидации данных
            with_layout_correction (bool): Коррекция layout'а текста
            ext (Dict[str, Any]): Дополнительные параметры сервиса в формате ключ-значение
            documents (List[DocumentModel]): Список документов сервиса
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
        
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/put_services__service_id_   
        """
        try: model = ServiceCreateModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'put',
            f'/core-api/crud/api/v1/services/{service_id}',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_delete_service(self, service_id: int):
        """
        Удаляет базу знаний (синхронно).
        
        Args:
            service_id (int): ID сервиса
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/delete_services__service_id_ 
        """
        resp = self.sync_request(
            'delete',
            f'/core-api/crud/api/v1/services/{service_id}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_delete_service(self, service_id: int):
        """
        Удаляет базу знаний (асинхронно).
        
        Args:
            service_id (int): ID сервиса
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/delete_services__service_id_ 
        """
        resp = await self.async_request(
            'delete',
            f'/core-api/crud/api/v1/services/{service_id}',
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_service_ext(self, service_id: int):
        """
        Получает хранилище произвольной служебной информации (userdate payload) (синхронно)
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": ext_data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__ext
        """
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/ext'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_service_ext(self, service_id: int):
        """
        Получает хранилище произвольной служебной информации (userdate payload) (асинхронно)
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": ext_data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__ext
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/ext',
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_service_documents(self, service_id: int, **kwargs):
        """
        Получает документы базы знаний с фильтрацией (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            offset (int): pagination offset (default 0)
            count (int):  pagination count (default 1000)
            sort_by (str): sort by 'id' or 'modified_at' (default is 'id')
            sort_order (str): sorting order 'asc' or 'desc' (default is 'asc')
            limit_paraphrases (int): limit number of paraphrases per document (default - 500000)
            limit_history (int): limit document's history changelog size (default - 100)
            include_suggested (int): DEPRECATED Включать в список документы со статусом рекомендации ((1 - да либо 0 - нет, default 0))
        
        Returns:
            dict: Результат операции {"result": documents_data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__documents 
        """
        try: model = ServiceDocumentsGetModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/documents',
            params=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_service_documents(self, service_id: int, **kwargs):
        """
        Получает документы базы знаний с фильтрацией (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            offset (int): pagination offset (default 0)
            count (int):  pagination count (default 1000)
            sort_by (str): sort by 'id' or 'modified_at' (default is 'id')
            sort_order (str): sorting order 'asc' or 'desc' (default is 'asc')
            limit_paraphrases (int): limit number of paraphrases per document (default - 500000)
            limit_history (int): limit document's history changelog size (default - 100)
            include_suggested (int): DEPRECATED Включать в список документы со статусом рекомендации ((1 - да либо 0 - нет, default 0))
        
        Returns:
            dict: Результат операции {"result": documents_data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__documents 
        """
        try: model = ServiceDocumentsGetModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/documents',
            params=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_post_service_document_xls(self, service_id: int, file_path: str, should_append: int = 1):
        """
        Загружает XLS файл с документами для базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            file_path (str): Путь к XLS файлу
            should_append (int): Добавить к существующим (1) или заменить (0)
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services__service_id__documents_xls
        """
        file_name = file_path.split(os.path.sep)[-1]
        file_ext = file_name.split('.')[-1]
        if file_ext != 'xls': return {"result": None, "errors": "Файл должен быть формата .xls"}
        if should_append not in [0, 1]: return {"result": None, "errors": "should_append должен быть или 0 или 1"}
        mime_type, _ = mimetypes.guess_type(file_path)
        data = MultipartEncoder(
            fields={
                'file': (file_name, open(file_path, 'rb'), mime_type), 
                'service_id': service_id, 
                "should_append": should_append
            }
        )
        headers = self._default_headers.copy()
        headers['Content-Type'] = data.content_type
        self._default_headers.update(headers)
        resp = self.sync_request(
            'post',
            '/core-api/crud/api/v1/services/documents/xls',
            data=data,
        ) 
        headers['Content-Type'] = 'application/json'
        self._default_headers.update(headers)
        return {"result": resp, "errors": None}
    
    async def async_post_service_document_xls(self, service_id: int, file_path: str, should_append: int = 1):
        """
        Загружает XLS файл с документами для базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            file_path (str): Путь к XLS файлу
            should_append (int): Добавить к существующим (1) или заменить (0)
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services__service_id__documents_xls
        """
        file_name = file_path.split(os.path.sep)[-1]
        file_ext = file_name.split('.')[-1]
        if file_ext != 'xls': return {"result": None, "errors": "Файл должен быть формата .xls"}
        if should_append not in [0, 1]: return {"result": None, "errors": "should_append должен быть или 0 или 1"}
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
        data.add_field('service_id', service_id)
        data.add_field('should_append', should_append)
        original_headers = self._default_headers.copy()
        headers = original_headers.copy()
        resp = await self.async_request(
            'post',
            '/core-api/crud/api/v1/services/documents/xls',
            data=data,
            headers=headers 
        )
        return {"result": resp, "errors": None}
    
    def sync_get_service_document_xls(self, service_id: int):
        """
        Получает XLS файл с документами базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            bytes: XLS файл с документами
        
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__documents_xls
        """
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/documents/xls'
        ) 
        return resp
    
    async def async_get_service_document_xls(self, service_id: int):
        """
        Получает XLS файл с документами базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            bytes: XLS файл с документами
        
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__documents_xls
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/documents/xls'
        ) 
        return resp
    
    def sync_service_document_xls_cancel(self, service_id: int):
        """
        Отменяет обработку XLS файла документов базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services__service_id__documents_xls_cancel
        """
        resp = self.sync_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/documents/xls/cancel'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_service_document_xls_cancel(self, service_id: int):
        """
        Отменяет обработку XLS файла документов базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services__service_id__documents_xls_cancel
        """
        resp = await self.async_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/documents/xls/cancel'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_service_document_xls_tags(self, service_id: int):
        """
        Получает теги документов базы знаний из XLS (синхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": tags_data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__documents_tags   
        """
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/documents/xls/tags'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_service_document_xls_tags(self, service_id: int):
        """
        Получает теги документов базы знаний из XLS (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": tags_data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__documents_tags   
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/documents/xls/tags'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_service_status(self, service_id: int):
        """
        Получает состояние базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": status_data, "errors": None}
            
        Link: 
           https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__status
        """
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/status'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_service_status(self, service_id: int):
        """
        Получает состояние базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": status_data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__status
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/status'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_service_publish_action(self, service_id: int):
        """
        Публикует базу знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services__service_id__actions_publish
        """
        resp = self.sync_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/actions/publish'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_service_publish_action(self, service_id: int):
        """
        Публикует базу знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services__service_id__actions_publish
        """
        resp = await self.async_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/actions/publish'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_service_stop_action(self, service_id: int):
        """
        Останавливает базу знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services__service_id__actions_stop
        """
        resp = self.sync_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/actions/stop'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_service_stop_action(self, service_id: int):
        """
        Останавливает базу знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services__service_id__actions_stop
        """
        resp = await self.async_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/actions/stop'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_service_clear_action(self, service_id: int):
        """
        Очищает базу знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services__service_id__actions_clear
        """
        resp = self.sync_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/actions/clear'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_service_clear_action(self, service_id: int):
        """
        Очищает базу знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services__service_id__actions_clear
        """
        resp = await self.async_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/actions/clear'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_service_create_token(self, service_id: int):
        """
        Создает токен для базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services__service_id__tokens
        """
        resp = self.sync_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/tokens'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_service_create_token(self, service_id: int):
        """
        Создает токен для базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services__service_id__tokens
        """
        resp = await self.async_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/tokens'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_service_get_token(self, service_id: int):
        """
        Получает токены базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__tokens
        """
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/tokens'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_service_get_token(self, service_id: int):
        """
        Получает токены базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__tokens
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/tokens'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_service_delete_token(self, service_id: int, token: str):
        """
        Удаляет токен базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            token (str): Токен для удаления
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/delete_services__service_id__tokens__token_
        """
        resp = self.sync_request(
            'delete',
            f'/core-api/crud/api/v1/services/{service_id}/tokens/{token}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_service_delete_token(self, service_id: int, token: str):
        """
        Удаляет токен базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            token (str): Токен для удаления
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/delete_services__service_id__tokens__token_
        """
        resp = await self.async_request(
            'delete',
            f'/core-api/crud/api/v1/services/{service_id}/tokens/{token}'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_service_snapshot_resore(self, service_id: int, file_path: str):
        """
        Восстанавливает базу знаний из снапшота (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            file_path (str): Путь к файлу снапшота
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services__service_id__snapshot
        """
        file_name = file_path.split(os.path.sep)[-1]
        mime_type, _ = mimetypes.guess_type(file_path)
        data = MultipartEncoder(fields={'snapshot_file': (file_name, open(file_path, 'rb'), mime_type)})
        headers = self._default_headers.copy()
        headers['Content-Type'] = data.content_type
        self._default_headers.update(headers)
        resp = self.sync_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/snapshot',
            data=data,
        ) 
        headers['Content-Type'] = 'application/json'
        self._default_headers.update(headers)
        return {"result": resp, "errors": None}
    
    async def async_service_snapshot_resore(self, service_id: int, file_path: str):
        """
        Восстанавливает базу знаний из снапшота (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            file_path (str): Путь к файлу снапшота
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services__service_id__snapshot
        """
        file_name = file_path.split(os.path.sep)[-1]
        mime_type, _ = mimetypes.guess_type(file_path)
        async with aiofiles.open(file_path, 'rb') as file:
            file_data = await file.read()
        data = FormData()
        data.add_field(
            'snapshot_file',
            file_data,
            filename=file_name,
            content_type=mime_type
        )
        original_headers = self._default_headers.copy()
        headers = original_headers.copy()
        resp = await self.async_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/snapshot',
            data=data,
            headers=headers 
        )
        return {"result": resp, "errors": None}
    
    def sync_service_get_snapshot(self, service_id: int):
        """
        Получает снапшот базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            bytes: Файл снапшота
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__snapshot
        """
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/snapshot'
        ) 
        return resp
    
    async def async_service_get_snapshot(self, service_id: int):
        """
        Получает снапшот базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            bytes: Файл снапшота
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__snapshot
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/snapshot'
        ) 
        return resp
    
    def sync_get_service_suggested_documents(self, service_id: int, **kwargs):
        """
        Получает рекомендации документов для базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            from (str): начало интервала ISO timestamp по умолчанию - 1 день назад
            to (str): конец интервала ISO timestamp по умолчанию - сегодня
            limit (int): лимит вывода
            offset (int): pagination offset (default 0)
            count (int): pagination count (default 9999) (alias for limit)
            sort_by (str): sort by 'id' or 'modified_at' (default is 'id')
            sort_order (str): sorting order 'asc' or 'desc' (default is 'asc')

        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__suggested_documents
        """
        try: model = SuggestedDocumentsParamsModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/suggested/documents',
            params=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_service_suggested_documents(self, service_id: int, **kwargs):
        """
        Получает рекомендации документов для базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            from (str): начало интервала ISO timestamp по умолчанию - 1 день назад
            to (str): конец интервала ISO timestamp по умолчанию - сегодня
            limit (int): лимит вывода
            offset (int): pagination offset (default 0)
            count (int): pagination count (default 9999) (alias for limit)
            sort_by (str): sort by 'id' or 'modified_at' (default is 'id')
            sort_order (str): sorting order 'asc' or 'desc' (default is 'asc')

        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__suggested_documents
        """
        try: model = SuggestedDocumentsParamsModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/suggested/documents',
            params=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_service_suggested_documents_count(self, service_id: int, **kwargs):
        """
        Получает количество рекомендаций документов для базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            from (str): начало интервала ISO timestamp по умолчанию - 1 день назад
            to (str): конец интервала ISO timestamp по умолчанию - сегодня
            limit (int): лимит вывода
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__suggested_documents_count
        """
        try: model = SuggestedDocumentsCountParamsModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/suggested/documents/count',
            params=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_service_suggested_documents_count(self, service_id: int, **kwargs):
        """
        Получает количество рекомендаций документов для базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            from (str): начало интервала ISO timestamp по умолчанию - 1 день назад
            to (str): конец интервала ISO timestamp по умолчанию - сегодня
            limit (int): лимит вывода
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__suggested_documents_count
        """
        try: model = SuggestedDocumentsCountParamsModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/suggested/documents/count',
            params=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_service_suggested_paraphrases(self, service_id: int, **kwargs):
        """
        Получает рекомендации формулировок для базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            from (str): начало интервала ISO timestamp по умолчанию - 1 день назад
            to (str): конец интервала ISO timestamp по умолчанию - сегодня
            limit (int): лимит вывода
            offset (int): pagination offset (default 0)
            count (int): pagination count (default 9999) (alias for limit)
            sort_by (str): sort by 'id' or 'modified_at' (default is 'id')
            sort_order (str): sorting order 'asc' or 'desc' (default is 'asc')

        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__suggested_paraphrases
        """
        try: model = SuggestedParaphrasesParamsModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/suggested/paraphrases',
            params=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_service_suggested_paraphrases(self, service_id: int, **kwargs):
        """
        Получает рекомендации формулировок для базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            from (str): начало интервала ISO timestamp по умолчанию - 1 день назад
            to (str): конец интервала ISO timestamp по умолчанию - сегодня
            limit (int): лимит вывода
            offset (int): pagination offset (default 0)
            count (int): pagination count (default 9999) (alias for limit)
            sort_by (str): sort by 'id' or 'modified_at' (default is 'id')
            sort_order (str): sorting order 'asc' or 'desc' (default is 'asc')

        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__suggested_paraphrases
        """
        try: model = SuggestedParaphrasesParamsModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/suggested/paraphrases',
            params=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_service_suggested_paraphrases_count(self, service_id: int, **kwargs):
        """
        Получает количество рекомендаций формулировок для базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            from (str): начало интервала ISO timestamp по умолчанию - 1 день назад
            to (str): конец интервала ISO timestamp по умолчанию - сегодня
            limit (int): лимит вывода
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__suggested_paraphrases_count
        """
        try: model = SuggestedParaphrasesCountParamsModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/suggested/paraphrases/count',
            params=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_service_suggested_paraphrases_count(self, service_id: int, **kwargs):
        """
        Получает количество рекомендаций формулировок для базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            from (str): начало интервала ISO timestamp по умолчанию - 1 день назад
            to (str): конец интервала ISO timestamp по умолчанию - сегодня
            limit (int): лимит вывода
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__suggested_paraphrases_count
        """
        try: model = SuggestedParaphrasesCountParamsModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/suggested/paraphrases/count',
            params=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_service_suggested_documents_validate(self, service_id: int, **kwargs):
        """
        Проверяет рекомендации документов на дубликаты, вызывается асинхронная зачада на сервере (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            from_time (str): начало интервала ISO timestamp
            to (str): конец интервала ISO timestamp
            document_ids List[int]: список идентификаторов документов для проверки
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services__service_id__suggested_documents_validate
        """
        try: model = SuggestedDocumentsValidateModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/suggested/documents/validate',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_service_suggested_documents_validate(self, service_id: int, **kwargs):
        """
        Проверяет рекомендации документов на дубликаты, вызывается асинхронная зачада на сервере (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            from_time (str): начало интервала ISO timestamp
            to (str): конец интервала ISO timestamp
            document_ids List[int]: список идентификаторов документов для проверки
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services__service_id__suggested_documents_validate
        """
        try: model = SuggestedDocumentsValidateModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/suggested/documents/validate',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_service_presets(self):
        """
        Получает список языков (синхронно).
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_presets
        """
        resp = self.sync_request(
            'get',
            '/core-api/crud/api/v1/services/presets'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_service_presets(self):
        """
        Получает список языков (асинхронно).
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_presets
        """
        resp = await self.async_request(
            'get',
            '/core-api/crud/api/v1/services/presets'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_service_documents_languages(self):
        """
        Получает список языков для документа с языковым контентом баз знаний (синхронно).
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_documents_languages
        """
        resp = self.sync_request(
            'get',
            '/core-api/crud/api/v1/services/documents/languages'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_service_documents_languages(self):
        """
        Получает список языков для документа с языковым контентом баз знаний (асинхронно).
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_documents_languages
        """
        resp = await self.async_request(
            'get',
            '/core-api/crud/api/v1/services/documents/languages'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_search_document_content(self, **kwargs):
        """
        Ищет по документам у всех или выбранных сервисов базы знаний по содержимому (синхронно).
        
        Args:
            query (str): поисковой запрос
            find_by [List[str]]: поля по которым искать (по всем если не указано) [answer, question, name, scenario]
            offset (int): pagination offset (default 0)
            count (int): pagination count (default 100)
            sort_by (str): sort by 'id' or 'modified_at' (default is 'modified_at')
            sort_order Literal["asc", "desc"]:sorting order 'asc' or 'desc' (default is 'desc')
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_search_documents_content
        """
        try: model = SearchDocumentsContentModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'get',
            '/core-api/crud/api/v1/services/search/documents/content',
            params=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_search_document_content(self, **kwargs):
        """
        Ищет по документам у всех или выбранных сервисов базы знаний по содержимому (асинхронно).
        
        Args:
            query (str): поисковой запрос
            find_by [List[str]]: поля по которым искать (по всем если не указано) [answer, question, name, scenario]
            offset (int): pagination offset (default 0)
            count (int): pagination count (default 100)
            sort_by (str): sort by 'id' or 'modified_at' (default is 'modified_at')
            sort_order Literal["asc", "desc"]:sorting order 'asc' or 'desc' (default is 'desc')
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_search_documents_content
        """
        try: model = SearchDocumentsContentModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'get',
            '/core-api/crud/api/v1/services/search/documents/content',
            params=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_post_search_document_content(self, **kwargs):
        """
        Ищет по документам у всех или выбранных сервисов базы знаний по содержимому (синхронно).
        
        Args:
            query (str): поисковой запрос
            find_by ([List[str]]): поля по которым искать (по всем если не указано) [answer, question, name, scenario]
            offset (int): pagination offset (default 0)
            count (int):pagination count (default 100)
            sort_by (str): sort by 'id' or 'modified_at' (default is 'modified_at')
            sort_order Literal["asc", "desc"]: sorting order 'asc' or 'desc' (default is 'desc')
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services_search_documents_content
        """
        try: model = SearchDocumentsContentModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'post',
            '/core-api/crud/api/v1/services/search/documents/content',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_post_search_document_content(self, **kwargs):
        """
        Ищет по документам у всех или выбранных сервисов базы знаний по содержимому (асинхронно).
        
        Args:
            query (str): поисковой запрос
            find_by ([List[str]]): поля по которым искать (по всем если не указано) [answer, question, name, scenario]
            offset (int): pagination offset (default 0)
            count (int):pagination count (default 100)
            sort_by (str): sort by 'id' or 'modified_at' (default is 'modified_at')
            sort_order Literal["asc", "desc"]: sorting order 'asc' or 'desc' (default is 'desc')
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services_search_documents_content
        """
        try: model = SearchDocumentsContentModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'post',
            '/core-api/crud/api/v1/services/search/documents/content',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_services_validations(self, **kwargs):
        """
        Запускает задачу на проверку баз знаний на наличие дубликатов (синхронно).
        
        Args:
            **kwargs: Параметры валидации (service_ids, min_confidence, min_answer_confidence)
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services_validations
        """
        try: model = ServicesValidationsModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'post',
            '/core-api/crud/api/v1/services/validations',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_services_validations(self, **kwargs):
        """
        Запускает задачу на проверку баз знаний на наличие дубликатов (асинхронно).
        
        Args:
            **kwargs: Параметры валидации (service_ids, min_confidence, min_answer_confidence)
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services_validations
        """
        try: model = ServicesValidationsModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'post',
            '/core-api/crud/api/v1/services/validations',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_services_validations_xls(self):
        """
        Получает результаты проверки баз знаний на дубликаты в XLS формате (синхронно).
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_validations
        """
        resp = self.sync_request(
            'get',
            '/core-api/crud/api/v1/services/validations'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_services_validations_xls(self):
        """
        Получает результаты проверки баз знаний на дубликаты в XLS формате (асинхронно).
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_validations
        """
        resp = await self.async_request(
            'get',
            '/core-api/crud/api/v1/services/validations'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_services_validations_status(self):
        """
        Получает статус проверки баз знаний на дубликаты (синхронно).
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_validations_status
        """
        resp = self.sync_request(
            'get',
            '/core-api/crud/api/v1/services/validations/status'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_services_validations_status(self):
        """
        Получает статус проверки баз знаний на дубликаты (асинхронно).
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_validations_status
        """
        resp = await self.async_request(
            'get',
            '/core-api/crud/api/v1/services/validations/status'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_post_service_attachment(self, service_id: int, file_path: str):
        """
        Загружает вложение в базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            file_path (str): Путь к файлу вложения
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services__service_id__attachments
        """
        file_name = file_path.split(os.path.sep)[-1]
        mime_type, _ = mimetypes.guess_type(file_path)
        data = MultipartEncoder(fields={'attachment_file': (file_name, open(file_path, 'rb'), mime_type)})
        headers = self._default_headers.copy()
        headers['Content-Type'] = data.content_type
        self._default_headers.update(headers)
        resp = self.sync_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/attachments',
            data=data,
        ) 
        headers['Content-Type'] = 'application/json'
        self._default_headers.update(headers)
        return {"result": resp, "errors": None}
    
    async def async_post_service_attachment(self, service_id: int, file_path: str):
        """
        Загружает вложение в базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            file_path (str): Путь к файлу вложения
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services__service_id__attachments
        """
        file_name = file_path.split(os.path.sep)[-1]
        mime_type, _ = mimetypes.guess_type(file_path)
        async with aiofiles.open(file_path, 'rb') as file:
            file_data = await file.read()
        data = FormData()
        data.add_field(
            'attachment_file',
            file_data,
            filename=file_name,
            content_type=mime_type
        )
        original_headers = self._default_headers.copy()
        headers = original_headers.copy()
        resp = await self.async_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/attachments',
            data=data,
            headers=headers 
        )
        return {"result": resp, "errors": None}
    
    def sync_get_service_attachments(self, service_id: int):
        """
        Получает список вложений базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__attachments
        """
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/attachments'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_service_attachmens(self, service_id: int):
        """
        Получает список вложений базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__attachments
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/attachments'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_service_attachment_info(self, service_id: int, attachment_id : int):
        """
        Получает информацию о вложении базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            attachment_id (int): ID вложения
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__attachments__attachment_id_
        """
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/attachments/{attachment_id}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_service_attachment_info(self, service_id: int, attachment_id : int):
        """
        Получает информацию о вложении базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            attachment_id (int): ID вложения
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__attachments__attachment_id_
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/attachments/{attachment_id}'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_update_service_attachment_info(self, service_id: int, attachment_id : int, **kwargs):
        """
        Обновляет информацию о вложении базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            attachment_id (int): ID вложения
            name (str): название вложения
            description (str): описание вложения
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/put_services__service_id__attachments__attachment_id_
        """
        try: model = UpdateServiceAttachmentModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'put',
            f'/core-api/crud/api/v1/services/{service_id}/attachments/{attachment_id}',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_update_service_attachment_info(self, service_id: int, attachment_id : int, **kwargs):
        """
        Обновляет информацию о вложении базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            attachment_id (int): ID вложения
            name (str): название вложения
            description (str): описание вложения
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/put_services__service_id__attachments__attachment_id_
        """
        try: model = UpdateServiceAttachmentModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'put',
            f'/core-api/crud/api/v1/services/{service_id}/attachments/{attachment_id}',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_delete_service_attachment(self, service_id: int, attachment_id : int):
        """
        Удаляет вложение базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            attachment_id (int): ID вложения
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/delete_services__service_id__attachments__attachment_id_
        """
        resp = self.sync_request(
            'delete',
            f'/core-api/crud/api/v1/services/{service_id}/attachments/{attachment_id}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_delete_service_attachment(self, service_id: int, attachment_id : int):
        """
        Удаляет вложение базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            attachment_id (int): ID вложения
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/delete_services__service_id__attachments__attachment_id_
        """
        resp = await self.async_request(
            'delete',
            f'/core-api/crud/api/v1/services/{service_id}/attachments/{attachment_id}'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_service_attachment_file(self, service_id: int, attachment_id : int):
        """
        Получает файл вложения базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            attachment_id (int): ID вложения
        
        Returns:
            bytes: Файл вложения
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__attachments__attachment_id__file
        """
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/attachments/{attachment_id}/file'
        ) 
        return resp
    
    async def async_get_service_attachment_file(self, service_id: int, attachment_id : int):
        """
        Получает файл вложения базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            attachment_id (int): ID вложения
        
        Returns:
            bytes: Файл вложения
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__attachments__attachment_id__file
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/attachments/{attachment_id}/file'
        ) 
        return resp
    
    def sync_get_service_datasource_status(self, service_id: int, datasource_id : int):
        """
        Получает статус индексации источника данных (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            datasource_id (int): ID источника данных
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__datasources__datasource_id__status
        """
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/datasources/{datasource_id}/status'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_service_datasource_status(self, service_id: int, datasource_id : int):
        """
        Получает статус индексации источника данных (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            datasource_id (int): ID источника данных
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__datasources__datasource_id__status
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/datasources/{datasource_id}/status'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_service_datasource_index(self, service_id: int, datasource_id : int, timestamp_format: str = None):
        """
        Получает индексированные элементы из источника данных(синхронно).
        
        Args:
            service_id (int): ID базы знаний
            datasource_id (int): ID источника данных
            timestamp_format (str, optional): Формат временной метки
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__datasources__datasource_id__index
        """
        params = None
        if timestamp_format: params = {'timestamp_format': timestamp_format}
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/datasources/{datasource_id}/index',
            params=params
        ) 
        return {"result": resp, "errors": None}
    
    async def async_service_datasource_index(self, service_id: int, datasource_id : int, timestamp_format: str = None):
        """
        Получает индексированные элементы из источника данных(асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            datasource_id (int): ID источника данных
            timestamp_format (str, optional): Формат временной метки
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__datasources__datasource_id__index
        """
        params = None
        if timestamp_format: params = {'timestamp_format': timestamp_format}
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/datasources/{datasource_id}/index',
            params=params
        ) 
        return {"result": resp, "errors": None}
    
    def sync_service_promt(self, service_id: int):
        """
        Получает структуру промпта (синхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__prompt
        """
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/prompt'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_service_promt(self, service_id: int):
        """
        Получает структуру промпта (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__prompt
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/prompt'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_update_service_prompt(self, service_id: int, **kwargs):
        """
        Обновляет структуру промпта (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            heading Optional[str]: заголовок промпта
            guidelines Optional[List[_GuidelineItem]]: список руководств
            qa Optional[List[_QAItem]]: список вопросов-ответов
            enabled_parts _EnabledParts: настройки включенных частей промпта
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/put_services__service_id__prompt
        """
        try: model = ServicePromptModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'put',
            f'/core-api/crud/api/v1/services/{service_id}/prompt',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_update_service_prompt(self, service_id: int, **kwargs):
        """
        Обновляет структуру промпта (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            heading Optional[str]: заголовок промпта
            guidelines Optional[List[_GuidelineItem]]: список руководств
            qa Optional[List[_QAItem]]: список вопросов-ответов
            enabled_parts _EnabledParts: настройки включенных частей промпта
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/put_services__service_id__prompt
        """
        try: model = ServicePromptModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'put',
            f'/core-api/crud/api/v1/services/{service_id}/prompt',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_partial_update_service_prompt(self, service_id: int, **kwargs):
        """
        Частично обновляет структуру промпта (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            heading Optional[str]: заголовок промпта
            guidelines Optional[List[_GuidelineItem]]: список руководств
            qa Optional[List[_QAItem]]: список вопросов-ответов
            enabled_parts _EnabledParts: настройки включенных частей промпта
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/patch_services__service_id__prompt
        """
        try: model = ServicePromptModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'patch',
            f'/core-api/crud/api/v1/services/{service_id}/prompt',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_partial_update_service_prompt(self, service_id: int, **kwargs):
        """
        Частично обновляет структуру промпта (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            heading Optional[str]: заголовок промпта
            guidelines Optional[List[_GuidelineItem]]: список руководств
            qa Optional[List[_QAItem]]: список вопросов-ответов
            enabled_parts _EnabledParts: настройки включенных частей промпта
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/patch_services__service_id__prompt
        """
        try: model = ServicePromptModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'patch',
            f'/core-api/crud/api/v1/services/{service_id}/prompt',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_service_promt_qa(self, service_id: int):
        """
        Получает QA в промте (синхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__prompt_qa
        """
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/prompt/qa'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_service_promt_qa(self, service_id: int):
        """
        Получает QA в промте (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__prompt_qa
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/prompt/qa'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_create_service_prompt_qa(self, service_id: int, **kwargs):
        """
        Создает новое QA в промпт (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            id (int): идентификатор QA (должен быть 0 для создания нового)
            type (_QAType): тип QA - 'standard' или 'clarifying'
            question (str): текст вопроса
            answer (str): текст ответа
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services__service_id__prompt_qa
        """
        try: model = ServicePromptQAModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/prompt/qa',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_create_service_prompt_qa(self, service_id: int, **kwargs):
        """
        Создает новое QA в промпт (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            id (int): идентификатор QA (должен быть 0 для создания нового)
            type (_QAType): тип QA - 'standard' или 'clarifying'
            question (str): текст вопроса
            answer (str): текст ответа
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/post_services__service_id__prompt_qa
        """
        try: model = ServicePromptQAModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/prompt/qa',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_update_service_prompt_qa(self, service_id: int, qa_id: int, **kwargs):
        """
        Обновляет элемент из списка PromptQA  (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            qa_id (int): ID вопроса-ответа
            heading (Optional[str]): заголовок промпта
            guidelines (Optional[List[_GuidelineItem]]): список руководств
            qa (Optional[List[_QAItem]]): список вопросов-ответов
            enabled_parts (_EnabledParts): настройки включенных частей промпта
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/patch_services__service_id__prompt_qa__qa_id_
        """
        try: model = ServicePromptQAModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'patch',
            f'/core-api/crud/api/v1/services/{service_id}/prompt/qa/{qa_id}',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_update_service_prompt_qa(self, service_id: int, qa_id: int, **kwargs):
        """
        Обновляет элемент из списка PromptQA  (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            qa_id (int): ID вопроса-ответа
            heading (Optional[str]): заголовок промпта
            guidelines (Optional[List[_GuidelineItem]]): список руководств
            qa (Optional[List[_QAItem]]): список вопросов-ответов
            enabled_parts (_EnabledParts): настройки включенных частей промпта
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/patch_services__service_id__prompt_qa__qa_id_
        """
        try: model = ServicePromptQAModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'patch',
            f'/core-api/crud/api/v1/services/{service_id}/prompt/qa/{qa_id}',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_delete_service_prompt_qa(self, service_id: int, qa_id: int):
        """
        Удаляет элемент из списка PromptQA  (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            qa_id (int): ID вопроса-ответа
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/delete_services__service_id__prompt_qa__qa_id_
        """
        resp = self.sync_request(
            'delete',
            f'/core-api/crud/api/v1/services/{service_id}/prompt/qa/{qa_id}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_delete_service_prompt_qa(self, service_id: int, qa_id: int):
        """
        Удаляет элемент из списка PromptQA  (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            qa_id (int): ID вопроса-ответа
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/delete_services__service_id__prompt_qa__qa_id_
        """
        resp = await self.async_request(
            'delete',
            f'/core-api/crud/api/v1/services/{service_id}/prompt/qa/{qa_id}'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_create_document(self, **kwargs):
        """
        Создает документ в базе знаний (синхронно).
        
        Args:
            service_id (int): ID сервиса, к которому принадлежит документ")
            name (str): название документа")
            question (str): основной вопрос документа
            answer (str): = ответ на вопрос
            status (_DocumentStatus): статус документа
            ext (Optional[Dict[str, Any]]): дополнительные данные в формате JSON
            paraphrases: (Optional[List[_ParaphraseItem]]): список парафразов (вариаций вопроса)
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/post_documents
        """
        try: model = CreateDocumentRequest(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'post',
            f'/core-api/crud/api/v1/documents',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_create_document(self, **kwargs):
        """
        Создает документ в базе знаний (асинхронно).
        
        Args:
            service_id (int): ID сервиса, к которому принадлежит документ")
            name (str): название документа")
            question (str): основной вопрос документа
            answer (str): = ответ на вопрос
            status (_DocumentStatus): статус документа
            ext (Optional[Dict[str, Any]]): дополнительные данные в формате JSON
            paraphrases: (Optional[List[_ParaphraseItem]]): список парафразов (вариаций вопроса)
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/post_documents
        """
        try: model = CreateDocumentRequest(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'post',
            f'/core-api/crud/api/v1/documents',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_document(self, document_id : int, limit_paraphrases: int = 500000, limit_history: int = 100):
        """
        Чтение документе (синхронно).
        
        Args:
            document_id (int): ID документа
            limit_paraphrases (int): Лимит парафразов (по умолчанию 500000)
            limit_history (int): Лимит истории (по умолчанию 100)
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/get_documents__document_id_
        """
        params = {}
        if limit_history: params['limit_history'] = limit_history
        if limit_paraphrases: params['limit_paraphrases'] = limit_paraphrases
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/documents/{document_id}',
            params=params
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_document(self, document_id : int, limit_paraphrases: int = 500000, limit_history: int = 100):
        """
        Чтение документе (асинхронно).
        
        Args:
            document_id (int): ID документа
            limit_paraphrases (int): Лимит парафразов (по умолчанию 500000)
            limit_history (int): Лимит истории (по умолчанию 100)
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/get_documents__document_id_
        """
        params = {}
        if limit_history: params['limit_history'] = limit_history
        if limit_paraphrases: params['limit_paraphrases'] = limit_paraphrases
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/documents/{document_id}',
            params=params
        ) 
        return {"result": resp, "errors": None}
    
    def sync_update_document(self, document_id: int, **kwargs):
        """
        Обновляет документ (синхронно).
        
        Args:
            document_id (int): ID документа
            service_id (int): ID сервиса, к которому принадлежит документ
            name (str): название документа
            question (str): основной вопрос документа
            answer (str): ответ на вопрос
            status (_DocumentStatus): статус документа
            ext (Optional[Dict[str, Any]]): дополнительные данные в формате JSON
            paraphrases (Optional[List[_ParaphraseItem]]): список парафразов (вариаций вопроса)
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/put_documents__document_id_
        """
        try: model = UpdateDocumentRequest(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'put',
            f'/core-api/crud/api/v1/documents/{document_id}',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_update_document(self, document_id: int, **kwargs):
        """
        Обновляет документ (асинхронно).
        
        Args:
            document_id (int): ID документа
            service_id (int): ID сервиса, к которому принадлежит документ
            name (str): название документа
            question (str): основной вопрос документа
            answer (str): ответ на вопрос
            status (_DocumentStatus): статус документа
            ext (Optional[Dict[str, Any]]): дополнительные данные в формате JSON
            paraphrases (Optional[List[_ParaphraseItem]]): список парафразов (вариаций вопроса)
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/put_documents__document_id_
        """
        try: model = UpdateDocumentRequest(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'put',
            f'/core-api/crud/api/v1/documents/{document_id}',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_delete_document(self, document_id : int):
        """
        Удаляет документ (синхронно).
        
        Args:
            document_id (int): ID документа
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/delete_documents__document_id_
        """
        resp = self.sync_request(
            'delete',
            f'/core-api/crud/api/v1/documents/{document_id}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_delete_document(self, document_id : int):
        """
        Удаляет документ (асинхронно).
        
        Args:
            document_id (int): ID документа
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/delete_documents__document_id_
        """
        resp = await self.async_request(
            'delete',
            f'/core-api/crud/api/v1/documents/{document_id}'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_document_accept_action(self, document_id : int):
        """
        Прием рекамендаций документа (синхронно).
        
        Args:
            document_id (int): ID документа
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/post_documents__document_id__actions_accept
        """
        resp = self.sync_request(
            'post',
            f'/core-api/crud/api/v1/documents/{document_id}/actions/accept'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_document_accept_action(self, document_id : int):
        """
        Прием рекамендаций документа (асинхронно).
        
        Args:
            document_id (int): ID документа
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/post_documents__document_id__actions_accept
        """
        resp = await self.async_request(
            'post',
            f'/core-api/crud/api/v1/documents/{document_id}/actions/accept'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_post_document_attachment(self, document_id: int, file_path: str):
        """
        Загружает вложение для документа (синхронно).
        
        Args:
            document_id (int): ID документа
            file_path (str): Путь к файлу вложения
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/post_documents__document_id__attachments
        """
        file_name = file_path.split(os.path.sep)[-1]
        mime_type, _ = mimetypes.guess_type(file_path)
        data = MultipartEncoder(fields={'attachment_file': (file_name, open(file_path, 'rb'), mime_type)})
        headers = self._default_headers.copy()
        headers['Content-Type'] = data.content_type
        self._default_headers.update(headers)
        resp = self.sync_request(
            'post',
            f'/core-api/crud/api/v1/documents/{document_id}/attachments',
            data=data,
        ) 
        headers['Content-Type'] = 'application/json'
        self._default_headers.update(headers)
        return {"result": resp, "errors": None}
    
    async def async_post_document_attachment(self, document_id: int, file_path: str):
        """
        Загружает вложение для документа (асинхронно).
        
        Args:
            document_id (int): ID документа
            file_path (str): Путь к файлу вложения
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/post_documents__document_id__attachments
        """
        file_name = file_path.split(os.path.sep)[-1]
        mime_type, _ = mimetypes.guess_type(file_path)
        async with aiofiles.open(file_path, 'rb') as file:
            file_data = await file.read()
        data = FormData()
        data.add_field(
            'attachment_file',
            file_data,
            filename=file_name,
            content_type=mime_type
        )
        original_headers = self._default_headers.copy()
        headers = original_headers.copy()
        resp = await self.async_request(
            'post',
            f'/core-api/crud/api/v1/documents/{document_id}/attachments',
            data=data,
            headers=headers 
        )
        return {"result": resp, "errors": None}
    
    def sync_get_document_attachments(self, document_id: int):
        """
        Получает список вложений документа (синхронно).
        
        Args:
            document_id (int): ID документа
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/get_documents__document_id__attachments
        """
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/documents/{document_id}/attachments'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_document_attachments(self, document_id: int):
        """
        Получает список вложений документа (асинхронно).
        
        Args:
            document_id (int): ID документа
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/get_documents__document_id__attachments
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/documents/{document_id}/attachments'
        )
        return {"result": resp, "errors": None}
    
    def sync_get_document_attachment_info(self, document_id: int, attachment_id: int):
        """
        Получает информацию о вложении документа (синхронно).
        
        Args:
            document_id (int): ID документа
            attachment_id (int): ID вложения
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/get_documents__document_id__attachments__attachment_id_
        """
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/documents/{document_id}/attachments/{attachment_id}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_document_attachment_info(self, document_id: int, attachment_id: int):
        """
        Получает информацию о вложении документа (асинхронно).
        
        Args:
            document_id (int): ID документа
            attachment_id (int): ID вложения
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/get_documents__document_id__attachments__attachment_id_
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/documents/{document_id}/attachments/{attachment_id}'
        )
        return {"result": resp, "errors": None}
    
    def sync_update_document_attachment_info(self, document_id: int, attachment_id: int, **kwargs):
        """
        Обновляет метаинформацию о вложении документа (синхронно).
        
        Args:
            document_id (int): ID документа
            attachment_id (int): ID вложения
            **kwargs: Поля для обновления (name, description)
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/put_documents__document_id__attachments__attachment_id_
        """
        try: model = DocumentAttachmentModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'put',
            f'/core-api/crud/api/v1/documents/{document_id}/attachments/{attachment_id}',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_update_document_attachment_info(self, document_id: int, attachment_id: int, **kwargs):
        """
        Обновляет метаинформацию о вложении документа (асинхронно).
        
        Args:
            document_id (int): ID документа
            attachment_id (int): ID вложения
            **kwargs: Поля для обновления (name, description)
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/put_documents__document_id__attachments__attachment_id_
        """
        try: model = DocumentAttachmentModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'put',
            f'/core-api/crud/api/v1/documents/{document_id}/attachments/{attachment_id}',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_delete_attachment(self, document_id: int, attachment_id: int):
        """
        Удаляет вложение документа (синхронно).
        
        Args:
            document_id (int): ID документа
            attachment_id (int): ID вложения
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/delete_documents__document_id__attachments__attachment_id_
        """
        resp = self.sync_request(
            'delete',
            f'/core-api/crud/api/v1/documents/{document_id}/attachments/{attachment_id}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_delete_attachment(self, document_id: int, attachment_id: int):
        """
        Удаляет вложение документа (асинхронно).
        
        Args:
            document_id (int): ID документа
            attachment_id (int): ID вложения
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/delete_documents__document_id__attachments__attachment_id_
        """
        resp = await self.async_request(
            'delete',
            f'/core-api/crud/api/v1/documents/{document_id}/attachments/{attachment_id}'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_attachment_file(self, document_id: int, attachment_id: int):
        """
        Получает файл вложения документа (синхронно).
        
        Args:
            document_id (int): ID документа
            attachment_id (int): ID вложения
        
        Returns:
            bytes: Файл вложения
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/get_documents__document_id__attachments__attachment_id__file
        """
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/documents/{document_id}/attachments/{attachment_id}/file'
        ) 
        return resp
    
    async def async_get_attachment_file(self, document_id: int, attachment_id: int):
        """
        Получает файл вложения документа (асинхронно).
        
        Args:
            document_id (int): ID документа
            attachment_id (int): ID вложения
        
        Returns:
            bytes: Файл вложения
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/get_documents__document_id__attachments__attachment_id__file
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/documents/{document_id}/attachments/{attachment_id}/file'
        ) 
        return resp
    
    def sync_create_document_context(self, document_id: int, **kwargs):
        """
        Добавляет контекст для документа (синхронно).
        
        Args:
            document_id (int): ID документа
            document_id (int) ID документа
            name (str) название документа
            question (str) вопрос документа
            answer (str) ответ документа
            status (_DocumentStatus) статус документа
            modified_at (str) время изменения (ISO timestamp)
            expired_at (Optional[str]) время истечения (ISO timestamp)
            ext (Dict[str, Any]) = дополнительные данные
            paraphrases_count (int) =количество парафразов
            suggested_paraphrases_count (int) количество предложенных парафразов
            paraphrases (List[_ParaphraseItem]) список парафразов
            attachments (List[_AttachmentItem]) список вложений
            context (Dict[str, Any]) контекстные данные
            answers (List[_AnswerItem]) список ответов на разных языках
            history (List[_HistoryItem]) история изменений документа
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/post_documents__document_id__contexts
        """
        try: model = DocumentContextModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'post',
            f'/core-api/crud/api/v1/documents/{document_id}/contexts',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_create_document_context(self, document_id: int, **kwargs):
        """
        Добавляет контекст для документа (асинхронно).
        
        Args:
            document_id (int): ID документа
            name (str) название документа
            question (str) вопрос документа
            answer (str) ответ документа
            status (_DocumentStatus) статус документа
            modified_at (str) время изменения (ISO timestamp)
            expired_at (Optional[str]) время истечения (ISO timestamp)
            ext (Dict[str, Any]) = дополнительные данные
            paraphrases_count (int) =количество парафразов
            suggested_paraphrases_count (int) количество предложенных парафразов
            paraphrases (List[_ParaphraseItem]) список парафразов
            attachments (List[_AttachmentItem]) список вложений
            context (Dict[str, Any]) контекстные данные
            answers (List[_AnswerItem]) список ответов на разных языках
            history (List[_HistoryItem]) история изменений документа
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/post_documents__document_id__contexts
        """
        try: model = DocumentContextModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'post',
            f'/core-api/crud/api/v1/documents/{document_id}/contexts',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_document_context(self, document_id: int):
        """
        Получает контекст документа (синхронно).
        
        Args:
            document_id (int): ID документа
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/get_documents__document_id__contexts
        """
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/documents/{document_id}/contexts'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_document_context(self, document_id: int):
        """
        Получает контекст документа (асинхронно).
        
        Args:
            document_id (int): ID документа
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/get_documents__document_id__contexts
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/documents/{document_id}/contexts'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_update_document_context(self, document_id: int, context_id: int, **kwargs):
        """
        Обновляет контекст документа (синхронно).
        
        Args:
            document_id (int): ID документа
            name (str) название документа
            question (str) вопрос документа
            answer (str) ответ документа
            status (_DocumentStatus) статус документа
            modified_at (str) время изменения (ISO timestamp)
            expired_at (Optional[str]) время истечения (ISO timestamp)
            ext (Dict[str, Any]) = дополнительные данные
            paraphrases_count (int) =количество парафразов
            suggested_paraphrases_count (int) количество предложенных парафразов
            paraphrases (List[_ParaphraseItem]) список парафразов
            attachments (List[_AttachmentItem]) список вложений
            context (Dict[str, Any]) контекстные данные
            answers (List[_AnswerItem]) список ответов на разных языках
            history (List[_HistoryItem]) история изменений документа
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/put_documents__document_id__contexts__context_id_
        """
        try: model = DocumentContextModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'put',
            f'/core-api/crud/api/v1/documents/{document_id}/contexts/{context_id}',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_update_document_context(self, document_id: int, context_id: int, **kwargs):
        """
        Обновляет контекст документа (асинхронно).
        
        Args:
            document_id (int): ID документа
            name (str) название документа
            question (str) вопрос документа
            answer (str) ответ документа
            status (_DocumentStatus) статус документа
            modified_at (str) время изменения (ISO timestamp)
            expired_at (Optional[str]) время истечения (ISO timestamp)
            ext (Dict[str, Any]) = дополнительные данные
            paraphrases_count (int) =количество парафразов
            suggested_paraphrases_count (int) количество предложенных парафразов
            paraphrases (List[_ParaphraseItem]) список парафразов
            attachments (List[_AttachmentItem]) список вложений
            context (Dict[str, Any]) контекстные данные
            answers (List[_AnswerItem]) список ответов на разных языках
            history (List[_HistoryItem]) история изменений документа
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/put_documents__document_id__contexts__context_id_
        """
        try: model = DocumentContextModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'put',
            f'/core-api/crud/api/v1/documents/{document_id}/contexts/{context_id}',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    
    def sync_delete_document_context(self, document_id: int, context_id: int):
        """
        Удаляет контекст документа (синхронно).
        
        Args:
            document_id (int): ID документа
            context_id (int): ID контекста
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/delete_documents__document_id__contexts__context_id_
        """
        resp = self.sync_request(
            'delete',
            f'/core-api/crud/api/v1/documents/{document_id}/contexts/{context_id}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_delete_document_context(self, document_id: int, context_id: int):
        """
        Удаляет контекст документа (асинхронно).
        
        Args:
            document_id (int): ID документа
            context_id (int): ID контекста
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/delete_documents__document_id__contexts__context_id_
        """
        resp = await self.async_request(
            'delete',
            f'/core-api/crud/api/v1/documents/{document_id}/contexts/{context_id}'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_update_document_tags(self, document_id: int, **kwargs):
        """
        Обновляет теги документа (синхронно).
        
        Args:
            document_id (int): ID документа
            tags (List[str]): список тегов документа
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/put_documents__document_id__tags
        """
        try: model = DocumentTagsModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'put',
            f'/core-api/crud/api/v1/documents/{document_id}/tags',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_update_document_tags(self, document_id: int, **kwargs):
        """
        Обновляет теги документа (асинхронно).
        
        Args:
            document_id (int): ID документа
            tags (List[str]): список тегов документа
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Documents%20CRUD%20API/put_documents__document_id__tags
        """
        try: model = DocumentTagsModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'put',
            f'/core-api/crud/api/v1/documents/{document_id}/tags',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    
    def sync_create_paraphrases(self, **kwargs):
        """
        Создает новой фурмулировки к документу (синхронно).
        
        Args:
            service_id (int) ID сервиса, к которому принадлежит документ
            document_id (int) ID документа, для которого создается фурмулировки
            paraphrase (str): текст фурмулировки
            author (str): автор фурмулировки
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Paraphrases%20CRUD%20API/post_paraphrases
        """
        try: model = CreateParaphraseModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'post',
            f'/core-api/crud/api/v1/paraphrases',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_create_paraphrases(self, **kwargs):
        """
        Создает новой фурмулировки к документу (асинхронно).
        
        Args:
            service_id (int) ID сервиса, к которому принадлежит документ
            document_id (int) ID документа, для которого создается фурмулировки
            paraphrase (str): текст фурмулировки
            author (str): автор фурмулировки
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Paraphrases%20CRUD%20API/post_paraphrases
        """
        try: model = CreateParaphraseModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'post',
            f'/core-api/crud/api/v1/paraphrases',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_paraphrases(self, **kwargs):
        """
        Получает всех переформулировок к документу с фильтрацией (синхронно).
        
        Args:
            document_id (int) ID документа
            limit_paraphrases (Optional[int])ограничение на количество формулировок в ответе
            offset_paraphrases (Optional[int]) смещение на выдачу формулировок в ответе
            offset (Optional[int]) pagination offset (default 0) (alias for offset_paraphrases)
            count (Optional[int]) pagination count (default 9999) (alias for limit_paraphrases)
            sort_by (Optional[str]) sort by 'id' or 'modified_at' (default is 'id')
            sort_order (Literal["asc", "desc")] sorting order 'asc' or 'desc' (default is 'asc')
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Paraphrases%20CRUD%20API/get_paraphrases
        """
        try: model = GetParaphrasesyParamsModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/paraphrases',
            params=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_paraphrases(self, **kwargs):
        """
        Получает всех переформулировок к документу с фильтрацией (асинхронно).
        
        Args:
            document_id (int) ID документа
            limit_paraphrases (Optional[int])ограничение на количество формулировок в ответе
            offset_paraphrases (Optional[int]) смещение на выдачу формулировок в ответе
            offset (Optional[int]) pagination offset (default 0) (alias for offset_paraphrases)
            count (Optional[int]) pagination count (default 9999) (alias for limit_paraphrases)
            sort_by (Optional[str]) sort by 'id' or 'modified_at' (default is 'id')
            sort_order (Literal["asc", "desc")] sorting order 'asc' or 'desc' (default is 'asc')
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Paraphrases%20CRUD%20API/get_paraphrases
        """
        try: model = GetParaphrasesyParamsModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/paraphrases',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_mass_update_paraphrases(self, **kwargs):
        """
        Массово обновляет формулировки для документа (синхронно).
        
        Args:
            paraphrases (List[MassUpdateParaphraseItemModel]) список парафразов для обновления
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Paraphrases%20CRUD%20API/put_paraphrases
        """
        try: model = MassUpdateParaphrasesModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'put',
            f'/core-api/crud/api/v1/paraphrases',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_mass_update_paraphrases(self, **kwargs):
        """
        Массово обновляет формулировки для документа (асинхронно).
        
        Args:
            paraphrases (List[MassUpdateParaphraseItemModel]) список парафразов для обновления
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Paraphrases%20CRUD%20API/put_paraphrases
        """
        try: model = MassUpdateParaphrasesModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'put',
            f'/core-api/crud/api/v1/paraphrases',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_mass_move_paraphrases(self, **kwargs):
        """
        Массово перемещает парафразы между документами (синхронно).
        
        Args:
            paraphrases (List[MassUpdateParaphraseItemModel]) список парафразов для перемещения
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Paraphrases%20CRUD%20API/post_paraphrases_actions_move
        """
        try: model = MassMoveParaphrasesModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'post',
            f'/core-api/crud/api/v1/paraphrases/actions/move',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_mass_move_paraphrases(self, **kwargs):
        """
        Массово перемещает парафразы между документами (асинхронно).
        
        Args:
            paraphrases (List[MassUpdateParaphraseItemModel]) список парафразов для перемещения
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Paraphrases%20CRUD%20API/post_paraphrases_actions_move
        """
        try: model = MassMoveParaphrasesModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'post',
            f'/core-api/crud/api/v1/paraphrases/actions/move',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_paraphrase(self, paraphrase_id: int):
        """
        Получает информацию о формулировке документа (синхронно).
        
        Args:
            paraphrase_id (int): ID парафраза
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Paraphrases%20CRUD%20API/get_paraphrases__paraphrase_id_
        """
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/paraphrases/{paraphrase_id}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_paraphrase(self, paraphrase_id: int):
        """
        Получает информацию о формулировке документа (синхронно).
        
        Args:
            paraphrase_id (int): ID парафраза
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Paraphrases%20CRUD%20API/get_paraphrases__paraphrase_id_
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/paraphrases/{paraphrase_id}'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_update_paraphrase(self, paraphrase_id: int, **kwargs):
        """
        Обновляет формулировки для документа (синхронно).
        
        Args:
            paraphrase_id (int): ID парафраза
            text (str) новый текст парафраза
            author (str) автор парафраза
            
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Paraphrases%20CRUD%20API/put_paraphrases__paraphrase_id_
        """
        try: model = UpdateParaphraseItemModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'put',
            f'/core-api/crud/api/v1/paraphrases/{paraphrase_id}',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_update_paraphrase(self, paraphrase_id: int, **kwargs):
        """
        Обновляет формулировки для документа (асинхронно).
        
        Args:
            paraphrase_id (int): ID парафраза
            text (str) новый текст парафраза
            author (str) автор парафраза
            
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Paraphrases%20CRUD%20API/put_paraphrases__paraphrase_id_
        """
        try: model = UpdateParaphraseItemModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'put',
            f'/core-api/crud/api/v1/paraphrases/{paraphrase_id}',
            json=json
        ) 
        return {"result": resp, "errors": None}    
    
    def sync_delete_paraphrase(self, paraphrase_id: int):
        """
        Удаляет формулировки для документа (синхронно).
        
        Args:
            paraphrase_id (int): ID парафраза
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Paraphrases%20CRUD%20API/delete_paraphrases__paraphrase_id_
        """
        resp = self.sync_request(
            'delete',
            f'/core-api/crud/api/v1/paraphrases/{paraphrase_id}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_delete_paraphrase(self, paraphrase_id: int):
        """
        Удаляет формулировки для документа (синхронно).
        
        Args:
            paraphrase_id (int): ID парафраза
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Paraphrases%20CRUD%20API/delete_paraphrases__paraphrase_id_
        """
        resp = await self.async_request(
            'delete',
            f'/core-api/crud/api/v1/paraphrases/{paraphrase_id}'
        ) 
        return {"result": resp, "errors": None} 
    
    def sync_accept_paraphrase(self, paraphrase_id: int):
        """
        Принимает рекомендации формулировки (синхронно).
        
        Args:
            paraphrase_id (int): ID парафраза
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Paraphrases%20CRUD%20API/post_paraphrases__paraphrase_id__actions_accept
        """
        resp = self.sync_request(
            'post',
            f'/core-api/crud/api/v1/paraphrases/{paraphrase_id}/actions/accept'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_accept_paraphrase(self, paraphrase_id: int):
        """
        Принимает рекомендации формулировки (асинхронно).
        
        Args:
            paraphrase_id (int): ID парафраза
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Paraphrases%20CRUD%20API/post_paraphrases__paraphrase_id__actions_accept
        """
        resp = await self.async_request(
            'post',
            f'/core-api/crud/api/v1/paraphrases/{paraphrase_id}/actions/accept'
        ) 
        return {"result": resp, "errors": None} 
    
    def sync_merge_groups(self, **kwargs):
        """
        Объединяет базу знаний в группы (синхронно).
        
        Args:
            services (List[int]) список ID сервисов для включения в группу
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Groups%20CRUD%20API/post_groups
        """
        try: model = GroupsListModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'post',
            f'/core-api/crud/api/v1/groups',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_merge_groups(self, **kwargs):
        """
        Объединяет базу знаний в группы (асинхронно).
        
        Args:
            services (List[int]) список ID сервисов для включения в группу
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Groups%20CRUD%20API/post_groups
        """
        try: model = GroupsListModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'post',
            f'/core-api/crud/api/v1/groups',
            json=json
        ) 
        return {"result": resp, "errors": None}  
    
    def sync_get_group(self, group_id_or_uid: str):
        """
        Получает информацию о группе (синхронно).
        
        Args:
            group_id_or_uid (str): ID или UID группы
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Groups%20CRUD%20API/get_groups__group_id_or_uid_
        """
        params = {}
        if group_id_or_uid: params['group_id_or_uid'] = group_id_or_uid
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/groups',
            params=params
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_group(self, group_id_or_uid: str):
        """
        Получает информацию о группе (асинхронно).
        
        Args:
            group_id_or_uid (str): ID или UID группы
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Groups%20CRUD%20API/get_groups__group_id_or_uid_
        """
        params = {}
        if group_id_or_uid: params['group_id_or_uid'] = group_id_or_uid
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/groups',
            params=params
        ) 
        return {"result": resp, "errors": None} 
    
    def sync_update_group(self, group_id_or_uid: str, **kwargs):
        """
        Обновляет группы (синхронно).
        
        Args:
            group_id_or_uid (str): ID или UID группы
            services (List[int]) список ID сервисов для включения в группу
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Groups%20CRUD%20API/put_groups__group_id_or_uid_
        """
        try: model = GroupsListModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'put',
            f'/core-api/crud/api/v1/groups/{group_id_or_uid}',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_update_group(self, group_id_or_uid: str, **kwargs):
        """
        Обновляет группы (асинхронно).
        
        Args:
            group_id_or_uid (str): ID или UID группы
            services (List[int]) список ID сервисов для включения в группу
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Groups%20CRUD%20API/put_groups__group_id_or_uid_
        """
        try: model = GroupsListModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'put',
            f'/core-api/crud/api/v1/groups/{group_id_or_uid}',
            json=json
        ) 
        return {"result": resp, "errors": None} 
    
    def sync_delete_group(self, group_id_or_uid: str):
        """
        Удаляет группу (синхронно).
        
        Args:
            group_id_or_uid (str): ID или UID группы
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Groups%20CRUD%20API/delete_groups__group_id_or_uid_
        """
        resp = self.sync_request(
            'delete',
            f'/core-api/crud/api/v1/groups/{group_id_or_uid}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_delete_group(self, group_id_or_uid: str):
        """
        Удаляет группу (асинхронно).
        
        Args:
            group_id_or_uid (str): ID или UID группы
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Groups%20CRUD%20API/delete_groups__group_id_or_uid_
        """
        resp = await self.async_request(
            'delete',
            f'/core-api/crud/api/v1/groups/{group_id_or_uid}'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_create_service_term(self, service_id: int, **kwargs):
        """
        Создает термина базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            term: (str): основной термин
            synonyms: (List[str]): список синонимов для термина
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Service%20Synonyms%20CRUD%20API/post_services__service_id__synonyms
        """
        try: model = CreateServiceTermModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/synonyms',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_create_service_term(self, service_id: int, **kwargs):
        """
        Создает термина базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            term: (str): основной термин
            synonyms: (List[str]): список синонимов для термина
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Service%20Synonyms%20CRUD%20API/post_services__service_id__synonyms
        """
        try: model = CreateServiceTermModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/synonyms',
            json=json
        ) 
        return {"result": resp, "errors": None} 
    
    def sync_get_service_terms(self, service_id: int):
        """
        Получает словарь терминов базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Service%20Synonyms%20CRUD%20API/get_services__service_id__synonyms
        """
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/synonyms'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_service_terms(self, service_id: int):
        """
        Получает словарь терминов базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Service%20Synonyms%20CRUD%20API/get_services__service_id__synonyms
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/synonyms'
        ) 
        return {"result": resp, "errors": None} 
    
    def sync_delete_service_term_or_term_synonym(self, service_id: int, term: str, synonym: str = None):
        """
        Удаляет термин со всеми синонимами либо из синонима термина (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            term (str): Термин для удаления
            synonym (str, optional): Синоним для удаления (если не указан, удаляется весь термин)
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Service%20Synonyms%20CRUD%20API/delete_services__service_id__synonyms
        """
        params = {'term': term}
        if synonym: params['synonym'] = synonym
        resp = self.sync_request(
            'delete',
            f'/core-api/crud/api/v1/services/{service_id}/synonyms',
            params=params
        ) 
        return {"result": resp, "errors": None}
    
    async def async_delete_service_term_or_term_synonym(self, service_id: int, term: str, synonym: str = None):
        """
        Удаляет термин со всеми синонимами либо из синонима термина (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            term (str): Термин для удаления
            synonym (str, optional): Синоним для удаления (если не указан, удаляется весь термин)
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Service%20Synonyms%20CRUD%20API/delete_services__service_id__synonyms
        """
        params = {'term': term}
        if synonym: params['synonym'] = synonym
        resp = await self.async_request(
            'delete',
            f'/core-api/crud/api/v1/services/{service_id}/synonyms',
            params=params
        ) 
        return {"result": resp, "errors": None} 
    
    def sync_rename_service_term(self, service_id: int, term: str, value: str):
        """
        Переименовывает термин базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            term (str): Текущее название термина
            value (str): Новое название термина
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Service%20Synonyms%20CRUD%20API/put_services__service_id__synonyms__term_
        """
        params = {'value': value}
        resp = self.sync_request(
            'put',
            f'/core-api/crud/api/v1/services/{service_id}/synonyms/{term}',
            params=params
        ) 
        return {"result": resp, "errors": None}
    
    async def async_rename_service_term(self, service_id: int, term: str, value: str):
        """
        Переименовывает термин базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            term (str): Текущее название термина
            value (str): Новое название термина
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Service%20Synonyms%20CRUD%20API/put_services__service_id__synonyms__term_
        """
        params = {'value': value}
        resp = await self.async_request(
            'put',
            f'/core-api/crud/api/v1/services/{service_id}/synonyms/{term}',
            params=params
        ) 
        return {"result": resp, "errors": None}
    
    def sync_delete_service_term(self, service_id: int, term: str):
        """
        Удаляет термин базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            term (str): Термин для удаления
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Service%20Synonyms%20CRUD%20API/delete_services__service_id__synonyms__term_
        """
        resp = self.sync_request(
            'delete',
            f'/core-api/crud/api/v1/services/{service_id}/synonyms/{term}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_delete_service_term(self, service_id: int, term: str):
        """
        Удаляет термин базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            term (str): Термин для удаления
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Service%20Synonyms%20CRUD%20API/delete_services__service_id__synonyms__term_
        """
        resp = await self.async_request(
            'delete',
            f'/core-api/crud/api/v1/services/{service_id}/synonyms/{term}'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_create_service_term_synonym(self, service_id: int, term: str, synonym: str):
        """
        Создает синоним (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            term (str): Термин
            synonym (str): Синоним для добавления
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Service%20Synonyms%20CRUD%20API/post_services__service_id__synonyms__term__items
        """
        json = {'synonym': synonym}
        resp = self.sync_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/synonyms/{term}/items',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_create_service_term_synonym(self, service_id: int, term: str, synonym: str):
        """
        Создает синоним (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            term (str): Термин
            synonym (str): Синоним для добавления
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Service%20Synonyms%20CRUD%20API/post_services__service_id__synonyms__term__items
        """
        json = {'synonym': synonym}
        resp = await self.async_request(
            'post',
            f'/core-api/crud/api/v1/services/{service_id}/synonyms/{term}/items',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_rename_service_term_synonym(self, service_id: int, term: str, synonym: str, new_name: str):
        """
        Переименовывает синоним термина базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            term (str): Термин
            synonym (str): Текущий синоним
            new_name (str): Новое название синонима
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Service%20Synonyms%20CRUD%20API/put_services__service_id__synonyms__term__items__synonym_
        """
        json = {'value': new_name}
        resp = self.sync_request(
            'put',
            f'/core-api/crud/api/v1/services/{service_id}/synonyms/{term}/items/{synonym}',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_rename_service_term_synonym(self, service_id: int, term: str, synonym: str, new_name: str):
        """
        Переименовывает синоним термина базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            term (str): Термин
            synonym (str): Текущий синоним
            new_name (str): Новое название синонима
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Service%20Synonyms%20CRUD%20API/put_services__service_id__synonyms__term__items__synonym_
        """
        json = {'value': new_name}
        resp = await self.async_request(
            'put',
            f'/core-api/crud/api/v1/services/{service_id}/synonyms/{term}/items/{synonym}',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_delete_service_term_synonym(self, service_id: int, term: str, synonym: str):
        """
        Удаляет синоним термина базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            term (str): Термин
            synonym (str): Синоним для удаления
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Service%20Synonyms%20CRUD%20API/delete_services__service_id__synonyms__term__items__synonym_
        """
        resp = self.sync_request(
            'delete',
            f'/core-api/crud/api/v1/services/{service_id}/synonyms/{term}/items/{synonym}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_delete_service_term_synonym(self, service_id: int, term: str, synonym: str):
        """
        Удаляет синоним термина базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            term (str): Термин
            synonym (str): Синоним для удаления
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Service%20Synonyms%20CRUD%20API/delete_services__service_id__synonyms__term__items__synonym_
        """
        resp = await self.async_request(
            'delete',
            f'/core-api/crud/api/v1/services/{service_id}/synonyms/{term}/items/{synonym}'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_create_user_term(self, user_id: int, **kwargs):
        """
        Создает термин для УЗ пользователя (синхронно).
        
        Args:
            user_id (int): ID пользователя
            term (str): основной термин
            synonyms (List[str]): список синонимов для термина
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/User%20Synonyms%20CRUD%20API/post_users__user_id__synonyms
        """
        try: model = CreateUserTermModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = self.sync_request(
            'post',
            f'/core-api/crud/api/v1/users/{user_id}/synonyms',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_create_user_term(self, user_id: int, **kwargs):
        """
        Создает термин для УЗ пользователя (асинхронно).
        
        Args:
            user_id (int): ID пользователя
            term (str): основной термин
            synonyms (List[str]): список синонимов для термина
        
        Returns:
            dict: Результат операции {"result": data, "errors": None} или {"result": None, "errors": validation_errors}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/User%20Synonyms%20CRUD%20API/post_users__user_id__synonyms
        """
        try: model = CreateUserTermModel(**kwargs)
        except ValidationError as e:
            return {
                "result": None,
                "errors": e.errors()
            }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            json = model.model_dump()
        resp = await self.async_request(
            'post',
            f'/core-api/crud/api/v1/users/{user_id}/synonyms',
            json=json
        ) 
        return {"result": resp, "errors": None} 
    
    def sync_get_user_term(self, user_id: int):
        """
        Получает термины для УЗ пользователя (синхронно).
        
        Args:
            user_id (int): ID пользователя
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/User%20Synonyms%20CRUD%20API/get_users__user_id__synonyms
        """
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/users/{user_id}/synonyms'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_user_term(self, user_id: int):
        """
        Получает термины для УЗ пользователя (асинхронно).
        
        Args:
            user_id (int): ID пользователя
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/User%20Synonyms%20CRUD%20API/get_users__user_id__synonyms
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/users/{user_id}/synonyms'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_delete_user_term_or_term_synonym(self, user_id: int, term: str, synonym: str = None):
        """
        Удаляет термин со всеми синонимами либо один из синонимов для УЗ пользователя (синхронно).
        
        Args:
            user_id (int): ID пользователя
            term (str): Термин для удаления
            synonym (str, optional): Синоним для удаления (если не указан, удаляется весь термин)
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/User%20Synonyms%20CRUD%20API/delete_users__user_id__synonyms
        """
        params = {'term': term}
        if synonym: params['synonym'] = synonym
        resp = self.sync_request(
            'delete',
            f'/core-api/crud/api/v1/users/{user_id}/synonyms',
            params=params
        ) 
        return {"result": resp, "errors": None}
    
    async def async_delete_user_term_or_term_synonym(self, user_id: int, term: str, synonym: str = None):
        """
        Удаляет термин со всеми синонимами либо один из синонимов для УЗ пользователя (асинхронно).
        
        Args:
            user_id (int): ID пользователя
            term (str): Термин для удаления
            synonym (str, optional): Синоним для удаления (если не указан, удаляется весь термин)
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/User%20Synonyms%20CRUD%20API/delete_users__user_id__synonyms
        """
        params = {'term': term}
        if synonym: params['synonym'] = synonym
        resp = await self.async_request(
            'delete',
            f'/core-api/crud/api/v1/users/{user_id}/synonyms',
            params=params
        ) 
        return {"result": resp, "errors": None}
    
    def sync_rename_user_term(self, user_id: int, term: str, new_name: str):
        """
        Переименовывает термин для УЗ пользователя (синхронно).
        
        Args:
            user_id (int): ID пользователя
            term (str): Текущее название термина
            new_name (str): Новое название термина
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/User%20Synonyms%20CRUD%20API/put_users__user_id__synonyms__term_
        """
        json = {'value': new_name}
        resp = self.sync_request(
            'put',
            f'/core-api/crud/api/v1/users/{user_id}/synonyms/{term}',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_rename_user_term(self, user_id: int, term: str, new_name: str):
        """
        Переименовывает термин для УЗ пользователя (асинхронно).
        
        Args:
            user_id (int): ID пользователя
            term (str): Текущее название термина
            new_name (str): Новое название термина
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/User%20Synonyms%20CRUD%20API/put_users__user_id__synonyms__term_
        """
        json = {'value': new_name}
        resp = await self.async_request(
            'put',
            f'/core-api/crud/api/v1/users/{user_id}/synonyms/{term}',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_delete_user_term(self, user_id: int, term: str):
        """
        Удаляет термин для УЗ пользователя (синхронно).
        
        Args:
            user_id (int): ID пользователя
            term (str): Термин для удаления
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/User%20Synonyms%20CRUD%20API/delete_users__user_id__synonyms__term_
        """
        resp = self.sync_request(
            'delete',
            f'/core-api/crud/api/v1/users/{user_id}/synonyms/{term}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_delete_user_term(self, user_id: int, term: str):
        """
        Удаляет термин для УЗ пользователя (асинхронно).
        
        Args:
            user_id (int): ID пользователя
            term (str): Термин для удаления
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/User%20Synonyms%20CRUD%20API/delete_users__user_id__synonyms__term_
        """
        resp = await self.async_request(
            'delete',
            f'/core-api/crud/api/v1/users/{user_id}/synonyms/{term}'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_create_user_synonym(self, user_id: int, term: str, synonym: str):
        """
        Создает синоним для УЗ пользователя (синхронно).
        
        Args:
            user_id (int): ID пользователя
            term (str): Термин
            synonym (str): Синоним для добавления
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/User%20Synonyms%20CRUD%20API/post_users__user_id__synonyms__term__items
        """
        json = {'synonym': synonym}
        resp = self.sync_request(
            'post',
            f'/core-api/crud/api/v1/users/{user_id}/synonyms/{term}/items',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_create_user_synonym(self, user_id: int, term: str, synonym: str):
        """
        Создает синоним для УЗ пользователя (асинхронно).
        
        Args:
            user_id (int): ID пользователя
            term (str): Термин
            synonym (str): Синоним для добавления
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/User%20Synonyms%20CRUD%20API/post_users__user_id__synonyms__term__items
        """
        json = {'synonym': synonym}
        resp = await self.async_request(
            'post',
            f'/core-api/crud/api/v1/users/{user_id}/synonyms/{term}/items',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_rename_user_synonym(self, user_id: int, term: str, synonym: str, new_name: str):
        """
        Переименовывает синоним для УЗ пользователя (синхронно).
        
        Args:
            user_id (int): ID пользователя
            term (str): Термин
            synonym (str): Текущий синоним
            new_name (str): Новое название синонима
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/User%20Synonyms%20CRUD%20API/put_users__user_id__synonyms__term__items__synonym_
        """
        json = {'value': new_name}
        resp = self.sync_request(
            'put',
            f'/core-api/crud/api/v1/users/{user_id}/synonyms/{term}/items/{synonym}',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    async def async_rename_user_synonym(self, user_id: int, term: str, synonym: str, new_name: str):
        """
        Переименовывает синоним для УЗ пользователя (асинхронно).
        
        Args:
            user_id (int): ID пользователя
            term (str): Термин
            synonym (str): Текущий синоним
            new_name (str): Новое название синонима
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/User%20Synonyms%20CRUD%20API/put_users__user_id__synonyms__term__items__synonym_
        """
        json = {'value': new_name}
        resp = await self.async_request(
            'put',
            f'/core-api/crud/api/v1/users/{user_id}/synonyms/{term}/items/{synonym}',
            json=json
        ) 
        return {"result": resp, "errors": None}
    
    def sync_delete_user_synonym(self, user_id: int, term: str, synonym: str):
        """
        Удаляет синоним для УЗ пользователя (синхронно).
        
        Args:
            user_id (int): ID пользователя
            term (str): Термин
            synonym (str): Синоним для удаления
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/User%20Synonyms%20CRUD%20API/delete_users__user_id__synonyms__term__items__synonym_
        """
        resp = self.sync_request(
            'delete',
            f'/core-api/crud/api/v1/users/{user_id}/synonyms/{term}/items/{synonym}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_delete_user_synonym(self, user_id: int, term: str, synonym: str):
        """
        Удаляет синоним для УЗ пользователя (асинхронно).
        
        Args:
            user_id (int): ID пользователя
            term (str): Термин
            synonym (str): Синоним для удаления
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/User%20Synonyms%20CRUD%20API/delete_users__user_id__synonyms__term__items__synonym_
        """
        resp = await self.async_request(
            'delete',
            f'/core-api/crud/api/v1/users/{user_id}/synonyms/{term}/items/{synonym}'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_service_snapshots(self, service_id: int):
        """
        Получает список снапшотов базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__snapshots
        """
        resp = self.sync_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/snapshots'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_service_snapshots(self, service_id: int):
        """
        Получает список снапшотов базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services__service_id__snapshots
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/snapshots'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_user_snapshots(self):
        """
        Получает список снапшотов пользователя (синхронно).
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_snapshots
        """
        resp = self.sync_request(
            'get',
            '/core-api/crud/api/v1/services/snapshots'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_user_snapshots(self):
        """
        Получает список снапшотов пользователя (асинхронно).
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_snapshots
        """
        resp = await self.async_request(
            'get',
            '/core-api/crud/api/v1/services/snapshots'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_snapshots_space_status(self):
        """
        Получает статус пространства для снапшотов (синхронно).
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_snapshots_space_status
        """
        resp = self.sync_request(
            'get',
            '/core-api/crud/api/v1/services/snapshots/space_status'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_snapshots_space_status(self):
        """
        Получает статус пространства для снапшотов (асинхронно).
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_snapshots_space_status
        """
        resp = await self.async_request(
            'get',
            '/core-api/crud/api/v1/services/snapshots/space_status'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_start_snapshot_restore(self, service_id: int, snapshot_id: int):
        """
        Запускает восстановление базы знаний из снапшота (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            snapshot_id (int): ID снапшота
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/put_services__service_id__snapshots__snapshot_id_
        """
        resp = self.sync_request(
            'put',
            f'/core-api/crud/api/v1/services/{service_id}/snapshots/{snapshot_id}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_start_snapshot_restore(self, service_id: int, snapshot_id: int):
        """
        Запускает восстановление базы знаний из снапшота (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            snapshot_id (int): ID снапшота
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/put_services__service_id__snapshots__snapshot_id_
        """
        resp = await self.async_request(
            'get',
            f'/core-api/crud/api/v1/services/{service_id}/snapshots/{snapshot_id}'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_delete_snapshot(self, service_id: int, snapshot_id: int):
        """
        Удаляет снапшот базы знаний (синхронно).
        
        Args:
            service_id (int): ID базы знаний
            snapshot_id (int): ID снапшота
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/delete_services__service_id__snapshots__snapshot_id_
        """
        resp = self.sync_request(
            'delete',
            f'/core-api/crud/api/v1/services/{service_id}/snapshots/{snapshot_id}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_delete_snapshot(self, service_id: int, snapshot_id: int):
        """
        Удаляет снапшот базы знаний (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
            snapshot_id (int): ID снапшота
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/delete_services__service_id__snapshots__snapshot_id_
        """
        resp = await self.async_request(
            'delete',
            f'/core-api/crud/api/v1/services/{service_id}/snapshots/{snapshot_id}'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_get_archives(self):
        """
        Получает список архивных (удаленных) баз знаний (синхронно).
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_archive
        """
        resp = self.sync_request(
            'get',
            '/core-api/crud/api/v1/services/archive'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_get_archives(self):
        """
        Получает список архивных (удаленных) баз знаний (асинхронно).
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/get_services_archive
        """
        resp = await self.async_request(
            'get',
            '/core-api/crud/api/v1/services/archive'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_clear_archives(self):
        """
        Очищает корзину архивных баз знаний (синхронно).
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/delete_services_archive
        """
        resp = self.sync_request(
            'delete',
            '/core-api/crud/api/v1/services/archive'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_clear_archives(self):
        """
        Очищает корзину архивных баз знаний (асинхронно).
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/delete_services_archive
        """
        resp = await self.async_request(
            'delete',
            '/core-api/crud/api/v1/services/archive'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_restore_service_from_recycle_bin(self, service_id: int):
        """
        Восстанавливает базу знаний из корзины (синхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/put_services_archive__service_id_
        """
        resp = self.sync_request(
            'put',
            f'/core-api/crud/api/v1/services/archive/{service_id}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_restore_service_from_recycle_bin(self, service_id: int):
        """
        Восстанавливает базу знаний из корзины (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/put_services_archive__service_id_
        """
        resp = await self.async_request(
            'put',
            f'/core-api/crud/api/v1/services/archive/{service_id}'
        ) 
        return {"result": resp, "errors": None}
    
    def sync_delete_service_from_recycle_bin(self, service_id: int):
        """
        Окончательно удаляет базу знаний из корзины (синхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/delete_services_archive__service_id_
        """
        resp = self.sync_request(
            'delete',
            f'/core-api/crud/api/v1/services/archive/{service_id}'
        ) 
        return {"result": resp, "errors": None}
    
    async def async_delete_service_from_recycle_bin(self, service_id: int):
        """
        Окончательно удаляет базу знаний из корзины (асинхронно).
        
        Args:
            service_id (int): ID базы знаний
        
        Returns:
            dict: Результат операции {"result": data, "errors": None}
            
        Link: 
            https://app.swaggerhub.com/apis-docs/AutoFAQ.ai/aq_kb_crud/1.0#/Services%20CRUD%20API/delete_services_archive__service_id_
        """
        resp = await self.async_request(
            'delete',
            f'/core-api/crud/api/v1/services/archive/{service_id}'
        ) 
        return {"result": resp, "errors": None}
