<script setup lang="ts">
import { ref, computed } from 'vue'
import { getUserLocation, PRESET_CITIES } from '@/services/api'

const emit = defineEmits<{
  (e: 'locationSelected', lat: number, lon: number): void
}>()

const props = defineProps<{
  currentLat?: number | null
  currentLon?: number | null
}>()

type LocationStatus = 'idle' | 'detecting' | 'granted' | 'denied' | 'error'

const status = ref<LocationStatus>('idle')
const errorMessage = ref('')
const manualLat = ref('')
const manualLon = ref('')
const showManual = ref(false)
const selectedCity = ref('')

const statusInfo = computed(() => {
  switch (status.value) {
    case 'detecting':
      return { icon: '📡', text: 'Mendeteksi lokasi...', color: 'var(--color-accent)' }
    case 'granted':
      return { icon: '✅', text: 'Lokasi terdeteksi', color: 'var(--color-severity-low)' }
    case 'denied':
      return { icon: '🚫', text: 'Akses lokasi ditolak', color: 'var(--color-severity-high)' }
    case 'error':
      return { icon: '⚠️', text: errorMessage.value, color: 'var(--color-severity-moderate)' }
    default:
      return { icon: '📍', text: 'Tentukan lokasi Anda', color: 'var(--color-text-secondary)' }
  }
})

const hasLocation = computed(() => props.currentLat != null && props.currentLon != null)

async function detectLocation() {
  status.value = 'detecting'
  errorMessage.value = ''

  try {
    const position = await getUserLocation()
    status.value = 'granted'
    emit('locationSelected', position.coords.latitude, position.coords.longitude)
  } catch (err: unknown) {
    if (err instanceof GeolocationPositionError) {
      switch (err.code) {
        case err.PERMISSION_DENIED:
          status.value = 'denied'
          errorMessage.value = 'Anda menolak akses lokasi'
          showManual.value = true
          break
        case err.POSITION_UNAVAILABLE:
          status.value = 'error'
          errorMessage.value = 'Informasi lokasi tidak tersedia'
          showManual.value = true
          break
        case err.TIMEOUT:
          status.value = 'error'
          errorMessage.value = 'Waktu deteksi lokasi habis'
          showManual.value = true
          break
      }
    } else {
      status.value = 'error'
      errorMessage.value = 'Gagal mendeteksi lokasi'
      showManual.value = true
    }
  }
}

function selectCity() {
  const city = PRESET_CITIES.find((c) => c.name === selectedCity.value)
  if (city) {
    manualLat.value = city.lat.toString()
    manualLon.value = city.lon.toString()
    submitManual()
  }
}

function submitManual() {
  const lat = parseFloat(manualLat.value)
  const lon = parseFloat(manualLon.value)

  if (isNaN(lat) || isNaN(lon)) {
    errorMessage.value = 'Masukkan latitude dan longitude yang valid'
    status.value = 'error'
    return
  }

  if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {
    errorMessage.value = 'Koordinat di luar batas valid'
    status.value = 'error'
    return
  }

  status.value = 'granted'
  emit('locationSelected', lat, lon)
}
</script>

