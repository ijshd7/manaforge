<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { fetchModels } from "@/lib/api";
import type { AssetType, GenerateRequest, OpenRouterModel } from "@/lib/types";
import { useGenerationStore } from "@/stores/generation";
import GenerationCard from "@/components/GenerationCard.vue";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast/use-toast";

const store = useGenerationStore();
const { toast } = useToast();

// Form state
const prompt = ref("");
const name = ref("");
const style = ref<"pixel" | "handdrawn">("pixel");
const frameCount = ref(4);
const soundDuration = ref(3);
const selectedLoreModel = ref("openai/gpt-4o-mini");
const selectedTypes = ref<Set<AssetType>>(new Set(["image"]));
const models = ref<OpenRouterModel[]>([]);
const modelsLoading = ref(false);

const ALL_TYPES: AssetType[] = ["image", "spritesheet", "sound", "lore"];
const isAllSelected = computed(() => ALL_TYPES.every((t) => selectedTypes.value.has(t)));

onMounted(async () => {
  modelsLoading.value = true;
  try {
    models.value = await fetchModels();
    if (models.value.length > 0 && !models.value.find((m) => m.id === selectedLoreModel.value)) {
      selectedLoreModel.value = models.value[0].id;
    }
  } catch {
    // Non-fatal — user can still type a model ID
  } finally {
    modelsLoading.value = false;
  }
});

function toggleType(type: AssetType) {
  const s = new Set(selectedTypes.value);
  s.has(type) ? s.delete(type) : s.add(type);
  selectedTypes.value = s;
}

function toggleAll() {
  if (isAllSelected.value) {
    selectedTypes.value = new Set();
  } else {
    selectedTypes.value = new Set(ALL_TYPES);
  }
}

const payload = computed<GenerateRequest>(() => ({
  prompt: prompt.value,
  name: name.value || prompt.value.slice(0, 40),
  style: style.value,
  frame_count: frameCount.value,
  lore_model: selectedLoreModel.value,
  sound_duration: soundDuration.value,
}));

