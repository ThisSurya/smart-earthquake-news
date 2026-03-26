<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type { NewsRecommendation } from '@/services/api'
import { calculateNewsDistance } from '@/utils/distance'

interface Props {
  userLat: number | null
  userLon: number | null
  recommendations: NewsRecommendation[]
  radiusKm?: number
}

const props = withDefaults(defineProps<Props>(), {
  radiusKm: 50
})

const mapContainer = ref<HTMLDivElement | null>(null)
let map: L.Map | null = null
let userMarker: L.Marker | null = null
let newsMarkers: L.Marker[] = []
let radiusCircles: L.Circle[] = []
let userRadiusCircle: L.Circle | null = null

// Custom icons
const getUserIcon = () => {
  return L.divIcon({
    html: '<div class="map-marker user-marker">📍</div>',
    className: 'custom-div-icon',
    iconSize: [30, 30],
    iconAnchor: [15, 15]
  })
}

const getNewsIcon = (isAffected: boolean) => {
  const emoji = isAffected ? '🔴' : '🟢'
  return L.divIcon({
    html: `<div class="map-marker news-marker ${isAffected ? 'affected' : 'safe'}">${emoji}</div>`,
    className: 'custom-div-icon',
    iconSize: [30, 30],
    iconAnchor: [15, 15]
  })
}

function initMap() {
  if (!mapContainer.value || map) return

  // Initialize map centered on Indonesia
  const centerLat = props.userLat ?? -2.5489
  const centerLon = props.userLon ?? 118.0149

  map = L.map(mapContainer.value).setView([centerLat, centerLon], 5)

  // Add OpenStreetMap tiles
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19
  }).addTo(map)
}

function clearMarkers() {
  newsMarkers.forEach(marker => marker.remove())
  radiusCircles.forEach(circle => circle.remove())
  newsMarkers = []
  radiusCircles = []

  if (userMarker) {
    userMarker.remove()
    userMarker = null
  }

  if (userRadiusCircle) {
    userRadiusCircle.remove()
    userRadiusCircle = null
  }
}

function updateMap() {
  if (!map) return

  clearMarkers()

  // Add user location marker
  if (props.userLat !== null && props.userLon !== null) {
    userMarker = L.marker([props.userLat, props.userLon], {
      icon: getUserIcon()
    }).addTo(map)

    userMarker.bindPopup(`
      <div class="map-popup user-popup">
        <h4>📍 Lokasi Anda</h4>
        <p>Lat: ${props.userLat.toFixed(4)}, Lon: ${props.userLon.toFixed(4)}</p>
      </div>
    `)

    // Draw user radius circle (area of interest)
    userRadiusCircle = L.circle([props.userLat, props.userLon], {
      color: '#3b82f6',
      fillColor: '#3b82f6',
      fillOpacity: 0.1,
      radius: props.radiusKm * 1000, // km to meters
      weight: 2,
      dashArray: '5, 5'
    }).addTo(map)

    userRadiusCircle.bindPopup(`
      <div class="map-popup">
        <h4>🔵 Area Pemantauan</h4>
        <p>Radius: ${props.radiusKm} km dari lokasi Anda</p>
      </div>
    `)

    // Center map on user location
    map.setView([props.userLat, props.userLon], 8)
  }

  // Add news recommendation markers
  props.recommendations.forEach((rec, index) => {
    if (!rec.latitude || !rec.longitude || !map) return

    const newsLat = parseFloat(rec.latitude)
    const newsLon = parseFloat(rec.longitude)

    if (isNaN(newsLat) || isNaN(newsLon)) return

    // Calculate distance from user to earthquake location
    const calculatedDistance = calculateNewsDistance(
      props.userLat,
      props.userLon,
      rec.latitude,
      rec.longitude
    )

    // Determine if user is affected (within radius)
    const isAffected = calculatedDistance !== null && calculatedDistance <= props.radiusKm

    // Add news marker
    const marker = L.marker([newsLat, newsLon], {
      icon: getNewsIcon(isAffected)
    }).addTo(map)

    const statusText = calculatedDistance !== null
      ? (isAffected
          ? `⚠️ DALAM RADIUS DAMPAK (${calculatedDistance.toFixed(1)} km dari Anda)`
          : `✅ Di luar radius dampak (${calculatedDistance.toFixed(1)} km dari Anda)`)
      : 'Jarak tidak dapat dihitung'

    const statusClass = isAffected ? 'status-danger' : 'status-safe'

    marker.bindPopup(`
      <div class="map-popup news-popup">
        <h4>📰 Berita Gempa #${index + 1}</h4>
        <p class="${statusClass}">${statusText}</p>
        <p><strong>Lokasi:</strong> ${newsLat.toFixed(4)}, ${newsLon.toFixed(4)}</p>
        <div class="popup-content">${rec.content?.substring(0, 200)}...</div>
      </div>
    `)

    newsMarkers.push(marker)

    // Draw radius circle around earthquake location (danger zone)
    const circleColor = isAffected ? '#ef4444' : '#22c55e'
    const circle = L.circle([newsLat, newsLon], {
      color: circleColor,
      fillColor: circleColor,
      fillOpacity: isAffected ? 0.2 : 0.1,
      radius: props.radiusKm * 1000, // km to meters
      weight: 2
    }).addTo(map)

    circle.bindPopup(`
      <div class="map-popup">
        <h4>${isAffected ? '🔴' : '🟢'} Radius Dampak</h4>
        <p>Area dalam radius ${props.radiusKm} km dari lokasi gempa</p>
      </div>
    `)

    radiusCircles.push(circle)
  })

  // Fit map bounds to show all markers
  if (newsMarkers.length > 0 && userMarker) {
    const group = L.featureGroup([userMarker, ...newsMarkers])
    map.fitBounds(group.getBounds().pad(0.1))
  }
}

