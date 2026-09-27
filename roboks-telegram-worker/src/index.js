/**
 * RoboKS — Cloudflare Worker: прийом заявок з сайту → Telegram
 *
 * Секрети (wrangler secret put ...):
 *   BOT_TOKEN
 *   ADMIN_CHAT_IDS   // наприклад: 279382634 або 111,222
 *
 * Деплой:
 *   npm i -g wrangler
 *   wrangler login
 *   wrangler secret put BOT_TOKEN
 *   wrangler secret put ADMIN_CHAT_IDS
 *   wrangler deploy
 */

function corsHeaders(origin) {
  return {
    'Access-Control-Allow-Origin': origin || '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json; charset=utf-8',
  };
}

function escapeHtml(s) {
  return String(s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

async function sendTelegram(token, chatId, text, parseMode) {
  const payload = {
    chat_id: chatId,
    text,
    disable_web_page_preview: true,
  };
  if (parseMode) payload.parse_mode = parseMode;
  const tgRes = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  try {
    return await tgRes.json();
  } catch {
    return { ok: false, description: 'Telegram empty response' };
  }
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '*';
    const headers = corsHeaders(origin);

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers });
    }

    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ ok: false, error: 'Method not allowed' }), {
        status: 405,
        headers,
      });
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return new Response(JSON.stringify({ ok: false, error: 'Invalid JSON' }), {
        status: 400,
        headers,
      });
    }

    const parentName = (body.parentName || '').toString().trim();
    const childName = (body.childName || '').toString().trim();
    const childAge = (body.childAge || '').toString().trim();
    const course = (body.course || '').toString().trim();
    const phone = (body.phone || '').toString().trim();
    const source = (body.source || 'site').toString().trim();
    const page = (body.page || '').toString().trim();

    if (!parentName || !childName || !phone) {
      return new Response(
        JSON.stringify({ ok: false, error: 'Заповніть ім\'я батька, дитини та телефон' }),
        { status: 400, headers }
      );
    }

    const token = env.BOT_TOKEN;
    const adminIds = (env.ADMIN_CHAT_IDS || '')
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);

    if (!token || adminIds.length === 0) {
      return new Response(
        JSON.stringify({ ok: false, error: 'Server misconfigured' }),
        { status: 500, headers }
      );
    }

    const text = [
      '🆕 <b>Заявка з сайту RoboKS</b>',
      '',
      `👤 Батько/мама: <b>${escapeHtml(parentName)}</b>`,
      `🧒 Дитина: <b>${escapeHtml(childName)}</b>`,
      `🎂 Вік: <b>${escapeHtml(childAge || '—')}</b>`,
      `📚 Курс: <b>${escapeHtml(course || '—')}</b>`,
      `📞 Телефон: <b>${escapeHtml(phone)}</b>`,
      `🔗 Джерело: ${escapeHtml(source)}`,
      page ? `🌐 Сторінка: ${escapeHtml(page)}` : '',
    ]
      .filter(Boolean)
      .join('\n');

    const results = [];
    for (const chatId of adminIds) {
      let tgJson = await sendTelegram(token, chatId, text, 'HTML');
      if (!tgJson.ok) {
        // повтор без HTML, якщо Telegram не розпарсив розмітку
        tgJson = await sendTelegram(token, chatId, text.replace(/<[^>]+>/g, ''), null);
      }
      results.push({ chatId, ok: tgJson.ok, description: tgJson.description || '' });
    }

    const anyOk = results.some((r) => r.ok);
    if (!anyOk) {
      const desc = results.map((r) => r.description).filter(Boolean).join('; ') || 'Telegram error';
      return new Response(
        JSON.stringify({ ok: false, error: desc, details: results }),
        { status: 502, headers }
      );
    }

    return new Response(JSON.stringify({ ok: true }), { status: 200, headers });
  },
};
