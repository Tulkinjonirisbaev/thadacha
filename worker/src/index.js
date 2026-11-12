// Приём заявки с лендинга Thadacha и отправка в Telegram.
// Токен бота и id чата — секреты воркера (TG_BOT_TOKEN, TG_CHAT_ID), в коде и на странице их нет.

const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

export default {
  async fetch(req, env) {
    const origin = req.headers.get('Origin') || '';
    const allowed = (env.ALLOWED_ORIGINS || '').split(',').map(s => s.trim()).filter(Boolean);
    const cors = {
      'Access-Control-Allow-Origin': allowed.includes(origin) ? origin : allowed[0] || '',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Vary': 'Origin',
    };
    const done = (status, body) => new Response(JSON.stringify(body), {
      status, headers: { 'Content-Type': 'application/json; charset=utf-8', ...cors },
    });

    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
    if (req.method !== 'POST') return done(405, { ok: false, error: 'method' });
    if (!allowed.includes(origin)) return done(403, { ok: false, error: 'origin' });
    if (!env.TG_BOT_TOKEN || !env.TG_CHAT_ID) return done(500, { ok: false, error: 'not_configured' });

    let data;
    try { data = JSON.parse((await req.text()).slice(0, 8192)); } catch { data = null; }
    if (!data || typeof data !== 'object') return done(422, { ok: false, error: 'validation' });

    // Ловушка для ботов: скрытое поле у человека остаётся пустым.
    if (data.website) return done(200, { ok: true });

    const f = {};
    for (const k of ['name', 'company', 'phone', 'seats', 'hosting']) {
      f[k] = String(data[k] ?? '').replace(/\s+/g, ' ').trim().slice(0, 120);
    }
    if (!f.name || !f.company || !/^[\d\s()+\-]{7,20}$/.test(f.phone)) {
      return done(422, { ok: false, error: 'validation' });
    }

    const time = new Intl.DateTimeFormat('ru-RU', {
      timeZone: 'Asia/Tashkent', day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit',
    }).format(new Date()).replace(',', '');
    const text = '<b>Новая заявка с лендинга Thadacha</b>\n\n'
      + `Имя: ${esc(f.name)}\nКомпания: ${esc(f.company)}\nТелефон: ${esc(f.phone)}\n`
      + `Сотрудников: ${esc(f.seats)}\nРазмещение: ${esc(f.hosting)}\nВремя: ${time}`;

    const tg = await fetch(`https://api.telegram.org/bot${env.TG_BOT_TOKEN}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: env.TG_CHAT_ID, text, parse_mode: 'HTML' }),
    });
    if (!tg.ok) {
      console.error('telegram', tg.status, (await tg.text()).slice(0, 200));
      return done(502, { ok: false, error: 'telegram' });
    }
    return done(200, { ok: true });
  },
};
