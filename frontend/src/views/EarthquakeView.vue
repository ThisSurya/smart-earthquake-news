<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import LocationPicker from '@/components/LocationPicker.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import NewsMapView from '@/components/NewsMapView.vue'
import { fetchNewsRecommendation, getUserLocation } from '@/services/api'
import type { NewsRecommendation } from '@/services/api'
import { calculateNewsDistance } from '@/utils/distance'

type ViewState = 'location' | 'loading' | 'success' | 'error'

// Helper function to calculate relative time
function getRelativeTime(datetime: string | null | undefined): { text: string; isRecent: boolean } {
  if (!datetime) return { text: 'Waktu tidak diketahui', isRecent: false }

  const now = new Date()
  const eventTime = new Date(datetime)
  const diffMs = now.getTime() - eventTime.getTime()
  const diffMinutes = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  const isRecent = diffMinutes < 30

  if (diffMinutes < 1) {
    return { text: 'Baru saja', isRecent: true }
  } else if (diffMinutes < 60) {
    return { text: `${diffMinutes} menit lalu`, isRecent }
  } else if (diffHours < 24) {
    return { text: `${diffHours} jam lalu`, isRecent: false }
  } else {
    return { text: `${diffDays} hari lalu`, isRecent: false }
  }
}

const state = ref<ViewState>('location')
const errorMessage = ref('')
const userLat = ref<number | null>(null)
const userLon = ref<number | null>(null)
const recommendations = ref<NewsRecommendation[]>([])
const expandedCards = ref<Set<number>>(new Set())
const DANGER_RADIUS_KM = 50
const showMapDetail = ref(false)

// Computed: Analisis dampak gempa
const impactAnalysis = computed(() => {
  const newsWithDistance = recommendations.value.map(rec => ({
    ...rec,
    calculatedDistance: calculateNewsDistance(
      userLat.value,
      userLon.value,
      rec.latitude,
      rec.longitude
    )
  }))

  const affected = newsWithDistance.filter(
    rec => rec.calculatedDistance !== null && rec.calculatedDistance <= DANGER_RADIUS_KM
  )
  const safe = newsWithDistance.filter(
    rec => rec.calculatedDistance !== null && rec.calculatedDistance > DANGER_RADIUS_KM
  )
  const unknown = newsWithDistance.filter(rec => rec.calculatedDistance === null)

  const isInDanger = affected.length > 0
  const closestDistance = affected.length > 0
    ? Math.min(...affected.map(r => r.calculatedDistance ?? Infinity))
    : null

  return {
    total: recommendations.value.length,
    affected: affected.length,
    safe: safe.length,
    unknown: unknown.length,
    isInDanger,
    closestDistance,
    status: isInDanger ? 'danger' : 'safe'
  }
})

// Computed: Sorted recommendations (prioritas gempa terdekat)
const sortedRecommendations = computed(() => {
  return [...recommendations.value].map(rec => ({
    ...rec,
    calculatedDistance: calculateNewsDistance(
      userLat.value,
      userLon.value,
      rec.latitude,
      rec.longitude
    )
  })).sort((a, b) => {
    const distA = a.calculatedDistance ?? Infinity
    const distB = b.calculatedDistance ?? Infinity
    return distA - distB // Terdekat dulu
  })
})

// Computed: Berita dalam radius bahaya (PRIORITAS)
const affectedNews = computed(() => {
  return sortedRecommendations.value.filter(
    rec => rec.calculatedDistance !== null && rec.calculatedDistance <= DANGER_RADIUS_KM
  )
})

// Computed: Berita di luar radius (AMAN)
const safeNews = computed(() => {
  return sortedRecommendations.value.filter(
    rec => rec.calculatedDistance !== null && rec.calculatedDistance > DANGER_RADIUS_KM
  )
})

function toggleExpand(id: number) {
  if (expandedCards.value.has(id)) {
    expandedCards.value.delete(id)
  } else {
    expandedCards.value.add(id)
  }
}

function isExpanded(id: number): boolean {
  return expandedCards.value.has(id)
}

