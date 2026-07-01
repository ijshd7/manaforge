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

interface SizePreset {
  label: string;
  width: number | null;
  height: number | null;
}

interface MusicModelVersion {
  id: string;
  label: string;
}

interface MusicGenre {
  label: string;
  // Prepended to the prompt (and stored raw in metadata); null = free-form prompt.
  value: string | null;
}

// MusicGen model versions exposed by Replicate (`meta/musicgen`).
const MUSIC_MODEL_VERSIONS: MusicModelVersion[] = [
  { id: "stereo-large", label: "Stereo Large" },
  { id: "stereo-melody-large", label: "Stereo Melody Large" },
  { id: "large", label: "Large (mono)" },
  { id: "melody-large", label: "Melody Large (mono)" },
];

// Curated game-music genre presets. The value is prepended to the user's prompt
// by the backend and saved raw in the asset metadata.
const MUSIC_GENRES: MusicGenre[] = [
  { label: "None (free-form)", value: null },
  { label: "Chiptune", value: "chiptune 8-bit video game music" },
  { label: "Orchestral", value: "epic orchestral cinematic score" },
  { label: "Ambient Dungeon", value: "dark ambient dungeon exploration music" },
  { label: "Battle Theme", value: "intense fast-paced battle theme" },
  { label: "Boss Fight", value: "epic dramatic boss fight music" },
  { label: "Tavern Folk", value: "cozy medieval tavern folk music" },
  { label: "Overworld", value: "adventurous overworld exploration theme" },
  { label: "Town Theme", value: "peaceful cheerful town theme" },
  { label: "Mysterious", value: "mysterious eerie atmospheric music" },
  { label: "Victory Fanfare", value: "triumphant heroic victory fanfare" },
];

const SIZE_PRESETS: SizePreset[] = [
  { label: "Original (1024×1024)", width: null, height: null },
  // Tiles & icons
  { label: "16×16 — tile / icon", width: 16, height: 16 },
  { label: "24×24 — small icon", width: 24, height: 24 },
  { label: "32×32 — tile / small sprite", width: 32, height: 32 },
  { label: "48×48 — medium tile", width: 48, height: 48 },
  { label: "64×64 — large icon / UI element", width: 64, height: 64 },
  // Character sprites (square)
  { label: "96×96 — small character", width: 96, height: 96 },
  { label: "128×128 — character sprite", width: 128, height: 128 },
  { label: "256×256 — detailed character", width: 256, height: 256 },
  // Character sprites (tall)
  { label: "32×64 — tall sprite (2:1)", width: 32, height: 64 },
  { label: "48×64 — tall sprite (3:4)", width: 48, height: 64 },
  { label: "64×128 — tall character", width: 64, height: 128 },
  // Card art (portrait)
  { label: "64×96 — card thumbnail", width: 64, height: 96 },
  { label: "128×192 — card illustration", width: 128, height: 192 },
  { label: "256×384 — full card art", width: 256, height: 384 },
  { label: "440×560 — card art (11:14)", width: 440, height: 560 },
  { label: "512×768 — tall card art (2:3)", width: 512, height: 768 },
  { label: "786×1024 — large portrait", width: 786, height: 1024 },
  // Square presets
  { label: "384×384 — medium square", width: 384, height: 384 },
  { label: "512×512 — large square", width: 512, height: 512 },
  // Scenes & backgrounds (landscape)
  { label: "192×128 — event scene (3:2)", width: 192, height: 128 },
  { label: "256×192 — scene panel", width: 256, height: 192 },
  { label: "512×384 — wide scene", width: 512, height: 384 },
  { label: "1024×512 — panoramic banner (2:1)", width: 1024, height: 512 },
  { label: "1024×576 — HD background (16:9)", width: 1024, height: 576 },
  { label: "1280×768 — widescreen background", width: 1280, height: 768 },
  // UI elements
  { label: "200×40 — UI button / bar", width: 200, height: 40 },
];

