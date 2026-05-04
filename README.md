# AI Knowledge Base & Workflow Repository

## 🎯 Назначение
Централизованное хранилище промптов, ролей, скиллов и рабочих процессов для эффективного взаимодействия с LLM. Репозиторий служит:
- **Базой знаний** для проверенных паттернов работы с ИИ
- **Контекстным источником** для формирования точных инструкций нейросетям
- **Полигоном** для экспериментов и сравнения моделей
- **Демонстрацией** глубины погружения в AI-разработку

## 📁 Структура

```
├── roles/              # Системные роли и персоны
├── skills/             # Конкретные навыки и умения
├── workflows/          # Последовательности действий (воркфлоу)
├── experiments/        # Гипотезы и тесты (тег: #experiment-ID)
├── comparisons/        # Сравнения моделей/подходов (тег: #comparison-ID)
├── snippets/           # Короткие промпты-кусочки
├── utils/              # Скрипты сборки контекста
└── .roo/               # Конфигурация для Roo Code
```

## 🏷️ Система тегирования

Каждый файл содержит YAML frontmatter с метаданными:

```yaml
---
type: role|skill|workflow|experiment|comparison|snippet
tags: [tag1, tag2]
models: [qwen, claude, gpt4]  # Для каких моделей актуально
vendor: [alibaba, anthropic, openai]
status: draft|verified|deprecated
experiment_id: EXP-001  # Для экспериментов
comparison_id: CMP-001  # Для сравнений
created: 2024-01-01
updated: 2024-01-01
---
```

### Типы файлов (`type`)
- `role` — кто я/агент (архитектор, ревьюер, дебаггер)
- `skill` — конкретное умение (рефакторинг, написание тестов)
- `workflow` — многошаговый процесс
- `experiment` — проверка гипотезы
- `comparison` — сравнение подходов/моделей
- `snippet` — короткий переиспользуемый фрагмент

### Статусы (`status`)
- `draft` — черновик, требует проверки
- `verified` — работает стабильно, можно использовать
- `deprecated` — устарело, не использовать

## 🚀 Быстрый старт

### 1. Добавление нового промпта
Создай файл в соответствующей папке с frontmatter:

```markdown
---
type: skill
tags: [python, refactoring, optimization]
models: [qwen, claude]
status: verified
---

# Оптимизация Python-кода

[Текст промпта...]
```

### 2. Сборка контекста
Используй скрипт для конкатенации с фильтрацией:

```bash
# Собрать всё
python utils/build_context.py

# Только верифицированные промпты по тегу
python utils/build_context.py --status verified --tags python,refactoring

# Только конкретный эксперимент
python utils/build_context.py --experiment EXP-001
```

### 3. Использование в Roo Code / VS Code
- Файл `.rooignore` исключает служебные файлы из контекста
- `AGENTS.md` дает общее описание проекта для ИИ-ассистентов
- `CONTEXT_SUMMARY.md` — краткая выжимка для быстрого понимания сути

## 📋 Индекс файлов

*Обновлено: 2026-05-04 22:43*

### 🎭 Роли (1)

| Файл | Статус | Теги | Модели |
|------|--------|------|--------|
| [senior-ai-architect.md](roles/senior-ai-architect.md) | ✅ verified | architect, system-design, planning | qwen, claude... |

### 💪 Навыки (1)

| Файл | Статус | Теги | Модели |
|------|--------|------|--------|
| [deep-code-review.md](skills/deep-code-review.md) | ✅ verified | code-review, quality, best-practices | qwen, claude... |

### ⚙️ Воркфлоу (1)

| Файл | Статус | Теги | Модели |
|------|--------|------|--------|
| [context-building.md](workflows/context-building.md) | ✅ verified | context-building, automation, preprocessing | qwen, claude... |

### 🧪 Эксперименты (1)

| Файл | Статус | Теги | Модели |
|------|--------|------|--------|
| [prompt-length-comparison.md](experiments/prompt-length-comparison.md) | 📝 draft | prompt-optimization, testing, hypothesis | qwen, claude `EXP-001` |

### ⚖️ Сравнения (0)

*Пока нет файлов*

### 📝 Сниппеты (1)

| Файл | Статус | Теги | Модели |
|------|--------|------|--------|
| [python-validation-pattern.md](snippets/python-validation-pattern.md) | ✅ verified | error-handling, validation, python | qwen, claude... |

🔧 Автоматизация

В репозитории предусмотрены скрипты:
- `utils/build_context.py` — сборка единого контекст-файла с фильтрами
- `utils/build_index.py` — обновление индекса файлов
- `utils/validate.py` — проверка корректности frontmatter

## 💡 Принципы

1. **Минимум оверхеда** — каждый файл должен приносить пользу
2. **Машиночитаемость** — структура позволяет парсить и фильтровать
3. **Версионирование** — git история хранит эволюцию промптов
4. **Актуальность** — устаревшее помечается `deprecated`, не удаляется сразу
