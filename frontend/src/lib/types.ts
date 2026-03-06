export type AssetType = 'image' | 'spritesheet' | 'sound' | 'lore'

export interface Asset {
  id: string
  type: AssetType
  name: string
  prompt: string
  style?: string
  file?: string
  content?: string
  metadata?: Record<string, unknown>
  created: string
  updated: string
  collectionId: string
  collectionName: string
}


export interface SSEEvent {
  progress: number
  message: string
  status: 'running' | 'done' | 'error'
  data?: Record<string, unknown>
}

export interface JobResult {
  jobId: string
  type: AssetType
  progress: number
  message: string
  status: 'idle' | 'running' | 'done' | 'error'
  errorDetail?: string
  result?: Asset
}

export interface GenerateRequest {
  prompt: string
  name: string
  style?: string
  frame_count?: number
  lore_model?: string
  sound_duration?: number
}

export interface OpenRouterModel {
  id: string
  name: string
}
