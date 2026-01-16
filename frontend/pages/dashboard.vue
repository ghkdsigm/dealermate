<script setup lang="ts">
import { useAuthStore } from "~/stores/auth";
import { useApi } from "~/composables/useApi";

const auth = useAuthStore();
const { request } = useApi();

if (!auth.token) {
  navigateTo("/");
}

const deals = ref<any[]>([]);
const selectedDealId = ref<number | null>(null);
const loadingDeals = ref(false);

async function loadDeals() {
  loadingDeals.value = true;
  try {
    deals.value = await request<any[]>("/deals");
    if (!selectedDealId.value && deals.value.length) selectedDealId.value = deals.value[0].id;
  } finally {
    loadingDeals.value = false;
  }
}

onMounted(loadDeals);
</script>

<template>
  <div class="min-h-screen">
    <TopBar />

    <div class="max-w-6xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-1">
        <div class="rounded-2xl bg-white shadow p-4">
          <div class="flex items-center justify-between">
            <h2 class="font-semibold">내 상담(Deal)</h2>
            <button class="text-sm underline" :disabled="loadingDeals" @click="loadDeals">새로고침</button>
          </div>
          <div class="mt-3">
            <DealList :items="deals" :selected-id="selectedDealId" @select="(id) => (selectedDealId = id)" />
          </div>
        </div>

        <div class="mt-6 rounded-2xl bg-white shadow p-4">
          <h2 class="font-semibold">빠른 질문 예시</h2>
          <ul class="mt-2 text-sm text-slate-700 space-y-1">
            <li>• “무사고 SUV 2000만원 이하 추천해줘”</li>
            <li>• “12가3456 리스크 고지 멘트 만들어줘”</li>
            <li>• “쏘렌토 시세 요약해줘”</li>
            <li>• “비교표 만들어줘”</li>
            <li>• “팔로업 카톡 문구”</li>
          </ul>
        </div>
      </div>

      <div class="lg:col-span-2">
        <div class="rounded-2xl bg-white shadow p-4">
          <div class="flex items-center justify-between">
            <h2 class="font-semibold">딜러메이트 Assistant</h2>
            <div class="text-xs text-slate-600">
              {{ auth.profile?.name }} ({{ auth.profile?.role }}) / {{ auth.profile?.branch_id }}
            </div>
          </div>

          <ChatPanel :deal-id="selectedDealId" />
        </div>
      </div>
    </div>
  </div>
</template>
