<script setup lang="ts">
import { computed } from 'vue'
import type { EarthquakeEvent, ClusteredResult } from '@/services/api'
import IncidentCard from './IncidentCard.vue'

const props = defineProps<{
  events: EarthquakeEvent[]
  clusters: ClusteredResult[]
  mode: 'events' | 'clusters' | null
  loading: boolean
}>()

const emit = defineEmits<{
  'select-event': [event: EarthquakeEvent]
  'select-cluster': [cluster: ClusteredResult]
}>()

const isClusterMode = computed(() => props.mode === 'clusters')

const sortedEvents = computed(() => {
  return [...props.events].sort(
    (a, b) => new Date(b.datetime).getTime() - new Date(a.datetime).getTime(),
  )
})

const sortedClusters = computed(() => {
  return [...props.clusters].sort((a, b) => {
    const latestA = Math.max(...a.events.map((e) => new Date(e.datetime).getTime()))
    const latestB = Math.max(...b.events.map((e) => new Date(e.datetime).getTime()))
    return latestB - latestA
  })
})

const totalEventCount = computed(() => {
  if (isClusterMode.value) {
    return props.clusters.reduce((sum, c) => sum + c.events.length, 0)
  }
  return props.events.length
})

function onCardSelect(event?: EarthquakeEvent, cluster?: ClusteredResult) {
  if (cluster) {
    emit('select-cluster', cluster)
  } else if (event) {
    emit('select-event', event)
  }
}
</script>

<template>
  <aside class="incident-feed">
    <div class="feed-header">
      <h2 class="feed-title">📰 Feed</h2>
      <span v-if="!loading" class="feed-count">
        {{ totalEventCount }} kejadian
      </span>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="feed-loading">
      <div v-for="i in 5" :key="i" class="skeleton-card">
        <div class="skeleton-strip"></div>
        <div class="skeleton-body">
          <div class="skeleton-line w60"></div>
          <div class="skeleton-line w90"></div>
          <div class="skeleton-line w40"></div>
        </div>
      </div>
    </div>

    <!-- Feed list -->
    <div v-else-if="totalEventCount > 0" class="feed-list">
      <!-- Cluster mode -->
      <template v-if="isClusterMode">
        <IncidentCard
          v-for="(cluster, i) in sortedClusters"
          :key="cluster.cluster_id"
          :cluster="cluster"
          :index="i"
          @select="onCardSelect"
        />
      </template>

      <!-- Event mode -->
      <template v-else>
        <IncidentCard
          v-for="(event, i) in sortedEvents"
          :key="event.id"
          :event="event"
          :index="i"
          @select="onCardSelect"
        />
      </template>
    </div>

    <!-- Empty state -->
    <div v-else class="feed-empty">
      <span class="empty-icon">📭</span>
      <p class="empty-text">Belum ada data kejadian</p>
      <p class="empty-hint">Pilih kota atau gunakan lokasi Anda</p>
    </div>
  </aside>
</template>

<style scoped>
.incident-feed {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: rgba(15, 23, 42, 0.6);
  border-left: 1px solid var(--color-border);
}

.feed-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md) var(--space-lg);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.feed-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.feed-count {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-muted);
  padding: 3px 10px;
  background: var(--color-bg-glass);
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border);
}

.feed-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-sm);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.feed-loading {
  flex: 1;
  padding: var(--space-sm);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.skeleton-card {
  display: flex;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--color-bg-glass);
  border: 1px solid var(--color-border);
}

.skeleton-strip {
  width: 4px;
  background: linear-gradient(180deg, var(--color-text-muted) 0%, transparent 100%);
  opacity: 0.3;
}

.skeleton-body {
  flex: 1;
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-line {
  height: 10px;
  border-radius: var(--radius-sm);
  background: linear-gradient(90deg, var(--color-bg-glass) 25%, rgba(255,255,255,0.08) 50%, var(--color-bg-glass) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.w60 { width: 60%; }
.w90 { width: 90%; }
.w40 { width: 40%; }

.feed-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  padding: var(--space-xl);
  text-align: center;
}

.empty-icon {
  font-size: 2.5rem;
}

.empty-text {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.empty-hint {
  font-size: 0.78rem;
  color: var(--color-text-muted);
}
</style>
