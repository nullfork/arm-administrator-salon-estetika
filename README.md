# АРМ администратора салона красоты "Эстетика"

Веб-приложение, разработанное в рамках выпускной квалификационной работы на тему:

**«Разработка автоматизированного рабочего места (АРМ) администратора салона красоты на примере ООО Салон красоты "Эстетика"»**

## О проекте

Система предназначена для автоматизации работы администратора салона красоты.

Приложение позволяет:
- вести клиентскую базу;
- управлять мастерами и услугами;
- оформлять записи клиентов;
- изменять статусы записей;
- проводить оплату;
- формировать квитанции;
- просматривать отчёты.

Проект реализован как учебный прототип на Flask и SQLite.

## Основные возможности

- авторизация пользователей;
- роли доступа;
- CRUD для клиентов;
- CRUD для мастеров;
- CRUD для услуг;
- журнал записей;
- фильтрация записей;
- заметки к записям;
- статусы записи;
- оплата и квитанция;
- отчёты по выручке, мастерам, услугам и расписанию.

## Технологический стек

- Python 3
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Login
- SQLite
- HTML / CSS
- Bootstrap 5

## Структура проекта

```text
arm-administrator-salon-estetika/
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── clients.py
│   │   ├── masters.py
│   │   ├── services.py
│   │   ├── appointments.py
│   │   ├── payments.py
│   │   └── reports.py
│   ├── templates/
│   └── static/
├── config.py
├── run.py
├── seed.py
├── requirements.txt
└── README.md
```

## Требования

Перед запуском должны быть установлены:
- Python 3.10 или выше
- Git
- pip
- venv

Проверка:

```bash
python --version
git --version
```

или:

```bash
python3 --version
git --version
```

---

# Установка и запуск

## 1. Клонирование репозитория

```bash
git clone https://github.com/nullfork/arm-administrator-salon-estetika.git
cd arm-administrator-salon-estetika
```

---

## 2. Запуск в Windows (PowerShell)

### Создание виртуального окружения

```powershell
python -m venv .venv
```

### Активация окружения

```powershell
.venv\Scripts\Activate.ps1
```

Если PowerShell запрещает запуск скриптов:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

После этого снова:

```powershell
.venv\Scripts\Activate.ps1
```

### Установка зависимостей

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Применение миграций

```powershell
flask --app run.py db upgrade
```

### Заполнение БД демонстрационными данными

```powershell
python seed.py
```

### Запуск проекта

```powershell
python run.py
```

Приложение будет доступно по адресу:

```text
http://127.0.0.1:5000
```

или:

```text
http://localhost:5000
```

---

## 3. Запуск в WSL (Ubuntu)

### Переход в папку проекта

```bash
cd ~/arm-administrator-salon-estetika
```

Если проект ещё не клонирован:

```bash
git clone https://github.com/nullfork/arm-administrator-salon-estetika.git
cd arm-administrator-salon-estetika
```

### Создание виртуального окружения

```bash
python3 -m venv .venv
```

### Активация окружения

```bash
source .venv/bin/activate
```

### Установка зависимостей

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Применение миграций

```bash
flask --app run.py db upgrade
```

### Заполнение БД демонстрационными данными

```bash
python seed.py
```

### Запуск проекта

```bash
python run.py
```

Обычно приложение доступно по адресу:

```text
http://127.0.0.1:5000
```

Если браузер открыт в Windows:

```text
http://localhost:5000
```

### Открытие проекта в VS Code через WSL

```bash
code .
```

---

## 4. Запуск в Linux

```bash
git clone https://github.com/nullfork/arm-administrator-salon-estetika.git
cd arm-administrator-salon-estetika
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
flask --app run.py db upgrade
python seed.py
python run.py
```

После запуска:

```text
http://127.0.0.1:5000
```

---

## 5. Запуск в macOS

```bash
git clone https://github.com/nullfork/arm-administrator-salon-estetika.git
cd arm-administrator-salon-estetika
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
flask --app run.py db upgrade
python seed.py
python run.py
```

После запуска:

```text
http://127.0.0.1:5000
```

---

# Быстрый запуск

## Windows

```powershell
git clone https://github.com/nullfork/arm-administrator-salon-estetika.git
cd arm-administrator-salon-estetika
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
flask --app run.py db upgrade
python seed.py
python run.py
```

## Linux / macOS / WSL

```bash
git clone https://github.com/nullfork/arm-administrator-salon-estetika.git
cd arm-administrator-salon-estetika
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
flask --app run.py db upgrade
python seed.py
python run.py
```

---

# Демонстрационные данные

После выполнения команды:

```bash
python seed.py
```

в систему автоматически добавляются:
- роли пользователей;
- тестовые учётные записи;
- клиенты;
- мастера;
- услуги;
- записи с разными статусами;
- оплаты и квитанции.

## Тестовые учётные записи

### Администратор
- логин: `admin`
- пароль: `admin123`

### Директор
- логин: `director`
- пароль: `director123`

---

# Работа с базой данных

## Применение миграций

```bash
flask --app run.py db upgrade
```

## Создание новой миграции

```bash
flask --app run.py db migrate -m "описание изменений"
flask --app run.py db upgrade
```

---

# Типовой сценарий демонстрации

1. Вход в систему
2. Открытие справочника клиентов
3. Создание новой записи
4. Фильтрация записей
5. Изменение статуса записи
6. Проведение оплаты
7. Просмотр квитанции
8. Открытие отчётов

---

# Возможные проблемы

## `flask: command not found`
Не активировано виртуальное окружение.

### Windows
```powershell
.venv\Scripts\Activate.ps1
```

### Linux / macOS / WSL
```bash
source .venv/bin/activate
```

## `ModuleNotFoundError`
Не установлены зависимости:

```bash
python -m pip install -r requirements.txt
```

## Ошибки базы данных
Применить миграции и заново наполнить БД:

```bash
flask --app run.py db upgrade
python seed.py
```
---

# Назначение проекта

Проект является учебным прототипом АРМ администратора салона красоты и подготовлен в рамках ВКР.

Его цель — продемонстрировать разработку информационной системы, автоматизирующей ключевые бизнес-процессы предприятия сферы услуг.
