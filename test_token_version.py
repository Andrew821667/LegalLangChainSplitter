
# 🧪 ТЕСТ ИСПРАВЛЕННОЙ ВЕРСИИ

import sys
sys.path.append('.')

from legal_langchain_splitter_token_fixed import LegalLangChainSplitter

# Конфигурация в ТОКЕНАХ
config = {
    "min_chunk_size": 500,    # ТОКЕНЫ
    "max_chunk_size": 1200,   # ТОКЕНЫ
    "chunk_overlap": 100,     # ТОКЕНЫ
    "encoding_name": "cl100k_base"
}

print("🧪 Тестирование исправленной версии...")

splitter = LegalLangChainSplitter(config)

# Тестовый правовой текст
test_text = """
Статья 1. Основные понятия

В настоящем Федеральном законе используются следующие основные понятия:

Пункт 1. Персональные данные - любая информация, относящаяся к прямо или косвенно определенному или определяемому физическому лицу (субъекту персональных данных).

Пункт 2. Оператор - государственный орган, муниципальный орган, юридическое или физическое лицо, самостоятельно или совместно с другими лицами организующие и (или) осуществляющие обработку персональных данных.

Статья 2. Правовое регулирование

Отношения, связанные с обработкой персональных данных, осуществляемой федеральными органами государственной власти, органами государственной власти субъектов Российской Федерации и органами местного самоуправления, регулируются федеральным законодательством.
""" * 4  # Увеличиваем для получения чанков

test_metadata = {
    "title": "ФЗ О персональных данных",
    "legal_document": True
}

print(f"📊 Исходный текст: {splitter._count_tokens(test_text)} токенов")

# Разбиваем
chunks = splitter.split(test_metadata, test_text)

print(f"📦 Получено чанков: {len(chunks)}")

for i, chunk in enumerate(chunks):
    metadata = chunk.metadata
    content = chunk.page_content
    
    print(f"\n📄 Чанк {i+1}:")
    print(f"   🔢 Токенов: {metadata['token_count']}")
    print(f"   📏 Символов: {metadata['char_count']}")
    print(f"   ✅ В диапазоне: {metadata['in_target_range']}")
    print(f"   📝 Начало: {content[:80]}...")

print("\n🎯 Проверка диапазонов:")
for i, chunk in enumerate(chunks):
    tokens = chunk.metadata['token_count']
    in_range = 500 <= tokens <= 1200
    status = "✅" if in_range else "⚠️"
    print(f"{status} Чанк {i+1}: {tokens} токенов")
