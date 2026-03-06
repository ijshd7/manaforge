import PocketBase from "pocketbase";

// PocketBase is exposed on port 8090 in both dev and prod (see docker-compose.yml)
const PB_URL = import.meta.env.VITE_POCKETBASE_URL || "http://localhost:8090";

export const pb = new PocketBase(PB_URL);

// Collection name constant to avoid magic strings
export const ASSETS_COLLECTION = "assets";
