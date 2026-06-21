// Cloudflare Worker for the Samaritan genealogy app.
// Serves the static site (public/) AND a tiny edit API backed by Workers KV:
//   GET  /api/data   -> the overrides JSON (public, read-only)
//   POST /api/login  -> {ok:true} if the password matches the ADMIN_PASSWORD secret
//   POST /api/save   -> stores the overrides JSON (requires Authorization: Bearer <password>)
// The base genealogy stays in the embedded data; admin edits are saved as an
// "overrides" layer in KV and merged on top in the browser.

const JSON_HEADERS = { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' };
const json = (obj, status = 200) => new Response(JSON.stringify(obj), { status, headers: JSON_HEADERS });

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    if (path === '/api/data' && request.method === 'GET') {
      const data = (env.GENEALOGY_KV && await env.GENEALOGY_KV.get('overrides')) || '{}';
      return new Response(data, { headers: JSON_HEADERS });
    }

    if (path === '/api/login' && request.method === 'POST') {
      let body = {};
      try { body = await request.json(); } catch (e) {}
      const ok = !!env.ADMIN_PASSWORD && body.password === env.ADMIN_PASSWORD;
      return json({ ok });
    }

    if (path === '/api/save' && request.method === 'POST') {
      const auth = request.headers.get('authorization') || '';
      if (!env.ADMIN_PASSWORD || auth !== 'Bearer ' + env.ADMIN_PASSWORD) {
        return json({ ok: false, error: 'unauthorized' }, 401);
      }
      const text = await request.text();
      if (text.length > 3000000) return json({ ok: false, error: 'too large' }, 413);
      try { JSON.parse(text); } catch (e) { return json({ ok: false, error: 'invalid json' }, 400); }
      await env.GENEALOGY_KV.put('overrides', text);
      return json({ ok: true, savedAt: new Date().toISOString() });
    }

    // everything else -> the static site
    return env.ASSETS.fetch(request);
  }
};
