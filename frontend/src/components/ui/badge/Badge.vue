<script setup lang="ts">
import type { HTMLAttributes } from "vue";
import { cn } from "@/lib/utils";
import { type BadgeVariants, badgeVariants } from ".";

interface Props {
  class?: HTMLAttributes["class"];
  variant?: BadgeVariants["variant"];
}

const props = withDefaults(defineProps<Props>(), { variant: "default" });
</script>

<template>
  <div :class="cn(badgeVariants({ variant: props.variant }), props.class)">
    <slot />
  </div>
</template>
