
# Tribute Webhook Forwarder

Простой сервер для приёма и пересылки вебхуков от [Tribute](https://wiki.tribute.tg/for-content-creators/api-documentation/webhooks) в зависимости от значения поля `subscription_name`.

---

## 🔧 Возможности

- Приём POST-запросов от Tribute
- Проверка подписи `X-Tribute-Signature` через HMAC-SHA256
- Динамическая маршрутизация по `subscription_name`
- Обновление маршрутов без перезапуска контейнера
- Эндпоинты управления `/routes` и `/reload-routes`

---

## 📁 Структура проекта

```tribute-webhook-forwarder/
├── docker-compose.yml
├── .env                     # Секретный ключ Tribute
├── forwarding\_rules.json    # Таблица маршрутов
└── app/
├── Dockerfile
├── main.py              # Flask-приложение
└── requirements.txt
````

---

## ⚙️ Установка

1. Клонируй репозиторий и перейди в директорию:

```bash
git clone https://your-repo-url.git
cd tribute-webhook-forwarder
````

2. Создай `.env` файл:

```env
TRIBUTE_SECRET_KEY=test_secret_key
```

3. Укажи маршруты в `forwarding_rules.json`:

```json
{
  "Prometey private": "http://ajxz2m04xb3tl6r6r5867liwxn3er6fv.oastify.com/tribute-webhook",
  "private_chanel": "http://lwlafxdfamg4yh4h4glhkwv7aygp4is7.oastify.com/tribute-webhook"
}
```

4. Запусти сервис:

```bash
docker-compose up --build -d
```

---

## 🚀 Использование

### Приём вебхуков

Tribute отправляет POST-запросы на `/webhook`. Пример:

```bash
curl -X POST http://localhost:8080/webhook \
  -H "Content-Type: application/json" \
  -H "X-Tribute-Signature: sha256=<signature>" \
  --data-binary @payload.json
```

### Перезагрузка маршрутов

После изменения `forwarding_rules.json`:

```bash
curl -X POST http://localhost:8080/reload-routes
```

### Просмотр текущих маршрутов

```bash
curl http://localhost:8080/routes
```

---

## 🛠️ Генерация подписи вручную (для тестов)

```bash
export TRIBUTE_SECRET_KEY=test_secret_key
SIGNATURE=$(openssl dgst -sha256 -hmac "$TRIBUTE_SECRET_KEY" payload.json | cut -d " " -f2)

curl -X POST http://localhost:8080/webhook \
  -H "Content-Type: application/json" \
  -H "X-Tribute-Signature: sha256=$SIGNATURE" \
  --data-binary @payload.json
```

---

## 📄 Пример `payload.json`

```json
{
  "name": "new_subscription",
  "created_at": "2025-07-06T12:00:00Z",
  "sent_at": "2025-07-06T12:00:01Z",
  "payload": {
    "subscription_name": "Prometey private",
    "subscription_id": 1001,
    "period_id": 5001,
    "period": "monthly",
    "price": 1000,
    "amount": 700,
    "currency": "eur",
    "user_id": 123,
    "telegram_user_id": 12345678,
    "channel_id": 999,
    "channel_name": "prometey",
    "expires_at": "2025-08-06T12:00:00Z"
  }
}
```

---

## 🧪 Эндпоинты

| Метод | URL              | Описание                                 |
| ----- | ---------------- | ---------------------------------------- |
| POST  | `/webhook`       | Основной приёмник вебхуков от Tribute    |
| GET   | `/routes`        | Посмотреть текущие правила маршрутизации |
| POST  | `/reload-routes` | Перезагрузить `forwarding_rules.json`    |


## ✅ Пример forwarding\_rules.json

```json
{
  "Prometey private": "http://ajxz2m04xb3tl6r6r5867liwxn3er6fv.oastify.com/tribute-webhook",
  "private_chanel": "http://lwlafxdfamg4yh4h4glhkwv7aygp4is7.oastify.com/tribute-webhook"
}
```

