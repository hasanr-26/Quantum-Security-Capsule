/* ==========================================================================
   api_client.js - real HTTPS transport layer for the workbench.

   Every call below is a genuine fetch() over the same TLS 1.3 connection that
   served this page. Timings come from performance.now() around the request, and
   the server's own processing time arrives back in the X-QSC-Process-Time-Ms
   response header - so the console distinguishes network cost from compute cost.
   ========================================================================== */

const QSC = (() => {

  const API_BASE = '';                               // same origin, port 8443
  const PROXY_BASE = `https://${location.hostname}:8444`;

  const listeners = [];

  /** Subscribes a handler to network console events. */
  function onLog(handler) { listeners.push(handler); }

  function log(message, kind = 'info') {
    const entry = {
      ts: new Date().toISOString().slice(11, 23),
      message,
      kind,
    };
    listeners.forEach((fn) => fn(entry));
    return entry;
  }

  /**
   * Issues a request and returns a structured result.
   *
   * Never throws on an HTTP error status - the caller inspects `ok`, so a 4xx
   * from the settlement engine is treated as data rather than as a crash.
   */
  async function call(method, path, options = {}) {
    const { body, params, base } = options;
    const root = base === 'proxy' ? PROXY_BASE : API_BASE;

    let url = `${root}${path}`;
    if (params) {
      const qs = new URLSearchParams(params).toString();
      if (qs) url += `?${qs}`;
    }

    const init = { method, headers: { 'X-QSC-Client': 'workbench' } };
    if (body !== undefined) {
      init.headers['Content-Type'] = 'application/json';
      init.body = JSON.stringify(body);
    }

    const label = `${method} ${path}${base === 'proxy' ? '  [via proxy :8444]' : ''}`;
    const started = performance.now();

    try {
      const response = await fetch(url, init);
      const elapsed = performance.now() - started;
      const serverMs = response.headers.get('X-QSC-Process-Time-Ms');
      const intercepted = response.headers.get('X-Intercepted-By');

      let data = null;
      const text = await response.text();
      if (text) {
        try { data = JSON.parse(text); } catch { data = { raw: text }; }
      }

      const detail = [
        `${response.status}`,
        `${elapsed.toFixed(1)}ms wire`,
        serverMs ? `${Number(serverMs).toFixed(1)}ms server` : null,
        intercepted ? 'INTERCEPTED' : null,
      ].filter(Boolean).join('  ');

      log(`${label}  ->  ${detail}`, response.ok ? 'net' : 'err');

      return {
        ok: response.ok,
        status: response.status,
        data,
        elapsedMs: elapsed,
        serverMs: serverMs ? Number(serverMs) : null,
        intercepted: Boolean(intercepted),
        headers: response.headers,
      };
    } catch (error) {
      const elapsed = performance.now() - started;
      log(`${label}  ->  TRANSPORT FAILURE  ${error.message}`, 'err');
      return {
        ok: false,
        status: 0,
        data: null,
        elapsedMs: elapsed,
        error: error.message,
      };
    }
  }

  /* ---- Endpoint wrappers ------------------------------------------------ */

  const health         = ()            => call('GET',  '/api/v1/health');
  const telemetry      = ()            => call('GET',  '/api/v1/network/telemetry');
  const tlsSession     = ()            => call('GET',  '/api/v1/network/tls');
  const parameters     = ()            => call('GET',  '/api/v1/pqc/parameters');
  const generateKeys   = ()            => call('POST', '/api/v1/pqc/keys/generate');
  const makePayload    = (kind)        => call('POST', '/api/v1/payloads/generate', { params: { kind } });
  const encapsulate    = (body)        => call('POST', '/api/v1/capsule/encapsulate', { body });
  const settle         = (capsule, base) => call('POST', '/api/v1/capsule/settle', { body: { capsule }, base });
  const legacyTransfer = (body, base)  => call('POST', '/api/v1/legacy/transfer', { body, base });
  const tamper         = (body)        => call('POST', '/api/v1/attack/tamper', { body });
  const replay         = (capsuleId)   => call('POST', '/api/v1/attack/replay', { params: { capsule_id: capsuleId } });

  const captures       = ()            => call('GET',    '/_intercept/captures', { base: 'proxy' });
  const clearCaptures  = ()            => call('DELETE', '/_intercept/captures', { base: 'proxy' });
  const quantumDecrypt = ()            => call('POST',   '/_intercept/quantum-decrypt', { base: 'proxy' });

  /* ---- Formatting helpers ----------------------------------------------- */

  const fmtBytes = (n) => {
    if (n === null || n === undefined) return '--';
    if (n < 1024) return `${n} B`;
    return `${(n / 1024).toFixed(1)} KiB`;
  };

  const fmtUptime = (seconds) => {
    if (seconds === null || seconds === undefined) return '--';
    const s = Math.floor(seconds);
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    return h > 0 ? `${h}h ${m}m` : `${m}m ${s % 60}s`;
  };

  const truncate = (text, n = 24) =>
    (text && text.length > n) ? `${text.slice(0, n)}...` : (text || '--');

  const escapeHtml = (value) => String(value ?? '')
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');

  return {
    API_BASE, PROXY_BASE,
    call, log, onLog,
    health, telemetry, tlsSession, parameters, generateKeys, makePayload,
    encapsulate, settle, legacyTransfer, tamper, replay,
    captures, clearCaptures, quantumDecrypt,
    fmtBytes, fmtUptime, truncate, escapeHtml,
  };
})();
