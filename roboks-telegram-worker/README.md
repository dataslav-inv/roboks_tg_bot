# RoboKS — заявки з сайту в Telegram

## Важливо про токен
Якщо BOT_TOKEN світився в чаті / на GitHub — **обов’язково** згенеруйте новий у @BotFather:
1. Відкрийте @BotFather
2. /mybots → ваш бот → API Token → Revoke current token
3. Скопіюйте новий токен і використовуйте лише як секрет Worker

## Деплой Worker (5–10 хв)

```bash
npm i -g wrangler
wrangler login
cd roboks-telegram-worker
wrangler secret put BOT_TOKEN
# вставте токен, Enter
wrangler secret put ADMIN_CHAT_IDS
# наприклад: 279382634
wrangler deploy
```

У відповіді буде URL на кшталт:
`https://roboks-leads.<ваш_акаунт>.workers.dev`

## Підключення сайту
У `index.html` знайдіть:

```js
const LEAD_WEBHOOK_URL = 'https://roboks-leads.YOUR_SUBDOMAIN.workers.dev';
```

Замініть на ваш URL з `wrangler deploy`, залийте `index.html` на Cloudflare Pages.

## Перевірка
1. Відкрийте сайт
2. Надішліть тестову заявку
3. У Telegram має прийти повідомлення адміну (ADMIN_CHAT_IDS)

Щоб бот міг писати вам у особисті: один раз напишіть боту /start з акаунта адміна.