function formatMarkdownToHtml(text: string): string {
  if (!text) return ''

  let html = text

  // Convert headers (### -> h3)
  html = html.replace(/^### (.+)$/gm, '<h3 class="md-h3">$1</h3>')

  // Convert bold (**text** -> <strong>)
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')

  // Convert list items (*   text -> <li>)
  html = html.replace(/^\*   (.+)$/gm, '<li>$1</li>')

  // Wrap consecutive <li> in <ul>
  html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>')

  // Convert paragraphs (double newline)
  html = html.split('\n\n').map(para => {
    if (para.startsWith('<h3') || para.startsWith('<ul')) {
      return para
    }
    return `<p>${para.replace(/\n/g, '<br>')}</p>`
  }).join('')

  return html
}

onMounted(async () => {
  // Try to auto-detect location silently
  try {
    const position = await getUserLocation()
    userLat.value = position.coords.latitude
    userLon.value = position.coords.longitude
    await loadData()
  } catch {
    // Don't show error — user will use the LocationPicker
    state.value = 'location'
  }
})

function onLocationSelected(lat: number, lon: number) {
  userLat.value = lat
  userLon.value = lon
  loadData()
}

async function loadData() {
  if (userLat.value == null || userLon.value == null) return

  state.value = 'loading'
  errorMessage.value = ''
  recommendations.value = []

  try {
    const data = await fetchNewsRecommendation(userLat.value, userLon.value)
    recommendations.value = data
    state.value = 'success'
  } catch (err: unknown) {
    state.value = 'error'
    errorMessage.value =
      err instanceof Error ? err.message : 'Terjadi kesalahan yang tidak diketahui'
  }
}
</script>

<template>
  <div class="earthquake-view">
    <!-- Hero Section -->
    <section class="hero fade-in">
      <h1 class="hero-title">
        <span class="hero-emoji">📰</span>
        Rekomendasi Berita Gempa
      </h1>
      <p class="hero-subtitle">
        Dapatkan rekomendasi berita gempa berdasarkan lokasi Anda — informasi terkini dari berbagai sumber terpercaya
      </p>
    </section>

    <!-- Alert Status Card (PRIORITAS - PALING ATAS) -->
    <section v-if="state === 'success' && recommendations.length > 0" class="section fade-in" style="animation-delay: 100ms">
      <div class="alert-status-card" :class="`status-${impactAnalysis.status}`">
        <div class="alert-icon">
          {{ impactAnalysis.isInDanger ? '⚠️' : '✅' }}
        </div>
        <div class="alert-content">
          <h2 class="alert-title">
            {{ impactAnalysis.isInDanger ? 'WASPADA - Ada Gempa di Sekitar Anda' : 'AMAN - Tidak Ada Gempa Berbahaya' }}
          </h2>
          <div class="alert-stats">
            <div class="stat-item primary">
              <span class="stat-number">{{ impactAnalysis.total }}</span>
              <span class="stat-label">Gempa Terdeteksi</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item" :class="impactAnalysis.affected > 0 ? 'danger' : ''">
              <span class="stat-number">{{ impactAnalysis.affected }}</span>
              <span class="stat-label">Dalam Radius {{ DANGER_RADIUS_KM }}km</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item safe">
              <span class="stat-number">{{ impactAnalysis.safe }}</span>
              <span class="stat-label">Di Luar Radius</span>
            </div>
          </div>
          <p v-if="impactAnalysis.isInDanger" class="alert-message danger">
            🚨 <strong>Gempa terdekat berjarak {{ impactAnalysis.closestDistance?.toFixed(1) }} km</strong> dari lokasi Anda.
            Segera baca rekomendasi keselamatan di bawah!
          </p>
          <p v-else class="alert-message safe">
            ✨ Lokasi Anda saat ini <strong>tidak berada dalam radius dampak</strong> gempa yang terdeteksi.
            Tetap waspada dan pantau informasi terkini.
          </p>
        </div>
      </div>
    </section>

    <!-- Location Picker -->
    <section class="section fade-in" style="animation-delay: 150ms">
      <LocationPicker :current-lat="userLat" :current-lon="userLon" @location-selected="onLocationSelected" />
    </section>

    <!-- Loading -->
    <section v-if="state === 'loading'" class="section">
      <LoadingSpinner size="lg" text="Mengambil rekomendasi berita..." />
    </section>

    <!-- Error -->
    <section v-if="state === 'error'" class="section">
      <div class="error-card glass">
        <span class="error-icon">⚠️</span>
        <h3 class="error-title">Gagal Memuat Data</h3>
        <p class="error-message">{{ errorMessage }}</p>
        <button id="btn-retry" class="btn-retry" @click="loadData">
          🔄 Coba Lagi
        </button>
      </div>
    </section>

    <!-- Map Toggle (setelah alert) -->
    <section v-if="state === 'success' && recommendations.length > 0" class="section">
      <button class="toggle-map-btn" @click="showMapDetail = !showMapDetail">
        {{ showMapDetail ? '📊 Sembunyikan Peta Detail' : '🗺️ Lihat Peta Detail' }}
        <span class="toggle-icon">{{ showMapDetail ? '▲' : '▼' }}</span>
      </button>
    </section>

    <!-- Map View (Collapsible) -->
    <section v-if="state === 'success' && recommendations.length > 0 && showMapDetail" class="section fade-in">
      <NewsMapView
        :user-lat="userLat"
        :user-lon="userLon"
        :recommendations="recommendations"
        :radius-km="DANGER_RADIUS_KM"
      />
    </section>

    <!-- News Recommendations -->
    <section v-if="state === 'success'" class="section fade-in" style="animation-delay: 200ms">
      <!-- PRIORITAS: Berita Dalam Radius Bahaya -->
      <div v-if="affectedNews.length > 0" class="news-section danger-section">
        <div class="section-header danger-header">
          <div class="header-content">
            <h2 class="section-title">🚨 PRIORITAS - Dalam Radius Dampak</h2>
            <span class="section-count">{{ affectedNews.length }} Berita</span>
          </div>
          <button id="btn-refresh" class="refresh-btn" @click="loadData" title="Refresh data">
            🔄
          </button>
        </div>

        <div class="rec-grid">
          <div v-for="(rec, index) in affectedNews" :key="rec.id" class="rec-card glass priority-card">
            <!-- Priority Badge -->
            <div class="priority-badge danger">
              🚨 PRIORITAS - DALAM RADIUS DAMPAK
            </div>

            <!-- Recent Earthquake Warning -->
            <div v-if="getRelativeTime(rec.datetime).isRecent" class="recent-warning">
              ⚡ PERINGATAN: GEMPA BARU TERJADI!
            </div>

            <!-- Card Header -->
            <div class="rec-header">
              <div class="rec-meta">
                <span v-if="rec.latitude && rec.longitude" class="rec-coords">
                  📍 {{ rec.latitude }}, {{ rec.longitude }}
                </span>
                <span v-if="rec.calculatedDistance !== null && rec.calculatedDistance !== undefined" class="rec-distance distance-danger">
                  ⚠️ {{ rec.calculatedDistance.toFixed(1) }} km dari Anda
                </span>
                <span class="rec-time" :class="{ 'time-recent': getRelativeTime(rec.datetime).isRecent }">
                  🕐 {{ getRelativeTime(rec.datetime).text }}
                </span>
              </div>
            </div>

            <!-- Card Content -->
            <div class="rec-content-wrapper" :class="{ 'is-expanded': isExpanded(rec.id) }">
              <div class="rec-content markdown-content" v-html="formatMarkdownToHtml(rec.content ?? '')"></div>
              <div v-if="!isExpanded(rec.id) && (rec.content?.length ?? 0) > 500" class="fade-overlay"></div>
            </div>

            <!-- Expand/Collapse Button -->
            <button v-if="(rec.content?.length ?? 0) > 500" class="btn-expand" @click="toggleExpand(rec.id)">
              {{ isExpanded(rec.id) ? '📖 Lihat Lebih Sedikit' : '📚 Lihat Selengkapnya' }}
            </button>
          </div>
        </div>
      </div>

      <!-- AMAN: Berita Di Luar Radius -->
      <div v-if="safeNews.length > 0" class="news-section safe-section">
        <div class="section-header safe-header">
          <div class="header-content">
            <h2 class="section-title">✅ AMAN - Di Luar Radius Dampak</h2>
            <span class="section-count">{{ safeNews.length }} Berita</span>
          </div>
        </div>

        <div class="rec-grid">
          <div v-for="(rec, index) in safeNews" :key="rec.id" class="rec-card glass">
            <!-- Priority Badge -->
            <div class="priority-badge safe">
              ✅ Di Luar Radius Dampak
            </div>

            <!-- Recent Earthquake Warning (even if outside radius) -->
            <div v-if="getRelativeTime(rec.datetime).isRecent" class="recent-warning">
              ⚡ PERINGATAN: GEMPA BARU TERJADI!
            </div>

            <!-- Card Header -->
            <div class="rec-header">
              <div class="rec-meta">
                <span v-if="rec.latitude && rec.longitude" class="rec-coords">
                  📍 {{ rec.latitude }}, {{ rec.longitude }}
                </span>
                <span v-if="rec.calculatedDistance !== null && rec.calculatedDistance !== undefined" class="rec-distance">
                  🛣️ {{ rec.calculatedDistance.toFixed(1) }} km dari Anda
                </span>
                <span class="rec-time" :class="{ 'time-recent': getRelativeTime(rec.datetime).isRecent }">
                  🕐 {{ getRelativeTime(rec.datetime).text }}
                </span>
              </div>
            </div>

            <!-- Card Content -->
            <div class="rec-content-wrapper" :class="{ 'is-expanded': isExpanded(rec.id) }">
              <div class="rec-content markdown-content" v-html="formatMarkdownToHtml(rec.content ?? '')"></div>
              <div v-if="!isExpanded(rec.id) && (rec.content?.length ?? 0) > 500" class="fade-overlay"></div>
            </div>

            <!-- Expand/Collapse Button -->
            <button v-if="(rec.content?.length ?? 0) > 500" class="btn-expand" @click="toggleExpand(rec.id)">
              {{ isExpanded(rec.id) ? '📖 Lihat Lebih Sedikit' : '📚 Lihat Selengkapnya' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="recommendations.length === 0" class="empty-state glass">
        <span class="empty-icon">📭</span>
        <h3 class="empty-title">Tidak Ada Rekomendasi</h3>
        <p class="empty-text">Belum ada rekomendasi berita untuk lokasi ini.</p>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer fade-in">
      <p>
        Rekomendasi disediakan berdasarkan data lokasi Anda. Informasi ini bertujuan sebagai referensi, bukan pengganti
        peringatan resmi.
      </p>
    </footer>
  </div>
</template>

<style scoped>
.earthquake-view {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
  padding-bottom: var(--space-3xl);
}

/* Hero */
.hero {
  text-align: center;
  padding: var(--space-2xl) 0 var(--space-md);
}

.hero-title {
  font-size: 2rem;
  font-weight: 800;
  color: var(--color-text-primary);
  letter-spacing: -0.03em;
  line-height: 1.2;
}

.hero-emoji {
  display: inline-block;
  margin-right: 4px;
  animation: pulse 3s ease-in-out infinite;
}

.hero-subtitle {
  margin-top: var(--space-sm);
  font-size: 1rem;
  color: var(--color-text-secondary);
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
}

/* Section */
.section {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
}

.section-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

/* News Section Separators */
.news-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.news-section + .news-section {
  margin-top: var(--space-2xl);
  padding-top: var(--space-2xl);
  border-top: 2px dashed var(--color-border);
}

.danger-section {
  padding: var(--space-lg);
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.05), transparent);
  border: 2px solid rgba(239, 68, 68, 0.2);
  border-radius: var(--radius-lg);
}

.safe-section {
  padding: var(--space-lg);
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.05), transparent);
  border: 1px solid rgba(34, 197, 94, 0.15);
  border-radius: var(--radius-lg);
}

