import { describe, it, expect, beforeEach, vi } from "vitest";
import { mount, VueWrapper, DOMWrapper } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";

// onMounted() calls fetchModels(), which does fetch("/api/models"). A relative URL
// throws in the node/jsdom test env, so stub the whole api module. The store also
// imports generateAll/generateSingle from here — stub them too (unused in these tests).
vi.mock("@/lib/api", () => ({
  fetchModels: vi.fn().mockResolvedValue([]),
  generateSingle: vi.fn(),
  generateAll: vi.fn(),
}));

import GenerateView from "./GenerateView.vue";

function findButtonByText(wrapper: VueWrapper, text: string): DOMWrapper<Element> | undefined {
  return wrapper.findAll("button").find((b) => b.text().toLowerCase().includes(text.toLowerCase()));
}

describe("GenerateView — music options block", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("hides the music controls until Music is selected", () => {
    const wrapper = mount(GenerateView);
    // Default selection is ["image"], so the music-only labels are absent.
    expect(wrapper.text()).not.toContain("Music Duration");
    expect(wrapper.text()).not.toContain("Music Model");
  });

  it("reveals genre, duration, and model controls after selecting Music", async () => {
    const wrapper = mount(GenerateView);
    const musicToggle = findButtonByText(wrapper, "music");
    if (!musicToggle) throw new Error("Music type toggle button not found");
    await musicToggle.trigger("click");

    expect(wrapper.text()).toContain("Genre");
    expect(wrapper.text()).toContain("Music Duration");
    expect(wrapper.text()).toContain("Music Model");
    // Curated genre presets and model versions render inside their selects.
    expect(wrapper.text()).toContain("Chiptune");
    expect(wrapper.text()).toContain("Stereo Large");
  });

  it("toggles the advanced temperature and guidance controls", async () => {
    const wrapper = mount(GenerateView);
    const musicToggle = findButtonByText(wrapper, "music");
    if (!musicToggle) throw new Error("Music type toggle button not found");
    await musicToggle.trigger("click");

    // Advanced controls are collapsed by default.
    expect(wrapper.text()).not.toContain("Temperature");

    const advancedToggle = findButtonByText(wrapper, "Advanced");
    if (!advancedToggle) throw new Error("Advanced toggle button not found");
    await advancedToggle.trigger("click");

    expect(wrapper.text()).toContain("Temperature");
    expect(wrapper.text()).toContain("Guidance");
  });
});
