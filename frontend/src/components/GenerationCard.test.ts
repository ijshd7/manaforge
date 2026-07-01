import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import GenerationCard from "./GenerationCard.vue";
import type { Asset, GenerateRequest, JobResult } from "@/lib/types";

const retryPayload: GenerateRequest = { prompt: "epic boss theme", name: "Boss Fight" };

// A complete record — pb.files.getUrl() returns "" (and the <audio> is gated off)
// unless id + collectionId + file are all present.
function musicAsset(overrides: Partial<Asset> = {}): Asset {
  return {
    id: "rec_music_1",
    type: "music",
    name: "Boss Fight",
    prompt: "epic boss theme",
    file: "boss_fight_music.mp3",
    metadata: { duration: 8, model_version: "stereo-large" },
    created: "2026-01-01T00:00:00Z",
    updated: "2026-01-01T00:00:00Z",
    collectionId: "pbc_1321337024",
    collectionName: "assets",
    ...overrides,
  };
}

function musicJob(overrides: Partial<JobResult> = {}): JobResult {
  return {
    jobId: "job_music_1",
    type: "music",
    progress: 100,
    message: "Done!",
    status: "done",
    result: musicAsset(),
    ...overrides,
  };
}

describe("GenerationCard — music", () => {
  it("labels the card as Music", () => {
    const wrapper = mount(GenerationCard, { props: { job: musicJob(), retryPayload } });
    expect(wrapper.text()).toContain("Music");
    expect(wrapper.text()).toContain("🎵");
  });

  it("renders an inline audio player for a completed music job", () => {
    const wrapper = mount(GenerationCard, { props: { job: musicJob(), retryPayload } });
    const audio = wrapper.find("audio");
    expect(audio.exists()).toBe(true);
    const source = audio.find("source");
    expect(source.attributes("type")).toBe("audio/mpeg");
    expect(source.attributes("src")).toContain("boss_fight_music.mp3");
  });

  it("does not render an audio player until the job is done", () => {
    const wrapper = mount(GenerationCard, {
      props: {
        job: musicJob({ status: "running", progress: 40, result: undefined }),
        retryPayload,
      },
    });
    expect(wrapper.find("audio").exists()).toBe(false);
  });
});
