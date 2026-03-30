<script setup lang="ts">
import { computed } from 'vue'
import { getSeverityLevel, formatDateTime, getSourceLabel } from '@/services/api'
import type { EarthquakeEvent, ClusteredResult } from '@/services/api'

const props = defineProps<{
  event?: EarthquakeEvent | null
  cluster?: ClusteredResult | null
}>()

const emit = defineEmits<{
  close: []
}>()

const isOpen = computed(() => !!props.event || !!props.cluster)

const isCluster = computed(() => !!props.cluster)

// For cluster — pick the latest event as the main display
const displayEvent = computed<EarthquakeEvent | null>(() => {
  if (props.event) return props.event
  if (props.cluster && props.cluster.events.length > 0) {
    return [...props.cluster.events].sort(
      (a, b) => new Date(b.datetime).getTime() - new Date(a.datetime).getTime(),
    )[0]
  }
  return null
})

const severity = computed(() => getSeverityLevel(displayEvent.value?.severity ?? null))
const source = computed(() => getSourceLabel(displayEvent.value?.source ?? ''))
const formattedDate = computed(() =>
  displayEvent.value ? formatDateTime(displayEvent.value.datetime) : '',
)

function close() {
  emit('close')
}

function onOverlayClick(e: MouseEvent) {
  if ((e.target as HTMLElement).classList.contains('detail-overlay')) {
    close()
  }
}
</script>

<template>
  <Transition name="panel">
    <div v-if="isOpen" class="detail-overlay" @click="onOverlayClick">
      <div class="detail-panel">
        <!-- Close button -->
        <button id="btn-close-detail" class="btn-close" @click="close">✕</button>

        <!-- Severity header bar -->
        <div class="panel-severity-bar" :style="{ background: severity.color }">
          <span v-if="displayEvent?.severity" class="severity-magnitude">
            M{{ displayEvent.severity }}
          </span>
          <span class="severity-text">{{ severity.label }}</span>
        </div>

        <div class="panel-content" v-if="displayEvent">
          <!-- Title -->
          <h2 class="panel-title">{{ displayEvent.title }}</h2>

          <!-- Cluster info -->
          <div v-if="isCluster && cluster" class="cluster-info">
            <span class="cluster-pill">{{ cluster.events.length }} kejadian dalam cluster</span>
          </div>

          <!-- Meta badges -->
          <div class="panel-badges">
            <span
              class="badge-source"
              :style="{ color: source.color, background: source.bg }"
            >
              {{ source.label }}
            </span>
            <span v-if="displayEvent.isOfficial" class="badge-official">
              ✅ Sumber Resmi
            </span>
            <span class="badge-confidence">
              Confidence: {{ displayEvent.confidence }}
            </span>
            <span class="badge-type">
              {{ displayEvent.type === 'earthquake' ? '🔴 Gempa' : '📰 Berita' }}
            </span>
          </div>

          <!-- Date & time -->
          <div class="panel-info-row">
            <span class="info-icon">🕐</span>
            <span class="info-value">{{ formattedDate }}</span>
          </div>

          <!-- Location -->
          <div class="panel-info-row" v-if="displayEvent.location">
            <span class="info-icon">📍</span>
            <div class="info-location">
              <span v-if="displayEvent.location.text" class="info-value">
                {{ displayEvent.location.text }}
              </span>
              <span class="info-coords">
                {{ displayEvent.location.lat.toFixed(4) }}, {{ displayEvent.location.lon.toFixed(4) }}
              </span>
            </div>
          </div>

          <!-- Full description -->
          <div class="panel-description">
            <h4 class="desc-label">Deskripsi</h4>
            <p class="desc-text">{{ displayEvent.description }}</p>
          </div>

          <!-- Image -->
          <div v-if="displayEvent.image?.large || displayEvent.image?.medium" class="panel-image">
            <img
              :src="(displayEvent.image.large || displayEvent.image.medium) ?? undefined"
              :alt="displayEvent.title"
              loading="lazy"
            />
          </div>

          <!-- Cluster events list -->
          <div v-if="isCluster && cluster && cluster.events.length > 1" class="cluster-events">
            <h4 class="cluster-events-title">Semua Kejadian dalam Cluster</h4>
            <div
              v-for="ev in cluster.events"
              :key="ev.id"
              class="cluster-event-item"
              :style="{ borderLeftColor: getSeverityLevel(ev.severity).color }"
            >
              <span class="cev-title">{{ ev.title }}</span>
              <span class="cev-meta">
                <span v-if="ev.severity" :style="{ color: getSeverityLevel(ev.severity).color }">
                  M{{ ev.severity }}
                </span>
                · {{ formatDateTime(ev.datetime) }}
              </span>
            </div>
          </div>

          <!-- Read more link -->
          <a
            v-if="displayEvent.id?.startsWith('http')"
            :href="displayEvent.id"
            target="_blank"
            rel="noopener noreferrer"
            class="panel-link"
          >
            Baca Selengkapnya →
          </a>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.detail-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 200;
  display: flex;
  justify-content: flex-end;
}