.danger-header {
  border-bottom: 2px solid rgba(239, 68, 68, 0.2);
  padding-bottom: var(--space-md);
  margin-bottom: var(--space-md);
}

.safe-header {
  border-bottom: 2px solid rgba(34, 197, 94, 0.2);
  padding-bottom: var(--space-md);
  margin-bottom: var(--space-md);
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.section-count {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-muted);
  padding: 4px 12px;
  background: var(--color-bg-glass);
  border-radius: var(--radius-full);
  align-self: flex-start;
}

/* Alert Status Card */
.alert-status-card {
  display: flex;
  gap: var(--space-xl);
  padding: var(--space-2xl);
  border-radius: var(--radius-lg);
  border: 2px solid;
  transition: all var(--transition-base);
  animation: slideInDown 0.4s ease-out;
}

@keyframes slideInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.alert-status-card.status-danger {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(220, 38, 38, 0.08));
  border-color: var(--color-severity-high);
  box-shadow: 0 4px 20px rgba(239, 68, 68, 0.2), var(--shadow-lg);
}

.alert-status-card.status-safe {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(22, 163, 74, 0.08));
  border-color: var(--color-severity-low);
  box-shadow: 0 4px 20px rgba(34, 197, 94, 0.2), var(--shadow-lg);
}

