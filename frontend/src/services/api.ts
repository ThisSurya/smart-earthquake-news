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
  severity: number | null
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
  latitude: string | null
  longitude: string | null
  content: string | null
  datetime: string | null
  created_at: string | null
  updated_at: string | null
}

export async function fetchNewsRecommendation(
  lat: number,
  lon: number,
  lokasi?: string,
  radius_km: number = 50.0,
): Promise<NewsRecommendation[]> {
  // 🎭 MOCK DATA MODE - Comment this block to use real API
  await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate network delay

  // const mockData: NewsRecommendation[] = [
  //   {
  //     id: 1,
  //     latitude: "-7.9461",
  //     longitude: "110.3035",
  //     content: "Berdasarkan data BMKG yang Anda berikan, wilayah seperti **Toli-toli (Sulawesi Tengah), Bener Meriah (Aceh), Boalemo (Gorontalo), Sukabumi (Jawa Barat), dan Nabire (Papua)** baru saja mengalami aktivitas seismik dengan skala M2.3 hingga M4.0.\n\nMeskipun kekuatan gempa tersebut tergolong kecil hingga sedang dengan skala intensitas (MMI) II-III, kewaspadaan tetap diperlukan karena beberapa gempa memiliki **kedalaman sangat dangkal (3-5 km)** yang guncangannya akan lebih terasa di permukaan.\n\nBerikut adalah langkah-langkah yang harus dilakukan jika Anda berada di lokasi tersebut:\n\n### 1. Saat Terjadi Guncangan (Tindakan Instan)\nJika Anda merasakan guncangan, jangan panik dan lakukan rumus **3M**:\n*   **Merunduk (Drop):** Segera turunkan posisi tubuh ke lantai agar tidak jatuh.\n*   **Melindungi Kepala (Cover):** Berlindunglah di bawah meja yang kuat untuk melindungi kepala dan leher dari jatuhan benda. Jika tidak ada meja, lindungi kepala dengan lengan atau bantal.\n*   **Menunggu (Hold on):** Bertahanlah di posisi tersebut sampai guncangan benar-benar berhenti.\n\n**Jika berada di luar ruangan:** Cari lahan terbuka, menjauhlah dari bangunan tinggi, tiang listrik, pohon, atau papan reklame yang berisiko roboh.\n\n### 2. Sesaat Setelah Guncangan Berhenti\n*   **Periksa Jalur Keluar:** Keluar dari bangunan menggunakan tangga darurat. **Jangan gunakan lift.**\n*   **Waspada Gempa Susulan:** Seringkali gempa pertama diikuti oleh gempa susulan. Pastikan Anda berada di tempat aman sebelum masuk kembali ke rumah.\n*   **Matikan Sumber Api/Listrik:** Segera matikan kompor, cabut peralatan listrik, dan tutup kran gas untuk mencegah kebakaran.\n\n### 3. Memahami Skala Intensitas (Bagian \"Dirasakan\")\nAnda menyebutkan bahwa semakin tinggi angkanya, semakin berdampak. Berikut penjelasannya berdasarkan data yang Anda berikan:\n*   **Skala II MMI (Bener Meriah, Gorontalo, Sukabumi, Nabire):** Guncangan dirasakan oleh beberapa orang, benda-benda ringan yang digantung mungkin bergoyang sedikit. Biasanya tidak menimbulkan kerusakan bangunan.\n*   **Skala III MMI (Toli-toli):** Guncangan dirasakan nyata di dalam rumah. Terasa seakan-akan ada truk besar yang berlalu di dekat rumah.\n\n**Peringatan Khusus Lokasi:**\n*   **Wilayah Darat (Galumpang, Bener Meriah, Nabire):** Karena kedalamannya sangat dangkal (3-10 km), waspadai rekahan tanah atau tanah longsor jika Anda berada di daerah lereng atau perbukitan.\n*   **Wilayah Laut (Sukabumi):** Meskipun gempa M3.7 tidak berpotensi tsunami, jika Anda merasakan gempa yang sangat kuat dan lama saat berada di pantai, segera menjauh dari bibir pantai menuju tempat yang lebih tinggi tanpa menunggu peringatan resmi.\n\n### 4. Informasi Penting Lainnya\n*   **Siapkan Tas Siaga Bencana:** Berisi dokumen penting, air minum, makanan instan, lampu senter, baterai cadangan, dan obat-obatan P3K.\n*   **Pantau Informasi Resmi:** Selalu rujuk informasi dari aplikasi **InfoBMKG**, akun media sosial resmi BMKG, atau BNPB. Jangan mudah percaya pada berita atau *broadcast* WhatsApp yang tidak jelas sumbernya (hoaks).\n*   **Cek Kondisi Bangunan:** Sebelum masuk kembali ke rumah, cek apakah ada retakan besar pada pilar atau dinding pendukung rumah. Jika ada kerusakan struktur, sebaiknya jangan masuk terlebih dahulu.\n\nTetap tenang dan waspada. Kondisi geologis Indonesia memang aktif, namun dengan kesiapsiagaan yang baik, risiko dapat diminimalisir.",
  //   },
  //   {
  //     id: 2,
  //     latitude: "-6.2088",
  //     longitude: "106.8456",
  //     content: "Wilayah Jakarta dan sekitarnya berada dalam zona rawan gempa sedang. Meskipun tidak sering terjadi gempa besar, wilayah ini tetap perlu kesiapsiagaan.\n\n### Langkah Mitigasi untuk Wilayah Jakarta:\n*   **Pastikan bangunan memiliki struktur tahan gempa** sesuai standar SNI.\n*   **Kenali jalur evakuasi** terdekat dari rumah, kantor, atau sekolah.\n*   **Siapkan tas siaga bencana** yang mudah dijangkau.\n\n### Titik Kumpul Darurat:\n*   Lapangan terbuka atau taman kota\n*   Area parkir luas yang jauh dari bangunan tinggi\n\nIngat: **Jangan panik** dan selalu ikuti arahan petugas saat terjadi bencana.",
  //   },
  //   {
  //     id: 3,
  //     latitude: "-7.2575",
  //     longitude: "112.7521",
  //     content: "Surabaya dan Jawa Timur perlu waspada terhadap aktivitas seismik dari segmen sesar selatan Jawa.\n\n### Status Terkini:\n*   Tidak ada ancaman tsunami langsung\n*   Aktivitas gempa tergolong rendah hingga sedang\n*   Kewaspadaan tetap diperlukan terutama di daerah pesisir\n\n### Tips Keselamatan:\n*   **Hindari bangunan tua** yang tidak memenuhi standar struktur\n*   **Jangan berlari keluar** saat terjadi gempa, berlindung terlebih dahulu\n*   **Jauh dari jendela kaca** yang bisa pecah\n\nPantau terus informasi dari BMKG dan BPBD setempat.",
  //   }
  // ]

  // return mockData
  // 🎭 END MOCK DATA MODE

  // REAL API CODE - Uncomment to use real API
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

    const result = await response.json()

    // Handle the API response structure: { success, message, data }
    if (result.success && Array.isArray(result.data)) {
      return result.data
    }

    // Fallback if the structure is different
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
