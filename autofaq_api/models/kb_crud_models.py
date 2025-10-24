
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Dict, Any, Literal


class UserCreateModel(BaseModel):
    email: str = Field(..., description="Email пользователя")
    name: str = Field(..., min_length=2, max_length=50, description="Имя пользователя")
    password: str = Field(..., min_length=8, max_length=100, description="Пароль пользователя")


class UserUpdateModel(BaseModel):
    token: str = Field(..., min_length=32, max_length=255, description="Токен аутентификации")
    name: str = Field(..., min_length=2, max_length=100, description="Название сервисного аккаунта")
    password: str = Field(..., min_length=8, max_length=100, description="Пароль сервисного аккаунта")
    max_services_count: int = Field(default=0, ge=0, le=1000, description="Максимальное количество сервисов")


class _LanguagePreset(str, Enum):
    """Пресеты языков для сервиса."""
    RU = "ru"
    EN = "en"
    MULTILINGUAL = "multilingual"

class _QueryLength(str, Enum):
    """Длина запроса для обработки."""
    AUTO = "auto"
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"

class _DocumentStatus(str, Enum):
    """Статусы документов."""
    OK = "OK"
    ERROR = "ERROR"
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"

class _HistoryAction(str, Enum):
    """Типы действий в истории изменений."""
    CS_UPDATE_DOCUMENT = "cs_update_document"
    CS_CREATE_DOCUMENT = "cs_create_document"
    CS_DELETE_DOCUMENT = "cs_delete_document"

class _AnswerModel(BaseModel):
    """Модель ответа на разных языках."""
    language: str = Field(..., description="Язык ответа", examples=["ru", "en"])
    text: str = Field(..., description="Текст ответа", examples=["Текст ответа на русском"])

class _ParaphraseModel(BaseModel):
    """Модель перефразировки вопроса."""
    paraphrase_id: int = Field(..., ge=0, description="ID перефразировки")
    text: str = Field(..., description="Текст перефразировки", examples=["Как приобрести собаку"])
    author: str = Field(..., description="Автор перефразировки", examples=["auto", "operator"])

class _AttachmentModel(BaseModel):
    """Модель вложения документа."""
    attachment_id: int = Field(..., ge=0, description="ID вложения")
    name: str = Field(..., description="Название вложения")
    description: Optional[str] = Field(None, description="Описание вложения")

class _ChangeItemModel(BaseModel):
    """Модель элемента изменений в истории."""
    item: str = Field(..., description="Изменяемый элемент", examples=["question", "answer"])
    value: str = Field(..., description="Новое значение", examples=["Новый текст вопроса"])

class _UserModel(BaseModel):
    """Модель пользователя."""
    id: str = Field(..., description="ID пользователя")
    name: str = Field(..., description="Имя пользователя")
    email: str = Field(..., description="Email пользователя")

class _HistoryItemModel(BaseModel):
    """Модель элемента истории изменений."""
    name: _HistoryAction = Field(..., description="Тип действия")
    created_at: str = Field(..., description="Дата и время создания")
    user: _UserModel = Field(..., description="Пользователь, выполнивший действие")
    changelist: List[_ChangeItemModel] = Field(..., description="Список изменений")

