<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
import Toaster from "@/components/ui/toast/Toaster.vue";
</script>

<template>
  <div class="min-h-screen bg-background">
    <nav class="border-b-2 border-primary bg-card">
      <div class="container mx-auto flex h-16 items-center gap-8 px-4">
        <span class="font-pixel text-xs text-primary" style="text-shadow: 2px 2px 0px #d97706">
          ✦ Manaforge ✦
        </span>
        <div class="flex gap-6">
          <RouterLink
            to="/"
            class="font-pixel text-xs text-muted-foreground transition-colors hover:text-primary"
            active-class="text-primary"
            :class="{ 'border-b-2 border-accent': $route.path === '/' }"
          >
            Generate
          </RouterLink>
          <RouterLink
            to="/archive"
            class="font-pixel text-xs text-muted-foreground transition-colors hover:text-primary"
            active-class="text-primary"
            :class="{ 'border-b-2 border-accent': $route.path === '/archive' }"
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