async function handleGenerate() {
  if (!prompt.value.trim()) {
    toast({
      title: "Prompt required",
      description: "Please enter a prompt before generating.",
      variant: "destructive",
    });
    return;
  }
  if (selectedTypes.value.size === 0) {
    toast({ title: "Select at least one asset type", variant: "destructive" });
    return;
  }

  try {
    if (isAllSelected.value || selectedTypes.value.size === 4) {
      await store.startAll(payload.value);
    } else if (selectedTypes.value.size === 1) {
      const type = [...selectedTypes.value][0];
      await store.startSingle(type, payload.value);
    } else {
      await store.startMultiple([...selectedTypes.value], payload.value);
    }
  } catch (err) {
    toast({
      title: "Failed to start generation",
      description: err instanceof Error ? err.message : "Unknown error",
      variant: "destructive",
    });
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto space-y-8">
    <div>
      <h1 class="font-pixel text-base text-primary">Generate Assets</h1>
      <p class="text-muted-foreground text-sm mt-2">
        Create game assets using AI. Select types, write a prompt, and generate.
      </p>
    </div>

    <!-- Form -->
    <div class="grid gap-6 md:grid-cols-2">
      <!-- Left: Prompt + Name -->
      <div class="space-y-4">
        <div class="space-y-1.5">
          <label class="text-sm font-medium">Asset Name</label>
          <input
            v-model="name"
            type="text"
            placeholder="e.g. Fire Dragon"
            class="w-full border-2 border-secondary bg-secondary px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent"
          />
        </div>

        <div class="space-y-1.5">
          <label class="text-sm font-medium">Prompt</label>
          <textarea
            v-model="prompt"
            rows="5"
            placeholder="Describe your game asset in detail…"
            class="w-full border-2 border-secondary bg-secondary px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent resize-none"
          />
        </div>

        <!-- Art Style -->
        <div class="space-y-1.5">
          <label class="text-sm font-medium">Art Style</label>
          <div class="flex gap-2">
            <button
              v-for="s in [
                { id: 'pixel', label: 'Pixel Art' },
                { id: 'handdrawn', label: 'Hand-drawn' },
              ]"
              :key="s.id"
              type="button"
              class="flex-1 border-2 px-3 py-2 text-sm font-medium transition-all"
              :class="
                style === s.id
                  ? 'border-primary bg-primary text-primary-foreground'
                  : 'border-secondary bg-secondary hover:border-primary'
              "
              @click="style = s.id as 'pixel' | 'handdrawn'"
            >
              {{ s.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- Right: Type selection + Options -->
      <div class="space-y-4">
        <div class="space-y-1.5">
          <div class="flex items-center justify-between">
            <label class="text-sm font-medium">Asset Types</label>
            <button
              type="button"
              class="text-xs text-muted-foreground hover:text-primary transition-colors"
              @click="toggleAll"
            >
              {{ isAllSelected ? "Deselect all" : "Select all" }}
            </button>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="type in ALL_TYPES"
              :key="type"
              type="button"
              class="flex items-center gap-2 border-2 px-3 py-2.5 text-sm font-medium transition-all text-left"
              :class="
                selectedTypes.has(type)
                  ? 'border-primary bg-primary text-primary-foreground'
                  : 'border-secondary bg-secondary hover:border-primary'
              "
              @click="toggleType(type)"
            >
              <span class="text-base">{{
                { image: "🖼️", spritesheet: "🎞️", sound: "🔊", lore: "📜" }[type]
              }}</span>
              <span class="capitalize">{{ type }}</span>
            </button>
          </div>
        </div>

        <!-- Spritesheet options -->
        <div v-if="selectedTypes.has('spritesheet')" class="space-y-1.5">
          <label class="text-sm font-medium">
            Frame Count: <span class="text-muted-foreground">{{ frameCount }}</span>
          </label>
          <input
            v-model.number="frameCount"
            type="range"
            min="2"
            max="12"
            class="w-full accent-primary"
          />
          <div class="flex justify-between text-xs text-muted-foreground">
            <span>2 frames</span>
            <span>12 frames</span>
          </div>
        </div>

        <!-- Sound options -->
        <div v-if="selectedTypes.has('sound')" class="space-y-1.5">
          <label class="text-sm font-medium">
            Duration: <span class="text-muted-foreground">{{ soundDuration }}s</span>
          </label>
          <input
            v-model.number="soundDuration"
            type="range"
            min="1"
            max="22"
            step="0.5"
            class="w-full accent-primary"
          />
          <div class="flex justify-between text-xs text-muted-foreground">
            <span>1s</span>
            <span>22s</span>
          </div>
        </div>

        <!-- Lore model selection -->
        <div v-if="selectedTypes.has('lore')" class="space-y-1.5">
          <label class="text-sm font-medium">Lore Model</label>
          <select
            v-model="selectedLoreModel"
            class="w-full border-2 border-secondary bg-secondary px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent"
          >
            <option v-if="modelsLoading" disabled>Loading models…</option>
            <option v-for="m in models" :key="m.id" :value="m.id">{{ m.name }}</option>
            <option v-if="!modelsLoading && models.length === 0" :value="selectedLoreModel">
              {{ selectedLoreModel }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Generate Button -->
    <Button
      class="w-full"
      size="lg"
      variant="cta"
      :disabled="store.isGenerating || selectedTypes.size === 0"
      @click="handleGenerate"
    >
      <span v-if="store.isGenerating">Generating…</span>
      <span v-else-if="isAllSelected">Generate All Assets</span>
      <span v-else>
        Generate
        {{ [...selectedTypes].map((t) => t.charAt(0).toUpperCase() + t.slice(1)).join(" + ") }}
      </span>
    </Button>

    <!-- Progress cards -->
    <div v-if="store.jobs.length > 0" class="space-y-4">
      <h2 class="font-pixel text-sm text-primary">Generation Progress</h2>
      <div class="grid gap-4 sm:grid-cols-2">
        <GenerationCard
          v-for="job in store.jobs"
          :key="job.jobId"
          :job="job"
          :retry-payload="payload"
          @retry="(j, p) => store.retryJob(j, p)"
        />
      </div>
    </div>
  </div>
</template>