class DocumentModel(BaseModel):
    """Модель документа для сервиса."""
    document_id: int = Field(..., ge=0, description="ID документа")
    name: str = Field(..., description="Название документа", examples=["Документ о покупке животных"])
    question: str = Field(..., min_length=1, max_length=1000, description="Текст вопроса", examples=["Как купить собаку"])
    answer: str = Field(..., min_length=1, description="Текст ответа", examples=["Для покупки собаки обратитесь к консультанту"])
    status: _DocumentStatus = Field(..., description="Статус документа")
    modified_at: str = Field(..., description="Дата и время последнего изменения")
    expired_at: Optional[str] = Field(None, description="Дата и время истечения срока действия")
    ext: Dict[str, Any] = Field(default_factory=dict, description="Дополнительные данные")
    paraphrases_count: int = Field(0, ge=0, description="Количество перефразировок")
    suggested_paraphrases_count: int = Field(0, ge=0, description="Количество предложенных перефразировок")
    paraphrases: List[_ParaphraseModel] = Field(default_factory=list, description="Список перефразировок")
    attachments: List[_AttachmentModel] = Field(default_factory=list, description="Список вложений")
    context: Dict[str, Any] = Field(default_factory=dict, description="Контекст документа")
    answers: List[_AnswerModel] = Field(default_factory=list, description="Ответы на разных языках")
    history: List[_HistoryItemModel] = Field(default_factory=list, description="История изменений документа")

    @field_validator('question')
    @classmethod
    def validate_question_length(cls, v: str) -> str:
        """Валидация длины вопроса."""
        if len(v.strip()) == 0:
            raise ValueError("Вопрос не может быть пустым")
        if len(v) > 1000:
            raise ValueError("Вопрос не должен превышать 1000 символов")
        return v.strip()

    @field_validator('answer')
    @classmethod
    def validate_answer_length(cls, v: str) -> str:
        """Валидация длины ответа."""
        if len(v.strip()) == 0:
            raise ValueError("Ответ не может быть пустым")
        return v.strip()

    @field_validator('modified_at', 'expired_at')
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Валидация формата даты."""
        if v is None:
            return v
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError("Неверный формат даты. Ожидается ISO 8601")

class ServiceCreateModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, use_enum_values=True)
    name: str = Field(..., min_length=1, max_length=255, description="Название сервиса")
    preset: _LanguagePreset = Field(default=_LanguagePreset.RU, description="Языковой пресет для обработки текста")
    trainable: bool = Field(default=True, description="Возможность обучения модели на данных сервиса") 
    max_trainable_score: float = Field(default=0.95, ge=0.0, le=1.0, description="Максимальный порог обучаемости модели (0.0-1.0)")
    min_levenstein_distance: int = Field(default=3, ge=0, le=10, description="Минимальное расстояние Левенштейна для схожести фраз")
    max_conf_mode_for_ident_phs: bool = Field(default=False, description="Максимальный режим уверенности для идентичных фраз")
    method: Literal["auto", "manual", "hybrid"] = Field(default="auto", description="Метод обработки запросов")
    split_by_linguistic_conjunctions: bool = Field(default=False, description="Разделение запросов по лингвистическим союзам")
    enable_tokenization: bool = Field(default=True, description="Включение токенизации текста")
    query_length: _QueryLength = Field(default=_QueryLength.AUTO, description="Длина обрабатываемых запросов")
    inequal_lang_penalty: float = Field(default=0.0, ge=0.0, le=1.0, description="Штраф за разные языки в запросе и ответе (0.0-1.0)")
    without_validation: bool = Field(default=False, description="Создание сервиса без валидации данных")
    with_layout_correction: bool = Field(default=True, description="Коррекция layout'а текста")
    ext: Dict[str, Any] = Field(default_factory=dict, description="Дополнительные параметры сервиса в формате ключ-значение") 
    documents: List[DocumentModel] = Field(default_factory=list, description="Список документов сервиса")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Валидация названия сервиса."""
        v = v.strip()
        if len(v) == 0:
            raise ValueError("Название сервиса не может быть пустым")
        if len(v) > 255:
            raise ValueError("Название сервиса не должно превышать 255 символов")
        return v

    @field_validator('max_trainable_score')
    @classmethod
    def validate_trainable_score(cls, v: float, values) -> float:
        """Валидация порога обучаемости."""
        if 'trainable' in values and not values['trainable'] and v > 0:
            raise ValueError("Порог обучаемости должен быть 0 при trainable=false")
        return round(v, 2)

    @field_validator('documents')
    @classmethod
    def validate_documents(cls, v: List[DocumentModel]) -> List[DocumentModel]:
        """Валидация списка документов."""
        if not v:
            return v
        
        # Проверка уникальности document_id
        document_ids = [doc.document_id for doc in v]
        if len(document_ids) != len(set(document_ids)):
            raise ValueError("Document IDs должны быть уникальными")
        
        # Проверка уникальности вопросов
        questions = [doc.question.lower().strip() for doc in v]
        if len(questions) != len(set(questions)):
            raise ValueError("Вопросы должны быть уникальными")
        
        return v

    @field_validator('inequal_lang_penalty')
    @classmethod
    def validate_penalty(cls, v: float) -> float:
        """Валидация штрафа за разные языки."""
        return round(v, 2)

    def model_dump(self, **kwargs) -> dict:
        """
        Сериализация модели в словарь.
        
        Returns:
            dict: Сериализованные данные сервиса
        """
        return super().model_dump(**kwargs)
    
