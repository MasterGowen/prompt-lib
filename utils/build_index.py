#!/usr/bin/env python3
"""
Build Index Script
Генерирует индекс всех файлов в README.md для быстрой навигации.
"""

import re
from pathlib import Path
from datetime import datetime

SOURCE_FOLDERS = ['roles', 'skills', 'workflows', 'experiments', 'comparisons', 'snippets']
README_FILE = 'README.md'


def parse_frontmatter(content: str) -> dict:
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
            
            if value.startswith('[') and value.endswith(']'):
                items = value[1:-1].split(',')
                metadata[key] = [item.strip() for item in items if item.strip()]
            else:
                metadata[key] = value
    
    return metadata


def collect_files():
    """Собирает информацию о всех файлах."""
    index = {folder: [] for folder in SOURCE_FOLDERS}
    
    for folder in SOURCE_FOLDERS:
        folder_path = Path(folder)
        if not folder_path.exists():
            continue
        
        for filepath in sorted(folder_path.rglob('*.md')):
            try:
                content = filepath.read_text(encoding='utf-8')
                metadata = parse_frontmatter(content)
                
                if metadata:
                    index[folder].append({
                        'path': filepath,
                        'type': metadata.get('type', 'unknown'),
                        'status': metadata.get('status', 'unknown'),
                        'tags': metadata.get('tags', []),
                        'models': metadata.get('models', []),
                        'experiment_id': metadata.get('experiment_id'),
                        'comparison_id': metadata.get('comparison_id'),
                    })
            except Exception as e:
                print(f"⚠️  Ошибка чтения {filepath}: {e}")
    
    return index


def generate_index_table(index: dict) -> str:
    """Генерирует Markdown-таблицу индекса."""
    lines = [
        "## 📋 Индекс файлов",
        "",
        f"*Обновлено: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        "",
    ]
    
    folder_names = {
        'roles': '🎭 Роли',
        'skills': '💪 Навыки',
        'workflows': '⚙️ Воркфлоу',
        'experiments': '🧪 Эксперименты',
        'comparisons': '⚖️ Сравнения',
        'snippets': '📝 Сниппеты',
    }
    
    for folder, name in folder_names.items():
        files = index.get(folder, [])
        
        lines.append(f"### {name} ({len(files)})")
        lines.append("")
        
        if files:
            lines.append("| Файл | Статус | Теги | Модели |")
            lines.append("|------|--------|------|--------|")
            
            for file_info in files:
                status_emoji = {
                    'verified': '✅',
                    'draft': '📝',
                    'deprecated': '❌',
                }.get(file_info['status'], '❓')
                
                tags_str = ', '.join(file_info['tags'][:3])  # Первые 3 тега
                if len(file_info['tags']) > 3:
                    tags_str += '...'
                
                models_str = ', '.join(file_info['models'][:2])  # Первые 2 модели
                if len(file_info['models']) > 2:
                    models_str += '...'
                
                extra = ""
                if file_info.get('experiment_id'):
                    extra = f" `{file_info['experiment_id']}`"
                if file_info.get('comparison_id'):
                    extra = f" `{file_info['comparison_id']}`"
                
                lines.append(
                    f"| [{file_info['path'].name}]({file_info['path']}) | "
                    f"{status_emoji} {file_info['status']} | "
                    f"{tags_str or '-'} | "
                    f"{models_str or '-'}{extra} |"
                )
        else:
            lines.append("*Пока нет файлов*")
        
        lines.append("")
    
    return '\n'.join(lines)


def update_readme():
    """Обновляет секцию индекса в README.md."""
    readme_path = Path(README_FILE)
    
    if not readme_path.exists():
        print(f"❌ Файл {README_FILE} не найден")
        return
    
    content = readme_path.read_text(encoding='utf-8')
    
    # Находим секцию индекса
    index_pattern = r'(## 📋 Индекс файлов\n\n.*?)(\n## |\Z)'
    match = re.search(index_pattern, content, re.DOTALL)
    
    if not match:
        print("⚠️  Секция индекса не найдена в README.md")
        print("Добавьте секцию '## 📋 Индекс файлов' в README.md")
        return
    
    # Собираем индекс и генерируем новую таблицу
    index = collect_files()
    new_index = generate_index_table(index)
    
    # Заменяем старую секцию на новую
    new_content = content[:match.start()] + new_index + '\n' + content[match.end():]
    
    readme_path.write_text(new_content, encoding='utf-8')
    print(f"✅ Индекс обновлен в {README_FILE}")
    
    # Вывод статистики
    total = sum(len(files) for files in index.values())
    print(f"📊 Всего файлов: {total}")
    for folder, files in index.items():
        if files:
            print(f"   {folder}: {len(files)}")


if __name__ == '__main__':
    update_readme()
