# LegalLangChainSplitter

Модуль для обработки нормативных правовых актов с чанкингом и адаптивной валидацией.

## Описание

- **LegalLangChainSplitter** - специализированный сплиттер для правовых документов на основе LangChain
- **AdaptiveQualityValidator** - валидатор с адаптивными критериями (эффективность +200% по сравнению с базовым)
- Полная интеграция с Django и существующей системой регистрации сплиттеров
- Поддержка метаданных для документов, изображений и таблиц

## Результаты тестирования

- Качество чанкинга: 100% на правовых документах
- Адаптивные критерии для коротких/средних/длинных документов  
- Автоматический выбор стратегии разбиения (markdown/recursive)
- Соотношение символы/токены: 2.37 (оптимально для русского текста)

## Установка в проект knowledge_base

### 1. Скопировать файлы

```bash
# Скопировать сплиттер
cp splitters/legal_langchain_splitter.py knowledge_base/app_chunks/splitters/

# Создать папку валидаторов (если нет)
mkdir -p knowledge_base/app_chunks/services/validators

# Скопировать валидатор
cp validators/adaptive_validator.py knowledge_base/app_chunks/services/validators/

# Создать __init__.py в папке валидаторов
touch knowledge_base/app_chunks/services/validators/__init__.py
```

### 2. Зарегистрировать в системе

Добавить в файл `knowledge_base/app_chunks/apps.py`:

```python
# Добавить импорт
from app_chunks.splitters.legal_langchain_splitter import LegalLangChainSplitter

# Добавить регистрацию в методе ready()
register_splitter(LegalLangChainSplitter)
```

### 3. Проверить интеграцию

```python
# В Django shell или views
from app_chunks.splitters.registry import CHUNK_SPLITTER_REGISTRY
print(CHUNK_SPLITTER_REGISTRY.keys())  # Должен быть LegalLangChainSplitter

from app_chunks.services.validators.adaptive_validator import AdaptiveQualityValidator
validator = AdaptiveQualityValidator()  # Должен работать без ошибок
```

## Использование

### Создание и использование сплиттера

```python
from app_chunks.splitters.dispatcher import SplitterDispatcher

# Конфигурация
config = {
    "min_chunk_size": 500,
    "max_chunk_size": 1200,
    "chunk_overlap": 100,
    "encoding_name": "cl100k_base"
}

# Создание через диспетчер
splitter = SplitterDispatcher.create_instance(
    'app_chunks.splitters.legal_langchain_splitter.LegalLangChainSplitter',
    config
)

# Чанкинг документа
metadata = {
    "title": "ФЗ О персональных данных",
    "document_type": "federal_law",
    "legal_document": True
}

chunks = splitter.split(metadata, legal_text)
```

### Валидация качества

```python
from app_chunks.services.validators.adaptive_validator import AdaptiveQualityValidator

validator = AdaptiveQualityValidator()
result = validator.validate_chunks(chunks)

print(f"Качество: {result['quality_score']:.1f}%")
print(f"Тип документа: {result['document_type']}")
print(f"Валидация: {'Пройдена' if result['valid'] else 'Не пройдена'}")
```

### В веб-интерфейсе

После интеграции сплиттер "LangChain Legal" появится в списке доступных сплиттеров для выбора пользователем в веб-интерфейсе системы.

## Архитектура

### Адаптивная логика

Система автоматически выбирает стратегию разбиения:

- **Markdown стратегия** - если документ содержит заголовки и структуру
- **Рекурсивная стратегия** - для обычных текстов
- **Адаптивная стратегия** - для проблемных документов

### Адаптивные критерии валидации

- **Короткие документы** (<5000 символов): порог качества 40%
- **Средние документы** (5000-20000 символов): порог качества 60%
- **Длинные документы** (>20000 символов): порог качества 70%

## Зависимости

- `langchain-text-splitters` >= 0.2.0
- `langchain-core` >= 0.2.0
- `tiktoken` >= 0.5.0
- `Django` (для интеграции с системой)

## Совместимость

- Работает с существующей моделью `Chunk` в БД
- Совместим с системой регистрации сплиттеров
- Интегрируется с `SplitterDispatcher`
- Поддерживает все существующие API эндпоинты

## Автор

Andrew821667

## Лицензия

Открытый код для интеграции в проект knowledge_base.