class ServicesGetModel(BaseModel):
    """
    Модель для получения списка базы знаний
    
    Attributes:
        offset (int): Смещение (количество записей для пропуска)
        count (int): Количество записей для возврата
        sort_by (str): Поле для сортировки
        sort_order (str): Порядок сортировки ('asc' или 'desc')
    """ 
    offset: int = Field(default=0, ge=0, description="Смещение (количество записей для пропуска)")
    count: int = Field(default=9999, ge=1, le=10000, description="Количество записей для возврата")
    sort_by: str = Field(default="id", min_length=1, escription="Поле для сортировки")
    sort_order: Literal["asc", "desc"] = Field(default="asc", description="Порядок сортировки")

class ServiceIdsModel(BaseModel):
    """
    Модель для валидации списка идентификаторов баз знаний.
    Attributes:
        service_ids (List[int]): Список идентификаторов сервисов
    """
    
    service_ids: List[int] = Field(default_factory=list,description="Список идентификаторов БЗ")
    
class ServiceGetModel(BaseModel):
    """
    Модель параметров для получения определенного БЗ
    
    Attributes:
        include_documents (int): Включать документы со статусом рекомендации
        include_suggested (int): Лимит перефразировок на документ
        limit_paraphrases (int): Лимит истории изменений документа
    """
    
    include_documents: int = Field(default=0, ge=0, le=1, description="Возвращать список документов (1 - да, 0 - нет)")
    include_suggested: int = Field(default=0, ge=0, le=1, description="Включать в список документы со статусом рекомендации (1 - да, 0 - нет)")
    include_suggested: int = Field(default=500000, ge=0, le=1000000, description="Лимит количества перефразировок на документ")
    limit_paraphrases: int = Field(default=100, ge=1, le=10000,description="Лимит размера истории изменений документа")
    
    
class ServiceDocumentsGetModel(BaseModel):
    """
    Модель параметров для получения документа БЗ
    
    Attributes:
        offset (int): Смещение для пагинации
        count (int): Количество документов для возврата
        sort_by (str): Поле для сортировки
        sort_order (str): Порядок сортировки
        limit_paraphrases (int): Лимит перефразировок на документ
        limit_history (int): Лимит истории изменений документа
        include_suggested (int): Включать документы со статусом рекомендации
    """
    
    offset: int = Field(default=0, ge=0, le=100000, description="Смещение для пагинации (количество документов для пропуска)")
    count: int = Field( default=1000, ge=1, le=10000, description="Количество документов для возврата")
    sort_by: str = Field(default="id", min_length=1, escription="Поле для сортировки документов")
    sort_order: Literal["asc", "desc"] = Field(default="asc", description="Порядок сортировки документов")
    limit_paraphrases: int = Field(default=500000, ge=0, le=1000000, description="Лимит количества перефразировок на документ")
    limit_history: int = Field(default=100, ge=1, le=10000, description="Лимит размера истории изменений документа")
    include_suggested: int = Field(default=0, ge=0, le=1, description="Включать в список документы со статусом рекомендации (1 - да, 0 - нет)")
    
    
    
class SuggestedDocumentsParamsModel(BaseModel):
    """
    Модель валидации query-параметров для эндпоинта получения предлагаемых документов.
    
    Attributes:
        from_time: Начало интервала в формате ISO timestamp (по умолчанию - 1 день назад)
        to: Конец интервала в формате ISO timestamp (по умолчанию - сегодня)
        limit: Лимит выводимых элементов (приоритет над count)
        offset: Смещение для пагинации (по умолчанию 0)
        count: Количество элементов для пагинации (alias для limit, по умолчанию 9999)
        sort_by: Поле для сортировки - 'id' или 'modified_at' (по умолчанию 'id')
        sort_order: Порядок сортировки - 'asc' или 'desc' (по умолчанию 'asc')
    """
    from_time: Optional[str] = Field(default=None, alias="from", description="Начало интервала ISO timestamp по умолчанию - 1 день назад")
    to: Optional[str] = Field(default=None, description="Конец интервала ISO timestamp по умолчанию - сегодня" )
    limit: Optional[int] = Field(default=None, ge=1, description="Лимит выводимых элементов" )
    offset: Optional[int] = Field(default=0, ge=0, description="Смещение для пагинации (по умолчанию 0)" )
    count: Optional[int] = Field(default=None, ge=1, description="Количество элементов для пагинации (по умолчанию 9999)")
    sort_by: Optional[str] = Field( default="id", description="Поле для сортировки - 'id' или 'modified_at' (по умолчанию 'id')")
    sort_order: Literal["asc", "desc"] = Field(default="asc", description="Порядок сортировки - 'asc' или 'desc' (по умолчанию 'asc')" )
    

