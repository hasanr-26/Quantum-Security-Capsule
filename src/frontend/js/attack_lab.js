/* ==========================================================================
   attack_lab.js - live tampering and replay against a real capsule.

   Both attacks run server-side against the genuine capsule bytes. Nothing is
   pre-scripted: the byte offset comes from the operator, the verdict comes
   from the same validation pipeline that settles legitimate traffic.
   ========================================================================== */

const AttackLab = (() => {

  let els = {};
  let currentCapsuleId = null;

  function mount(refs) {
    els = refs;

    els.flipBtn.addEventListener('click', flipBit);
    els.replayBtn.addEventListener('click', replayCapsule);

    // Selecting a byte in the hex view arms that offset for the bit flip.
    HexInspector.onByteSelect((offset) => {
      els.offsetInput.value = offset;
    });
  }

  function setCapsule(capsuleId) {
    currentCapsuleId = capsuleId;
    els.flipBtn.disabled = !capsuleId;
    els.replayBtn.disabled = !capsuleId;
  }

  async function flipBit() {
    if (!currentCapsuleId) return;

    const offset = Number(els.offsetInput.value);
    const bit = Number(els.bitInput.value);
    const limit = HexInspector.byteCount();

    if (!Number.isInteger(offset) || offset < 0 || offset >= limit) {
      renderNotice(`Offset must be between 0 and ${limit - 1}.`, 'warn');
      return;
    }

    els.flipBtn.disabled = true;
    const result = await QSC.tamper({
      capsule_id: currentCapsuleId,
      byte_offset: offset,
      bit,
    });
    els.flipBtn.disabled = false;

    if (!result.ok) {
      renderNotice(result.data?.detail || 'Tamper request failed.', 'fail');
      return;
    }

    const data = result.data;
    HexInspector.markFlipped(offset);

    // A tamper can be rejected before the pipeline even runs - a flipped byte in
    // a JSON delimiter makes the capsule unparseable - so the outcome is read
    // from the status, with the failing stage named only when there is one.
    const caught = (data.stage_diagnostics || []).find((s) => s.status === 'FAIL');
    let summary;
    if (data.status === 'REJECTED') {
      summary = caught
        ? `Stopped at stage ${caught.stage} &mdash; ${QSC.escapeHtml(caught.name)}`
        : QSC.escapeHtml(data.reason || 'Rejected before validation.');
    } else {
      summary = 'Accepted &mdash; no control objected to this change.';
    }

    els.result.innerHTML = `
      <div class="divider"></div>
      <div class="split-head">
        <span>Tamper Result</span>
        <span class="pill pill--${data.status === 'REJECTED' ? 'rejected' : 'settled'}">${data.status}</span>
      </div>
      <div class="kv">
        <div class="kv__k">Byte offset</div><div class="kv__v">${offset} (0x${offset.toString(16)})</div>
        <div class="kv__k">Bit flipped</div><div class="kv__v">${bit}</div>
        <div class="kv__k">Byte value</div><div class="kv__v">0x${data.byte_before} &rarr; 0x${data.byte_after}</div>
        <div class="kv__k">Field affected</div><div class="kv__v">${QSC.escapeHtml(data.affected_field || 'structural')}</div>
        <div class="kv__k">Outcome</div><div class="kv__v">${summary}</div>
      </div>
      <div class="divider"></div>
      <div id="tamper-stages"></div>`;

    PipelineView.render(
      document.getElementById('tamper-stages'),
      data.stage_diagnostics,
      { emptyText: QSC.escapeHtml(data.reason || '') }
    );

    QSC.log(
      `bit flip at byte ${offset} in ${data.affected_field || 'structural'} -> ${data.status}`,
      data.status === 'REJECTED' ? 'ok' : 'err'
    );
  }

  async function replayCapsule() {
    if (!currentCapsuleId) return;

    els.replayBtn.disabled = true;
    const result = await QSC.replay(currentCapsuleId);
    els.replayBtn.disabled = false;

    if (!result.ok) {
      renderNotice(result.data?.detail || 'Replay request failed.', 'fail');
      return;
    }

    const data = result.data;
    els.result.innerHTML = `
      <div class="divider"></div>
      <div class="split-head">
        <span>Replay Result</span>
        <span class="pill pill--${data.status === 'REJECTED' ? 'rejected' : 'settled'}">${data.status}</span>
      </div>
      <p class="section-note">${QSC.escapeHtml(data.reason)}</p>
      <div class="kv">
        <div class="kv__k">Replay cache size</div><div class="kv__v">${data.replay_cache_size}</div>
      </div>
      <div class="divider"></div>
      <div id="replay-stages"></div>`;

    PipelineView.render(document.getElementById('replay-stages'), data.stage_diagnostics);
    QSC.log(`verbatim replay -> ${data.status}`, data.status === 'REJECTED' ? 'ok' : 'err');
  }

  function renderNotice(message, tone) {
    els.result.innerHTML = `
      <div class="divider"></div>
      <span class="pill pill--${tone}">${QSC.escapeHtml(message)}</span>`;
  }

  function reset() {
    els.result.innerHTML = '';
    HexInspector.clearFlips();
  }

  return { mount, setCapsule, reset };
})();
