<script setup lang="ts">
import { onMounted, watch, ref } from 'vue'
import { useNews } from '@/composables/useNews'
import Header from '@/components/Header.vue'
import MapView from '@/components/MapView.vue'
import IncidentFeed from '@/components/IncidentFeed.vue'
import DetailPanel from '@/components/DetailPanel.vue'
import type { EarthquakeEvent, ClusteredResult } from '@/services/api'

const { state, fetchData, selectEvent, selectCluster, clearSelection, detectUserLocation, setUserLocation } = useNews()

const mapRef = ref<InstanceType<typeof MapView> | null>(null)
const currentLocationName = ref<string>('')

async function onLocationChange(lat: number, lon: number, name?: string) {
  setUserLocation(lat, lon)
  currentLocationName.value = name || `${lat.toFixed(2)}, ${lon.toFixed(2)}`
  await fetchData(lat, lon)
}

function onSelectEvent(event: EarthquakeEvent) {
  selectEvent(event)
}

function onSelectCluster(cluster: ClusteredResult) {
  selectCluster(cluster)
}

function onCloseDetail() {
  clearSelection()
}

onMounted(async () => {
  // Try to auto-detect location
  const loc = await detectUserLocation()
  if (loc) {
    currentLocationName.value = 'Lokasi Saya'
    await fetchData(loc.lat, loc.lon)
  }
})
</script>

<template>
  <div class="dashboard-layout">
    <Header @location-change="onLocationChange" />

    <!-- Status bar -->
    <div class="status-bar" v-if="currentLocationName || state.error">
      <div class="status-left" v-if="currentLocationName">
        <span class="status-icon">📍</span>
        <span class="status-text">{{ currentLocationName }}</span>
        <span v-if="state.loading" class="status-loading">
          <span class="spinner-xs"></span> Memuat data...
        </span>
        <span v-else-if="state.mode === 'clusters'" class="status-count">
          {{ state.clusters.length }} cluster
        </span>
        <span v-else-if="state.mode === 'events'" class="status-count">
          {{ state.events.length }} kejadian
        </span>
      </div>
      <div v-if="state.error" class="status-error">
        ⚠️ {{ state.error }}
        <button class="btn-retry-sm" @click="fetchData(state.userLocation!.lat, state.userLocation!.lon)">
          Coba Lagi
        </button>
      </div>
    </div>

    <!-- Main grid -->
    <div class="dashboard-grid">
      <div class="grid-map">
        <MapView
          ref="mapRef"
          :events="state.events"
          :clusters="state.clusters"
          :user-location="state.userLocation"
          @select-event="onSelectEvent"
          @select-cluster="onSelectCluster"
        />
      </div>

      <div class="grid-feed">
        <IncidentFeed
          :events="state.events"
          :clusters="state.clusters"
          :mode="state.mode"
          :loading="state.loading"
          @select-event="onSelectEvent"
          @select-cluster="onSelectCluster"
        />
      </div>
    </div>

    <!-- Detail panel overlay -->
    <DetailPanel
      :event="state.selectedEvent"
      :cluster="state.selectedCluster"
      @close="onCloseDetail"
    />
  </div>
</template>

<style scoped>
.dashboard-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.status-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
  padding: 6px var(--space-lg);
  background: rgba(30, 41, 59, 0.8);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
  flex-wrap: wrap;
}

.status-left {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.status-icon {
  font-size: 0.85rem;
}

.status-text {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.status-loading {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  color: var(--color-primary-light);
  font-weight: 500;
}

.spinner-xs {
  width: 12px;
  height: 12px;
  border: 2px solid var(--color-text-muted);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.status-count {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--color-text-muted);
  padding: 2px 8px;
  background: var(--color-bg-glass);
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border);
}

.status-error {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: 0.78rem;
  color: #ef4444;
  font-weight: 500;
}

.btn-retry-sm {
  padding: 3px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid #ef4444;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-retry-sm:hover {
  background: #ef4444;
  color: #fff;
}

.dashboard-grid {
  flex: 1;
  display: grid;
  grid-template-columns: 70% 30%;
  min-height: 0;
}

.grid-map {
  min-height: 0;
  overflow: hidden;
}

.grid-feed {
  min-height: 0;
  overflow: hidden;
}

@media (max-width: 900px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
    grid-template-rows: 55% 45%;
  }

  .grid-feed :deep(.incident-feed) {
    border-left: none;
    border-top: 1px solid var(--color-border);
  }
}

@media (max-width: 640px) {
  .dashboard-grid {
    grid-template-rows: 50% 50%;
  }

  .status-bar {
    padding: 4px var(--space-md);
  }
}
</style>
