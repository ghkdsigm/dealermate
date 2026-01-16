<script setup lang="ts">
import { useApi } from "~/composables/useApi";

const props = defineProps<{ dealId: number | null }>();
const { request } = useApi();

const input = ref("");
const loading = ref(false);
const messages = ref<any[]>([
  { role: "assistant", text: "안녕하세요. 조건 또는 차량번호로 질문해 주세요." }
]);

async function send() {
  const msg = input.value.trim();
  if (!msg || loading.value) return;

  messages.value.push({ role: "user", text: msg });
  input.value = "";
  loading.value = true;

  try {
    const res = await request<any>("/assistant/assist", {
      method: "POST",
      body: { deal_id: props.dealId, message: msg }
    });
    const header = `[intent: ${res.intent}] tools: ${(res.used_tools || []).join(", ")}`;
    const body = JSON.stringify(res.result, null, 2);
    messages.value.push({ role: "assistant", text: `${header}\n${body}` });
  } catch (e: any) {
    messages.value.push({ role: "assistant", text: e?.data?.detail || "요청 실패" });
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="mt-4 flex flex-col gap-3">
    <div class="h-[480px] overflow-auto rounded-xl border bg-slate-50 p-3 space-y-3">
      <div
        v-for="(m, idx) in messages"
        :key="idx"
        class="rounded-xl p-3 text-sm whitespace-pre-wrap"
        :class="m.role === 'user' ? 'bg-white border ml-10' : 'bg-slate-900 text-white mr-10'"
      >
        {{ m.text }}
      </div>
    </div>

    <div class="flex gap-2">
      <input
        v-model="input"
        class="flex-1 rounded-xl border px-3 py-2"
        placeholder="예: 무사고 SUV 2000만원 이하 추천"
        @keydown.enter.prevent="send"
      />
      <button
        class="rounded-xl bg-slate-900 text-white px-4 py-2 font-medium disabled:opacity-50"
        :disabled="loading"
        @click="send"
      >
        {{ loading ? "처리 중" : "전송" }}
      </button>
    </div>
  </div>
</template>
