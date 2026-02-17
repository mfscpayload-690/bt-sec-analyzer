<script>
  import { activePage, engineStatus } from './lib/stores/app.js';
  import { getStatus } from './lib/services/api.js';
  import { onMount } from 'svelte';

  import Sidebar from './lib/components/Sidebar.svelte';
  import Dashboard from './lib/components/Dashboard.svelte';
  import AttackPanel from './lib/components/AttackPanel.svelte';
  import LogViewer from './lib/components/LogViewer.svelte';
  import TerminalPanel from './lib/components/TerminalPanel.svelte';
  import ReportPanel from './lib/components/ReportPanel.svelte';
  import Settings from './lib/components/Settings.svelte';
  import Toasts from './lib/components/Toasts.svelte';

  onMount(async () => {
    try {
      const status = await getStatus();
      engineStatus.set({ ...status, connected: true });
    } catch {
      engineStatus.update(s => ({ ...s, connected: false }));
    }
  });
</script>

<div class="flex min-h-screen bg-slate-950 text-slate-200">
  <Sidebar />

  <main class="flex-1 overflow-y-auto">
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

<Toasts />