class SuggestedDocumentsCountParamsModel(BaseModel):
    """
    Модель валидации query-параметров для эндпоинта получения количества предлагаемых документов.
    
    Attributes:
        from_time: Начало интервала в формате ISO timestamp (по умолчанию - 1 день назад)
        to: Конец интервала в формате ISO timestamp (по умолчанию - сегодня)
        limit: Лимит выводимых элементов (приоритет над count)
    """
    from_time: Optional[str] = Field(default=None, alias="from", description="Начало интервала ISO timestamp по умолчанию - 1 день назад")
    to: Optional[str] = Field(default=None, description="Конец интервала ISO timestamp по умолчанию - сегодня" )
    limit: Optional[int] = Field(default=None, ge=1, description="Лимит выводимых элементов" )
    

class SuggestedParaphrasesParamsModel(BaseModel):
    """
    Модель валидации query-параметров для эндпоинта получения предлагаемых формулировок.
    
    Attributes:
        from_time: Начало интервала в формате ISO timestamp (по умолчанию - 1 день назад)
        to: Конец интервала в формате ISO timestamp (по умолчанию - сегодня)
        limit: Лимит выводимых элементов (приоритет над count)
        offset: Смещение для пагинации (по умолчанию 0)
        count: Количество элементов для пагинации (alias для limit, по умолчанию 9999)
        sort_by: Поле для сортировки - 'id' или 'modified_at' (по умолчанию 'id')
        sort_order: Порядок сортировки - 'asc' или 'desc' (по умолчанию 'asc')
    """
    from_time: Optional[str] = Field(default=None, alias="from", description="Начало интервала ISO timestamp по умолчанию - 1 день назад")
    to: Optional[str] = Field(default=None, description="Конец интервала ISO timestamp по умолчанию - сегодня" )
    limit: Optional[int] = Field(default=None, ge=1, description="Лимит выводимых элементов" )
    offset: Optional[int] = Field(default=0, ge=0, description="Смещение для пагинации (по умолчанию 0)" )
    count: Optional[int] = Field(default=None, ge=1, description="Количество элементов для пагинации (по умолчанию 9999)")
    sort_by: Optional[str] = Field( default="id", description="Поле для сортировки - 'id' или 'modified_at' (по умолчанию 'id')")
    sort_order: Literal["asc", "desc"] = Field(default="asc", description="Порядок сортировки - 'asc' или 'desc' (по умолчанию 'asc')" )
    
    
class SuggestedParaphrasesCountParamsModel(BaseModel):
    """
    Модель валидации query-параметров для эндпоинта получения количества предлагаемых рекомендаций.
    
    Attributes:
        from_time: Начало интервала в формате ISO timestamp (по умолчанию - 1 день назад)
        to: Конец интервала в формате ISO timestamp (по умолчанию - сегодня)
        limit: Лимит выводимых элементов (приоритет над count)
    """
    from_time: Optional[str] = Field(default=None, alias="from", description="Начало интервала ISO timestamp по умолчанию - 1 день назад")
    to: Optional[str] = Field(default=None, description="Конец интервала ISO timestamp по умолчанию - сегодня" )
    limit: Optional[int] = Field(default=None, ge=1, description="Лимит выводимых элементов" )
    

class SuggestedDocumentsValidateModel(BaseModel):
    """
    Модель валидации запроса для эндпоинта валидации предлагаемых документов на дубликаты (асинхронно).
    
    Attributes:
        from_time: Начало интервала в формате ISO timestamp
        to: Конец интервала в формате ISO timestamp  
        document_ids: Список идентификаторов документов для проверки
    """
    from_time: Optional[str] = Field(default=None, alias="from", description="начало интервала ISO timestamp")
    to: Optional[str] = Field(default=None, description="конец интервала ISO timestamp")
    document_ids: List[int] = Field(..., description="список идентификаторов документов для проверки")
    

