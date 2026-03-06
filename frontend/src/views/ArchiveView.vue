<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from "vue";
import type { AssetType } from "@/lib/types";
import { useAssetsStore } from "@/stores/assets";
import AssetCard from "@/components/AssetCard.vue";
import { Button } from "@/components/ui/button";

const store = useAssetsStore();

const FILTERS: { label: string; value: AssetType | undefined }[] = [
  { label: "All", value: undefined },
  { label: "🖼️ Images", value: "image" },
  { label: "🎞️ Spritesheets", value: "spritesheet" },
  { label: "🔊 Sounds", value: "sound" },
  { label: "📜 Lore", value: "lore" },
];

const activeFilter = ref<AssetType | undefined>(undefined);

onMounted(() => {
  store.load();
  store.subscribeRealtime();
});

onUnmounted(() => {
  store.unsubscribeRealtime();
});

watch(activeFilter, (type) => store.load(type, 1));

async function handleDelete(id: string) {
  if (!confirm("Delete this asset? This cannot be undone.")) return;
  await store.remove(id);
}

function goToPage(page: number) {
  store.load(activeFilter.value, page);
}
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold">Asset Archive</h1>
      <p class="text-muted-foreground text-sm mt-1">
        {{ store.totalItems }} asset{{ store.totalItems !== 1 ? "s" : "" }} saved
      </p>
    </div>

    <!-- Filter tabs -->
    <div class="flex gap-2 flex-wrap">
      <button
        v-for="f in FILTERS"
        :key="f.label"
        type="button"
        class="rounded-full px-4 py-1.5 text-sm font-medium transition-colors border"
        :class="
          activeFilter === f.value
            ? 'bg-primary text-primary-foreground border-primary'
            : 'bg-background border-input hover:bg-accent'
        "
        @click="activeFilter = f.value"
      >
        {{ f.label }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
      <div v-for="i in 8" :key="i" class="rounded-lg border bg-muted animate-pulse aspect-[4/5]" />
    </div>

    <!-- Error -->
    <div v-else-if="store.error" class="rounded-lg border border-destructive p-6 text-center">
      <p class="text-destructive font-medium">Failed to load assets</p>
      <p class="text-sm text-muted-foreground mt-1">{{ store.error }}</p>
      <Button variant="outline" class="mt-3" @click="store.load(activeFilter)">Retry</Button>
    </div>

    <!-- Empty state -->
    <div
      v-else-if="store.items.length === 0"
      class="rounded-lg border border-dashed p-12 text-center"
    >
      <p class="text-4xl mb-3">🗃️</p>
      <p class="font-medium">No assets yet</p>
      <p class="text-sm text-muted-foreground mt-1">
        Generate some assets and they'll appear here.
      </p>
    </div>

    <!-- Asset grid -->
    <div v-else class="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
      <AssetCard
        v-for="asset in store.items"
        :key="asset.id"
        :asset="asset"
        @delete="handleDelete"
      />
    </div>

    <!-- Pagination -->
    <div v-if="store.totalPages > 1" class="flex items-center justify-center gap-2 pt-4">
      <Button
        variant="outline"
        size="sm"
        :disabled="store.currentPage <= 1"
        @click="goToPage(store.currentPage - 1)"
      >
        Previous
      </Button>
      <span class="text-sm text-muted-foreground">
        Page {{ store.currentPage }} of {{ store.totalPages }}
      </span>
      <Button
        variant="outline"
        size="sm"
        :disabled="store.currentPage >= store.totalPages"
        @click="goToPage(store.currentPage + 1)"
      >
        Next
      </Button>
    </div>
  </div>
</template>