onMounted(() => {
  initMap()
  updateMap()
})

watch(
  () => [props.userLat, props.userLon, props.recommendations, props.radiusKm],
  () => {
    updateMap()
  },
  { deep: true }
)

onBeforeUnmount(() => {
  clearMarkers()
  if (map) {
    map.remove()
    map = null
  }
})
</script>

<template>
  <div class="news-map-view">
    <div class="map-header">
      <h3 class="map-title">🗺️ Peta Dampak Gempa</h3>
      <div class="map-legend">
        <div class="legend-item">
          <span class="legend-marker user">📍</span>
          <span>Lokasi Anda</span>
        </div>
        <div class="legend-item">
          <span class="legend-marker affected">🔴</span>
          <span>Dalam radius dampak</span>
        </div>
        <div class="legend-item">
          <span class="legend-marker safe">🟢</span>
          <span>Di luar radius dampak</span>
        </div>
      </div>
    </div>
    <div ref="mapContainer" class="map-container"></div>
    <div class="map-info">
      <p>
        <strong>Info:</strong> Radius merah menunjukkan area dampak gempa ({{ radiusKm }} km).
        Jika lokasi Anda berada dalam radius merah, Anda berada dalam area yang berpotensi terdampak.
      </p>
    </div>
  </div>
</template>

<style scoped>
.news-map-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  padding: var(--space-lg);
  background: var(--color-bg-glass);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.map-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
  flex-wrap: wrap;
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--color-border);
}

.map-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.map-legend {
  display: flex;
  gap: var(--space-md);
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

.legend-marker {
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.map-container {
  width: 100%;
  height: 500px;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.map-info {
  padding: var(--space-sm) var(--space-md);
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.map-info strong {
  color: var(--color-primary);
  font-weight: 600;
}

/* Custom Leaflet popup styles */
:deep(.leaflet-popup-content-wrapper) {
  border-radius: var(--radius-md);
  padding: 0;
  overflow: hidden;
}

:deep(.leaflet-popup-content) {
  margin: 0;
  min-width: 250px;
}

:deep(.map-popup) {
  padding: var(--space-md);
}

:deep(.map-popup h4) {
  margin: 0 0 var(--space-sm) 0;
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

:deep(.map-popup p) {
  margin: var(--space-xs) 0;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

:deep(.map-popup .status-danger) {
  color: var(--color-severity-high);
  font-weight: 600;
  padding: 4px 8px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: var(--radius-sm);
}

:deep(.map-popup .status-safe) {
  color: var(--color-severity-low);
  font-weight: 600;
  padding: 4px 8px;
  background: rgba(34, 197, 94, 0.1);
  border-radius: var(--radius-sm);
}

:deep(.map-popup .popup-content) {
  margin-top: var(--space-sm);
  padding-top: var(--space-sm);
  border-top: 1px solid var(--color-border);
  font-size: 0.8rem;
  color: var(--color-text-muted);
  line-height: 1.5;
  max-height: 100px;
  overflow-y: auto;
}

/* Custom marker styles */
:deep(.map-marker) {
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
  animation: markerPulse 2s ease-in-out infinite;
}

:deep(.map-marker.user-marker) {
  font-size: 2rem;
}

:deep(.map-marker.affected) {
  animation: markerPulse 1s ease-in-out infinite;
}

@keyframes markerPulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .map-container {
    height: 400px;
  }

  .map-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .map-legend {
    width: 100%;
    justify-content: space-between;
  }

  .legend-item {
    font-size: 0.75rem;
  }
}

@media (max-width: 480px) {
  .map-container {
    height: 300px;
  }

  .news-map-view {
    padding: var(--space-md);
  }
}
</style>