class SearchDocumentsContentModel(BaseModel):
    """
    Модель валидации query-параметров для эндпоинта поиска по документам для всех или выбранных БЗ.
    
    Attributes:
        find_by: Поля по которым искать [answer, question, name, scenario] (по всем если не указано)
        offset: Смещение для пагинации (по умолчанию 0)
        count: Количество элементов для пагинации (по умолчанию 100)
        sort_by: Поле для сортировки - 'id' или 'modified_at' (по умолчанию 'modified_at')
        sort_order: Порядок сортировки - 'asc' или 'desc' (по умолчанию 'desc')
    """
    query: str = Field(..., description="поисковой запрос")
    find_by: Optional[List[str]] = Field(default=None, description="поля по которым искать (по всем если не указано) [answer, question, name, scenario]")
    offset: Optional[int] = Field(default=0, ge=0, description="pagination offset (default 0)")
    count: Optional[int] = Field(default=100, ge=1, le=1000, description="pagination count (default 100)")
    sort_by: Optional[str] = Field(default="modified_at", description="sort by 'id' or 'modified_at' (default is 'modified_at')")
    sort_order: Literal["asc", "desc"] = Field(default="asc", description="sorting order 'asc' or 'desc' (default is 'desc')")


class ServicesValidationsModel(BaseModel):
    """
    Модель валидации запроса для эндпоинта валидации сервисов.
    
    Attributes:
        service_ids: Список идентификаторов сервисов для проверки (обязательный)
        min_confidence: Минимальный общий уровень уверенности (по умолчанию 0.95)
        min_answer_confidence: Минимальный уровень уверенности для ответов (по умолчанию 0.9)
    """
    service_ids: List[int] = Field(..., min_items=1, description="список идентификаторов сервисов для проверки")
    min_confidence: float = Field(default=0.95, ge=0.0, le=1.0, description="минимальный общий уровень уверенности (по умолчанию 0.95)")
    min_answer_confidence: float = Field(default=0.9, ge=0.0, le=1.0, description="минимальный уровень уверенности для ответов (по умолчанию 0.9)")
    
    
class UpdateServiceAttachmentModel(BaseModel):
    """
    Модель валидации запроса для обновления вложения БЗ.
    
    Attributes:
        name: Название вложения (обязательное поле)
        description: Описание вложения (опциональное поле)
    """
    name: str = Field(..., min_length=1, max_length=255, description="название вложения")
    description: Optional[str] = Field(default=None, max_length=1000, description="описание вложения")
    
    
class _QAType(str, Enum):
    """Типы вопросов-ответов"""
    STANDARD = "standard"
    CLARIFYING = "clarifying"


class _GuidelineItem(BaseModel):
    """
    Модель элемента руководства (guideline)
    
    Attributes:
        id: Идентификатор руководства
        text: Текст руководства
    """
    id: int = Field(..., ge=0, description="идентификатор руководства")
    text: str = Field(..., min_length=1, description="текст руководства")


class _QAItem(BaseModel):
    """
    Модель элемента вопрос-ответ
    
    Attributes:
        id: Идентификатор QA
        type: Тип QA - 'standard' или 'clarifying'
        question: Текст вопроса
        answer: Текст ответа
    """
    id: int = Field(..., ge=0, description="идентификатор QA")
    type: _QAType = Field(..., description="тип QA - 'standard' или 'clarifying'")
    question: str = Field(..., min_length=1, description="текст вопроса")
    answer: str = Field(..., min_length=1, description="текст ответа")


class _EnabledParts(BaseModel):
    """
    Модель включенных частей промпта
    
    Attributes:
        heading: Включена ли заголовочная часть
        guidelines: Включены ли руководства
        standard_qa: Включены ли стандартные QA
        clarifying_qa: Включены ли уточняющие QA
    """
    heading: bool = Field(..., description="включена ли заголовочная часть")
    guidelines: bool = Field(..., description="включены ли руководства")
    standard_qa: bool = Field(..., description="включены ли стандартные QA")
    clarifying_qa: bool = Field(..., description="включены ли уточняющие QA")


class ServicePromptModel(BaseModel):
    """
    Модель валидации запроса для обновления промпта сервиса.
    
    Attributes:
        heading: Заголовок промпта
        guidelines: Список руководств
        qa: Список вопросов-ответов
        enabled_parts: Настройки включенных частей промпта
    """
    heading: Optional[str] = Field(default=None, max_length=1000, description="заголовок промпта" )
    guidelines: Optional[List[_GuidelineItem]] = Field(default=None, description="список руководств")
    qa: Optional[List[_QAItem]] = Field(default=None, description="список вопросов-ответов")
    enabled_parts: _EnabledParts = Field(None, description="настройки включенных частей промпта")
    