<template>
  <div class="location-picker-container glass">
    <!-- Left Section: Location Controls -->
    <div class="picker-controls">
      <div class="controls-header">
        <h3 class="controls-title">📍 Pilih Lokasi</h3>
        <div v-if="hasLocation" class="location-badge">
          <span class="badge-icon">✓</span>
          <span class="badge-text">Lokasi Aktif</span>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions">
        <button
          id="btn-detect-location"
          class="btn btn-detect"
          :disabled="status === 'detecting'"
          @click="detectLocation"
        >
          <span class="btn-icon">{{ status === 'detecting' ? '⏳' : '🎯' }}</span>
          <div class="btn-content">
            <span class="btn-title">Deteksi Otomatis</span>
            <span class="btn-subtitle">Gunakan GPS perangkat</span>
          </div>
        </button>

        <button
          id="btn-toggle-manual"
          class="btn btn-manual"
          :class="{ active: showManual }"
          @click="showManual = !showManual"
        >
          <span class="btn-icon">⚙️</span>
          <div class="btn-content">
            <span class="btn-title">Input Manual</span>
            <span class="btn-subtitle">Pilih kota atau koordinat</span>
          </div>
        </button>
      </div>

      <!-- Manual Input (Compact) -->
      <transition name="expand">
        <div v-if="showManual" class="manual-compact">
          <div class="city-quick-select">
            <label class="compact-label">🏙️ Kota Populer</label>
            <select
              id="city-dropdown"
              v-model="selectedCity"
              class="compact-select"
              @change="selectCity"
            >
              <option value="">-- Pilih kota --</option>
              <option v-for="city in PRESET_CITIES" :key="city.name" :value="city.name">
                {{ city.name }}
              </option>
            </select>
          </div>

          <div class="divider-compact">
            <span class="divider-text">atau masukkan koordinat</span>
          </div>

          <div class="coords-compact">
            <input
              id="input-lat"
              v-model="manualLat"
              type="number"
              step="any"
              class="compact-input"
              placeholder="Latitude (e.g., -6.2088)"
            />
            <input
              id="input-lon"
              v-model="manualLon"
              type="number"
              step="any"
              class="compact-input"
              placeholder="Longitude (e.g., 106.8456)"
            />
            <button id="btn-submit-coords" class="btn-submit" @click="submitManual">
              🔍 Cari
            </button>
          </div>
        </div>
      </transition>

      <!-- Current Coordinates Display -->
      <div v-if="hasLocation" class="current-location-display">
        <div class="location-item">
          <span class="location-label">Latitude:</span>
          <span class="location-value">{{ currentLat?.toFixed(6) }}</span>
        </div>
        <div class="location-item">
          <span class="location-label">Longitude:</span>
          <span class="location-value">{{ currentLon?.toFixed(6) }}</span>
        </div>
      </div>
    </div>

    <!-- Right Section: Status & Preview -->
    <div class="picker-preview">
      <!-- Status Display -->
      <div class="status-display" :class="`status-${status}`">
        <div class="status-icon-large">{{ statusInfo.icon }}</div>
        <div class="status-content">
          <h4 class="status-title">{{ statusInfo.text }}</h4>
          <p v-if="status === 'idle'" class="status-description">
            Pilih metode untuk menentukan lokasi Anda dan mendapatkan rekomendasi berita gempa
          </p>
          <p v-else-if="status === 'detecting'" class="status-description">
            Mohon izinkan akses lokasi di browser Anda...
          </p>
          <p v-else-if="status === 'granted' && hasLocation" class="status-description">
            Lokasi berhasil dideteksi. Klik "Cari" untuk melihat rekomendasi berita
          </p>
          <p v-else-if="status === 'denied'" class="status-description">
            Anda menolak akses lokasi. Silakan gunakan input manual atau ubah pengaturan browser
          </p>
          <p v-else-if="status === 'error'" class="status-description">
            {{ errorMessage }}. Silakan coba lagi atau gunakan input manual
          </p>
        </div>
      </div>

      <!-- Info Cards -->
      <div class="info-cards">
        <div class="info-card">
          <span class="info-icon">🎯</span>
          <div class="info-text">
            <strong>Akurasi Tinggi</strong>
            <span>GPS memberikan hasil terbaik</span>
          </div>
        </div>
        <div class="info-card">
          <span class="info-icon">🔒</span>
          <div class="info-text">
            <strong>Privasi Aman</strong>
            <span>Data lokasi tidak disimpan</span>
          </div>
        </div>
        <div class="info-card">
          <span class="info-icon">⚡</span>
          <div class="info-text">
            <strong>Hasil Instan</strong>
            <span>Rekomendasi dalam hitungan detik</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Split-Screen Container */
.location-picker-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-xl);
  border-radius: var(--radius-lg);
  padding: var(--space-xl);
  min-height: 400px;
}

/* Left Section: Controls */
.picker-controls {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.controls-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
  margin-bottom: var(--space-sm);
}

.controls-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.location-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(22, 163, 74, 0.08));
  border: 1px solid var(--color-severity-low);
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  color: var(--color-severity-low);
  font-weight: 600;
}

.badge-icon {
  font-size: 0.85rem;
}

/* Quick Actions */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.btn {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-bg-glass);
  cursor: pointer;
  transition: all var(--transition-base);
  text-align: left;
}

