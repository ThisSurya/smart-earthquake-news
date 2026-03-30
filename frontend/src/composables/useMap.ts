import { onBeforeUnmount, type Ref } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type { EarthquakeEvent, ClusteredResult } from '@/services/api'

export interface MapInstance {
  map: L.Map
  markersLayer: L.LayerGroup
}

const EVENT_MARKER_COLOR = '#f59e0b'
const CLUSTER_MARKER_COLOR = '#22c55e'

const DARK_TILE_URL = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
const DARK_TILE_ATTR =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>'

function createMarkerIcon(count?: number): L.DivIcon {
  const color = count ? CLUSTER_MARKER_COLOR : EVENT_MARKER_COLOR
  const size = count ? Math.min(44 + count * 2, 60) : 32
  const borderWidth = count ? 3 : 2

  const innerHtml = count
    ? `<div style="
        width:${size}px;height:${size}px;
        background:${color};
        border:${borderWidth}px solid rgba(255,255,255,0.9);
        border-radius:50%;
        display:flex;align-items:center;justify-content:center;
        color:#fff;font-weight:800;font-size:${count > 9 ? 12 : 14}px;
        box-shadow:0 0 12px ${color}88, 0 2px 8px rgba(0,0,0,0.4);
        font-family:'Inter',sans-serif;
      ">${count}</div>`
    : `<div style="
        width:${size}px;height:${size}px;
        background:${color};
        border:${borderWidth}px solid rgba(255,255,255,0.8);
        border-radius:50%;
        box-shadow:0 0 10px ${color}66, 0 2px 6px rgba(0,0,0,0.3);
      "></div>`

  return L.divIcon({
    html: innerHtml,
    className: 'event-marker',
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  })
}

function createUserIcon(): L.DivIcon {
  return L.divIcon({
    html: `<div style="
      width:20px;height:20px;
      background:#3b82f6;
      border:3px solid #fff;
      border-radius:50%;
      box-shadow:0 0 16px rgba(59,130,246,0.6), 0 0 32px rgba(59,130,246,0.3);
      animation: userPulse 2s ease-in-out infinite;
    "></div>`,
    className: 'user-location-marker',
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  })
}

export function useMap(containerRef: Ref<HTMLDivElement | null>) {
  let mapInstance: MapInstance | null = null

  function initMap(center: [number, number] = [-2.5, 118.0], zoom: number = 5): MapInstance | null {
    if (!containerRef.value) return null
    if (mapInstance) return mapInstance

    const map = L.map(containerRef.value, {
      zoomControl: false,
      attributionControl: true,
    }).setView(center, zoom)

    // Dark tile layer that matches the UI
    L.tileLayer(DARK_TILE_URL, {
      attribution: DARK_TILE_ATTR,
      maxZoom: 19,
      subdomains: 'abcd',
    }).addTo(map)

    // Zoom control on bottom-right
    L.control.zoom({ position: 'bottomright' }).addTo(map)

    const markersLayer = L.layerGroup().addTo(map)

    mapInstance = { map, markersLayer }
    return mapInstance
  }

  function renderMarkers(
    events: EarthquakeEvent[],
    clusters: ClusteredResult[],
    onEventClick: (event: EarthquakeEvent) => void,
    onClusterClick?: (cluster: ClusteredResult) => void,
  ) {
    if (!mapInstance) return

    mapInstance.markersLayer.clearLayers()

    if (clusters.length > 0) {
      // Render cluster markers
      clusters.forEach((cluster) => {
        const centroid = cluster.centroid
        if (!centroid) return

        const icon = createMarkerIcon(cluster.events.length)

        const marker = L.marker([centroid.lat, centroid.lon], { icon }).addTo(
          mapInstance!.markersLayer,
        )

        marker.on('click', () => {
          if (onClusterClick) onClusterClick(cluster)
        })
      })
    } else {
      // Render individual event markers
      events.forEach((event) => {
        if (!event.location?.lat || !event.location?.lon) return

        const icon = createMarkerIcon()
        const marker = L.marker([event.location.lat, event.location.lon], { icon }).addTo(
          mapInstance!.markersLayer,
        )

        marker.on('click', () => {
          onEventClick(event)
        })
      })
    }
  }

  function setUserLocationMarker(lat: number, lon: number) {
    if (!mapInstance) return

    const icon = createUserIcon()
    L.marker([lat, lon], { icon, zIndexOffset: 1000 }).addTo(mapInstance.markersLayer)
  }

  function flyTo(lat: number, lon: number, zoom: number = 10) {
    if (!mapInstance) return
    mapInstance.map.flyTo([lat, lon], zoom, {
      duration: 1.5,
    })
  }

  function fitBounds() {
    if (!mapInstance) return
    const bounds = mapInstance.markersLayer.getBounds()
    if (bounds.isValid()) {
      mapInstance.map.fitBounds(bounds, { padding: [40, 40], maxZoom: 12 })
    }
  }

  function invalidateSize() {
    if (mapInstance) {
      mapInstance.map.invalidateSize()
    }
  }

  onBeforeUnmount(() => {
    if (mapInstance) {
      mapInstance.markersLayer.clearLayers()
      mapInstance.map.remove()
      mapInstance = null
    }
  })

  return {
    initMap,
    renderMarkers,
    setUserLocationMarker,
    flyTo,
    fitBounds,
    invalidateSize,
  }
}
