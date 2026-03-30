import { reactive, computed } from 'vue'
import {
  fetchEarthquakeNews,
  getUserLocation,
  type EarthquakeEvent,
  type ClusteredResult,
} from '@/services/api'

export interface NewsState {
  events: EarthquakeEvent[]
  clusters: ClusteredResult[]
  selectedEvent: EarthquakeEvent | null
  selectedCluster: ClusteredResult | null
  userLocation: { lat: number; lon: number } | null
  loading: boolean
  error: string | null
  mode: 'events' | 'clusters' | null
}

const state = reactive<NewsState>({
  events: [],
  clusters: [],
  selectedEvent: null,
  selectedCluster: null,
  userLocation: null,
  loading: false,
  error: null,
  mode: null,
})

function isClusteredResult(item: unknown): item is ClusteredResult {
  return (
    typeof item === 'object' &&
    item !== null &&
    'cluster_id' in item &&
    'events' in item
  )
}

/**
 * All events flattened — from clusters or direct events
 */
const allEvents = computed<EarthquakeEvent[]>(() => {
  if (state.mode === 'clusters') {
    return state.clusters.flatMap((c) => c.events)
  }
  return state.events
})

/**
 * Sorted by datetime descending (newest first)
 */
const sortedEvents = computed<EarthquakeEvent[]>(() => {
  return [...allEvents.value].sort(
    (a, b) => new Date(b.datetime).getTime() - new Date(a.datetime).getTime(),
  )
})

async function fetchData(lat: number, lon: number, search?: string) {
  state.loading = true
  state.error = null
  state.events = []
  state.clusters = []
  state.selectedEvent = null
  state.selectedCluster = null
  state.mode = null

  try {
    const response = await fetchEarthquakeNews(lat, lon, search)

    if (!response.results || response.results.length === 0) {
      state.mode = 'events'
      return
    }

    // Detect if results are clusters or flat events
    const firstItem = response.results[0]
    if (isClusteredResult(firstItem)) {
      state.clusters = response.results as ClusteredResult[]
      state.mode = 'clusters'
    } else {
      state.events = response.results as EarthquakeEvent[]
      state.mode = 'events'
    }
  } catch (err: unknown) {
    state.error = err instanceof Error ? err.message : 'Terjadi kesalahan yang tidak diketahui'
  } finally {
    state.loading = false
  }
}

function selectEvent(event: EarthquakeEvent) {
  state.selectedEvent = event
  state.selectedCluster = null
}

function selectCluster(cluster: ClusteredResult) {
  state.selectedCluster = cluster
  state.selectedEvent = null
}

function clearSelection() {
  state.selectedEvent = null
  state.selectedCluster = null
}

async function detectUserLocation(): Promise<{ lat: number; lon: number } | null> {
  try {
    const position = await getUserLocation()
    const loc = {
      lat: position.coords.latitude,
      lon: position.coords.longitude,
    }
    state.userLocation = loc
    return loc
  } catch {
    return null
  }
}

function setUserLocation(lat: number, lon: number) {
  state.userLocation = { lat, lon }
}

export function useNews() {
  return {
    state,
    allEvents,
    sortedEvents,
    fetchData,
    selectEvent,
    selectCluster,
    clearSelection,
    detectUserLocation,
    setUserLocation,
  }
}