.btn:hover:not(:disabled) {
  border-color: var(--color-border-hover);
  background: var(--color-bg-card-hover);
  transform: translateX(4px);
  box-shadow: var(--shadow-md);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn.active {
  border-color: var(--color-primary);
  background: rgba(59, 130, 246, 0.08);
}

.btn-detect {
  border-color: var(--color-primary);
}

.btn-detect:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.08);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.btn-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.btn-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.btn-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.btn-subtitle {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

/* Manual Input Compact */
.manual-compact {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  padding: var(--space-md);
  background: rgba(0, 0, 0, 0.02);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.city-quick-select {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.compact-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.compact-select {
  padding: var(--space-sm);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  color: var(--color-text-primary);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all var(--transition-base);
}

.compact-select:hover {
  border-color: var(--color-border-hover);
}

.compact-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.divider-compact {
  text-align: center;
  position: relative;
  margin: var(--space-xs) 0;
}

.divider-compact::before,
.divider-compact::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 42%;
  height: 1px;
  background: var(--color-border);
}

.divider-compact::before {
  left: 0;
}

.divider-compact::after {
  right: 0;
}

.divider-text {
  font-size: 0.7rem;
  color: var(--color-text-muted);
  padding: 0 var(--space-sm);
  background: rgba(0, 0, 0, 0.02);
}

.coords-compact {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.compact-input {
  padding: var(--space-sm);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  color: var(--color-text-primary);
  font-size: 0.85rem;
  transition: all var(--transition-base);
}

.compact-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.btn-submit {
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-sm);
  border: none;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: white;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-base);
}

.btn-submit:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* Current Location Display */
.current-location-display {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  padding: var(--space-md);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(37, 99, 235, 0.02));
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: var(--radius-md);
}

.location-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
}

.location-label {
  color: var(--color-text-secondary);
  font-weight: 600;
}

.location-value {
  color: var(--color-primary);
  font-family: 'Courier New', monospace;
  font-weight: 600;
}

/* Right Section: Preview */
.picker-preview {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  padding: var(--space-lg);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.03), transparent);
  border-radius: var(--radius-md);
  border: 1px solid rgba(59, 130, 246, 0.1);
}

/* Status Display */
.status-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-xl);
  text-align: center;
  border-radius: var(--radius-md);
  transition: all var(--transition-base);
}

.status-display.status-idle {
  background: linear-gradient(135deg, rgba(100, 100, 100, 0.05), transparent);
  border: 1px dashed var(--color-border);
}

.status-display.status-detecting {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.05));
  border: 1px solid rgba(59, 130, 246, 0.3);
  animation: pulse 2s ease-in-out infinite;
}

.status-display.status-granted {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(22, 163, 74, 0.05));
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.status-display.status-denied,
.status-display.status-error {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.05));
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.status-icon-large {
  font-size: 3.5rem;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.status-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.status-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.status-description {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0;
}

/* Info Cards */
.info-cards {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.info-card {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  background: var(--color-bg-glass);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  transition: all var(--transition-base);
}

.info-card:hover {
  border-color: var(--color-border-hover);
  transform: translateX(4px);
}

.info-icon {
  font-size: 1.3rem;
  flex-shrink: 0;
}

.info-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 0.8rem;
}

.info-text strong {
  color: var(--color-text-primary);
  font-weight: 600;
}

.info-text span {
  color: var(--color-text-muted);
  font-size: 0.75rem;
}

/* Animations */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  max-height: 500px;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}

/* Responsive */
@media (max-width: 1024px) {
  .location-picker-container {
    grid-template-columns: 1fr;
    gap: var(--space-lg);
  }

  .picker-preview {
    order: -1;
  }

  .status-display {
    padding: var(--space-lg);
  }

  .status-icon-large {
    font-size: 2.5rem;
  }
}

@media (max-width: 640px) {
  .location-picker-container {
    padding: var(--space-lg);
    min-height: auto;
  }

  .controls-title {
    font-size: 1.1rem;
  }

  .btn-icon {
    font-size: 1.2rem;
  }

  .btn-title {
    font-size: 0.85rem;
  }

  .btn-subtitle {
    font-size: 0.7rem;
  }

  .status-icon-large {
    font-size: 2rem;
  }

  .status-title {
    font-size: 1rem;
  }

  .status-description {
    font-size: 0.8rem;
  }

  .info-card {
    padding: var(--space-xs) var(--space-sm);
  }
}
</style>
