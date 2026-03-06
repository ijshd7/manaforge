<script setup lang="ts">
import { computed } from 'vue'
import type { JobResult, GenerateRequest } from '@/lib/types'
import { pb } from '@/lib/pb'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const props = defineProps<{
  job: JobResult
  retryPayload: GenerateRequest
}>()

const emit = defineEmits<{
  retry: [job: JobResult, payload: GenerateRequest]
}>()

const typeLabels: Record<string, string> = {
  image: 'Image',
  spritesheet: 'Spritesheet',
  sound: 'Sound',
  lore: 'Lore',
}

const typeIcons: Record<string, string> = {
  image: '🖼️',
  spritesheet: '🎞️',
  sound: '🔊',
  lore: '📜',
}

const fileUrl = computed(() => {
  const r = props.job.result
  if (!r || !r.file) return null
  // Use the PocketBase SDK to build the correct file URL
  return pb.files.getUrl(r, r.file as string)
})

const isImage = computed(() => props.job.type === 'image' || props.job.type === 'spritesheet')
const isSound = computed(() => props.job.type === 'sound')
const isLore = computed(() => props.job.type === 'lore')

function downloadFile() {
  if (fileUrl.value) {
    const a = document.createElement('a')
    a.href = fileUrl.value
    a.download = `${props.job.result?.name || props.job.type}`
    a.click()
  } else if (isLore.value && props.job.result?.content) {
    const blob = new Blob([props.job.result.content as string], { type: 'text/plain' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `${props.job.result?.name || 'lore'}.txt`
    a.click()
  }
}
</script>

<template>
  <Card
    :class="[
      'transition-all',
      job.status === 'error' && 'border-destructive',
      job.status === 'done' && 'border-green-500/50',
    ]"
  >
    <CardHeader class="pb-3">
      <div class="flex items-center justify-between">
        <CardTitle class="text-base flex items-center gap-2">
          <span>{{ typeIcons[job.type] }}</span>
          <span>{{ typeLabels[job.type] }}</span>
        </CardTitle>
        <Badge
          :variant="
            job.status === 'error'
              ? 'destructive'
              : job.status === 'done'
                ? 'default'
                : 'secondary'
          "
        >
          {{ job.status }}
        </Badge>
      </div>
    </CardHeader>

    <CardContent class="space-y-3">
      <!-- Progress bar (shown while running) -->
      <div v-if="job.status === 'running'" class="space-y-1.5">
        <Progress :model-value="job.progress" class="h-2" />
        <p class="text-xs text-muted-foreground">{{ job.message }}</p>
      </div>

      <!-- Error state -->
      <div v-if="job.status === 'error'" class="space-y-2">
        <p class="text-sm text-destructive font-medium">Generation failed</p>
        <p class="text-xs text-muted-foreground break-words">{{ job.errorDetail }}</p>
        <Button
          size="sm"
          variant="outline"
          class="border-destructive text-destructive hover:bg-destructive hover:text-destructive-foreground"
          @click="emit('retry', job, retryPayload)"
        >
          Retry
        </Button>
      </div>

      <!-- Done state: preview -->
      <div v-if="job.status === 'done'" class="space-y-3">
        <!-- Image / Spritesheet preview -->
        <img
          v-if="isImage && fileUrl"
          :src="fileUrl"
          :alt="job.result?.name as string"
          class="w-full rounded-md object-contain max-h-64 border"
        />

        <!-- Sound player -->
        <div v-if="isSound && fileUrl">
          <audio controls class="w-full">
            <source :src="fileUrl" type="audio/mpeg" />
          </audio>
        </div>

        <!-- Lore text -->
        <div
          v-if="isLore && job.result?.content"
          class="max-h-48 overflow-y-auto rounded-md bg-muted p-3 text-sm leading-relaxed"
        >
          {{ job.result.content }}
        </div>

        <div class="flex items-center justify-between pt-1">
          <p class="text-xs text-muted-foreground">{{ job.message }}</p>
          <Button v-if="fileUrl || isLore" size="sm" variant="outline" @click="downloadFile">
            Download
          </Button>
        </div>
      </div>
    </CardContent>
  </Card>
</template>
