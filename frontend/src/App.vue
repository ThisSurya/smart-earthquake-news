<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <nav class="navbar">
    <div class="navbar-inner">
      <div class="navbar-brand">
        <span class="brand-icon">🌍</span>
        <div class="brand-text">
          <span class="brand-title">Smart News</span>
          <span class="brand-subtitle">Earthquake Monitor</span>
        </div>
      </div>
      <div class="navbar-badge">
        <span class="live-dot"></span>
        <span class="live-text">LIVE</span>
      </div>
    </div>
  </nav>

  <main class="main-content">
    <RouterView />
  </main>
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--color-border);
}

.navbar-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-md) var(--space-xl);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.brand-icon {
  font-size: 1.75rem;
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.brand-title {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
}

.brand-subtitle {
  font-weight: 400;
  font-size: 0.7rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.navbar-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.25);
  border-radius: var(--radius-full);
}

.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ef4444;
  animation: seismicPulse 2s infinite;
}

.live-text {
  font-size: 0.7rem;
  font-weight: 700;
  color: #ef4444;
  letter-spacing: 0.1em;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-xl);
}

@media (max-width: 640px) {
  .navbar-inner {
    padding: var(--space-sm) var(--space-md);
  }

  .main-content {
    padding: var(--space-md);
  }

  .brand-icon {
    font-size: 1.4rem;
  }

  .brand-title {
    font-size: 0.95rem;
  }
}
</style>
