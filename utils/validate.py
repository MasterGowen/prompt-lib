#!/usr/bin/env python3
"""
Validate Script
Проверяет корректность frontmatter во всех файлах базы знаний.
"""

import re
from pathlib import Path

SOURCE_FOLDERS = ['roles', 'skills', 'workflows', 'experiments', 'comparisons', 'snippets']
VALID_TYPES = ['role', 'skill', 'workflow', 'experiment', 'comparison', 'snippet']
VALID_STATUSES = ['draft', 'verified', 'deprecated']
REQUIRED_FIELDS = ['type', 'tags', 'status']


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Извлекает YAML frontmatter и возвращает (metadata, body)."""
    match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if not match:
        return {}, ""
    
    fm_text = match.group(1)
    body = match.group(2)
    metadata = {}
    
    for line in fm_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if value.startswith('[') and value.endswith(']'):
                items = value[1:-1].split(',')
                metadata[key] = [item.strip() for item in items if item.strip()]
            else:
                metadata[key] = value
    
    return metadata, body


def validate_file(filepath: Path) -> list[str]:
    """Проверяет файл и возвращает список ошибок."""
    errors = []
    
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        return [f"Не удалось прочитать файл: {e}"]
    
    metadata, body = parse_frontmatter(content)
    
    # Проверка наличия frontmatter
    if not metadata:
        errors.append("❌ Отсутствует YAML frontmatter")
        return errors
    
    # Проверка обязательных полей
    for field in REQUIRED_FIELDS:
        if field not in metadata:
            errors.append(f"❌ Отсутствует обязательное поле '{field}'")
    
    # Проверка типа
    if 'type' in metadata:
        if metadata['type'] not in VALID_TYPES:
            errors.append(f"❌ Неверный тип '{metadata['type']}'. Допустимы: {', '.join(VALID_TYPES)}")
        
        # Проверка соответствия типа папке
        folder = filepath.parent.name
        type_to_folder = {
            'role': 'roles',
            'skill': 'skills',
            'workflow': 'workflows',
            'experiment': 'experiments',
            'comparison': 'comparisons',
            'snippet': 'snippets',
        }
        expected_folder = type_to_folder.get(metadata['type'])
        if expected_folder and folder != expected_folder:
            errors.append(f"⚠️  Файл типа '{metadata['type']}' должен быть в папке '{expected_folder}', а не в '{folder}'")
    
    # Проверка статуса
    if 'status' in metadata:
        if metadata['status'] not in VALID_STATUSES:
            errors.append(f"❌ Неверный статус '{metadata['status']}'. Допустимы: {', '.join(VALID_STATUSES)}")
    
    # Проверка тегов
    if 'tags' in metadata:
        if not isinstance(metadata['tags'], list) or len(metadata['tags']) == 0:
            errors.append("❌ Теги должны быть непустым списком")
    
    # Проверка experiment_id для экспериментов
    if metadata.get('type') == 'experiment':
        if 'experiment_id' not in metadata:
            errors.append("❌ Для типа 'experiment' обязательно поле 'experiment_id'")
        elif not re.match(r'^EXP-\d{3}$', metadata['experiment_id']):
            errors.append(f"⚠️  experiment_id должен быть в формате EXP-XXX (например, EXP-001), текущий: {metadata['experiment_id']}")
    
    # Проверка comparison_id для сравнений
    if metadata.get('type') == 'comparison':
        if 'comparison_id' not in metadata:
            errors.append("❌ Для типа 'comparison' обязательно поле 'comparison_id'")
        elif not re.match(r'^CMP-\d{3}$', metadata['comparison_id']):
            errors.append(f"⚠️  comparison_id должен быть в формате CMP-XXX (например, CMP-001), текущий: {metadata['comparison_id']}")
    
    # Проверка наличия тела промпта
    if not body or not body.strip():
        errors.append("⚠️  Файл не содержит тела промпта (только frontmatter)")
    
    # Предупреждение о пустых моделях
    if 'models' in metadata and (not metadata['models'] or len(metadata['models']) == 0):
        errors.append("⚠️  Поле 'models' указано, но пусто. Лучше удалить его или добавить модели.")
    
    return errors


def validate_all():
    """Запускает валидацию всех файлов."""
    print("🔍 Валидация файлов базы знаний...\n")
    
    total_files = 0
    files_with_errors = 0
    total_errors = 0
    
    for folder in SOURCE_FOLDERS:
        folder_path = Path(folder)
        if not folder_path.exists():
            continue
        
        for filepath in sorted(folder_path.rglob('*.md')):
            total_files += 1
            errors = validate_file(filepath)
            
            if errors:
                files_with_errors += 1
                total_errors += len(errors)
                
                print(f"\n📁 {filepath}")
                for error in errors:
                    print(f"   {error}")
    
    print("\n" + "="*50)
    print(f"📊 Итоги:")
    print(f"   Всего файлов: {total_files}")
    print(f"   Файлов с ошибками: {files_with_errors}")
    print(f"   Всего ошибок: {total_errors}")
    
    if total_errors == 0:
        print("\n✅ Все файлы валидны!")
    else:
        print(f"\n⚠️  Найдены проблемы. Исправьте их перед использованием.")
    
    return total_errors == 0


if __name__ == '__main__':
    success = validate_all()
    exit(0 if success else 1)
