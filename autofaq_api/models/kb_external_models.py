from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator
from typing import List, Optional, Literal
from datetime import datetime
import uuid

REASONS_LITERAL = Literal['ClosedByBot', 'ClosedByOperator', 'ClosedByOperatorWithBot', 'ClosedByTimer']
STATUSES = ['ClosedByBot', 'ClosedByOperator', 'ClosedByOperatorWithBot', 'ClosedByTimer']

class _ChannelUser(BaseModel):
    id: str = Field(..., description="ID пользователя")
    login: str = Field(..., description="Логин пользователя")
    email: str = Field(..., description="Email пользователя")
    phone: str = Field(..., description="Телефон пользователя")
    fullName: str = Field(..., description="Полное имя пользователя")
    payload: dict = Field(default={}, description="Дополнительные данные пользователя")

    class Config:
        populate_by_name = True
     
class _Operator(BaseModel):
    email: str = Field(None, description="Email оператора")
    login: str = Field(None, description="Логин оператора")
    phone: str = Field(None, description="Телефон оператора")
    fullName: str = Field(None, description="Полное имя оператора")
    payload: dict = Field(default={}, description="Дополнительные данные оператора")
    

class QuestionModel(BaseModel):
    dt: datetime = Field(..., description="Дата и время сообщения")
    text: str = Field(..., description="Текст сообщения")
    fileIds: List[str] = Field(default=[], description="Список ID файлов")
    channelUser: _ChannelUser = Field(..., description="Информация о пользователе канала")
    
    @field_validator('fileIds')
    def validate_file_ids(cls, v):
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid UUID format: {v}")

    @field_validator('dt')
    def validate_dt_format(cls, v):
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00')).isoformat().split('+')[0]+'Z'
            except ValueError:
                raise ValueError("Invalid datetime format. Expected ISO 8601 format")
        elif isinstance(v, datetime):
            return v.isoformat().split('+')[0]+'Z'
        return v

    # class Config:
    #     json_encoders = {
    #         datetime: lambda v: v.isoformat().replace('+00:00', 'Z')
    #     }
    #     populate_by_name = True
    
    
class CloseСonversationModel(BaseModel):
    reason: REASONS_LITERAL = Field(default='ClosedByBot', description="Причина закрытия")
    closeToAutofaqServiceId: int = Field(None, description="ID сервиса AutoFAQ")
    closeToAutofaqDocumentId: int = Field(None, description="ID документа AutoFAQ")
    operator: _Operator = Field(None, description="Информация об операторе")
    
    
class GetConversationsModel(BaseModel):
    tsFrom: Optional[datetime] = Field(None, description="Начальная дата периода")
    tsTo: Optional[datetime] = Field(None, description="Конечная дата периода")
    limit: Optional[int] = Field(50, ge=1, le=100, description="Лимит записей (1-100)")
    page: Optional[int] = Field(1, ge=1, description="Номер страницы")
    orderDirection: Optional[Literal["Asc", "Desc"]] = Field("Desc", description="Направление сортировки")
    conversationStatusList: Optional[List[str]] = Field(None, description="Список статусов диалогов")
    channelUserQuery: Optional[str] = Field(None, description="Поиск по пользователю канала")
    participatingOperatorList: Optional[List[str]] = Field(None, description="Список операторов")
    themeList: Optional[List[str]] = Field(None, description="Список тем")
    groupList: Optional[List[str]] = Field(None, description="Список групп")

    @field_validator('tsTo')
    def validate_date_range(cls, v, values):
        if 'tsFrom' in values and values['tsFrom'] and v:
            if v <= values['tsFrom']:
                raise ValueError('tsTo must be greater than tsFrom')
        return v

    @field_validator('conversationStatusList')
    def validate_conversation_status(cls, v):
        for i in v:
            if i not in STATUSES:
                raise ValueError(f'Status must be one of: {", ".join(STATUSES)}')
        return v
    
    
class _Interval(BaseModel):
    start: datetime = Field(..., description="Начало интервала")
    end: datetime = Field(..., description="Конец интервала")

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def validate_end_after_start(self):
        if self.end <= self.start:
            raise ValueError('end must be after start')
        return self


