---
type: snippet
tags: [error-handling, validation, python]
models: [qwen, claude, gpt4]
status: verified
created: 2024-01-01
updated: 2024-01-01
---

# Валидация входных данных (Python)

## Сниппет промпта
Используй этот паттерн для генерации кода валидации:

```
При работе с пользовательским вводом всегда применяй следующий паттерн:
1. Явно объяви ожидаемую схему данных (тип, диапазон, формат)
2. Используй early validation — отклоняй невалидные данные как можно раньше
3. Возвращай понятные ошибки с указанием поля и причины
4. Для сложных структур используй библиотеки валидации (pydantic, marshmallow)
5. Логируй попытки невалидного ввода для мониторинга атак

Пример на Python:
```python
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional

class UserInput(BaseModel):
    email: EmailStr
    age: int = Field(ge=0, le=150)
    username: str = Field(min_length=3, max_length=20)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

# Использование
try:
    user = UserInput(**request_data)
except ValidationError as e:
    return {"error": "Invalid input", "details": e.errors()}
```
```

## Когда использовать
- Генерация API endpoints
- Обработка форм
- Парсинг конфигов
- Работа с внешними данными

## Модели
Работает стабильно на Qwen, Claude, GPT-4
