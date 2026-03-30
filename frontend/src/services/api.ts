export interface LocationData {
  lat: number
  lon: number
  text?: string
}

export interface ImageData {
  small?: string | null
  medium?: string | null
  large?: string | null
  extraLarge?: string | null
}

export interface EarthquakeEvent {
  id: string
  title: string
  description: string
  source: 'bmkg' | 'cnn' | 'kumparan'
  type: 'earthquake' | 'news'
  datetime: string
  location: LocationData
  severity?: number | null
  confidence: string
  isOfficial: boolean
  image: ImageData | null
}

export interface ClusteredResult {
  cluster_id: number
  events: EarthquakeEvent[]
  centroid?: LocationData
}

export interface ApiResponse {
  message: string
  results: ClusteredResult[] | EarthquakeEvent[]
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function fetchEarthquakeNews(
  lat: number,
  lon: number,
  search?: string,
): Promise<ApiResponse> {
  const params = new URLSearchParams({
    user_lat: lat.toString(),
    user_lon: lon.toString(),
  })

  if (search) {
    params.append('search', search)
  }

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 30000)

  try {
    const response = await fetch(`${API_BASE_URL}/news?${params.toString()}`, {
      signal: controller.signal,
      headers: {
        Accept: 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`Server error: ${response.status} ${response.statusText}`)
    }

    return await response.json()
  } catch (error: unknown) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new Error('Request timeout — server tidak merespons dalam 30 detik')
    }
    throw error
  } finally {
    clearTimeout(timeoutId)
  }
}

export function getUserLocation(): Promise<GeolocationPosition> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation tidak didukung oleh browser Anda'))
      return
    }

    navigator.geolocation.getCurrentPosition(resolve, reject, {
      enableHighAccuracy: false,
      timeout: 10000,
      maximumAge: 300000,
    })
  })
}

export const PRESET_CITIES: { name: string; lat: number; lon: number }[] = [
  { name: 'Jakarta', lat: -6.2088, lon: 106.8456 },
  { name: 'Surabaya', lat: -7.2575, lon: 112.7521 },
  { name: 'Bandung', lat: -6.9175, lon: 107.6191 },
  { name: 'Yogyakarta', lat: -7.7956, lon: 110.3695 },
  { name: 'Semarang', lat: -6.9666, lon: 110.4196 },
  { name: 'Medan', lat: 3.5952, lon: 98.6722 },
  { name: 'Makassar', lat: -5.1477, lon: 119.4327 },
  { name: 'Denpasar', lat: -8.6705, lon: 115.2126 },
  { name: 'Palembang', lat: -2.9761, lon: 104.7754 },
  { name: 'Manado', lat: 1.4748, lon: 124.8421 },
  { name: 'Padang', lat: -0.9471, lon: 100.4172 },
  { name: 'Ambon', lat: -3.6954, lon: 128.1814 },
  { name: 'Jayapura', lat: -2.5337, lon: 140.7183 },
  { name: 'Mataram', lat: -8.5833, lon: 116.1167 },
  { name: 'Palu', lat: -0.8917, lon: 119.8707 },
]

export interface NewsRecommendation {
  id: number
  latitude: string | number | null
  longitude: string | number | null
  content: string | null
  datetime: string | null
  created_at: string | null
  updated_at: string | null
}

export interface NewsRecommendationResponse {
  success: boolean
  message: string
  data: NewsRecommendation[]
}

export async function fetchNewsRecommendation(
  lat: number,
  lon: number,
  lokasi?: string,
  radius_km: number = 50.0,
): Promise<NewsRecommendation[]> {
  const params = new URLSearchParams({
    latitude: lat.toString(),
    longitude: lon.toString(),
    radius_km: radius_km.toString(),
  })

  if (lokasi) {
    params.append('lokasi', lokasi)
  }

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 30000)

  try {
    const response = await fetch(`${API_BASE_URL}/news/recommendation?${params.toString()}`, {
      signal: controller.signal,
      headers: {
        Accept: 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`Server error: ${response.status} ${response.statusText}`)
    }

    const result = await response.json() as NewsRecommendationResponse | NewsRecommendation[]

    if (!Array.isArray(result) && result.success && Array.isArray(result.data)) {
      return result.data.map(item => ({
        ...item,
        latitude: item.latitude ?? null,
        longitude: item.longitude ?? null,
      }))
    }

    return Array.isArray(result) ? result : []
  } catch (error: unknown) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new Error('Request timeout — server tidak merespons dalam 30 detik')
    }
    throw error
  } finally {
    clearTimeout(timeoutId)
  }

}

export function getSeverityLevel(magnitude: number | null): {
  label: string
  color: string
  level: 'low' | 'moderate' | 'high' | 'extreme'
} {
  if (!magnitude)
    return { label: 'N/A', color: 'var(--color-text-muted)', level: 'low' }
  if (magnitude < 3)
    return { label: 'Ringan', color: 'var(--color-severity-low)', level: 'low' }
  if (magnitude < 5)
    return {
      label: 'Sedang',
      color: 'var(--color-severity-moderate)',
      level: 'moderate',
    }
  if (magnitude < 7)
    return { label: 'Kuat', color: 'var(--color-severity-high)', level: 'high' }
  return {
    label: 'Sangat Kuat',
    color: 'var(--color-severity-extreme)',
    level: 'extreme',
  }
}

export function formatDateTime(dateStr: string): string {
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('id-ID', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return dateStr
  }
}

export function getSourceLabel(source: string): {
  label: string
  color: string
  bg: string
} {
  switch (source) {
    case 'bmkg':
      return {
        label: 'BMKG',
        color: '#22c55e',
        bg: 'rgba(34, 197, 94, 0.12)',
      }
    case 'cnn':
      return {
        label: 'CNN Indonesia',
        color: '#ef4444',
        bg: 'rgba(239, 68, 68, 0.12)',
      }
    case 'kumparan':
      return {
        label: 'Kumparan',
        color: '#3b82f6',
        bg: 'rgba(59, 130, 246, 0.12)',
      }
    default:
      return {
        label: source,
        color: 'var(--color-text-secondary)',
        bg: 'var(--color-bg-glass)',
      }
  }
}
