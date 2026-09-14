# VKBotKit

Python-фреймворк для создания чат-ботов в сообществах ВКонтакте. Работает поверх VK Bots API и `aiohttp`, помогает структурировать код бота и настраивать функционал.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/github/license/vkbotkit/vkbotkit)
![Version](https://img.shields.io/badge/version-1.3-green)

## Возможности

- Асинхронная работа на базе `aiohttp`
- Система фильтров для событий, сообщений и action-событий
- Регистрация обработчиков через callback-инструменты
- Работа с Longpoll
- Объекты для клавиатур, упоминаний и удобного тайпинга

## Установка

Проект пока не публикуется на PyPI. Установка из репозитория:

```bash
pip install git+https://github.com/vkbotkit/vkbotkit.git@v1.3
```

Или клонированием:

```bash
git clone https://github.com/vkbotkit/vkbotkit.git
cd vkbotkit
pip install -r requirements.txt
pip install .
```

## Требования

- Python 3.8+
- `aiohttp`
- Токен сообщества ВКонтакте с правами на работу с Bots API

## Быстрый старт

> ⚠️ Пример ниже — заглушка. Замените его рабочим кодом (см. репозиторий [examples](https://github.com/vkbotkit/examples/tree/v1.3)).

```python
from vkbotkit import ...

# 1. Создать бота с токеном сообщества
# 2. Зарегистрировать обработчик сообщений
# 3. Запустить longpoll
```

Готовый шаблон проекта: [vkbotkit/template](https://github.com/vkbotkit/template/tree/v1.3)

## Структура фреймворка

| Модуль | Назначение |
| --- | --- |
| `vkbotkit` | Основной функционал фреймворка |
| `vkbotkit.objects` | Вспомогательные объекты для работы модулей |
| `vkbotkit.objects.callback` | Инструменты для регистрации обработчиков |
| `vkbotkit.objects.data` | Обёртки вокруг dict |
| `vkbotkit.objects.enums` | Вспомогательные списки |
| `vkbotkit.objects.exceptions` | Исключения |
| `vkbotkit.objects.filters` | Фильтры |
| `vkbotkit.objects.filters.actions` | Фильтры для action-событий |
| `vkbotkit.objects.filters.events` | Фильтры для событий Longpoll |
| `vkbotkit.objects.filters.filter` | Базовые фильтры |
| `vkbotkit.objects.filters.message` | Фильтры для сообщений |
| `vkbotkit.objects.keyboard` | Объекты клавиатуры |
| `vkbotkit.objects.mention` | Объект упоминания |
| `vkbotkit.objects.package` | Объект события и объекты для тайпинга |
| `vkbotkit.utils` | Прикладные инструменты |

## Полезные ссылки

- [Шаблон проекта](https://github.com/vkbotkit/template/tree/v1.3)
- [Примеры](https://github.com/vkbotkit/examples/tree/v1.3)

## Лицензия

Распространяется на условиях лицензии, указанной в файле [LICENSE](https://github.com/vkbotkit/vkbotkit/blob/v1.3/LICENSE).
