import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import AssetCard from "./AssetCard.vue";
import type { Asset } from "@/lib/types";

function musicAsset(overrides: Partial<Asset> = {}): Asset {
  return {
    id: "rec_music_1",
    type: "music",
    name: "Tavern Folk",
    prompt: "cozy medieval tavern",
    file: "tavern_music.mp3",
    metadata: { genre: "Tavern Folk" },
    created: "2026-01-01T00:00:00Z",
    updated: "2026-01-01T00:00:00Z",
    collectionId: "pbc_1321337024",
    collectionName: "assets",
    ...overrides,
  };
}

describe("AssetCard — music", () => {
  it("renders an inline audio player for a music asset with a file", () => {
    const wrapper = mount(AssetCard, { props: { asset: musicAsset() } });
    const audio = wrapper.find("audio");
    expect(audio.exists()).toBe(true);
    const source = audio.find("source");
    expect(source.attributes("type")).toBe("audio/mpeg");
    expect(source.attributes("src")).toContain("tavern_music.mp3");
  });

  it("shows a music type badge", () => {
    const wrapper = mount(AssetCard, { props: { asset: musicAsset() } });
    expect(wrapper.text()).toContain("music");
    expect(wrapper.text()).toContain("🎵");
  });

  it("falls back to the music icon when the asset has no file", () => {
    const wrapper = mount(AssetCard, { props: { asset: musicAsset({ file: undefined }) } });
    expect(wrapper.find("audio").exists()).toBe(false);
    expect(wrapper.text()).toContain("🎵");
  });
});
