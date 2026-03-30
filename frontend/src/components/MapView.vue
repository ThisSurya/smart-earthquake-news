<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { useMap } from '@/composables/useMap'
import type { EarthquakeEvent, ClusteredResult } from '@/services/api'

const props = defineProps<{
  events: EarthquakeEvent[]
  clusters: ClusteredResult[]
  userLocation: { lat: number; lon: number } | null
}>()

const emit = defineEmits<{
  'select-event': [event: EarthquakeEvent]
  'select-cluster': [cluster: ClusteredResult]
}>()

const mapContainer = ref<HTMLDivElement | null>(null)
const { initMap, renderMarkers, setUserLocationMarker, fitBounds, invalidateSize } = useMap(mapContainer)

function onEventClick(event: EarthquakeEvent) {
  emit('select-event', event)
}

function onClusterClick(cluster: ClusteredResult) {
  emit('select-cluster', cluster)
}

function updateMarkers() {
  renderMarkers(props.events, props.clusters, onEventClick, onClusterClick)

  if (props.userLocation) {
    setUserLocationMarker(props.userLocation.lat, props.userLocation.lon)
  }

  nextTick(() => {
    fitBounds()
  })
}

onMounted(() => {
  const center: [number, number] = props.userLocation
    ? [props.userLocation.lat, props.userLocation.lon]
    : [-2.5, 118.0]
  initMap(center, props.userLocation ? 8 : 5)
  updateMarkers()
})

watch(
  () => [props.events, props.clusters, props.userLocation],
  () => {
    updateMarkers()
  },
  { deep: true },
)

// Expose invalidateSize for parent to call after layout changes
defineExpose({ invalidateSize })
</script>

<template>
  <div class="map-view">
    <div ref="mapContainer" class="map-container"></div>

    <!-- Legend overlay -->
    <div class="map-legend">
      <div class="legend-item">
        <span class="legend-dot" style="background: #f59e0b"></span>
        <span>Kejadian</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot" style="background: #22c55e"></span>
        <span>Cluster</span>
      </div>
      <div class="legend-item" v-if="userLocation">
        <span class="legend-dot user-dot"></span>
        <span>Anda</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.map-view {
  position: relative;
  width: 100%;
  height: 100%;
}

.map-container {
  width: 100%;
  height: 100%;
}

.map-legend {
  position: absolute;
  bottom: 16px;
  left: 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px 14px;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(8px);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  z-index: 10;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.7rem;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  border: 1.5px solid rgba(255, 255, 255, 0.6);
}

.legend-dot.user-dot {
  background: #3b82f6;
  box-shadow: 0 0 6px rgba(59, 130, 246, 0.5);
}

/* Fix leaflet z-index in scoped context */
:deep(.leaflet-pane) {
  z-index: 1;
}

:deep(.leaflet-control) {
  z-index: 5;
}

:deep(.event-marker) {
  background: none !important;
  border: none !important;
}

:deep(.user-location-marker) {
  background: none !important;
  border: none !important;
}

@keyframes userPulse {
  0%, 100% {
    box-shadow: 0 0 16px rgba(59, 130, 246, 0.6), 0 0 32px rgba(59, 130, 246, 0.3);
  }
  50% {
    box-shadow: 0 0 24px rgba(59, 130, 246, 0.8), 0 0 48px rgba(59, 130, 246, 0.4);
  }
}
</style>
