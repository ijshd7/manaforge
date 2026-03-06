<script setup lang="ts">
import { useToast } from "./use-toast";

const { toasts, dismiss } = useToast();
</script>

<template>
  <div class="fixed bottom-4 right-4 z-50 flex flex-col gap-2 w-80">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="rounded-lg border p-4 shadow-lg text-sm"
        :class="
          toast.variant === 'destructive'
            ? 'bg-destructive text-destructive-foreground border-destructive'
            : 'bg-card text-card-foreground border-border'
        "
      >
        <div class="flex items-start justify-between gap-2">
          <div>
            <p v-if="toast.title" class="font-semibold">{{ toast.title }}</p>
            <p v-if="toast.description" class="text-xs mt-0.5 opacity-90">
              {{ toast.description }}
            </p>
          </div>
          <button
            class="shrink-0 opacity-70 hover:opacity-100 transition-opacity"
            @click="dismiss(toast.id)"
          >
            &times;
          </button>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
