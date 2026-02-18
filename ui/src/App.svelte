<script>
  import { activePage, engineStatus } from './lib/stores/app.js';
  import { getStatus } from './lib/services/api.js';
  import { logError, onError, CATEGORIES } from './lib/services/errors.js';
  import { onMount } from 'svelte';

  import Sidebar from './lib/components/Sidebar.svelte';
  import Dashboard from './lib/components/Dashboard.svelte';
  import AttackPanel from './lib/components/AttackPanel.svelte';
  import LogViewer from './lib/components/LogViewer.svelte';
  import TerminalPanel from './lib/components/TerminalPanel.svelte';
  import ReportPanel from './lib/components/ReportPanel.svelte';
  import Settings from './lib/components/Settings.svelte';
  import Toasts from './lib/components/Toasts.svelte';

  let retryTimer;

  async function checkStatus() {
    try {
      const status = await getStatus();
      engineStatus.set({ ...status, connected: true });
    } catch {
      engineStatus.update(s => ({ ...s, connected: false }));
      retryTimer = setTimeout(checkStatus, 5000);
    }
  }

  onMount(() => {
    checkStatus();

    const pollTimer = setInterval(() => {
      if ($engineStatus.connected) checkStatus();
    }, 30000);

    const handleError = (event) => {
      logError(event.error ?? event.message, 'window.onerror', CATEGORIES.UI);
    };
    const handleRejection = (event) => {
      logError(event.reason, 'unhandledrejection', CATEGORIES.UI);
      event.preventDefault();
    };

    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleRejection);

    return () => {
      clearTimeout(retryTimer);
      clearInterval(pollTimer);
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleRejection);
    };
  });
</script>

<!-- Root layout: topbar + sidebar + content -->
<div class="flex flex-col h-screen overflow-hidden" style="background: var(--bg-base);">

  <!-- ── Top Header Bar ─────────────────────────────────────────────── -->
  <header class="flex items-center justify-between px-4 h-11 shrink-0 border-b"
    style="background: var(--bg-surface); border-color: var(--border);">

    <!-- Left: brand -->
    <div class="flex items-center gap-3">
      <!-- BT Logo icon -->
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
        <path d="M12 2 L18 7 L13 12 L18 17 L12 22 L12 12 Z" stroke="#22d3ee" stroke-width="1.5" fill="none"/>
        <path d="M12 12 L6 7" stroke="#22d3ee" stroke-width="1.5"/>
        <path d="M12 12 L6 17" stroke="#22d3ee" stroke-width="1.5"/>
      </svg>
      <span class="text-sm font-semibold tracking-wide" style="color: var(--text-bright);">
        bt-sec-analyzer
      </span>
      <span class="text-xs px-1.5 py-0.5 rounded font-mono"
        style="background: rgba(34,211,238,0.08); color: var(--cyan); border: 1px solid rgba(34,211,238,0.2);">
        v0.1.0
      </span>
    </div>

    <!-- Right: status pills -->
    <div class="flex items-center gap-4 text-xs">
      <!-- Ethical mode -->
      <div class="flex items-center gap-1.5">
        <span class="status-dot {$engineStatus.ethical_mode ? 'online' : 'warn'}"></span>
        <span style="color: var(--text-dim);">Ethical Mode</span>
        <span style="color: {$engineStatus.ethical_mode ? 'var(--green)' : 'var(--amber)'};">
          {$engineStatus.ethical_mode ? 'ON' : 'OFF'}
        </span>
      </div>

      <div style="width: 1px; height: 16px; background: var(--border);"></div>

      <!-- Adapter -->
      <div class="flex items-center gap-1.5">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
          style="color: var(--text-dim);">
          <circle cx="12" cy="12" r="3"/><path d="M6.34 17.66a8 8 0 0 1 0-11.32M17.66 6.34a8 8 0 0 1 0 11.32"/>
        </svg>
        <span class="mono" style="color: var(--text-dim);">{$engineStatus.adapter || 'hci0'}</span>
      </div>

      <div style="width: 1px; height: 16px; background: var(--border);"></div>

      <!-- Connection -->
      <div class="flex items-center gap-1.5">
        <span class="status-dot pulse {$engineStatus.connected ? 'online' : 'offline'}"></span>
        <span style="color: {$engineStatus.connected ? 'var(--green)' : 'var(--red)'};">
          {$engineStatus.connected ? 'CONNECTED' : 'OFFLINE'}
        </span>
      </div>
    </div>
  </header>

  <!-- ── Body: sidebar + page content ────────────────────────────────── -->
  <div class="flex flex-1 overflow-hidden">
    <Sidebar />
    <main class="flex-1 overflow-y-auto" style="background: var(--bg-base);">
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