.alert-icon {
  font-size: 4rem;
  flex-shrink: 0;
  animation: pulseScale 2s ease-in-out infinite;
}

@keyframes pulseScale {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.alert-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.alert-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-text-primary);
  margin: 0;
  letter-spacing: -0.02em;
}

.alert-stats {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-number {
  font-size: 2rem;
  font-weight: 800;
  color: var(--color-text-primary);
  line-height: 1;
}

.stat-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-item.primary .stat-number {
  color: var(--color-primary);
}

.stat-item.danger .stat-number {
  color: var(--color-severity-high);
}

.stat-item.safe .stat-number {
  color: var(--color-severity-low);
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: var(--color-border);
}

.alert-message {
  font-size: 0.95rem;
  line-height: 1.7;
  padding: var(--space-md);
  border-radius: var(--radius-md);
  margin: 0;
}

.alert-message.danger {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: var(--color-severity-high);
}

.alert-message.safe {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  color: var(--color-severity-low);
}

.alert-message strong {
  font-weight: 700;
}

/* Toggle Map Button */
.toggle-map-btn {
  width: 100%;
  padding: var(--space-md) var(--space-lg);
  border-radius: var(--radius-md);
  background: var(--color-bg-glass);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all var(--transition-base);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
}

.toggle-map-btn:hover {
  background: var(--color-bg-card-hover);
  border-color: var(--color-border-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.toggle-icon {
  font-size: 0.7rem;
  transition: transform var(--transition-base);
}

.refresh-btn {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--color-bg-glass);
  border: 1px solid var(--color-border);
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-base);
  flex-shrink: 0;
}

.refresh-btn:hover {
  background: var(--color-bg-card-hover);
  border-color: var(--color-border-hover);
  transform: rotate(180deg);
}

/* Error */
.error-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-2xl);
  border-radius: var(--radius-lg);
  text-align: center;
}