class ServicePromptQAModel(BaseModel):
    """
    Модель валидации запроса для создания вопроса-ответа в промпте сервиса.
    
    Attributes:
        id: Идентификатор QA (должен быть 0 для создания нового)
        type: Тип QA - 'standard' или 'clarifying'
        question: Текст вопроса
        answer: Текст ответа
    """
    id: int = Field(0, ge=0, description="идентификатор QA (должен быть 0 для создания нового)")
    type: _QAType = Field(None, description="тип QA - 'standard' или 'clarifying'")
    question: str = Field(None, min_length=1, max_length=5000, description="текст вопроса")
    answer: str = Field(None, min_length=1, max_length=10000, description="текст ответа")
   
    
class _ParaphraseItem(BaseModel):
    """
    Модель парафраза (вариации вопроса)
    
    Attributes:
        text: Текст парафраза
    """
    paraphrase_id: int = Field(None, ge=0, description="ID парафраза")
    text: str = Field(None, min_length=1, description="текст парафраза")
    author: str = Field(None, min_length=1, description="автор парафраза")
    

class CreateDocumentRequest(BaseModel):
    """
    Модель валидации запроса для создания документа.
    
    Attributes:
        service_id: ID сервиса, к которому принадлежит документ
        name: Название документа
        question: Основной вопрос документа
        answer: Ответ на вопрос
        status: Статус документа (по умолчанию 'OK')
        ext: Дополнительные данные в формате JSON
        paraphrases: Список парафразов (вариаций вопроса)
    """
    service_id: int = Field(..., gt=0, description="ID сервиса, к которому принадлежит документ")
    name: str = Field(...,  min_length=1, max_length=500, description="название документа")
    question: str = Field(..., min_length=1, max_length=5000, description="основной вопрос документа")
    answer: str = Field(..., min_length=1, max_length=10000, description="ответ на вопрос")
    status: _DocumentStatus = Field(default=_DocumentStatus.OK, description="статус документа")
    ext: Optional[Dict[str, Any]] = Field(default_factory=dict, description="дополнительные данные в формате JSON")
    paraphrases: Optional[List[_ParaphraseItem]] = Field(default=None, description="список парафразов (вариаций вопроса)")
    
    
class UpdateDocumentRequest(BaseModel):
    """
    Модель валидации запроса для обновления документа.
    
    Attributes:
        service_id: ID сервиса, к которому принадлежит документ
        name: Название документа
        question: Основной вопрос документа
        answer: Ответ на вопрос
        status: Статус документа (по умолчанию 'OK')
        ext: Дополнительные данные в формате JSON
        paraphrases: Список парафразов (вариаций вопроса)
    """
    service_id: int = Field(..., gt=0, description="ID сервиса, к которому принадлежит документ")
    name: str = Field(None,  min_length=1, max_length=500, description="название документа")
    question: str = Field(None, min_length=1, max_length=5000, description="основной вопрос документа")
    answer: str = Field(None, min_length=1, max_length=10000, description="ответ на вопрос")
    status: _DocumentStatus = Field(None, description="статус документа")
    ext: Optional[Dict[str, Any]] = Field(None, description="дополнительные данные в формате JSON")
    paraphrases: Optional[List[_ParaphraseItem]] = Field(None, description="список парафразов (вариаций вопроса)")

    
class DocumentAttachmentModel(BaseModel):
    name: str = Field(..., description="Название вложения")
    description: Optional[str] = Field(None, description="Описание вложения")
    

class _AnswerItem(BaseModel):
    """
    Модель ответа на разных языках
    
    Attributes:
        language: Язык ответа
        text: Текст ответа
    """
    language: str = Field(..., min_length=1, max_length=10, description="язык ответа")
    text: str = Field(..., min_length=1, description="текст ответа")
    

class _AttachmentItem(BaseModel):
    """
    Модель вложения документа
    
    Attributes:
        attachment_id: ID вложения
        name: Название вложения
        description: Описание вложения
    """
    attachment_id: int = Field(..., ge=0, description="ID вложения")
    name: str = Field(..., min_length=1, description="название вложения")
    description: Optional[str] = Field(default=None, description="описание вложения")
    

