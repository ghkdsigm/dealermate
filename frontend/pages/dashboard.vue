<script setup lang="ts">
import { useAuthStore } from "~/stores/auth";
import { useApi } from "~/composables/useApi";

const auth = useAuthStore();
const { request } = useApi();

if (!auth.token) {
  navigateTo("/");
}

type QuickQuestion = { id: number; text: string; created_at: string };

const deals = ref<any[]>([]);
const selectedDealId = ref<number | null>(null);
const loadingDeals = ref(false);

const quickQuestions = ref<QuickQuestion[]>([]);
const loadingQuickQuestions = ref(false);

const addModalOpen = ref(false);
const addText = ref("");
const savingAdd = ref(false);

const confirmOpen = ref(false);
const confirmId = ref<number | null>(null);
const confirmText = ref("");
const deleting = ref(false);

const draftMessage = ref("");

const filterState = ref<Record<string, any>>({
  complexes: [],
  no_accident: false,
  year_from: null,
  year_to: null,
  km_from: null,
  km_to: null,
  price_from: null,
  price_to: null
});

const listingSearchLoading = ref(false);
const listingResult = ref<any[] | null>(null);

async function loadDeals() {
  loadingDeals.value = true;
  try {
    deals.value = await request<any[]>("/deals");
    if (!selectedDealId.value && deals.value.length) selectedDealId.value = deals.value[0].id;
  } finally {
    loadingDeals.value = false;
  }
}

async function loadQuickQuestions() {
  loadingQuickQuestions.value = true;
  try {
    quickQuestions.value = await request<QuickQuestion[]>("/quick-questions");
  } finally {
    loadingQuickQuestions.value = false;
  }
}

function openAddModal() {
  addText.value = "";
  addModalOpen.value = true;
}

async function addQuickQuestion() {
  const text = addText.value.trim();
  if (!text || savingAdd.value) return;

  savingAdd.value = true;
  try {
    const created = await request<QuickQuestion>("/quick-questions", {
      method: "POST",
      body: { text }
    });
    quickQuestions.value = [created, ...quickQuestions.value];
    addModalOpen.value = false;
  } finally {
    savingAdd.value = false;
  }
}

function askDelete(q: QuickQuestion) {
  confirmId.value = q.id;
  confirmText.value = q.text;
  confirmOpen.value = true;
}

async function deleteQuickQuestion() {
  if (!confirmId.value || deleting.value) return;
  deleting.value = true;
  try {
    await request("/quick-questions/" + String(confirmId.value), { method: "DELETE" });
    quickQuestions.value = quickQuestions.value.filter((x) => x.id !== confirmId.value);
    confirmOpen.value = false;
    confirmId.value = null;
  } finally {
    deleting.value = false;
  }
}

function selectQuickQuestion(text: string) {
  draftMessage.value = text;
}

async function runListingSearch() {
  listingSearchLoading.value = true;
  try {
    const res = await request<any>("/filters/search", {
      method: "POST",
      body: { query: "", filters: filterState.value, top_k: 50 }
    });
    const data = res?.data?.items || res?.result?.data?.items || res?.data?.data?.items;
    listingResult.value = Array.isArray(data) ? data : [];
  } finally {
    listingSearchLoading.value = false;
  }
}

function formatMoneyManwon(n: number | null | undefined) {
  if (!n && n !== 0) return "-";
  return `${n.toLocaleString()}만원`;
}