.error-icon {
  font-size: 2.5rem;
}

.error-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-severity-high);
}

.error-message {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  max-width: 400px;
}

.btn-retry {
  padding: 10px 24px;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: white;
  font-weight: 600;
  font-size: 0.85rem;
  border: none;
  cursor: pointer;
  transition: all var(--transition-base);
}

.btn-retry:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg), var(--shadow-glow);
}

/* Empty state */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-3xl);
  border-radius: var(--radius-lg);
  text-align: center;
}

.empty-icon {
  font-size: 3rem;
}

.empty-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.empty-text {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

/* Footer */
.footer {
  margin-top: var(--space-xl);
  padding: var(--space-lg);
  border-top: 1px solid var(--color-border);
  text-align: center;
}

.footer p {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  line-height: 1.6;
}

/* Recommendations */
.rec-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-lg);
  max-width: 900px;
  margin: 0 auto;
}

@media (min-width: 1200px) {
  .rec-grid {
    max-width: 1000px;
  }
}

.rec-card {
  padding: var(--space-lg) var(--space-xl);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  transition: all var(--transition-base);
}

.rec-card:hover {
  border-color: var(--color-border-hover);
  box-shadow: var(--shadow-lg);
}

.rec-card.priority-card {
  border: 2px solid var(--color-severity-high);
  background: linear-gradient(to bottom, rgba(239, 68, 68, 0.05), transparent);
}

