# Асинхронный HTTP-сервер на Python

## 📦 Установка

1. Клонируйте репозиторий:
```bash
git https://github.com/PavelMartinelli/WebServer.git
cd webserver
```
2. Установите зависимости:

```bash
pip install -r requirements.txt
```

## 🚀 Запуск сервера
```bash
python run_server.py
```
Сервер запустится по адресу: http://localhost:8080 используя конфигурацию по умолчанию 

## ⚙️ Конфигурация
Измените файл server.json в корне проекта:

```json
{
  "host": "127.0.0.1",
  "port": 8080,
  "static_dir": "static",
  "open_file_cache": {
    "enabled": true,
    "max_size": 100
  }
}
```
Параметры:

host - IP сервера

port - порт сервера

static_dir - директория со статическими файлами

open_file_cache - настройки кэша файлов


## 🌟 Возможности
### 1. Статические файлы
### 2. Поддержка HTML, CSS, JS, изображений
### 3. Кэширование открытых файлов
### 4. Динамические маршруты. Обработка GET-параметров
### 5. Обработка ошибок
### 6. Кастомные страницы для ошибок (400, 403, 404, 500 и др.)
### 7. Защита от path traversal атак

## 🛠 Примеры использования
#### Главная страница:
```Copy
http://localhost:8080/
```
#### Пример с параметрами:

Приветствие: 
```Copy
http://localhost:8080/greet?name=John&age=25
```
Калькулятор:

```Copy
http://localhost:8080/calculator?a=15&b=5&op=mul
```