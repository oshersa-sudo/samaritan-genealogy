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
      // password is the real secret; username is an extra check (only enforced if ADMIN_USER is set)
      const userOk = !env.ADMIN_USER || body.user === env.ADMIN_USER;
      const ok = !!env.ADMIN_PASSWORD && body.password === env.ADMIN_PASSWORD && userOk;
      return json({ ok });
    }

    // ----- person photos (stored one KV key per person, kept out of the overrides blob) -----
    if (path === '/api/photo' && request.method === 'GET') {
      const id = url.searchParams.get('id') || '';
      const data = id && env.GENEALOGY_KV && await env.GENEALOGY_KV.get('photo:' + id);
      if (!data) return new Response('', { status: 404 });
      const m = /^data:([^;]+);base64,(.*)$/s.exec(data);
      if (!m) return new Response('', { status: 404 });
      const bin = atob(m[2]);
      const arr = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
      return new Response(arr, { headers: { 'content-type': m[1], 'cache-control': 'public, max-age=31536000, immutable' } });
    }

    if (path === '/api/photo' && request.method === 'POST') {
      const auth = request.headers.get('authorization') || '';
      if (!env.ADMIN_PASSWORD || auth !== 'Bearer ' + env.ADMIN_PASSWORD) {
        return json({ ok: false, error: 'unauthorized' }, 401);
      }
      const id = url.searchParams.get('id') || '';
      if (!id) return json({ ok: false, error: 'no id' }, 400);
      const body = await request.text();
      if (body.length > 1500000) return json({ ok: false, error: 'too large' }, 413);
      if (!body) { await env.GENEALOGY_KV.delete('photo:' + id); return json({ ok: true, deleted: true }); }
      if (!/^data:[^;]+;base64,/.test(body)) return json({ ok: false, error: 'not an image data url' }, 400);
      await env.GENEALOGY_KV.put('photo:' + id, body);
      return json({ ok: true });
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
