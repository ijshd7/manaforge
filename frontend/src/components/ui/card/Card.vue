<script setup lang="ts">
import type { HTMLAttributes } from "vue";
import { cn } from "@/lib/utils";

interface Props {
  class?: HTMLAttributes["class"];
}
const props = defineProps<Props>();
</script>

<template>
  <div :class="cn('border-2 border-primary bg-card text-card-foreground pixel-box', props.class)">
    <slot />
  </div>
</template>
