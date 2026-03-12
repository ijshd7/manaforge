<script setup lang="ts">
import { type HTMLAttributes, computed } from "vue";
import { ProgressIndicator, ProgressRoot, type ProgressRootProps } from "radix-vue";
import { cn } from "@/lib/utils";

interface Props extends ProgressRootProps {
  class?: HTMLAttributes["class"];
  indicatorClass?: HTMLAttributes["class"];
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: 0,
});

const delegatedProps = computed(() => {
  const { class: _, indicatorClass: __, ...delegated } = props;
  return delegated;
});
</script>

<template>
  <ProgressRoot
    v-bind="delegatedProps"
    :class="cn('relative h-4 w-full overflow-hidden border-2 border-secondary bg-muted', props.class)"
  >
    <ProgressIndicator
      class="h-full w-full flex-1 bg-linear-to-r from-primary to-accent transition-all"
      :class="indicatorClass"
      :style="`transform: translateX(-${100 - (props.modelValue ?? 0)}%)`"
    />
  </ProgressRoot>
</template>
