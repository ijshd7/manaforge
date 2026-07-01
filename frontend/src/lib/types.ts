export type AssetType = "image" | "spritesheet" | "sound" | "lore" | "music";

export interface Asset {
  id: string;
  type: AssetType;
  name: string;
  prompt: string;
  style?: string;
  file?: string;
  content?: string;
  metadata?: Record<string, unknown>;
  created: string;
  updated: string;
  collectionId: string;
  collectionName: string;
}

export interface SSEEvent {
  progress: number;
  message: string;
  status: "running" | "done" | "error";
  data?: Record<string, unknown>;
}

export interface JobResult {
  jobId: string;
  type: AssetType;
  progress: number;
  message: string;
  status: "idle" | "running" | "done" | "error";
  errorDetail?: string;
  result?: Asset;
}

export interface GenerateRequest {
  prompt: string;
  name: string;
  style?: string;
  frame_count?: number;
  lore_model?: string;
  sound_duration?: number;
  target_width?: number | null;
  target_height?: number | null;
  music_duration?: number;
  music_model_version?: string;
  music_temperature?: number;
  music_guidance?: number;
  music_genre?: string | null;
  // Melody conditioning: base64 `data:` URI of an optional reference clip, plus
  // whether to continue from it (true) or mimic its melody (false).
  music_input_audio?: string | null;
  music_continuation?: boolean;
}

export interface OpenRouterModel {
  id: string;
  name: string;
}