/* Priority Badge */
.priority-badge {
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  text-align: center;
  margin-bottom: var(--space-sm);
  animation: slideInFromTop 0.4s ease-out;
}

@keyframes slideInFromTop {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.priority-badge.danger {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(220, 38, 38, 0.15));
  color: var(--color-severity-high);
  border: 1px solid var(--color-severity-high);
}

.priority-badge.safe {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(22, 163, 74, 0.15));
  color: var(--color-severity-low);
  border: 1px solid var(--color-severity-low);
}

.rec-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--color-border);
}

.rec-content-wrapper {
  position: relative;
  max-height: 300px;
  overflow: hidden;
  transition: max-height 0.3s ease-in-out;
}

.rec-content-wrapper.is-expanded {
  max-height: none;
  overflow: visible;
}

.fade-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 80px;
  background: linear-gradient(to bottom, transparent, var(--color-bg-card));
  pointer-events: none;
}

.rec-content-wrapper.is-expanded .fade-overlay {
  display: none;
}

.rec-content {
  font-size: 0.95rem;
  color: var(--color-text-primary);
  line-height: 1.8;
}

/* Markdown Styling */
.markdown-content :deep(p) {
  margin-bottom: var(--space-md);
}

.markdown-content :deep(h3) {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-top: var(--space-lg);
  margin-bottom: var(--space-sm);
  padding-left: var(--space-sm);
  border-left: 3px solid var(--color-primary);
}

.markdown-content :deep(h3:first-child) {
  margin-top: 0;
}

.markdown-content :deep(strong) {
  font-weight: 700;
  color: var(--color-primary);
}

.markdown-content :deep(ul) {
  margin: var(--space-md) 0;
  padding-left: var(--space-xl);
  list-style: none;
}

.markdown-content :deep(li) {
  position: relative;
  margin-bottom: var(--space-sm);
  padding-left: var(--space-sm);
}

.markdown-content :deep(li::before) {
  content: '•';
  position: absolute;
  left: -16px;
  color: var(--color-primary);
  font-weight: bold;
}

.btn-expand {
  padding: var(--space-sm) var(--space-lg);
  border-radius: var(--radius-md);
  background: var(--color-bg-glass);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all var(--transition-base);
  align-self: center;
  margin-top: var(--space-sm);
}

.btn-expand:hover {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.rec-meta {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  flex-wrap: wrap;
}

.rec-coords,
.rec-distance {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  background: var(--color-bg-glass);
  border: 1px solid var(--color-border);
}

.rec-distance.distance-danger {
  background: rgba(239, 68, 68, 0.15);
  color: var(--color-severity-high);
  border-color: var(--color-severity-high);
  font-weight: 700;
  animation: pulseGlow 2s ease-in-out infinite;
}

@keyframes pulseGlow {
  0%, 100% {
    box-shadow: 0 0 5px rgba(239, 68, 68, 0.3);
  }
  50% {
    box-shadow: 0 0 15px rgba(239, 68, 68, 0.6);
  }
}

/* Responsive */
@media (max-width: 640px) {
  .hero-title {
    font-size: 1.5rem;
  }

  .hero-subtitle {
    font-size: 0.88rem;
  }

  .alert-status-card {
    flex-direction: column;
    gap: var(--space-lg);
    padding: var(--space-lg);
  }

  .alert-icon {
    font-size: 3rem;
    text-align: center;
  }

  .alert-title {
    font-size: 1.2rem;
  }

  .alert-stats {
    flex-direction: column;
    gap: var(--space-md);
    align-items: stretch;
  }

  .stat-divider {
    display: none;
  }

  .stat-item {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-sm);
    background: var(--color-bg-glass);
    border-radius: var(--radius-sm);
  }

  .stat-number {
    font-size: 1.5rem;
  }

  .stat-label {
    font-size: 0.75rem;
  }

  .alert-message {
    font-size: 0.85rem;
  }

  .toggle-map-btn {
    font-size: 0.85rem;
  }
}
</style>
