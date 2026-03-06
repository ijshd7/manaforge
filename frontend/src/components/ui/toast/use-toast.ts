import { ref } from "vue";

export interface Toast {
  id: string;
  title?: string;
  description?: string;
  variant?: "default" | "destructive";
  duration?: number;
}

const toasts = ref<Toast[]>([]);

export function useToast() {
  function toast(options: Omit<Toast, "id">) {
    const id = Math.random().toString(36).slice(2);
    const t: Toast = { id, duration: 5000, ...options };
    toasts.value.push(t);
    setTimeout(() => dismiss(id), t.duration);
  }

  function dismiss(id: string) {
    toasts.value = toasts.value.filter((t) => t.id !== id);
  }

  return { toast, toasts, dismiss };
}
