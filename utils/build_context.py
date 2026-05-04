#!/usr/bin/env python3
"""
Build Context Script
Собирает все промпты из репозитория в единый файл с фильтрацией по тегам, статусу и типам.

Использование:
    python build_context.py                          # собрать всё
    python build_context.py --status verified        # только проверенные
    python build_context.py --tags python,refactor   # по тегам
    python build_context.py --experiment EXP-001     # конкретный эксперимент
    python build_context.py --type role,skill        # по типам
    python build_context.py --output my_context.md   # свой файл вывода
"""

import os
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Set

# Папки для сканирования
SOURCE_FOLDERS = ['roles', 'skills', 'workflows', 'experiments', 'comparisons', 'snippets']
DEFAULT_OUTPUT = 'generated_context.md'


def parse_frontmatter(content: str) -> Dict:
    """Извлекает YAML frontmatter из файла."""
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not match:
        return {}
    
    fm_text = match.group(1)
    metadata = {}
    
    for line in fm_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            # Парсим списки [item1, item2]
            if value.startswith('[') and value.endswith(']'):
                items = value[1:-1].split(',')
                metadata[key] = [item.strip() for item in items if item.strip()]
            else:
                metadata[key] = value
    
    return metadata


def read_file_with_metadata(filepath: Path) -> Optional[Dict]:
    """Читает файл и возвращает контент с метаданными."""
    try:
        content = filepath.read_text(encoding='utf-8')
        metadata = parse_frontmatter(content)
        
        if not metadata:
            print(f"⚠️  Файл без frontmatter: {filepath}")
            return None
        
        # Находим тело промпта (после frontmatter)
        body_match = re.search(r'^---\n.*?\n---\n(.*)', content, re.DOTALL)
        body = body_match.group(1).strip() if body_match else content
        
        return {
            'path': filepath,
            'metadata': metadata,
            'body': body,
            'full_content': content
        }
    except Exception as e:
        print(f"❌ Ошибка чтения {filepath}: {e}")
        return None


def matches_filters(item: Dict, args) -> bool:
    """Проверяет, соответствует ли элемент фильтрам."""
    meta = item['metadata']
    
    # Фильтр по статусу
    if args.status:
        if meta.get('status') != args.status:
            return False
    
    # Фильтр по типам
    if args.type:
        allowed_types = [t.strip() for t in args.type.split(',')]
        if meta.get('type') not in allowed_types:
            return False
    
    # Фильтр по тегам (должен содержать хотя бы один из указанных)
    if args.tags:
        required_tags = [t.strip() for t in args.tags.split(',')]
        file_tags = meta.get('tags', [])
        if not any(tag in file_tags for tag in required_tags):
            return False
    
    # Фильтр по экспериментам
    if args.experiment:
        if meta.get('experiment_id') != args.experiment:
            return False
    
    # Фильтр по сравнениям
    if args.comparison:
        if meta.get('comparison_id') != args.comparison:
            return False
    
    # Фильтр по моделям
    if args.models:
        required_models = [m.strip() for m in args.models.split(',')]
        file_models = meta.get('models', [])
        if not any(model in file_models for model in required_models):
            return False
    
    return True


def collect_files(args) -> List[Dict]:
    """Собирает все файлы из исходных папок."""
    collected = []
    
    for folder in SOURCE_FOLDERS:
        folder_path = Path(folder)
        if not folder_path.exists():
            continue
        
        for filepath in folder_path.rglob('*.md'):
            item = read_file_with_metadata(filepath)
            if item and matches_filters(item, args):
                collected.append(item)
    
    # Сортировка: сначала verified, потом по типу, потом по имени
    status_order = {'verified': 0, 'draft': 1, 'deprecated': 2}
    collected.sort(key=lambda x: (
        status_order.get(x['metadata'].get('status'), 99),
        x['metadata'].get('type', ''),
        x['path'].name
    ))
    
    return collected


def build_context(items: List[Dict], args) -> str:
    """Генерирует итоговый контекст-файл."""
    lines = [
        "# Generated AI Context",
        f"Generated: {datetime.now().isoformat()}",
        f"Filters: status={args.status or 'all'}, tags={args.tags or 'all'}, types={args.type or 'all'}",
        f"Total files: {len(items)}",
        "",
        "---",
        ""
    ]
    
    for item in items:
        meta = item['metadata']
        
        # Добавляем разделитель и информацию о файле
        lines.append(f"## File: {item['path']}")
        lines.append(f"**Type**: {meta.get('type', 'unknown')}")
        lines.append(f"**Status**: {meta.get('status', 'unknown')}")
        lines.append(f"**Tags**: {', '.join(meta.get('tags', []))}")
        if meta.get('models'):
            lines.append(f"**Models**: {', '.join(meta.get('models', []))}")
        if meta.get('experiment_id'):
            lines.append(f"**Experiment ID**: {meta.get('experiment_id')}")
        if meta.get('comparison_id'):
            lines.append(f"**Comparison ID**: {meta.get('comparison_id')}")
        lines.append("")
        lines.append("### Content")
        lines.append("")
        lines.append(item['body'])
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Сборка контекста из базы знаний AI')
    parser.add_argument('--status', choices=['draft', 'verified', 'deprecated'], help='Фильтр по статусу')
    parser.add_argument('--tags', help='Фильтр по тегам (через запятую)')
    parser.add_argument('--type', help='Фильтр по типам (role,skill,workflow,...)')
    parser.add_argument('--experiment', help='Фильтр по ID эксперимента')
    parser.add_argument('--comparison', help='Фильтр по ID сравнения')
    parser.add_argument('--models', help='Фильтр по моделям (qwen,claude,gpt4)')
    parser.add_argument('--output', default=DEFAULT_OUTPUT, help=f'Выходной файл (по умолчанию: {DEFAULT_OUTPUT})')
    parser.add_argument('--quiet', action='store_true', help='Не выводить статистику')
    
    args = parser.parse_args()
    
    # Сбор файлов
    print(f"🔍 Сканирование папок: {', '.join(SOURCE_FOLDERS)}")
    items = collect_files(args)
    
    if not items:
        print("⚠️  Ничего не найдено по заданным фильтрам")
        return
    
    # Генерация контекста
    context = build_context(items, args)
    
    # Запись в файл
    output_path = Path(args.output)
    output_path.write_text(context, encoding='utf-8')
    
    if not args.quiet:
        print(f"\n✅ Контекст собран!")
        print(f"📁 Файл: {output_path.absolute()}")
        print(f"📊 Файлов включено: {len(items)}")
        print(f"📏 Размер: {output_path.stat().st_size / 1024:.2f} KB")
        
        # Статистика по типам
        type_counts = {}
        for item in items:
            t = item['metadata'].get('type', 'unknown')
            type_counts[t] = type_counts.get(t, 0) + 1
        
        if type_counts:
            print("\n📈 По типам:")
            for t, count in sorted(type_counts.items()):
                print(f"   {t}: {count}")


if __name__ == '__main__':
    main()
