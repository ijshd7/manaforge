import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { generateAll, generateSingle } from "@/lib/api";
import { streamJob } from "@/lib/sse";
import type { Asset, AssetType, GenerateRequest, JobResult } from "@/lib/types";
import { useToast } from "@/components/ui/toast/use-toast";

export const useGenerationStore = defineStore("generation", () => {
  const jobs = ref<JobResult[]>([]);
  const isGenerating = computed(() => jobs.value.some((j) => j.status === "running"));

  async function startSingle(type: AssetType, payload: GenerateRequest) {
    jobs.value = [];
    const { job_id } = await generateSingle(type, payload);
    const job: JobResult = {
      jobId: job_id,
      type,
      progress: 0,
      message: "Starting...",
      status: "running",
    };
    jobs.value = [job];
    await _streamOne(job);
  }

  async function startMultiple(types: AssetType[], payload: GenerateRequest) {
    jobs.value = [];
    // Kick off all requests concurrently, collect job entries
    const results = await Promise.all(
      types.map(async (type) => {
        const { job_id } = await generateSingle(type, payload);
        return {
          jobId: job_id,
          type,
          progress: 0,
          message: "Starting...",
          status: "running" as const,
        };
      })
    );
    jobs.value = results;
    await Promise.all(results.map((j) => _streamOne(j)));
  }

  async function startAll(payload: GenerateRequest) {
    jobs.value = [];
    const { jobs: jobMap } = await generateAll(payload);

    const types: AssetType[] = ["image", "spritesheet", "sound", "lore"];
    jobs.value = types.map((type) => ({
      jobId: jobMap[type],
      type,
      progress: 0,
      message: "Starting...",
      status: "running" as const,
    }));

    await Promise.all(jobs.value.map((j) => _streamOne(j)));
  }

  async function retryJob(jobResult: JobResult, payload: GenerateRequest) {
    const { job_id } = await generateSingle(jobResult.type, payload);
    const idx = jobs.value.findIndex((j) => j.jobId === jobResult.jobId);
    if (idx === -1) return;

    jobs.value[idx] = {
      ...jobs.value[idx],
      jobId: job_id,
      progress: 0,
      message: "Retrying...",
      status: "running",
      errorDetail: undefined,
      result: undefined,
    };
    await _streamOne(jobs.value[idx]);
  }

  async function _streamOne(jobRef: JobResult) {
    const { toast } = useToast();
    try {
      for await (const event of streamJob(jobRef.jobId)) {
        const idx = jobs.value.findIndex((j) => j.jobId === jobRef.jobId);
        if (idx === -1) return;

        jobs.value[idx].progress = event.progress;
        jobs.value[idx].message = event.message;

        if (event.status === "done") {
          jobs.value[idx].status = "done";
          jobs.value[idx].result = event.data as Asset & { file_url?: string };
        } else if (event.status === "error") {
          jobs.value[idx].status = "error";
          jobs.value[idx].errorDetail = (event.data?.detail as string) || event.message;

          const service = event.data?.service as string | undefined;
          toast({
            title: `${jobRef.type} generation failed${service ? ` [${service}]` : ""}`,
            description: jobs.value[idx].errorDetail,
            variant: "destructive",
          });
        } else {
          jobs.value[idx].status = "running";
        }
      }
    } catch (err) {
      const idx = jobs.value.findIndex((j) => j.jobId === jobRef.jobId);
      if (idx !== -1) {
        jobs.value[idx].status = "error";
        jobs.value[idx].errorDetail = err instanceof Error ? err.message : "Connection error";
        const { toast } = useToast();
        toast({
          title: `${jobRef.type} stream error`,
          description: jobs.value[idx].errorDetail,
          variant: "destructive",
        });
      }
    }
  }

  function clearJobs() {
    jobs.value = [];
  }

  return { jobs, isGenerating, startSingle, startMultiple, startAll, retryJob, clearJobs };
});
