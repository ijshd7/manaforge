<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import Toaster from '@/components/ui/toast/Toaster.vue'
</script>

<template>
  <div class="min-h-screen bg-background">
    <nav class="border-b bg-card">
      <div class="container mx-auto flex h-14 items-center gap-6 px-4">
        <span class="font-bold text-lg tracking-tight">Manaforge</span>
        <div class="flex gap-4">
          <RouterLink
            to="/"
            class="text-sm font-medium text-muted-foreground transition-colors hover:text-primary"
            active-class="text-foreground"
          >
            Generate
          </RouterLink>
          <RouterLink
            to="/archive"
            class="text-sm font-medium text-muted-foreground transition-colors hover:text-primary"
            active-class="text-foreground"
          >
            Archive
          </RouterLink>
        </div>
      </div>
    </nav>
    <main class="container mx-auto px-4 py-8">
      <RouterView />
    </main>
    <Toaster />
  </div>
</template>
