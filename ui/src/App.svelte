<script>
  import { activePage, engineStatus, deviceCount, activeAttackCount } from './lib/stores/app.js';
  import { logError, CATEGORIES } from './lib/services/errors.js';
  import { onMount } from 'svelte';

  import Sidebar      from './lib/components/Sidebar.svelte';
  import Dashboard    from './lib/components/Dashboard.svelte';
  import AttackPanel  from './lib/components/AttackPanel.svelte';
  import LogViewer    from './lib/components/LogViewer.svelte';
  import TerminalPanel from './lib/components/TerminalPanel.svelte';
  import ReportPanel  from './lib/components/ReportPanel.svelte';
  import Settings     from './lib/components/Settings.svelte';
  import Toasts       from './lib/components/Toasts.svelte';

  // ── Uptime counter ───────────────────────────────────────────────────────
  let sessionStart = Date.now();
  let uptimeStr    = $state('00:00');

  // ── Status polling — uses raw fetch to avoid routing /status 500s
  //    through the logError → forwardToBackend → /api/log → 500 cycle.
  // ─────────────────────────────────────────────────────────────────────────
  let retryTimer;

  async function checkStatus() {
    clearTimeout(retryTimer);               // ← prevents timer stacking
    try {
      const res = await fetch('/api/status');
      if (res.ok) {
        const data = await res.json();
        engineStatus.set({ ...data, connected: true });
        return;                             // ← success: no retry scheduled
      }
    } catch {
      // ECONNREFUSED / network error — swallowed intentionally
    }
    // Any non-2xx or network error → mark offline, schedule single retry
    engineStatus.update(s => ({ ...s, connected: false }));
    retryTimer = setTimeout(checkStatus, 5000);
  }

  const pageMeta = {
    dashboard: { label: 'Dashboard',     sub: 'Device Discovery' },
    attacks:   { label: 'Attack Panel',  sub: 'Simulations' },
    logs:      { label: 'Log Viewer',    sub: 'Structured Output' },
    terminal:  { label: 'Terminal',      sub: 'Interactive Shell' },
    reports:   { label: 'Reports',       sub: 'Export & Analysis' },
    settings:  { label: 'Settings',      sub: 'Configuration' },
  };

  onMount(() => {
    checkStatus();

    // Poll only when already connected (no stacking)
    const pollTimer = setInterval(() => {
      if ($engineStatus.connected) checkStatus();
    }, 30000);

    // Uptime clock
    const uptimeClock = setInterval(() => {
      const s = Math.floor((Date.now() - sessionStart) / 1000);
      const m = Math.floor(s / 60);
      const h = Math.floor(m / 60);
      uptimeStr = h > 0
        ? `${String(h).padStart(2,'0')}:${String(m%60).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`
        : `${String(m).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`;
    }, 1000);

    // Global unhandled error capture
    const handleError = (ev) => logError(ev.error ?? ev.message, 'window', CATEGORIES.UI);
    const handleReject = (ev) => { logError(ev.reason, 'unhandledrejection', CATEGORIES.UI); ev.preventDefault(); };
    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleReject);

    return () => {
      clearTimeout(retryTimer);
      clearInterval(pollTimer);
      clearInterval(uptimeClock);
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleReject);
    };
  });
</script>

