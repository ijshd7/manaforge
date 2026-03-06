<script setup lang="ts">
import { computed } from "vue";
import type { Asset } from "@/lib/types";
import { pb } from "@/lib/pb";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const props = defineProps<{ asset: Asset }>();
const emit = defineEmits<{ delete: [id: string] }>();

const typeIcons: Record<string, string> = {
  image: "🖼️",
  spritesheet: "🎞️",
  sound: "🔊",
  lore: "📜",
};

const fileUrl = computed(() => {
  if (!props.asset.file) return null;
  return pb.files.getUrl(props.asset, props.asset.file);
});

const formattedDate = computed(() => {
  return new Date(props.asset.created).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
});

async function downloadAsset() {
  if (fileUrl.value) {
    try {
      const response = await fetch(fileUrl.value);
      const blob = await response.blob();
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = props.asset.name;
      a.click();
      URL.revokeObjectURL(a.href);
    } catch (err) {
      console.error("Failed to download asset:", err);
    }
  } else if (props.asset.content) {
    const blob = new Blob([props.asset.content], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `${props.asset.name}.txt`;
    a.click();
    URL.revokeObjectURL(a.href);
  }
}
</script>

<template>
  <Card class="flex flex-col overflow-hidden">
    <!-- Preview area -->
    <div class="relative bg-muted aspect-video flex items-center justify-center overflow-hidden">
      <!-- Image / Spritesheet -->
      <img
        v-if="(asset.type === 'image' || asset.type === 'spritesheet') && fileUrl"
        :src="fileUrl"
        :alt="asset.name"
        class="w-full h-full object-contain"
      />

      <!-- Sound player -->
      <div v-else-if="asset.type === 'sound' && fileUrl" class="w-full px-4">
        <audio controls class="w-full">
          <source :src="fileUrl" type="audio/mpeg" />
        </audio>
      </div>

      <!-- Lore preview -->
      <div
        v-else-if="asset.type === 'lore' && asset.content"
        class="p-4 text-xs text-muted-foreground leading-relaxed line-clamp-6 text-left w-full"
      >
        {{ asset.content }}
      </div>

      <!-- Fallback -->
      <span v-else class="text-4xl">{{ typeIcons[asset.type] }}</span>

      <!-- Type badge overlay -->
      <Badge class="absolute top-2 right-2 capitalize" variant="secondary">
        {{ typeIcons[asset.type] }} {{ asset.type }}
      </Badge>
    </div>

    <CardContent class="flex-1 pt-4 pb-2 space-y-1">
      <p class="font-medium text-sm truncate">{{ asset.name }}</p>
      <p class="text-xs text-muted-foreground truncate" :title="asset.prompt">
        {{ asset.prompt }}
      </p>
      <p class="text-xs text-muted-foreground">{{ formattedDate }}</p>
    </CardContent>

    <CardFooter class="gap-2 pt-0">
      <Button size="sm" variant="outline" class="flex-1" @click="downloadAsset"> Download </Button>
      <Button
        size="sm"
        variant="ghost"
        class="text-destructive hover:bg-destructive hover:text-destructive-foreground"
        @click="emit('delete', asset.id)"
      >
        Delete
      </Button>
    </CardFooter>
  </Card>
</template>
