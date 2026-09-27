# Railway + PostgreSQL для бота RoboKS

Замінити в проєкті:
- `config.py` → цей `config.py`
- `bot/db/database.py` → цей `database.py`
- `requirements.txt` → цей файл
- додати `Procfile`

`models.py`, хендлери і `main.py` не змінюються.

Локальний `.env` після заміни має містити `DATABASE_URL`.
aiosqlite можна прибрати з requirements.

## Кроки в Railway

1. Залийте репозиторій на GitHub без `.env`, `venv/`, `data/leads.db`.
2. railway.app → New Project → Deploy from GitHub.
3. New → Database → PostgreSQL.
4. Відкрийте сервіс бота → Variables:
   - `BOT_TOKEN`
   - `ADMIN_CHAT_IDS=279382634`
   - `DATABASE_URL` — Add Reference → Postgres → `DATABASE_URL`
5. Settings → Start Command: `python main.py`
   або залиште Procfile `worker: python main.py`.
6. Deploy. У логах: `Database initialized` → `Bot starting...`
7. Зупиніть бота на своєму ПК.

Railway сам підставить внутрішній URL Postgres. Для локального тесту
скопіюйте публічний URL бази в локальний `.env`.

## Перевірка

- /start боту
- тестова заявка в боті
- /leads і /stats адміном
- після редеплою заявки лишаються (це вже Postgres, не файл SQLite)
