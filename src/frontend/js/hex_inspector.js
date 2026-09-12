/* ==========================================================================
   hex_inspector.js - Wireshark-style byte viewer for the capsule wire format.

   The bytes rendered here are the exact canonical JSON encoding the server
   hashed, signed and transmitted - not a re-serialisation. Selecting a field
   highlights precisely the byte range it occupies, using offsets computed
   server-side in src/capsule/wire.py.
   ========================================================================== */

const HexInspector = (() => {

  const BYTES_PER_ROW = 16;

  /* Muted, distinguishable field colours - signal, not decoration. */
  const FIELD_COLOURS = {
    version:            '#64748b',
    capsule_id:         '#3b82f6',
    sender_id:          '#0ea5e9',
    recipient_id:       '#06b6d4',
    issued_at:          '#94a3b8',
    expires_at:         '#94a3b8',
    policy:             '#8b5cf6',
    nonce:              '#f59e0b',
    kem_ciphertext:     '#10b981',
    payload_ciphertext: '#22c55e',
    payload_tag:        '#eab308',
    replay_token:       '#f97316',
    integrity_hash:     '#ec4899',
    signature:          '#ef4444',
  };

  const FIELD_NOTES = {
    version:            'Protocol version. Checked at stage 1.',
    capsule_id:         'Unique id. Also the AES-GCM associated data and HKDF salt.',
    sender_id:          'Originating institution. Visible to any interceptor.',
    recipient_id:       'Destination institution. Visible to any interceptor.',
    issued_at:          'Issue timestamp, part of the replay token binding.',
    expires_at:         'TTL bound. Enforced at stage 2.',
    policy:             'Classification, jurisdiction and hop limit. Covered by the integrity hash.',
    nonce:              '96-bit AES-GCM initialisation vector.',
    kem_ciphertext:     'ML-KEM-768 encapsulation, 1088 bytes. Yields the shared secret.',
    payload_ciphertext: 'AES-256-GCM sealed payload. Opaque without the KEM secret.',
    payload_tag:        '128-bit GCM authentication tag.',
    replay_token:       'SHA3-512 single-use token. Enforced at stage 3.',
    integrity_hash:     'SHA3-512 over every other field. Enforced at stage 4.',
    signature:          'ML-DSA-65 signature, 3309 bytes. Excluded from the hash, verified at stage 5.',
  };

  let state = {
    bytes: null,
    offsets: {},
    capsuleId: null,
    activeField: null,
    selectedOffset: null,
    flipped: new Set(),
  };

  let els = {};
  let byteSelectHandler = null;

  function mount(refs) {
    els = refs;
    els.legend.addEventListener('click', (event) => {
      const item = event.target.closest('.legend__item');
      if (item) selectField(item.dataset.field);
    });
    els.view.addEventListener('click', (event) => {
      const cell = event.target.closest('[data-offset]');
      if (cell) selectByte(Number(cell.dataset.offset));
    });
  }

  function onByteSelect(handler) { byteSelectHandler = handler; }

  /** Decodes the base64 wire format into a byte array and renders it. */
  function load(wireB64, fieldOffsets, capsuleId) {
    const binary = atob(wireB64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);

    state = {
      bytes,
      offsets: fieldOffsets || {},
      capsuleId,
      activeField: null,
      selectedOffset: null,
      flipped: new Set(),
    };

    renderLegend();
    render();
    els.meta.textContent = `${bytes.length} bytes  |  ${capsuleId}`;
  }

  /** Returns the field owning a given byte offset, if any. */
  function fieldAt(offset) {
    for (const [name, span] of Object.entries(state.offsets)) {
      if (offset >= span.key_start && offset < span.value_end) return name;
    }
    return null;
  }

  function renderLegend() {
    const names = Object.keys(state.offsets);
    els.legend.innerHTML = names.map((name) => {
      const colour = FIELD_COLOURS[name] || '#94a3b8';
      const span = state.offsets[name];
      return `<span class="legend__item" data-field="${name}" title="${QSC.escapeHtml(FIELD_NOTES[name] || '')}">
        <span style="color:${colour}">&#9632;</span> ${name}
        <span class="muted">${span.length}B</span>
      </span>`;
    }).join('');
  }

  function render() {
    const { bytes } = state;
    if (!bytes) return;

    const rows = [];
    for (let base = 0; base < bytes.length; base += BYTES_PER_ROW) {
      const hexCells = [];
      const asciiCells = [];

      for (let i = 0; i < BYTES_PER_ROW; i += 1) {
        const offset = base + i;
        if (offset >= bytes.length) {
          hexCells.push('<span class="hex__b">  </span>');
          continue;
        }

        const value = bytes[offset];
        const field = fieldAt(offset);
        const colour = field ? (FIELD_COLOURS[field] || '#94a3b8') : null;

        const classes = ['hex__b'];
        if (field) classes.push('is-field');
        if (state.activeField && field === state.activeField) classes.push('is-sel');
        if (state.flipped.has(offset)) classes.push('is-flip');
        if (state.selectedOffset === offset) classes.push('is-sel');

        const style = (colour && !classes.includes('is-sel') && !classes.includes('is-flip'))
          ? ` style="color:${colour}"` : '';

        hexCells.push(
          `<span class="${classes.join(' ')}" data-offset="${offset}"${style}>${value.toString(16).padStart(2, '0')}</span>`
        );

        const printable = value >= 32 && value < 127 ? String.fromCharCode(value) : '.';
        const aClasses = ['hex__a'];
        if (state.activeField && field === state.activeField) aClasses.push('is-field');
        if (state.flipped.has(offset)) aClasses.push('is-flip');
        asciiCells.push(
          `<span class="${aClasses.join(' ')}" data-offset="${offset}">${QSC.escapeHtml(printable)}</span>`
        );
      }

      rows.push(
        `<div class="hex__row">
          <span class="hex__offset">${base.toString(16).padStart(8, '0')}</span>
          <span class="hex__bytes">${hexCells.join('')}</span>
          <span class="hex__ascii">|${asciiCells.join('')}|</span>
        </div>`
      );
    }

    els.view.innerHTML = rows.join('');
  }

  function selectField(name) {
    state.activeField = state.activeField === name ? null : name;
    [...els.legend.querySelectorAll('.legend__item')].forEach((item) => {
      item.classList.toggle('is-active', item.dataset.field === state.activeField);
    });
    render();

    if (state.activeField) {
      const span = state.offsets[state.activeField];
      showDetail({
        field: state.activeField,
        offset: span.value_start,
        length: span.length,
        note: FIELD_NOTES[state.activeField],
      });
      const row = els.view.querySelector(`[data-offset="${span.value_start}"]`);
      if (row) row.scrollIntoView({ block: 'center', behavior: 'smooth' });
      if (byteSelectHandler) byteSelectHandler(span.value_start);
    }
  }

  function selectByte(offset) {
    state.selectedOffset = offset;
    const field = fieldAt(offset);
    const value = state.bytes[offset];
    render();
    showDetail({
      field,
      offset,
      byteHex: value.toString(16).padStart(2, '0'),
      byteBin: value.toString(2).padStart(8, '0'),
      byteChar: value >= 32 && value < 127 ? String.fromCharCode(value) : '(non-printable)',
      note: field ? FIELD_NOTES[field] : 'Structural JSON byte, outside any field value.',
    });
    if (byteSelectHandler) byteSelectHandler(offset);
  }

  function showDetail(info) {
    const rows = [
      ['Byte offset', `${info.offset}  (0x${info.offset.toString(16)})`],
      ['Field', info.field || 'structural'],
    ];
    if (info.byteHex) {
      rows.push(['Value (hex)', `0x${info.byteHex}`]);
      rows.push(['Value (bin)', info.byteBin]);
      rows.push(['Character', info.byteChar]);
    }
    if (info.length) rows.push(['Field length', `${info.length} bytes`]);

    els.detail.innerHTML = rows.map(([k, v]) =>
      `<div class="kv__k">${k}</div><div class="kv__v">${QSC.escapeHtml(v)}</div>`
    ).join('') + (info.note
      ? `<div class="kv__k" style="grid-column:1/-1; padding-top:8px; line-height:1.55">${QSC.escapeHtml(info.note)}</div>`
      : '');
  }

  function markFlipped(offset) {
    state.flipped.add(offset);
    render();
  }

  function clearFlips() {
    state.flipped.clear();
    render();
  }

  const hasCapsule = () => Boolean(state.bytes);
  const byteCount  = () => (state.bytes ? state.bytes.length : 0);
  const getOffsets = () => state.offsets;

  return { mount, load, onByteSelect, selectField, markFlipped, clearFlips, hasCapsule, byteCount, getOffsets, FIELD_COLOURS };
})();