// Form state
const prompt = ref("");
const name = ref("");
const style = ref<"pixel" | "handdrawn">("pixel");
const frameCount = ref(4);
const soundDuration = ref(3);
const selectedLoreModel = ref("openai/gpt-4o-mini");
const musicDuration = ref(8);
const musicModelVersion = ref("stereo-large");
const musicTemperature = ref(1.0);
const musicGuidance = ref(3);
const selectedMusicGenre = ref<MusicGenre>(MUSIC_GENRES[0]);
const musicInputAudio = ref<string | null>(null);
const musicInputAudioName = ref<string | null>(null);
const musicContinuation = ref(false);
const melodyFileInput = ref<HTMLInputElement | null>(null);
const showMusicAdvanced = ref(false);
const selectedTypes = ref<Set<AssetType>>(new Set(["image"]));
const selectedSizePreset = ref<SizePreset>(SIZE_PRESETS[0]);
const models = ref<OpenRouterModel[]>([]);
const modelsLoading = ref(false);

const ALL_TYPES: AssetType[] = ["image", "spritesheet", "sound", "lore", "music"];
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

// Reference clip cap. Melody conditioning only needs a short seed; the clip is
// base64-encoded into the JSON payload, so bound it to protect the backend.
const MAX_MELODY_BYTES = 10 * 1024 * 1024; // 10 MB

// Bumped on every new selection / clear so a slow FileReader from a superseded
// pick can't clobber a newer one (and an in-flight read is dropped on clear).
let melodyReadToken = 0;

function onMelodyFileChange(e: Event) {
  const input = e.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  if (file.size > MAX_MELODY_BYTES) {
    toast({
      title: "Reference clip too large",
      description: "Please use an audio clip under 10 MB.",
      variant: "destructive",
    });
    input.value = "";
    return;
  }
  const token = ++melodyReadToken;
  const reader = new FileReader();
  reader.onload = () => {
    if (token !== melodyReadToken) return; // superseded by a newer selection/clear
    musicInputAudio.value = typeof reader.result === "string" ? reader.result : null;
    musicInputAudioName.value = file.name;
  };
  reader.onerror = () => {
    if (token !== melodyReadToken) return;
    toast({ title: "Failed to read reference clip", variant: "destructive" });
    input.value = "";
  };
  reader.readAsDataURL(file);
}

function clearMelodyFile() {
  melodyReadToken++; // invalidate any in-flight read
  musicInputAudio.value = null;
  musicInputAudioName.value = null;
  // Reset the native <input> too, or re-selecting the same file won't refire change.
  if (melodyFileInput.value) melodyFileInput.value.value = "";
}

