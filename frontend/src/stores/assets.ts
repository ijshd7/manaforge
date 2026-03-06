import { defineStore } from "pinia";
import { ref } from "vue";
import { ASSETS_COLLECTION, pb } from "@/lib/pb";
import type { Asset, AssetType } from "@/lib/types";

export const useAssetsStore = defineStore("assets", () => {
  const items = ref<Asset[]>([]);
  const totalItems = ref(0);
  const totalPages = ref(0);
  const currentPage = ref(1);
  const currentType = ref<AssetType | undefined>(undefined);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function load(type?: AssetType, page = 1) {
    loading.value = true;
    error.value = null;
    currentType.value = type;
    currentPage.value = page;

    try {
      const res = await pb.collection(ASSETS_COLLECTION).getList<Asset>(page, 24, {
        sort: "-name",
        filter: type ? `type="${type}"` : undefined,
      });
      items.value = res.items;
      totalItems.value = res.totalItems;
      totalPages.value = res.totalPages;
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Failed to load assets";
    } finally {
      loading.value = false;
    }
  }

  async function remove(id: string) {
    await pb.collection(ASSETS_COLLECTION).delete(id);
    items.value = items.value.filter((a) => a.id !== id);
    totalItems.value = Math.max(0, totalItems.value - 1);
  }

  // Subscribe to real-time PocketBase updates so the archive
  // refreshes automatically when the backend saves a new asset.
  function subscribeRealtime() {
    pb.collection(ASSETS_COLLECTION).subscribe<Asset>("*", (e) => {
      if (e.action === "create") {
        // Only prepend if it matches the current filter (or no filter)
        if (!currentType.value || e.record.type === currentType.value) {
          items.value = [e.record, ...items.value];
          totalItems.value += 1;
        }
      } else if (e.action === "delete") {
        items.value = items.value.filter((a) => a.id !== e.record.id);
        totalItems.value = Math.max(0, totalItems.value - 1);
      }
    });
  }

  function unsubscribeRealtime() {
    pb.collection(ASSETS_COLLECTION).unsubscribe("*");
  }

  // Helper: get the browser-accessible URL for an asset's file
  function getFileUrl(asset: Asset): string | null {
    if (!asset.file) return null;
    return pb.files.getUrl(asset, asset.file);
  }

  return {
    items,
    totalItems,
    totalPages,
    currentPage,
    currentType,
    loading,
    error,
    load,
    remove,
    subscribeRealtime,
    unsubscribeRealtime,
    getFileUrl,
  };
});
