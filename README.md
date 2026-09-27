# Telegram-бот STEM RoboKS (Дніпро)

Бот для прийому заявок на перше заняття, інформації про курси та зв’язку з адміністратором.

## Можливості

- Заявка на перше заняття (покрокова анкета)
- Інформація про курси, ціни, контакти, FAQ
- Пересилання заявок адмінам
- Адмін-команди: `/leads`, `/lead_id`, `/stats`
- Зміна статусу заявки прямо з картки

## Вимоги

- Python 3.11+
- Telegram Bot Token

## Встановлення

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Відредагуйте .env — вкажіть BOT_TOKEN і ADMIN_CHAT_IDS