class _UserInfo(BaseModel):
    """
    Модель информации о пользователе
    
    Attributes:
        id: ID пользователя
        name: Имя пользователя
        email: Email пользователя
    """
    id: str = Field(..., min_length=1, description="ID пользователя")
    name: str = Field(..., min_length=1, description="имя пользователя")
    email: str = Field(..., min_length=1, description="email пользователя")
    

class _ChangeItem(BaseModel):
    """
    Модель элемента изменений в истории
    
    Attributes:
        item: Название измененного элемента
        value: Новое значение
    """
    item: str = Field(..., min_length=1, description="название измененного элемента")
    value: str = Field(..., description="новое значение")
    

class _HistoryItem(BaseModel):
    """
    Модель элемента истории изменений
    
    Attributes:
        name: Название операции
        created_at: Время создания (ISO timestamp)
        user: Информация о пользователе
        changelist: Список изменений
    """
    name: str = Field(..., min_length=1, description="название операции")
    created_at: str = Field(..., description="время создания (ISO timestamp)")
    user: _UserInfo = Field(..., description="информация о пользователе")
    changelist: List[_ChangeItem] = Field(..., description="список изменений")
    
    
class DocumentContextModel(BaseModel):
    """
    Модель документа в контексте
    
    Attributes:
        document_id: ID документа
        name: Название документа
        question: Вопрос документа
        answer: Ответ документа
        status: Статус документа
        modified_at: Время изменения (ISO timestamp)
        expired_at: Время истечения (ISO timestamp, опционально)
        ext: Дополнительные данные
        paraphrases_count: Количество парафразов
        suggested_paraphrases_count: Количество предложенных парафразов
        paraphrases: Список парафразов
        attachments: Список вложений
        context: Контекстные данные
        answers: Список ответов на разных языках
        history: История изменений документа
    """
    name: str = Field(..., min_length=1, description="название документа")
    question: str = Field(..., min_length=1, description="вопрос документа")
    answer: str = Field(..., min_length=1, description="ответ документа")
    status: _DocumentStatus = Field(..., description="статус документа")
    modified_at: str = Field(..., description="время изменения (ISO timestamp)")
    expired_at: Optional[str] = Field(default=None, description="время истечения (ISO timestamp)")
    ext: Dict[str, Any] = Field(default_factory=dict, description="дополнительные данные")
    paraphrases_count: int = Field(..., ge=0, description="количество парафразов")
    suggested_paraphrases_count: int = Field(..., ge=0, description="количество предложенных парафразов")
    paraphrases: List[_ParaphraseItem] = Field(..., description="список парафразов")
    attachments: List[_AttachmentItem] = Field(..., description="список вложений")
    context: Dict[str, Any] = Field(default_factory=dict, description="контекстные данные")
    answers: List[_AnswerItem] = Field(..., description="список ответов на разных языках")
    history: List[_HistoryItem] = Field(..., description="история изменений документа")
    
    
class DocumentTagsModel(BaseModel):
    """
    Модель валидации запроса для обновления тегов документа.
    
    Attributes:
        tags: Список тегов документа
    """
    tags: List[str] = Field(..., description="список тегов документа")
    
    
class CreateParaphraseModel(BaseModel):
    """
    Модель валидации запроса для создания парафраза.
    
    Attributes:
        service_id: ID сервиса, к которому принадлежит документ
        document_id: ID документа, для которого создается парафраз
        paraphrase: Текст парафраза
        author: Автор парафраза

    """
    service_id: int = Field(..., gt=0, description="ID сервиса, к которому принадлежит документ")
    document_id: int = Field(..., gt=0, description="ID документа, для которого создается парафраз")
    paraphrase: str = Field(..., min_length=1, max_length=5000, description="текст парафраза")
    author: str = Field(..., min_length=1, max_length=255, description="автор парафраза")
    