.detail-panel {
  width: 480px;
  max-width: 100%;
  height: 100vh;
  background: var(--color-bg-secondary);
  border-left: 1px solid var(--color-border);
  overflow-y: auto;
  position: relative;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.3);
}

.btn-close {
  position: absolute;
  top: var(--space-md);
  right: var(--space-md);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  background: var(--color-bg-glass);
  color: var(--color-text-primary);
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition: all var(--transition-fast);
}

.btn-close:hover {
  background: var(--color-severity-high);
  color: #fff;
  border-color: var(--color-severity-high);
}

.panel-severity-bar {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-lg) var(--space-xl);
  padding-right: 60px;
}

.severity-magnitude {
  font-size: 1.6rem;
  font-weight: 800;
  color: #fff;
}

.severity-text {
  font-size: 0.9rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.panel-content {
  padding: var(--space-lg) var(--space-xl);
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.panel-title {
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--color-text-primary);
  line-height: 1.35;
  letter-spacing: -0.02em;
}

.cluster-info {
  display: flex;
}

.cluster-pill {
  padding: 4px 14px;
  border-radius: var(--radius-full);
  font-size: 0.78rem;
  font-weight: 600;
  background: rgba(99, 102, 241, 0.12);
  color: var(--color-primary-light);
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.panel-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.badge-source {
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-size: 0.7rem;
  font-weight: 700;
}

.badge-official {
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-size: 0.7rem;
  font-weight: 600;
  background: rgba(34, 197, 94, 0.12);
  color: var(--color-severity-low);
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.badge-confidence {
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-size: 0.7rem;
  font-weight: 600;
  background: var(--color-bg-glass);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  text-transform: capitalize;
}

.badge-type {
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-size: 0.7rem;
  font-weight: 600;
  background: var(--color-bg-glass);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.panel-info-row {
  display: flex;
  align-items: flex-start;
  gap: var(--space-sm);
}

.info-icon {
  font-size: 1rem;
  flex-shrink: 0;
  margin-top: 1px;
}

.info-value {
  font-size: 0.85rem;
  color: var(--color-text-primary);
  line-height: 1.5;
}

.info-location {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-coords {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  font-family: 'Courier New', monospace;
}

.panel-description {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.desc-label {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.desc-text {
  font-size: 0.88rem;
  color: var(--color-text-secondary);
  line-height: 1.7;
}

.panel-image {
  border-radius: var(--radius-md);
  overflow: hidden;
  max-height: 240px;
}

.panel-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cluster-events {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.cluster-events-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.cluster-event-item {
  padding: var(--space-sm) var(--space-md);
  background: var(--color-bg-glass);
  border-radius: var(--radius-md);
  border-left: 3px solid;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.cev-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.35;
}

.cev-meta {
  font-size: 0.72rem;
  color: var(--color-text-muted);
}

.panel-link {
  display: inline-block;
  padding: 10px 20px;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: #fff;
  font-weight: 600;
  font-size: 0.85rem;
  text-align: center;
  transition: all var(--transition-base);
}

.panel-link:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg), var(--shadow-glow);
  color: #fff;
}

/* Transitions */
.panel-enter-active {
  transition: opacity 0.3s ease;
}
.panel-enter-active .detail-panel {
  transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.panel-leave-active {
  transition: opacity 0.25s ease;
}
.panel-leave-active .detail-panel {
  transition: transform 0.25s ease;
}

.panel-enter-from {
  opacity: 0;
}
.panel-enter-from .detail-panel {
  transform: translateX(100%);
}

.panel-leave-to {
  opacity: 0;
}
.panel-leave-to .detail-panel {
  transform: translateX(100%);
}

@media (max-width: 640px) {
  .detail-panel {
    width: 100%;
  }
}
</style>
