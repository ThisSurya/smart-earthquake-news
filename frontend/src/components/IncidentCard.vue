<script setup lang="ts">
import { computed } from 'vue'
import { formatDateTime, getSourceLabel } from '@/services/api'
import type { EarthquakeEvent, ClusteredResult } from '@/services/api'

const props = defineProps<{
  event?: EarthquakeEvent
  cluster?: ClusteredResult
  index?: number
}>()

const emit = defineEmits<{
  select: [event?: EarthquakeEvent, cluster?: ClusteredResult]
}>()

const isCluster = computed(() => !!props.cluster)

// For cluster mode
const clusterEventCount = computed(() => props.cluster?.events.length ?? 0)
const latestEvent = computed(() => {
  if (!props.cluster) return null
  return [...props.cluster.events].sort(
    (a, b) => new Date(b.datetime).getTime() - new Date(a.datetime).getTime(),
  )[0]
})
const clusterCentroidText = computed(() => {
  const c = props.cluster?.centroid
  if (!c) return 'Lokasi tidak diketahui'
  return c.text || `${c.lat.toFixed(2)}, ${c.lon.toFixed(2)}`
})

// For single event mode
const currentEvent = computed(() => props.event ?? latestEvent.value)
const source = computed(() => getSourceLabel(currentEvent.value?.source ?? ''))
const formattedDate = computed(() =>
  currentEvent.value ? formatDateTime(currentEvent.value.datetime) : '',
)
const descriptionPreview = computed(() => {
  const desc = currentEvent.value?.description ?? ''
  return desc.length > 120 ? desc.substring(0, 120) + '…' : desc
})

function onClick() {
  emit('select', props.event, props.cluster)
}
</script>

<template>
  <article
    class="incident-card glass"
    :class="{ 'cluster-card': isCluster }"
    :style="{ animationDelay: `${(index || 0) * 60}ms` }"
    @click="onClick"
  >
    <div class="card-body">
      <!-- Cluster mode -->
      <template v-if="isCluster && cluster">
        <div class="card-top-row">
          <span class="cluster-badge">
            {{ clusterEventCount }} kejadian
          </span>
          <span
            class="source-chip"
            :style="{ color: source.color, background: source.bg }"
          >
            {{ source.label }}
          </span>
        </div>

        <h4 class="card-title">{{ latestEvent?.title || 'Cluster Event' }}</h4>
        <p class="card-desc">{{ descriptionPreview }}</p>

        <div class="card-meta-row">
          <span class="meta-chip">📍 {{ clusterCentroidText }}</span>
          <span class="meta-chip">🕐 {{ formattedDate }}</span>
        </div>
      </template>

      <!-- Single event mode -->
      <template v-else-if="currentEvent">
        <div class="card-top-row">
          <span
            class="source-chip"
            :style="{ color: source.color, background: source.bg }"
          >
            {{ source.label }}
          </span>
        </div>

        <h4 class="card-title">{{ currentEvent.title }}</h4>
        <p class="card-desc">{{ descriptionPreview }}</p>

        <div class="card-meta-row">
          <span v-if="currentEvent.location?.text" class="meta-chip">
            📍 {{ currentEvent.location.text }}
          </span>
          <span class="meta-chip">🕐 {{ formattedDate }}</span>
        </div>

        <div class="card-badges">
          <span v-if="currentEvent.isOfficial" class="badge badge-official">
            ✅ Official
          </span>
          <span class="badge badge-confidence">
            {{ currentEvent.confidence }}
          </span>
        </div>
      </template>
    </div>
  </article>
</template>

<style scoped>
.incident-card {
  display: flex;
  border-radius: var(--radius-lg);
  overflow: hidden;
  cursor: pointer;
  transition: all var(--transition-base);
  animation: slideUp var(--transition-slow) both;
}

.incident-card:hover {
  transform: translateY(-2px);
  border-color: var(--color-border-hover);
  box-shadow: var(--shadow-lg);
}

.card-body {
  flex: 1;
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.card-top-row {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--space-sm);
}

.cluster-badge {
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-size: 0.7rem;
  font-weight: 700;
  background: rgba(99, 102, 241, 0.15);
  color: var(--color-primary-light);
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.source-chip {
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.03em;
}

.card-title {
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.35;
  letter-spacing: -0.01em;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-desc {
  font-size: 0.78rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.card-meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.meta-chip {
  font-size: 0.7rem;
  color: var(--color-text-muted);
  padding: 2px 8px;
  background: var(--color-bg-glass);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.card-badges {
  display: flex;
  gap: 6px;
  margin-top: 2px;
}

.badge {
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: 0.65rem;
  font-weight: 600;
}

.badge-official {
  background: rgba(34, 197, 94, 0.12);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.badge-confidence {
  background: var(--color-bg-glass);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  text-transform: capitalize;
}
</style>
