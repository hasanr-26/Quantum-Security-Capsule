/* ==========================================================================
   pipeline_view.js - renders the five-stage zero-trust validation trace.

   Shared by the Settlement tab and the Attack Lab, because a rejection should
   be presented exactly as legibly as a success: same stages, same timings,
   same layout - only the outcome differs.
   ========================================================================== */

const PipelineView = (() => {

  const CLASS_FOR = { PASS: 'pass', FAIL: 'fail', SKIPPED: 'skip' };

  function render(container, stages, options = {}) {
    if (!stages || stages.length === 0) {
      container.innerHTML = `<div class="empty">${options.emptyText || 'No diagnostics available.'}</div>`;
      return;
    }

    container.innerHTML = stages.map((stage) => {
      const tone = CLASS_FOR[stage.status] || 'skip';
      const timing = stage.status === 'SKIPPED'
        ? '<span class="muted">--</span>'
        : formatMicros(stage.elapsed_us);

      return `
        <div class="stage stage--${tone}">
          <div class="stage__num">${String(stage.stage).padStart(2, '0')}</div>
          <div>
            <div class="stage__name">${QSC.escapeHtml(stage.name)}</div>
            <div class="stage__control">${QSC.escapeHtml(stage.control)}</div>
            <div class="stage__detail">${QSC.escapeHtml(stage.detail)}</div>
          </div>
          <div class="stage__time">${timing}</div>
          <div style="text-align:right"><span class="pill pill--${tone}">${stage.status}</span></div>
        </div>`;
    }).join('');
  }

  /**
   * Formats a microsecond timing at a sensible scale.
   *
   * Stages differ by three orders of magnitude - a version string comparison
   * costs about a microsecond, ML-DSA verification costs several milliseconds -
   * so a single unit would make the cheap stages unreadable.
   */
  function formatMicros(us) {
    if (us === null || us === undefined) return '--';
    if (us >= 1000) return `${(us / 1000).toFixed(2)} ms`;
    return `${us.toFixed(1)} &micro;s`;
  }

  return { render, formatMicros };
})();