class _EveryWeekPlan(BaseModel):
    daysOfWeek: List[Literal["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]] = Field(
        ..., description="Дни недели"
    )
    time: str = Field(..., pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$', description="Время в формате HH:MM:SS")
    timezone: str = Field(..., description="Часовой пояс")

    model_config = ConfigDict(from_attributes=True)
    
    
class _Plan(BaseModel):
    everyWeek: _EveryWeekPlan = Field(..., description="План на каждую неделю")

    model_config = ConfigDict(from_attributes=True)


class _TextContent(BaseModel):
    value: str = Field(..., description="Текст сообщения")
    type: Literal["text"] = Field("text", description="Тип контента")

    model_config = ConfigDict(from_attributes=True)


class _FilterItem(BaseModel):
    userId: Optional[str] = Field(None, description="ID пользователя")
    userFullName: Optional[str] = Field(None, description="Полное имя пользователя")
    userPhone: Optional[str] = Field(None, description="Телефон пользователя")
    userPayload_studentId: Optional[str] = Field(None, alias="userPayload.studentId", description="Student ID из payload")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class PostDelayedDeliveryModel(BaseModel):
    serviceId: str = Field(..., description="ID сервиса")
    groupId: str = Field(None, description="ID группы")
    channelId: str = Field(..., description="ID канала")
    state: Literal["Active", "Inactive", "Draft"] = Field(..., description="Статус рассылки")
    name: str = Field(None, min_length=1, max_length=255, description="Название рассылки")
    title: str = Field(..., min_length=1, max_length=255, description="Заголовок рассылки")
    description: Optional[str] = Field(None, description="Описание рассылки")
    interval: _Interval = Field(None, description="Интервал рассылки")
    plan: _Plan = Field(None, description="План рассылки")
    text: _TextContent = Field(..., description="Текст сообщения")
    filterType: Literal["static", "dynamic",] = Field(..., description="Тип фильтра")
    filter: List[_FilterItem] = Field(None, description="Фильтр пользователей")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True
    )


class VarModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название")
    value: str = Field(..., min_length=1, max_length=500, description="Значение")
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        from_attributes=True
    )

class _DateRange(BaseModel):
    from_: datetime = Field(..., alias="from")
    to: datetime

    class Config:
        populate_by_name = True
        
    @field_validator('from_')
    def validate_dt_format(cls, v, values):
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00')).isoformat().split('+')[0]+'Z'
            except ValueError:
                raise ValueError("Invalid datetime format. Expected ISO 8601 format")
        elif isinstance(v, datetime):
            return v.isoformat().split('+')[0]+'Z'
        return v

    @field_validator('to')
    def validate_to_date(cls, v, values):
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00')).isoformat().split('+')[0]+'Z'
            except ValueError:
                raise ValueError("Invalid datetime format. Expected ISO 8601 format")
        elif isinstance(v, datetime):
            return v.isoformat().split('+')[0]+'Z'
        return v
    
    
class ConversationsCountReportModel(BaseModel):
    dateRange: _DateRange = Field(..., description="Интервал времени")
    dateGrouping: Literal["ByDay", "ByWeek", "ByMonth", "ByYear"] = Field("ByWeek")
    additionalGrouping: Literal["ByGroup", "ByChannel", "ByOperator"] = Field("ByGroup")
    knowledgeBases: list = Field(default=[])
    documentTags: list = Field(default=[])
    groups: list = Field(default=[])
    filters: list = Field(default=[])


class OperatorsReportModel(BaseModel):
    dateRange: _DateRange = Field(..., description="Временной диапазон отчета")
    operators: list = Field(default=[], description="Список операторов для фильтрации")
    groups: list = Field(default=[], description="Список групп для фильтрации")
    dateGrouping: Literal["ByDay", "ByWeek", "ByMonth", "ByYear"] = Field(
        "ByDay", 
        description="Группировка по дате"
    )
    additionalGrouping: Literal["ByOperator", "ByGroup", "ByChannel", "None"] = Field(
        "ByGroup", 
        description="Дополнительная группировка"
    )
    knowledgeBases: list = Field(default=[], description="Список баз знаний для фильтрации")