class GetParaphrasesyParamsModel(BaseModel):
    """
    Модель валидации query-параметров для эндпоинта получения парафразов.
    
    Attributes:
        document_id: ID документа (обязательный параметр)
        limit_paraphrases: Ограничение на количество формулировок в ответе
        offset_paraphrases: Смещение на выдачу формулировок в ответе
        offset: Pagination offset (alias for offset_paraphrases, default 0)
        count: Pagination count (alias for limit_paraphrases, default 9999)
        sort_by: Поле для сортировки - 'id' или 'modified_at' (default 'id')
        sort_order: Порядок сортировки - 'asc' или 'desc' (default 'asc')

    """
    document_id: int = Field(..., gt=0, description="ID документа")
    limit_paraphrases: Optional[int] = Field(default=None, ge=1, description="ограничение на количество формулировок в ответе")
    offset_paraphrases: Optional[int] = Field(default=None, ge=0, description="смещение на выдачу формулировок в ответе")
    offset: Optional[int] = Field(default=0, ge=0, description="pagination offset (default 0) (alias for offset_paraphrases)")
    count: Optional[int] = Field(default=None, ge=1, description="pagination count (default 9999) (alias for limit_paraphrases)")
    sort_by: Optional[str] = Field(default="id", description="sort by 'id' or 'modified_at' (default is 'id')")
    sort_order: Literal["asc", "desc"] = Field(default="asc", description="sorting order 'asc' or 'desc' (default is 'asc')")
    
    
class MassUpdateParaphraseItemModel(BaseModel):
    """
    Модель элемента парафраза для обновления.
    
    Attributes:
        paraphrase_id: ID парафраза для обновления
        text: Новый текст парафраза
        author: Автор парафраза
    """
    paraphrase_id: int = Field(..., gt=0, description="ID парафраза для обновления")
    text: str = Field(..., min_length=1, max_length=5000, description="новый текст парафраза")
    author: str = Field(..., min_length=1, max_length=255, description="автор парафраза")
    

class UpdateParaphraseItemModel(BaseModel):
    """
    Модель элемента парафраза для обновления.
    
    Attributes:
        text: Новый текст парафраза
        author: Автор парафраза
    """
    text: str = Field(..., min_length=1, max_length=5000, description="новый текст парафраза")
    author: str = Field(..., min_length=1, max_length=255, description="автор парафраза")
    

class MassUpdateParaphrasesModel(BaseModel):
    """
    Модель валидации запроса для массового обновления парафразов.
    
    Attributes:
        paraphrases: Список парафразов для обновления
    """
    paraphrases: List[MassUpdateParaphraseItemModel] = Field(..., min_items=1, description="список парафразов для обновления")
    
    
class MoveParaphraseItemModel(BaseModel):
    """
    Модель элемента парафраза для перемещения.
    
    Attributes:
        paraphrase_id: ID парафраза для перемещения
        text: Текст парафраза
        document_id: Исходный ID документа парафраза
        target_document_id: Целевой ID документа для перемещения
    """
    paraphrase_id: int = Field(..., gt=0, description="ID парафраза для перемещения")
    text: str = Field(..., min_length=1, max_length=5000, description="текст парафраза")
    document_id: int = Field(..., gt=0, description="исходный ID документа парафраза")
    target_document_id: int = Field(..., gt=0, description="целевой ID документа для перемещения")
    
    
class MassMoveParaphrasesModel(BaseModel):
    """
    Модель валидации запроса для массового перемещения парафразов.
    
    Используется для валидации тела запроса к API перемещения парафразов
    между документами. Поддерживает перемещение нескольких парафразов за один запрос.
    
    Attributes:
        paraphrases: Список парафразов для перемещения
    """
    paraphrases: List[MoveParaphraseItemModel] = Field(..., min_items=1, description="список парафразов для перемещения")
    
    
class GroupsListModel(BaseModel):
    """
    Модель валидации запроса для объеденение группы сервисов.
    
    Attributes:
        services: Список ID сервисов для включения в группу
    """
    services: List[int] = Field(..., description="список ID сервисов для включения в группу")


class CreateServiceTermModel(BaseModel):
    """
    Модель валидации запроса для создания синонимов сервиса.
    
    Attributes:
        term: Основной термин
        synonyms: Список синонимов для термина
        
    """
    term: str = Field(..., min_length=1, max_length=255, description="основной термин")
    synonyms: List[str] = Field(default_factory=list, description="список синонимов для термина")
    
    
class CreateUserTermModel(BaseModel):
    """
    Модель валидации запроса для создания синонимов сервиса.
    
    Attributes:
        term: Основной термин
        synonyms: Список синонимов для термина
        
    """
    term: str = Field(..., min_length=1, max_length=255, description="основной термин")
    synonyms: List[str] = Field(default_factory=list, description="список синонимов для термина")