# API-сервис сокращения ссылок
## Описание
Сервис, который позволяет пользователям сокращать длинные ссылки, получать их аналитику и управлять ими. <br>
Развернутый сервис можно найти по ссылке: https://url-short-service.onrender.com/docs
### Основные функции
`POST /links/shorten` – создает короткую ссылку с проверкой её уникальности, позволяет добавить дату истечения срока действия ссылки и добавить её в проект.<br>
`DELETE /links/{short_code}` – удаляет связь короткой ссылки и оригинального URL.<br>
`PUT /links/{short_code}` – привязывает к короткой ссылке новую длинную.<br>
`GET /links/{short_code}` – перенаправляет на оригинальный URL.<br>
`GET /links/search/` – осуществляет поиск короткой ссылки по оригинальному URL.<br>
`GET /links/popular_links/` – выводит детальную статистику по 10 самым популярным по посещаемости ссылкам.<br>
`GET /links/{short_code}/stats` – отображает оригинальный URL, возвращает дату создания, количество переходов, дату последнего использования.<br>
`PUT /links/{short_code}/project` – позволяет добавить ссылку в проект или переместить в новый.<br>
`GET /links/{short_code}/project/links` – выводит все ссылки, которые есть в указанном проекте.<br>

В проекте есть не до конца реализованная функция регистрации:<br>
`POST /links/register` – пользователь может зарегистрироваться, указав свои логин, почту и пароль.<br>
`POST /links/token` – по логину и паролю пользователь может получить токен.<br>

Кроме того, в проекте реализовано удаление неиспользуемых ссылок с использованием планировщика:<br>
Спустя 30 дней после последнего перехода по ссылке она удаляется. <br>

---

### Инструкция по запуску
1. **Склонируйте репозиторий** <br>
`git clone git@github.com:akiltrebreg/url_short_service.git` <br>
2. **Соберите и запустите контейнеры Docker** <br>
`docker-compose up --build` <br>
3. **Откройте Swagger UI** <br>
Перейдите по адресу http://localhost:8000/docs, чтобы ознакомиться с документацией API <br>

---
### Примеры запросов
#### POST /links/shorten
![https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/post_links_shorten_1.png](https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/post_links_shorten_1.png)
![https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/post_links_shorten_2.png](https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/post_links_shorten_2.png)
#### GET /links/{short_code}
![https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/post_links_shorten_1.png](https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/get_links_short_code_1.png)
#### GET /links/search/
![https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/get_links_search_1.png](https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/get_links_search_1.png)
#### GET /links/popular_links/
![https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/get_links_popular_links_1.png](https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/get_links_popular_links_1.png)
#### GET /links/{short_code}/stats
![https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/get_links_short_code_stats_1.png](https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/get_links_short_code_stats_1.png)
#### PUT /links/{short_code}/project
![https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/put_links_short_code_project_1.png](https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/put_links_short_code_project_1.png)
#### GET /links/{short_code}/project/links
![https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/get_links_project_project_name_links_1.png](https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/get_links_project_project_name_links_1.png)
#### PUT /links/{short_code}
![https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/put_links_short_code_1.png](https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/put_links_short_code_1.png)
#### DELETE /links/{short_code}
![https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/delete_links_short_code_1.png](https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/delete_links_short_code_1.png)

---
Автор проекта пыталась реализовать обработку токена и привязку к зарегистрированному пользователю:
![https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/registry_show.png](https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/registry_show.png)
Но ей не удалось это победить, поэтому был оставлен только первичный функционал регистрации и получения токена:
#### POST /links/register
![https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/post_links_register_1.png](https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/post_links_register_1.png)
#### POST /links/token
![https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/post_links_token_1.png](https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/post_links_token_1.png)
![https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/post_links_token_2.png](https://github.com/akiltrebreg/url_short_service/blob/main/screenshots/post_links_token_2.png)

---
## Описание базы данных

Проект использует реляционную базу данных PostgreSQL с использованием SQLAlchemy ORM, а также Redis для кэширования и хранения временных данных. В базе данных определены две основные таблицы: `shortened_urls` и `users`.

### Таблица `shortened_urls`

Таблица хранит информацию о сокращённых ссылках. Каждая ссылка может быть сгенерирована с уникальным коротким кодом или кастомным псевдонимом. Также хранится оригинальный URL, дата создания, дата истечения срока действия, количество кликов и информация о последнем доступе.

#### Структура таблицы:

| Поле             | Тип данных   | Описание                                      |
|------------------|--------------|-----------------------------------------------|
| `id`             | Integer      | Уникальный идентификатор ссылки (Primary Key) |
| `short_code`     | String       | Уникальный короткий код для ссылки            |
| `original_url`   | String       | Оригинальная ссылка                           |
| `custom_alias`   | String       | Кастомный псевдоним для ссылки (опционально)  |
| `created_at`     | DateTime     | Дата и время создания сокращённой ссылки     |
| `expires_at`     | DateTime     | Дата истечения срока действия ссылки (опционально) |
| `clicks`         | Integer      | Количество кликов по ссылке                  |
| `last_accessed_at` | DateTime   | Дата последнего использования ссылки         |
| `project_name`   | String       | Наименование проекта (опционально)            |
| `owner_id`       | Integer      | Идентификатор пользователя, которому принадлежит ссылка (ForeignKey) - эта часть в проекте не реализована |

#### Валидация:
- Кастомный псевдоним (`custom_alias`), если используется, должен быть длиной от 3 до 30 символов.

#### Связи:
- Каждая сокращённая ссылка связана с конкретным пользователем через внешний ключ (`owner_id`), который ссылается на таблицу `users`.

<br>

### Таблица `users`

Таблица хранит информацию о пользователях, зарегистрированных в сервисе. Каждый пользователь имеет уникальный логин и почтовый адрес. Также хранится захэшированный пароль и дата создания аккаунта.

#### Структура таблицы:

| Поле           | Тип данных     | Описание                              |
|----------------|----------------|---------------------------------------|
| `id`           | Integer        | Уникальный идентификатор пользователя (Primary Key) |
| `username`     | String         | Логин пользователя (уникальный, обязательный) |
| `email`        | String         | Почтовый адрес пользователя (уникальный, обязательный) |
| `hashed_password` | String      | Захэшированный пароль пользователя (обязателен) |
| `created_at`   | DateTime       | Дата и время создания аккаунта        |

#### Валидация:
- Логин (`username`) должен быть длиной от 3 до 30 символов.
- Почтовый адрес (`email`) должен содержать символ `@`.

#### Связи:
- Пользователь может иметь несколько сокращённых ссылок через связь с таблицей `shortened_urls`.

---

### Лицензия
Этот проект выполнен на условиях лицензии MIT.
