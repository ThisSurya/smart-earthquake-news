<script setup lang="ts">
import { ref, watch } from 'vue'
import { PRESET_CITIES, getUserLocation } from '@/services/api'

const emit = defineEmits<{
  'location-change': [lat: number, lon: number, name?: string]
}>()

const selectedCity = ref('')
const locating = ref(false)
const locationError = ref('')

function onCityChange() {
  const city = PRESET_CITIES.find((c) => c.name === selectedCity.value)
  if (city) {
    locationError.value = ''
    emit('location-change', city.lat, city.lon, city.name)
  }
}

async function useMyLocation() {
  locating.value = true
  locationError.value = ''
  try {
    const position = await getUserLocation()
    selectedCity.value = ''
    emit('location-change', position.coords.latitude, position.coords.longitude, 'Lokasi Saya')
  } catch {
    locationError.value = 'Gagal mendapatkan lokasi'
  } finally {
    locating.value = false
  }
}

watch(selectedCity, () => {
  if (selectedCity.value) onCityChange()
})
</script>

<template>
  <header class="dashboard-header">
    <div class="header-left">
      <div class="brand">
        <span class="brand-icon">🌍</span>
        <div class="brand-text">
          <span class="brand-title">Smart News AI</span>
          <span class="brand-subtitle">Earthquake & Disaster Monitoring</span>
        </div>
      </div>
    </div>

    <div class="header-controls">
      <div class="city-select-wrapper">
        <select
          id="city-select"
          v-model="selectedCity"
          class="city-select"
        >
          <option value="" disabled>Pilih Kota...</option>
          <option v-for="city in PRESET_CITIES" :key="city.name" :value="city.name">
            {{ city.name }}
          </option>
        </select>
      </div>

      <button
        id="btn-use-location"
        class="btn-location"
        :disabled="locating"
        @click="useMyLocation"
      >
        <span v-if="locating" class="spinner-sm"></span>
        <span v-else>📍</span>
        {{ locating ? 'Mencari...' : 'Lokasi Saya' }}
      </button>

      <div class="live-indicator">
        <span class="live-dot"></span>
        <span class="live-label">LIVE</span>
      </div>
    </div>

    <p v-if="locationError" class="location-error">{{ locationError }}</p>
  </header>
</template>

<style scoped>
.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--color-border);
  flex-wrap: wrap;
  position: relative;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.brand {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.brand-icon {
  font-size: 1.6rem;
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
}

.brand-title {
  font-weight: 800;
  font-size: 1.05rem;
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
}

.brand-subtitle {
  font-weight: 400;
  font-size: 0.65rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.city-select-wrapper {
  position: relative;
}

.city-select {
  appearance: none;
  padding: 8px 32px 8px 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-bg-input);
  color: var(--color-text-primary);
  font-size: 0.82rem;
  font-weight: 500;
  font-family: var(--font-family);
  cursor: pointer;
  transition: all var(--transition-fast);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  min-width: 140px;
}

.city-select:hover,
.city-select:focus {
  border-color: var(--color-primary);
  outline: none;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.15);
}

.city-select option {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.btn-location {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-bg-glass);
  color: var(--color-text-primary);
  font-size: 0.82rem;
  font-weight: 600;
  font-family: var(--font-family);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.btn-location:hover:not(:disabled) {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
  box-shadow: var(--shadow-glow);
}

.btn-location:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner-sm {
  width: 14px;
  height: 14px;
  border: 2px solid var(--color-text-muted);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 10px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.25);
  border-radius: var(--radius-full);
}

.live-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #ef4444;
  animation: seismicPulse 2s infinite;
}

.live-label {
  font-size: 0.65rem;
  font-weight: 700;
  color: #ef4444;
  letter-spacing: 0.1em;
}

.location-error {
  width: 100%;
  font-size: 0.78rem;
  color: var(--color-severity-high);
  text-align: right;
  margin-top: -4px;
}

@media (max-width: 640px) {
  .dashboard-header {
    padding: var(--space-sm) var(--space-md);
  }

  .header-controls {
    width: 100%;
    justify-content: space-between;
  }

  .city-select {
    min-width: 110px;
    font-size: 0.78rem;
  }
}
</style>