onMounted(async () => {
  await Promise.all([loadDeals(), loadQuickQuestions()]);
});
</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-slate-50 to-white">
    <TopBar />

    <div class="max-w-7xl mx-auto px-6 py-6 space-y-6">
      <FilterPanel v-model="filterState" @search="runListingSearch" />

      <div
        v-if="listingResult"
        class="rounded-2xl bg-white shadow ring-1 ring-black/5 overflow-hidden"
      >
        <div class="px-5 py-4 flex items-center justify-between">
          <div>
            <div class="font-semibold">검색 결과</div>
            <div class="text-xs text-slate-600">현재 필터 기준으로 조회한 매물 목록입니다.</div>
          </div>
          <div class="text-xs text-slate-600">
            {{ listingSearchLoading ? '조회 중...' : `${listingResult.length}건` }}
          </div>
        </div>

        <div class="overflow-auto border-t">
          <table class="min-w-full text-sm">
            <thead class="bg-slate-50 text-slate-600">
              <tr>
                <th class="text-left font-semibold px-4 py-3">모델</th>
                <th class="text-left font-semibold px-4 py-3">연식</th>
                <th class="text-left font-semibold px-4 py-3">주행</th>
                <th class="text-left font-semibold px-4 py-3">연료</th>
                <th class="text-left font-semibold px-4 py-3">가격</th>
                <th class="text-right font-semibold px-4 py-3">추가</th>
              </tr>
            </thead>
            <tbody class="divide-y">
              <tr v-for="it in listingResult" :key="it.listing_id" class="hover:bg-slate-50">
                <td class="px-4 py-3">
                  <div class="font-medium text-slate-900">{{ it.model }}</div>
                  <div class="text-xs text-slate-600">{{ it.plate }} · {{ it.branch_id }}</div>
                </td>
                <td class="px-4 py-3">{{ it.year }}</td>
                <td class="px-4 py-3">{{ it.km?.toLocaleString() }} Km</td>
                <td class="px-4 py-3">{{ it.fuel }}</td>
                <td class="px-4 py-3">{{ formatMoneyManwon(it.price) }}</td>
                <td class="px-4 py-3 text-right">
                  <button
                    type="button"
                    class="rounded-xl bg-slate-900 text-white px-3 py-2 text-xs font-semibold hover:bg-slate-800"
                    @click="selectQuickQuestion(`이 차량 설명과 추천 포인트를 정리해줘: ${it.model} (${it.plate}) ${it.year}년 ${it.km}km ${it.fuel} ${formatMoneyManwon(it.price)}`)"
                  >
                    입력에 넣기
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div class="lg:col-span-4 space-y-6">
          <div class="rounded-2xl bg-white shadow ring-1 ring-black/5">
            <div class="px-5 py-4 flex items-center justify-between">
              <div>
                <div class="font-semibold">내 상담</div>
                <div class="text-xs text-slate-600">진행 중인 고객 상담을 선택하세요.</div>
              </div>
              <button
                type="button"
                class="rounded-xl border px-3 py-2 text-sm hover:bg-slate-50 disabled:opacity-50"
                :disabled="loadingDeals"
                @click="loadDeals"
              >
                새로고침
              </button>
            </div>
            <div class="px-4 pb-4">
              <DealList :items="deals" :selected-id="selectedDealId" @select="(id) => (selectedDealId = id)" />
            </div>
          </div>

          <div class="rounded-2xl bg-white shadow ring-1 ring-black/5">
            <div class="px-5 py-4 flex items-center justify-between">
              <div>
                <div class="font-semibold">빠른 질문 예시</div>
                <div class="text-xs text-slate-600">자주 쓰는 질문을 저장하고 한 번에 입력에 넣을 수 있어요.</div>
              </div>
              <button
                type="button"
                class="rounded-xl bg-slate-900 text-white px-3 py-2 text-sm font-semibold hover:bg-slate-800"
                @click="openAddModal"
                aria-label="질문 추가"
              >
                <span class="inline-flex items-center gap-2">
                  <svg viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
                  </svg>
                  
                </span>
              </button>
            </div>

            <div class="px-4 pb-4">
              <div v-if="loadingQuickQuestions" class="text-sm text-slate-600 px-1 py-2">로딩 중...</div>
              <ul v-else class="space-y-2">
                <li
                  v-for="q in quickQuestions"
                  :key="q.id"
                  class="group rounded-xl border bg-white hover:bg-slate-50 px-3 py-2 flex items-center justify-between gap-3"
                >
                  <button
                    type="button"
                    class="text-left flex-1 text-sm text-slate-800"
                    @click="selectQuickQuestion(q.text)"
                  >
                    {{ q.text }}
                  </button>
                  <button
                    type="button"
                    class="rounded-lg p-2 text-slate-400 hover:text-red-600 hover:bg-white"
                    @click="askDelete(q)"
                    aria-label="삭제"
                  >
                    <svg viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M3 6h18M8 6V4h8v2m-9 0v16a2 2 0 002 2h6a2 2 0 002-2V6"
                      />
                    </svg>
                  </button>
                </li>
                <li v-if="quickQuestions.length === 0" class="text-sm text-slate-600 px-1 py-2">
                  아직 저장된 질문이 없습니다.
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div class="lg:col-span-8">
          <div class="rounded-2xl bg-white shadow ring-1 ring-black/5">
            <div class="px-5 py-4 flex items-center justify-between">
              <div>
                <div class="font-semibold">딜러메이트 Assistant</div>
                <div class="text-xs text-slate-600">필터 조건은 추천(recommend) 의도에서 자동 반영됩니다.</div>
              </div>
              <div class="text-xs text-slate-600">
                {{ auth.profile?.name }} ({{ auth.profile?.role }}) / {{ auth.profile?.branch_id }}
              </div>
            </div>

            <div class="px-5 pb-5">
              <ChatPanel :deal-id="selectedDealId" :draft-message="draftMessage" :filters="filterState" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <ModalBase :open="addModalOpen" title="자주 묻는 질문 추가" @close="addModalOpen = false">
      <div class="space-y-4">
        <label class="block">
          <div class="text-xs font-semibold text-slate-600 mb-1">질문</div>
          <input
            v-model="addText"
            class="w-full rounded-xl border px-3 py-2"
            placeholder="예: 무사고 SUV 2000만원 이하 추천해줘"
            @keydown.enter.prevent="addQuickQuestion"
          />
        </label>
        <div class="flex justify-end gap-2">
          <button type="button" class="rounded-xl border px-4 py-2 text-sm hover:bg-slate-50" @click="addModalOpen = false">
            취소
          </button>
          <button
            type="button"
            class="rounded-xl bg-slate-900 text-white px-4 py-2 text-sm font-semibold hover:bg-slate-800 disabled:opacity-50"
            :disabled="savingAdd || !addText.trim()"
            @click="addQuickQuestion"
          >
            {{ savingAdd ? '저장 중...' : '추가하기' }}
          </button>
        </div>
      </div>
    </ModalBase>

    <ConfirmDialog
      :open="confirmOpen"
      title="질문 삭제"
      :message="`질문을 삭제하시겠습니까?\n\n${confirmText}`"
      confirmText="삭제"
      cancelText="취소"
      :danger="true"
      @close="confirmOpen = false"
      @confirm="deleteQuickQuestion"
    />
  </div>
</template>
