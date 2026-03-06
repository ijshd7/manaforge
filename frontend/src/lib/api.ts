import type { AssetType, GenerateRequest, OpenRouterModel } from './types'

const BASE = '/api'

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `HTTP ${res.status}`
    try {
      const body = await res.json()
      detail = body.detail || detail
    } catch {
      // ignore parse error
    }
    throw new Error(detail)
  }
  return res.json()
}

export async function generateSingle(
  type: AssetType,
  payload: GenerateRequest,
): Promise<{ job_id: string }> {
  const res = await fetch(`${BASE}/generate/${type}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return handleResponse(res)
}

export async function generateAll(
  payload: GenerateRequest,
): Promise<{ jobs: Record<AssetType, string> }> {
  const res = await fetch(`${BASE}/generate/all`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return handleResponse(res)
}

export async function fetchModels(): Promise<OpenRouterModel[]> {
  const res = await fetch(`${BASE}/models`)
  return handleResponse(res)
}
