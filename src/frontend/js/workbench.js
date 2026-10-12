/* ==========================================================================
   workbench.js - application controller.

   Wires the tabs together, polls live telemetry, and drives the settlement,
   interception and cryptography views. All state shown here originates from
   the running node; nothing is cached fixtures.
   ========================================================================== */

(() => {

  const $ = (id) => document.getElementById(id);

  let currentCapsule = null;   // most recent encapsulate() response
  let telemetryTimer = null;

  /* ---------------------------------------------------------------- tabs -- */

  function initTabs() {
    const tabs = [...document.querySelectorAll('.tab')];
    tabs.forEach((tab) => {
      tab.addEventListener('click', () => {
        tabs.forEach((t) => t.setAttribute('aria-selected', String(t === tab)));
        document.querySelectorAll('.view').forEach((view) => {
          view.classList.toggle('is-active', view.id === `view-${tab.dataset.view}`);
        });
        if (tab.dataset.view === 'visualizer') Visualizer3D.activate();
        if (tab.dataset.view === 'intercept') refreshCaptures();
      });
    });
  }

  /* ------------------------------------------------------ network console -- */

  function initLog() {
    const log = $('net-log');
    QSC.onLog(({ ts, message, kind }) => {
      const line = document.createElement('div');
      line.className = 'log__line';
      line.innerHTML =
        `<span class="log__ts">${ts}</span><span class="log__msg log__msg--${kind}">${QSC.escapeHtml(message)}</span>`;
      log.appendChild(line);
      while (log.childElementCount > 400) log.removeChild(log.firstChild);
      log.scrollTop = log.scrollHeight;
    });
    $('btn-clear-log').addEventListener('click', () => { log.innerHTML = ''; });
  }

  /* ----------------------------------------------------------- telemetry -- */

  async function refreshTelemetry() {
    const result = await QSC.telemetry();
    if (!result.ok || !result.data) return;
    const t = result.data;

    $('node-id').textContent = `${t.node_id}  ::  ${location.host}`;
    $('stat-uptime').textContent = QSC.fmtUptime(t.uptime_seconds);
    $('stat-requests').textContent = t.api_requests_served;
    $('stat-capsules').textContent = t.capsules_built;
    $('stat-rejected').textContent = t.capsules_rejected;
    $('stat-replay').textContent = t.replay_cache_size;
    $('stat-kemfp').textContent =
      t.keyset_fingerprints.ml_kem_768_public
        ? t.keyset_fingerprints.ml_kem_768_public.slice(0, 12)
        : 'not loaded';
  }

  async function probeTls(announce = false) {
    const result = await QSC.tlsSession();
    if (!result.ok || !result.data) return;

    const live = result.data.live_handshake;
    const config = result.data.configuration;

    if (live.connected) {
      $('stat-tls').innerHTML = `<span class="dot dot--live"></span>${live.protocol}`;
      $('stat-cipher').textContent = live.cipher_suite;
    } else {
      $('stat-tls').innerHTML = '<span class="dot dot--down"></span>offline';
      $('stat-cipher').textContent = '--';
    }

    renderTlsDetails(live, config);
    if (announce) {
      QSC.log(
        live.connected
          ? `TLS probe: ${live.protocol} / ${live.cipher_suite} / handshake ${live.tls_handshake_ms}ms`
          : `TLS probe failed: ${live.error}`,
        live.connected ? 'ok' : 'err'
      );
    }
  }

  function renderTlsDetails(live, config) {
    if (!live.connected) {
      $('tls-details').innerHTML =
        `<div class="empty">Handshake probe failed:<br>${QSC.escapeHtml(live.error || 'unreachable')}</div>`;
      return;
    }

    const cert = live.server_certificate || {};
    const rows = [
      ['Endpoint', live.endpoint],
      ['Protocol', live.protocol],
      ['Cipher suite', live.cipher_suite],
      ['Symmetric strength', `${live.symmetric_key_bits} bit`],
      ['Certificate verified', live.certificate_verified ? 'yes' : 'no'],
      ['Subject CN', cert.subject_common_name],
      ['Organisation', cert.subject_organization],
      ['Valid until', cert.not_after],
      ['SANs', (cert.subject_alt_names || []).join(', ')],
      ['TCP connect', `${live.tcp_connect_ms} ms`],
      ['TLS handshake', `${live.tls_handshake_ms} ms`],
      ['OpenSSL', config.openssl_version],
    ];

    $('tls-details').innerHTML = `
      <p class="section-note">
        Values below come from a real handshake performed by the server against
        itself over the loopback interface at probe time.
      </p>
      <div class="kv">
        ${rows.map(([k, v]) =>
          `<div class="kv__k">${k}</div><div class="kv__v">${QSC.escapeHtml(v ?? '--')}</div>`).join('')}
      </div>
      <div class="divider"></div>
      <div class="split-head"><span>Handshake sequence</span></div>
      <div class="mono-sm muted" style="line-height:1.8">
        ${live.handshake_stages.map((s, i) => `${String(i + 1).padStart(2, '0')}  ${s}`).join('<br>')}
      </div>
      <div class="divider"></div>
      <div class="split-head"><span>Quantum exposure of this channel</span></div>
      <div class="kv">
        <div class="kv__k">Key exchange</div><div class="kv__v">${QSC.escapeHtml(live.quantum_exposure.key_exchange)}</div>
        <div class="kv__k">Certificate signature</div><div class="kv__v">${QSC.escapeHtml(live.quantum_exposure.certificate_signature)}</div>
        <div class="kv__k">Broken by</div><div class="kv__v" style="color:var(--red)">Shor's algorithm</div>
      </div>
      <p class="section-note" style="margin-top:10px">
        ${QSC.escapeHtml(live.quantum_exposure.assessment)}
      </p>`;
  }

  /* ------------------------------------------------------- crypto params -- */

  async function loadParameters() {
    const result = await QSC.parameters();
    if (!result.ok) return;
    const p = result.data;

    const block = (title, standard, entries) => `
      <div class="split-head"><span>${title}</span><span>${standard}</span></div>
      <div class="kv" style="margin-bottom:16px">
        ${entries.map(([k, v]) =>
          `<div class="kv__k">${k}</div><div class="kv__v">${QSC.escapeHtml(v)}</div>`).join('')}
      </div>`;

    $('crypto-params').innerHTML =
      block('ML-KEM-768 &mdash; Key Encapsulation', p.kem.standard, [
        ['Hardness assumption', p.kem.hardness_assumption],
        ['Polynomial degree n', p.kem.polynomial_degree_n],
        ['Modulus q', p.kem.modulus_q],
        ['Module rank k', p.kem.module_rank_k],
        ['NIST category', p.kem.nist_security_category],
        ['Public key', `${p.kem.public_key_bytes} B`],
        ['Private key', `${p.kem.private_key_bytes} B`],
        ['Ciphertext', `${p.kem.ciphertext_bytes} B`],
        ['Shared secret', `${p.kem.shared_secret_bytes} B`],
      ]) +
      block('ML-DSA-65 &mdash; Digital Signature', p.dsa.standard, [
        ['Hardness assumption', p.dsa.hardness_assumption],
        ['Polynomial degree n', p.dsa.polynomial_degree_n],
        ['Modulus q', p.dsa.modulus_q],
        ['Matrix (k, l)', `(${p.dsa.matrix_k}, ${p.dsa.matrix_l})`],
        ['NIST category', p.dsa.nist_security_category],
        ['Public key', `${p.dsa.public_key_bytes} B`],
        ['Private key', `${p.dsa.private_key_bytes} B`],
        ['Signature', `${p.dsa.signature_bytes} B`],
      ]) +
      block('AES-256-GCM &mdash; Payload Encryption', p.symmetric.standard, [
        ['Key size', `${p.symmetric.key_bits} bit`],
        ['Nonce', `${p.symmetric.nonce_bits} bit`],
        ['Auth tag', `${p.symmetric.tag_bits} bit`],
      ]) +
      block('SHA3-512 &mdash; Integrity Lock', p.hash.standard, [
        ['Construction', p.hash.construction],
        ['Digest', `${p.hash.digest_bits} bit`],
      ]) +
      block('HKDF-SHA3-512 &mdash; Key Derivation', p.kdf.standard, [
        ['Algorithm', p.kdf.algorithm],
        ['Purpose', 'Derives the AES content key from the ML-KEM shared secret'],
      ]);
  }

  /* ---------------------------------------------------------- settlement -- */

  async function rotateKeys() {
    $('btn-keys').disabled = true;
    const result = await QSC.generateKeys();
    $('btn-keys').disabled = false;
    if (!result.ok) return;

    const k = result.data;
    QSC.log(
      `keyset rotated - ML-KEM ${k.key_sizes.ml_kem_768_public_bytes}B in ` +
      `${k.timings.ml_kem_768_keygen_ms}ms, ML-DSA ${k.key_sizes.ml_dsa_65_public_bytes}B in ` +
      `${k.timings.ml_dsa_65_keygen_ms}ms`,
      'ok'
    );
    refreshTelemetry();
  }

  async function buildCapsule() {
    $('btn-build').disabled = true;
    $('settle-status').textContent = 'building';

    const result = await QSC.encapsulate({
      payload_kind: $('payload-kind').value,
      policy: {
        classification: 'CONFIDENTIAL',
        jurisdiction: 'GLOBAL',
        max_hops: 3,
        ttl_seconds: Number($('ttl').value) || 300,
      },
    });

    $('btn-build').disabled = false;
    if (!result.ok) {
      $('settle-status').textContent = 'build failed';
      return;
    }

    currentCapsule = result.data;
    $('btn-settle').disabled = false;
    $('settle-status').textContent = 'ready to transmit';

    renderCapsuleSummary(currentCapsule);
    HexInspector.load(
      currentCapsule.wire_format_b64,
      currentCapsule.field_offsets,
      currentCapsule.capsule_id
    );
    AttackLab.setCapsule(currentCapsule.capsule_id);
    AttackLab.reset();

    $('stage-list').innerHTML =
      '<div class="empty">Capsule built. Transmit it to run the validation pipeline.</div>';
    $('decrypted-output').textContent = 'Awaiting settlement.';
    $('decrypt-meta').textContent = '--';

    QSC.log(
      `capsule ${currentCapsule.capsule_id} built in ${currentCapsule.timings.capsule_build_ms}ms  ` +
      `(${currentCapsule.plaintext_size_bytes}B payload -> ${currentCapsule.wire_size_bytes}B wire)`,
      'ok'
    );
    refreshTelemetry();
  }

  function renderCapsuleSummary(capsule) {
    const sizes = capsule.component_sizes;
    const rows = [
      ['Capsule ID', capsule.capsule_id],
      ['Standard', capsule.descriptor.label],
      ['Corridor', capsule.descriptor.corridor || '--'],
      ['Payload', `${capsule.plaintext_size_bytes} B`],
      ['On the wire', `${capsule.wire_size_bytes} B`],
      ['Expansion', `${capsule.expansion_ratio}x`],
      ['KEM ciphertext', `${sizes.kem_ciphertext_bytes} B`],
      ['ML-DSA signature', `${sizes.signature_bytes} B`],
      ['GCM tag', `${sizes.gcm_tag_bytes} B`],
      ['Build time', `${capsule.timings.capsule_build_ms} ms`],
      ['SHA3-512', `${capsule.sha3_hash.slice(0, 20)}...`],
    ];
    $('capsule-summary').innerHTML = rows.map(([k, v]) =>
      `<div class="kv__k">${k}</div><div class="kv__v truncate" title="${QSC.escapeHtml(v)}">${QSC.escapeHtml(v)}</div>`
    ).join('');
  }

  async function settleCapsule() {
    if (!currentCapsule) return;

    const viaProxy = $('route').value === 'proxy';
    $('btn-settle').disabled = true;
    $('settle-status').textContent = viaProxy ? 'transmitting via proxy' : 'transmitting';

    const result = await QSC.settle(currentCapsule.capsule, viaProxy ? 'proxy' : undefined);
    $('btn-settle').disabled = false;

    if (!result.ok || !result.data) {
      $('settle-status').textContent = 'transport failure';
      return;
    }

    const data = result.data;
    $('settle-status').innerHTML =
      `<span class="pill pill--${data.status === 'SETTLED' ? 'settled' : 'rejected'}">${data.status}</span>`;

    PipelineView.render($('stage-list'), data.stage_diagnostics);

    if (data.decrypted_payload) {
      $('decrypted-output').className = 'code code--plain';
      $('decrypted-output').textContent = data.decrypted_payload;
      $('decrypt-meta').textContent =
        `${data.timings.validation_ms} ms validate  |  ${data.timings.decryption_ms} ms decrypt`;
    } else {
      $('decrypted-output').className = 'code code--leak';
      $('decrypted-output').textContent =
        `No payload released.\n\n${data.reason}`;
      $('decrypt-meta').textContent = 'rejected';
    }

    QSC.log(
      `settlement ${data.status}${viaProxy ? ' (through interception proxy)' : ''} - ${data.reason}`,
      data.status === 'SETTLED' ? 'ok' : 'err'
    );
    refreshTelemetry();
  }

  /* ------------------------------------------------------- interception -- */

  async function sendLegacy() {
    const generated = await QSC.makePayload($('intercept-kind').value);
    if (!generated.ok) return;
    const payload = generated.data.payload_raw;

    const result = await QSC.legacyTransfer({ payload_raw: payload }, 'proxy');
    QSC.log(
      result.ok
        ? `plaintext payment relayed through the proxy - ${generated.data.size_bytes}B exposed at the hop`
        : 'legacy transfer failed',
      result.ok ? 'warn' : 'err'
    );
    refreshCaptures();
  }

  async function sendCapsuleThroughProxy() {
    const generated = await QSC.makePayload($('intercept-kind').value);
    if (!generated.ok) return;

    const built = await QSC.encapsulate({ payload_raw: generated.data.payload_raw });
    if (!built.ok) return;

    const settled = await QSC.settle(built.data.capsule, 'proxy');
    QSC.log(
      settled.ok
        ? `capsule relayed through the proxy - ${settled.data.status}`
        : 'capsule relay failed',
      settled.ok ? 'ok' : 'err'
    );
    refreshCaptures();
  }

  async function refreshCaptures() {
    const result = await QSC.captures();
    if (!result.ok || !result.data) {
      $('capture-rows').innerHTML =
        '<tr><td colspan="6"><div class="empty">Proxy unreachable. Start the node without --no-proxy.</div></td></tr>';
      return;
    }

    const data = result.data;
    $('capture-meta').textContent = `${QSC.fmtBytes(data.total_bytes_harvested)} harvested`;
    $('harvest-stats').innerHTML = [
      ['Flows harvested', data.total_flows],
      ['Bytes recorded', QSC.fmtBytes(data.total_bytes_harvested)],
      ['Upstream', data.upstream],
    ].map(([k, v]) =>
      `<div class="kv__k">${k}</div><div class="kv__v truncate">${QSC.escapeHtml(v)}</div>`).join('');

    if (data.flows.length === 0) {
      $('capture-rows').innerHTML =
        '<tr><td colspan="6"><div class="empty">No traffic intercepted yet.</div></td></tr>';
      return;
    }

    $('capture-rows').innerHTML = data.flows.map((flow) => {
      const protection = flow.analysis.protection;
      const tone = protection === 'QSC_CAPSULE' ? 'pass'
                 : protection === 'TLS_ONLY' ? 'fail' : 'skip';
      return `<tr>
        <td class="val">${flow.capture_id}</td>
        <td>${flow.method}</td>
        <td class="val truncate">${QSC.escapeHtml(flow.path)}</td>
        <td class="num">${flow.request_bytes}</td>
        <td class="num">${flow.round_trip_ms}</td>
        <td><span class="pill pill--${tone}">${protection}</span></td>
      </tr>`;
    }).join('');
  }

  async function runQuantumDecrypt() {
    $('btn-quantum').disabled = true;
    const result = await QSC.quantumDecrypt();
    $('btn-quantum').disabled = false;
    if (!result.ok || !result.data) return;

    const data = result.data;
    $('forensics-meta').textContent =
      `${data.breached_count} breached  |  ${data.resisted_count} resisted`;

    if (data.flows_analysed === 0) {
      $('forensics').innerHTML =
        '<div class="empty">Nothing harvested yet. Send traffic through the proxy first.</div>';
      return;
    }

    const breached = data.breached.map((b) => `
      <div class="split-head">
        <span style="color:var(--red)">BREACHED &mdash; ${QSC.escapeHtml(b.path)}</span>
        <span>${b.capture_id}</span>
      </div>
      <p class="section-note">${QSC.escapeHtml(b.detail)}</p>
      <div class="kv" style="margin-bottom:8px">
        <div class="kv__k">Sensitive fields recovered</div>
        <div class="kv__v" style="color:var(--red)">${(b.recovered_plaintext_fields || []).join(', ') || 'none'}</div>
      </div>
      <pre class="code code--leak">${QSC.escapeHtml(
        typeof b.recovered_body?.payload_raw === 'string'
          ? b.recovered_body.payload_raw
          : JSON.stringify(b.recovered_body, null, 2)
      )}</pre>
      <div class="divider"></div>`).join('');

    const resisted = data.resisted.map((r) => `
      <div class="split-head">
        <span style="color:var(--green)">RESISTED &mdash; ${QSC.escapeHtml(r.path)}</span>
        <span>${r.capture_id}</span>
      </div>
      <p class="section-note">${QSC.escapeHtml(r.detail)}</p>
      <div class="kv" style="margin-bottom:8px">
        <div class="kv__k">Routing metadata visible</div>
        <div class="kv__v">${QSC.escapeHtml(r.visible_metadata.sender_id)} &rarr; ${QSC.escapeHtml(r.visible_metadata.recipient_id)}</div>
        ${Object.entries(r.opaque_ciphertext).map(([name, blob]) =>
          `<div class="kv__k">${name}</div><div class="kv__v">${blob.bytes} B ciphertext</div>`).join('')}
        <div class="kv__k">Shor applicable</div>
        <div class="kv__v" style="color:var(--green)">${r.residual_hardness.shor_applicable ? 'yes' : 'no'}</div>
      </div>
      <p class="section-note">${QSC.escapeHtml(r.residual_hardness.reason)}</p>
      <div class="divider"></div>`).join('');

    $('forensics').innerHTML = `
      <div class="kv" style="margin-bottom:12px">
        <div class="kv__k">Threat model</div><div class="kv__v">${QSC.escapeHtml(data.threat_model.event)}</div>
        <div class="kv__k">Status</div><div class="kv__v"><span class="pill pill--warn">${data.threat_model.status}</span></div>
        <div class="kv__k">Captured bytes are real</div><div class="kv__v">${data.threat_model.captured_bytes_are_real ? 'yes' : 'no'}</div>
        <div class="kv__k">TLS layer</div><div class="kv__v" style="color:var(--red)">${data.threat_model.tls_layer}</div>
      </div>
      <div class="divider"></div>
      ${breached}${resisted}
      <p class="section-note" style="color:var(--text-meta)">${QSC.escapeHtml(data.conclusion)}</p>`;

    QSC.log(`quantum forensics: ${data.conclusion}`, 'warn');
  }

  /* ---------------------------------------------------------------- boot -- */

  function init() {
    initTabs();
    initLog();

    HexInspector.mount({
      view: $('hex-view'),
      legend: $('hex-legend'),
      meta: $('hex-meta'),
      detail: $('byte-detail'),
    });

    AttackLab.mount({
      flipBtn: $('btn-flip'),
      replayBtn: $('btn-replay'),
      offsetInput: $('flip-offset'),
      bitInput: $('flip-bit'),
      result: $('attack-result'),
    });

    Visualizer3D.mount({
      container: $('stage3d'),
      hudMode: $('hud-mode'),
      hudPhase: $('hud-phase'),
      hudPayload: $('hud-payload'),
      hudStatus: $('hud-status-text'),
      timeline: $('timeline'),
      log: $('viz-log'),
    });

    $('btn-keys').addEventListener('click', rotateKeys);
    $('btn-build').addEventListener('click', buildCapsule);
    $('btn-settle').addEventListener('click', settleCapsule);
    $('btn-probe').addEventListener('click', () => probeTls(true));

    $('btn-send-legacy').addEventListener('click', sendLegacy);
    $('btn-send-capsule').addEventListener('click', sendCapsuleThroughProxy);
    $('btn-quantum').addEventListener('click', runQuantumDecrypt);
    $('btn-clear-captures').addEventListener('click', async () => {
      await QSC.clearCaptures();
      $('forensics').innerHTML = '<div class="empty">Harvest archive cleared.</div>';
      $('forensics-meta').textContent = '--';
      refreshCaptures();
    });

    $('btn-mode-tls').addEventListener('click', () => Visualizer3D.setMode('tls'));
    $('btn-mode-qsc').addEventListener('click', () => Visualizer3D.setMode('qsc'));
    $('btn-run').addEventListener('click', () => Visualizer3D.runFullProcess());
    $('btn-attack').addEventListener('click', () => Visualizer3D.runAttack());
    $('btn-reset3d').addEventListener('click', () => Visualizer3D.reset());
    $('btn-clear-viz-log').addEventListener('click', () => Visualizer3D.clearNarration());

    QSC.log(`workbench connected to ${location.origin} over TLS`, 'ok');

    loadParameters();
    probeTls(true);
    refreshTelemetry();
    telemetryTimer = setInterval(refreshTelemetry, 4000);
  }

  document.addEventListener('DOMContentLoaded', init);
})();
