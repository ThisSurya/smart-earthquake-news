<script setup lang="ts">
import { computed } from 'vue'
import { getSeverityLevel, formatDateTime, getSourceLabel } from '@/services/api'
import type { EarthquakeEvent } from '@/services/api'

const props = defineProps<{
  event: EarthquakeEvent
  index?: number
}>()

const severity = computed(() => getSeverityLevel(props.event.severity ?? null))
const source = computed(() => getSourceLabel(props.event.source))
const formattedDate = computed(() => formatDateTime(props.event.datetime))
const animDelay = computed(() => `${(props.index || 0) * 80}ms`)
</script>

<template>
  <article class="eq-card glass slide-up" :style="{ animationDelay: animDelay }">
    <!-- Severity strip -->
    <div class="severity-strip" :style="{ background: severity.color }"></div>

    <div class="card-body">
      <!-- Header -->
      <div class="card-header">
        <div class="header-left">
          <span
            v-if="event.severity"
            class="magnitude-badge"
            :style="{ background: severity.color, color: '#fff' }"
          >
            M{{ event.severity }}
          </span>
          <span
            v-if="event.type === 'earthquake'"
            class="type-badge"
          >
            🔴 Gempa
          </span>
          <span v-else class="type-badge news">📰 Berita</span>
        </div>

        <span
          class="source-badge"
          :style="{ color: source.color, background: source.bg, borderColor: source.color }"
        >
          {{ source.label }}
        </span>
      </div>

      <!-- Title -->
      <h3 class="card-title">{{ event.title }}</h3>

      <!-- Description -->
      <p class="card-description">{{ event.description }}</p>

      <!-- Meta info -->
      <div class="card-meta">
        <div class="meta-item">
          <span class="meta-icon">🕐</span>
          <span class="meta-text">{{ formattedDate }}</span>
        </div>

        <div v-if="event.location?.text" class="meta-item">
          <span class="meta-icon">📍</span>
          <span class="meta-text">{{ event.location.text }}</span>
        </div>

        <div v-if="event.severity" class="meta-item">
          <span class="meta-icon">📊</span>
          <span class="meta-text severity-text" :style="{ color: severity.color }">
            {{ severity.label }}
          </span>
        </div>

        <div v-if="event.isOfficial" class="meta-item official">
          <span class="meta-icon">✅</span>
          <span class="meta-text">Sumber Resmi</span>
        </div>
      </div>

      <!-- Coordinates -->
      <div v-if="event.location?.lat && event.location?.lon" class="coords-row">
        <span class="coord-chip">
          Lat: {{ event.location.lat.toFixed(4) }}
        </span>
        <span class="coord-chip">
          Lon: {{ event.location.lon.toFixed(4) }}
        </span>
      </div>

      <!-- Image -->
      <div v-if="event.image?.large || event.image?.small" class="card-image">
        <img
          :src="(event.image?.large || event.image?.small) ?? undefined"
          :alt="event.title"
          loading="lazy"
        />
      </div>

      <!-- Footer -->
      <div class="card-footer">
        <span class="confidence-label">
          Keyakinan: <strong>{{ event.confidence }}</strong>
        </span>
        <a
          v-if="event.id && event.id.startsWith('http')"
          :href="event.id"
          target="_blank"
          rel="noopener noreferrer"
          class="source-link"
        >
          Baca Selengkapnya →
        </a>
      </div>
    </div>
  </article>
</template>

<style scoped>
.eq-card {
  position: relative;
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all var(--transition-base);
  display: flex;
}

.eq-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl);
  border-color: var(--color-border-hover);
}

.severity-strip {
  width: 4px;
  flex-shrink: 0;
}

.card-body {
  flex: 1;
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

/* Header */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.magnitude-badge {
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.02em;
}

.type-badge {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.type-badge.news {
  color: var(--color-primary-light);
}

.source-badge {
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  border: 1px solid;
}

/* Title */
.card-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.4;
  letter-spacing: -0.01em;
}

/* Description */
.card-description {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

/* Meta */
.card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm) var(--space-md);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.78rem;
}

.meta-icon {
  font-size: 0.85rem;
}

.meta-text {
  color: var(--color-text-muted);
}

.severity-text {
  font-weight: 600;
}

.meta-item.official .meta-text {
  color: var(--color-severity-low);
  font-weight: 500;
}

/* Coords */
.coords-row {
  display: flex;
  gap: var(--space-sm);
  flex-wrap: wrap;
}

.coord-chip {
  padding: 2px 10px;
  background: var(--color-bg-glass);
  border-radius: var(--radius-full);
  font-family: 'Courier New', monospace;
  font-size: 0.72rem;
  color: var(--color-text-muted);
}

/* Image */
.card-image {
  border-radius: var(--radius-md);
  overflow: hidden;
  max-height: 200px;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-slow);
}

.eq-card:hover .card-image img {
  transform: scale(1.03);
}

/* Footer */
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--space-sm);
  padding-top: var(--space-sm);
  border-top: 1px solid var(--color-border);
}

.confidence-label {
  font-size: 0.72rem;
  color: var(--color-text-muted);
  text-transform: capitalize;
}

.confidence-label strong {
  color: var(--color-text-secondary);
}

.source-link {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--color-primary-light);
  transition: color var(--transition-fast);
}

.source-link:hover {
  color: var(--color-primary);
}

/* Responsive */
@media (max-width: 640px) {
  .card-body {
    padding: var(--space-md);
  }

  .card-title {
    font-size: 0.95rem;
  }
}
</style>