<div class="flex flex-col h-screen overflow-hidden" style="background: var(--bg-base);">

  <!-- ═══ Header ════════════════════════════════════════════════════════ -->
  <header class="flex items-center justify-between px-5 shrink-0 border-b"
    style="height: var(--header-h); background: var(--bg-surface); border-color: var(--border);">

    <!-- Left: brand -->
    <div class="flex items-center gap-3 min-w-0">
      <!-- Bluetooth icon -->
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" style="flex-shrink:0;">
        <path d="M12 2 L18 7 L13 12 L18 17 L12 22 L12 12 Z"
          stroke="var(--cyan)" stroke-width="1.5" stroke-linejoin="round" fill="none"/>
        <path d="M12 12 L6 7" stroke="var(--cyan)" stroke-width="1.5" stroke-linecap="round"/>
        <path d="M12 12 L6 17" stroke="var(--cyan)" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
      <div class="flex items-baseline gap-1.5 min-w-0">
        <span class="text-sm font-bold tracking-wider" style="color: var(--text-bright);">BT-SEC</span>
        <span class="text-sm font-light tracking-widest" style="color: var(--text-dim);">ANALYZER</span>
        <span class="text-[9px] px-1.5 py-0.5 rounded mono ml-1 hidden sm:inline"
          style="background:rgba(34,211,238,0.07);color:var(--cyan);border:1px solid rgba(34,211,238,0.15);">
          v0.1.0
        </span>
      </div>
    </div>

    <!-- Center: breadcrumb -->
    <div class="hidden md:flex items-center gap-1.5 text-xs mono" style="color: var(--text-dim);">
      <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
        style="color:var(--cyan);opacity:0.7;">
        <polyline points="9 18 15 12 9 6"/>
      </svg>
      <span style="color:var(--text-dim);">{pageMeta[$activePage]?.label ?? $activePage}</span>
      <span style="opacity:0.4;">/</span>
      <span style="color:var(--text-dim);opacity:0.7;">{pageMeta[$activePage]?.sub ?? ''}</span>
    </div>

    <!-- Right: status bar -->
    <div class="flex items-center gap-4">

      <!-- Uptime -->
      <div class="hidden lg:flex items-center gap-1.5 text-[10px] mono" style="color: var(--text-dim);">
        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
        </svg>
        {uptimeStr}
      </div>

      <div class="hidden lg:block" style="width:1px;height:14px;background:var(--border);"></div>

      <!-- Device count -->
      <div class="hidden sm:flex items-center gap-1.5 text-[10px]">
        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
          style="color:var(--text-dim);">
          <circle cx="12" cy="12" r="3"/>
          <path d="M6.34 17.66a8 8 0 0 1 0-11.32M17.66 6.34a8 8 0 0 1 0 11.32"/>
        </svg>
        <span class="mono font-medium" style="color: var(--cyan);">{$deviceCount}</span>
        <span style="color: var(--text-dim);">devices</span>
      </div>

      <div style="width:1px;height:14px;background:var(--border);"></div>

      <!-- Ethical mode -->
      <div class="flex items-center gap-1.5 text-[10px]">
        <span class="status-dot {$engineStatus.ethical_mode ? 'online' : 'warn'}"></span>
        <span class="hidden sm:inline" style="color:var(--text-dim);">Ethical</span>
        <span style="color:{$engineStatus.ethical_mode ? 'var(--green)' : 'var(--amber)'};">
          {$engineStatus.ethical_mode ? 'ON' : 'OFF'}
        </span>
      </div>

      <div style="width:1px;height:14px;background:var(--border);"></div>

      <!-- Connection pill -->
      <div class="flex items-center gap-1.5 text-[10px] px-2 py-1 rounded"
        style="background:{$engineStatus.connected ? 'rgba(16,185,129,0.08)' : 'rgba(239,68,68,0.08)'};
               border:1px solid {$engineStatus.connected ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'};">
        <span class="status-dot pulse {$engineStatus.connected ? 'online' : 'offline'}"></span>
        <span class="mono font-medium hidden sm:inline"
          style="color:{$engineStatus.connected ? 'var(--green)' : 'var(--red)'};">
          {$engineStatus.connected ? 'LIVE' : 'OFFLINE'}
        </span>
      </div>
    </div>
  </header>

  <!-- ═══ Body ══════════════════════════════════════════════════════════ -->
  <div class="flex flex-1 overflow-hidden">
    <Sidebar />

    <!-- Main content: relative so overlay can be positioned inside it -->
    <main class="flex-1 overflow-y-auto relative" style="background: var(--bg-base);">

      <!-- ── Offline overlay ──────────────────────────────────────────── -->
      {#if !$engineStatus.connected}
        <div class="absolute inset-0 z-20 flex items-center justify-center"
          style="background: rgba(7,11,18,0.88); backdrop-filter: blur(4px);">
          <div class="card p-8 max-w-md w-full mx-4 space-y-5 text-center"
            style="border-color: rgba(239,68,68,0.25);">

            <!-- Red warning icon -->
            <div class="w-14 h-14 rounded-full flex items-center justify-center mx-auto"
              style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.25);">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--red)" stroke-width="1.5">
                <path d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </div>

            <div>
              <h2 class="text-sm font-semibold mb-1" style="color: var(--text-bright);">Backend Offline</h2>
              <p class="text-xs" style="color: var(--text-dim);">
                The Python engine is not reachable on port 8745.
              </p>
            </div>

            <!-- Start command -->
            <div class="rounded-lg p-3 text-left"
              style="background: var(--bg-base); border: 1px solid var(--border);">
              <p class="text-[9px] uppercase tracking-widest mb-1.5" style="color: var(--text-dim);">Start command</p>
              <p class="text-[11px] mono break-all" style="color: var(--cyan);">
                poetry run uvicorn bt_sectester.core.api_bridge:app --host 127.0.0.1 --port 8745
              </p>
            </div>

            <!-- Retry button -->
            <button type="button" onclick={checkStatus}
              class="flex items-center gap-2 mx-auto px-5 py-2 rounded-lg text-xs font-semibold transition-all"
              style="background:rgba(34,211,238,0.08);color:var(--cyan);border:1px solid rgba(34,211,238,0.25);">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
                <path d="M21 3v5h-5"/>
                <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
                <path d="M8 16H3v5"/>
              </svg>
              Retry Connection
            </button>
          </div>
        </div>
      {/if}

      <!-- ── Page content ──────────────────────────────────────────────── -->
      {#if $activePage === 'dashboard'}
        <Dashboard />
      {:else if $activePage === 'attacks'}
        <AttackPanel />
      {:else if $activePage === 'logs'}
        <LogViewer />
      {:else if $activePage === 'terminal'}
        <TerminalPanel />
      {:else if $activePage === 'reports'}
        <ReportPanel />
      {:else if $activePage === 'settings'}
        <Settings />
      {/if}
    </main>
  </div>
</div>

<Toasts />