const payload = computed<GenerateRequest>(() => ({
  prompt: prompt.value,
  name: name.value || prompt.value.slice(0, 40),
  style: style.value,
  frame_count: frameCount.value,
  lore_model: selectedLoreModel.value,
  sound_duration: soundDuration.value,
  target_width: selectedSizePreset.value.width,
  target_height: selectedSizePreset.value.height,
  music_duration: musicDuration.value,
  music_model_version: musicModelVersion.value,
  music_temperature: musicTemperature.value,
  music_guidance: musicGuidance.value,
  music_genre: selectedMusicGenre.value.value,
  music_input_audio: musicInputAudio.value,
  music_continuation: musicContinuation.value,
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
    if (isAllSelected.value || selectedTypes.value.size === ALL_TYPES.length) {
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
                { image: "🖼️", spritesheet: "🎞️", sound: "🔊", lore: "📜", music: "🎵" }[type]
              }}</span>
              <span class="capitalize">{{ type }}</span>
            </button>
          </div>
        </div>

        <!-- Output size (image + spritesheet) -->
        <div
          v-if="selectedTypes.has('image') || selectedTypes.has('spritesheet')"
          class="space-y-1.5"
        >
          <label class="text-sm font-medium">Output Size</label>
          <select
            v-model="selectedSizePreset"
            class="w-full border-2 border-secondary bg-secondary px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent"
          >
            <option
              v-for="preset in SIZE_PRESETS"
              :key="preset.label"
              :value="preset"
            >
              {{ preset.label }}
            </option>
          </select>
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

        <!-- Music options -->
        <div v-if="selectedTypes.has('music')" class="space-y-4">
          <div class="space-y-1.5">
            <label class="text-sm font-medium">Genre</label>
            <select
              v-model="selectedMusicGenre"
              class="w-full border-2 border-secondary bg-secondary px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent"
            >
              <option v-for="genre in MUSIC_GENRES" :key="genre.label" :value="genre">
                {{ genre.label }}
              </option>
            </select>
          </div>

          <div class="space-y-1.5">
            <label class="text-sm font-medium">
              Music Duration: <span class="text-muted-foreground">{{ musicDuration }}s</span>
            </label>
            <input
              v-model.number="musicDuration"
              type="range"
              min="3"
              max="30"
              step="1"
              class="w-full accent-primary"
            />
            <div class="flex justify-between text-xs text-muted-foreground">
              <span>3s</span>
              <span>30s</span>
            </div>
          </div>

          <div class="space-y-1.5">
            <label class="text-sm font-medium">Music Model</label>
            <select
              v-model="musicModelVersion"
              class="w-full border-2 border-secondary bg-secondary px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent focus:border-accent"
            >
              <option v-for="mv in MUSIC_MODEL_VERSIONS" :key="mv.id" :value="mv.id">
                {{ mv.label }}
              </option>
            </select>
          </div>

          <!-- Melody conditioning (optional reference clip) -->
          <div class="space-y-1.5">
            <label class="text-sm font-medium">
              Reference Melody <span class="text-muted-foreground">(optional)</span>
            </label>
            <input
              ref="melodyFileInput"
              type="file"
              accept="audio/*"
              class="w-full text-sm text-muted-foreground file:mr-3 file:border-2 file:border-secondary file:bg-secondary file:px-3 file:py-1.5 file:text-sm file:font-medium hover:file:border-primary"
              @change="onMelodyFileChange"
            />
            <div
              v-if="musicInputAudioName"
              class="flex items-center justify-between gap-2 text-xs text-muted-foreground"
            >
              <span class="truncate">🎼 {{ musicInputAudioName }}</span>
              <button
                type="button"
                class="hover:text-primary transition-colors"
                @click="clearMelodyFile"
              >
                Remove
              </button>
            </div>
            <template v-if="musicInputAudio">
              <label class="flex items-center gap-2 text-sm font-medium">
                <input v-model="musicContinuation" type="checkbox" class="accent-primary" />
                Continue from clip
                <span class="text-muted-foreground">(off = match melody)</span>
              </label>
              <p class="text-xs text-muted-foreground">
                Melody matching needs a Melody model version (e.g. Stereo Melody Large).
              </p>
            </template>
          </div>

          <!-- Advanced (collapsible) -->
          <div class="space-y-1.5">
            <button
              type="button"
              class="text-xs text-muted-foreground hover:text-primary transition-colors"
              @click="showMusicAdvanced = !showMusicAdvanced"
            >
              {{ showMusicAdvanced ? "▾" : "▸" }} Advanced
            </button>
            <div v-if="showMusicAdvanced" class="space-y-4 pt-1">
              <div class="space-y-1.5">
                <label class="text-sm font-medium">
                  Temperature:
                  <span class="text-muted-foreground">{{ musicTemperature.toFixed(1) }}</span>
                </label>
                <input
                  v-model.number="musicTemperature"
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  class="w-full accent-primary"
                />
                <div class="flex justify-between text-xs text-muted-foreground">
                  <span>0.0</span>
                  <span>2.0</span>
                </div>
              </div>

              <div class="space-y-1.5">
                <label class="text-sm font-medium">
                  Guidance: <span class="text-muted-foreground">{{ musicGuidance }}</span>
                </label>
                <input
                  v-model.number="musicGuidance"
                  type="range"
                  min="1"
                  max="10"
                  step="1"
                  class="w-full accent-primary"
                />
                <div class="flex justify-between text-xs text-muted-foreground">
                  <span>1</span>
                  <span>10</span>
                </div>
              </div>
            </div>
          </div>
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
