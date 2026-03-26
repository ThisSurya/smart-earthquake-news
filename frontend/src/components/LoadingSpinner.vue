<script setup lang="ts">
defineProps<{
  size?: 'sm' | 'md' | 'lg'
  text?: string
}>()
</script>

<template>
  <div class="loading-container" :class="`size-${size || 'md'}`">
    <div class="spinner">
      <div class="ring"></div>
      <div class="ring"></div>
      <div class="ring"></div>
      <span class="seismic-icon">📡</span>
    </div>
    <p v-if="text" class="loading-text">{{ text }}</p>
  </div>
</template>

<style scoped>
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-lg);
  padding: var(--space-2xl);
}

.spinner {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.size-sm .spinner { width: 40px; height: 40px; }
.size-md .spinner { width: 64px; height: 64px; }
.size-lg .spinner { width: 96px; height: 96px; }

.ring {
  position: absolute;
  border: 2px solid transparent;
  border-radius: 50%;
  animation: spin 1.5s linear infinite;
}

.ring:nth-child(1) {
  width: 100%;
  height: 100%;
  border-top-color: var(--color-primary);
  border-right-color: var(--color-primary);
}

.ring:nth-child(2) {
  width: 75%;
  height: 75%;
  border-bottom-color: var(--color-accent);
  border-left-color: var(--color-accent);
  animation-duration: 1.2s;
  animation-direction: reverse;
}

.ring:nth-child(3) {
  width: 50%;
  height: 50%;
  border-top-color: var(--color-severity-high);
  animation-duration: 0.9s;
}

.seismic-icon {
  font-size: 1.2rem;
  animation: pulse 2s ease-in-out infinite;
}

.size-sm .seismic-icon { font-size: 0.8rem; }
.size-lg .seismic-icon { font-size: 1.8rem; }

.loading-text {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  text-align: center;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
