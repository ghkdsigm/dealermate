<script setup lang="ts">
import { useApi } from "~/composables/useApi";

type FilterState = {
  sido?: string;
  sigungu?: string;
  complexes?: string[];
  maker?: string;
  model?: string;
  fuel?: string;
  gear?: string;
  color?: string;
  year_from?: number | null;
  year_to?: number | null;
  km_from?: number | null;
  km_to?: number | null;
  price_from?: number | null;
  price_to?: number | null;
  no_accident?: boolean;
};

const props = defineProps<{
  modelValue: FilterState;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", v: FilterState): void;
  (e: "search"): void;
}>();

const { request } = useApi();

const open = ref(true);
const loadingOpts = ref(false);

const opts = ref<any>(null);

const filters = computed({
  get: () => props.modelValue,
  set: (v: FilterState) => emit("update:modelValue", v)
});

function set<K extends keyof FilterState>(key: K, value: FilterState[K]) {
  filters.value = { ...filters.value, [key]: value };
}

function reset() {
  filters.value = {
    complexes: [],
    no_accident: false,
    year_from: null,
    year_to: null,
    km_from: null,
    km_to: null,
    price_from: null,
    price_to: null
  };
}

async function loadOptions() {
  loadingOpts.value = true;
  try {
    const res = await request<any>("/filters/options");
    opts.value = res?.data || res?.result?.data || res?.data;
  } finally {
    loadingOpts.value = false;
  }
}

const makers = computed(() => opts.value?.makers || []);
const modelsByMaker = computed<Record<string, string[]>>(() => opts.value?.models_by_maker || {});
const models = computed(() => (filters.value.maker ? modelsByMaker.value[filters.value.maker] || [] : []));

const sidos = computed(() => opts.value?.regions?.sido || []);
const sigunguBySido = computed<Record<string, string[]>>(() => opts.value?.regions?.sigungu_by_sido || {});
const sigungus = computed(() => (filters.value.sido ? sigunguBySido.value[filters.value.sido] || [] : []));
const complexes = computed(() => (opts.value?.regions?.complexes || []).filter((x: string) => x !== "전체선택"));

const fuels = computed(() => opts.value?.fuels || []);
const gears = computed(() => opts.value?.gears || []);
const colors = computed(() => opts.value?.colors || []);

watch(
  () => filters.value.maker,
  () => {
    if (filters.value.model) set("model", undefined);
  }
);

watch(
  () => filters.value.sido,
  () => {
    if (filters.value.sigungu) set("sigungu", undefined);
  }
);

onMounted(loadOptions);
</script>

<template>
  <div class="rounded-2xl bg-white shadow ring-1 ring-black/5">
    <div class="px-5 py-4 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <div class="w-9 h-9 rounded-xl bg-slate-900 text-white flex items-center justify-center">
          <svg viewBox="0 0 24 24" class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 5h18M3 12h18M3 19h18" />
          </svg>
        </div>
        <div>
          <div class="font-semibold">차량 필터</div>
          <div class="text-xs text-slate-600">조건을 좁혀 추천/검색 결과를 더 정확하게 만듭니다.</div>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <button
          type="button"
          class="rounded-xl border px-3 py-2 text-sm hover:bg-slate-50"
          @click="open = !open"
        >
          {{ open ? '닫기' : '열기' }}
        </button>
        <button
          type="button"
          class="rounded-xl border px-3 py-2 text-sm hover:bg-slate-50"
          @click="reset"
        >
          검색초기화
        </button>
        <button
          type="button"
          class="rounded-xl bg-slate-900 text-white px-4 py-2 text-sm font-semibold hover:bg-slate-800 disabled:opacity-50"
          :disabled="loadingOpts"
          @click="emit('search')"
        >
          검색
        </button>
      </div>
    </div>

    <div v-if="open" class="px-5 pb-5">
      <div v-if="loadingOpts" class="text-sm text-slate-600">필터 옵션 로딩 중...</div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <div class="lg:col-span-4 rounded-xl border p-4">
          <div class="text-xs font-semibold text-slate-600">지역/단지</div>
          <div class="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
            <label class="text-sm">
              <div class="text-xs text-slate-600 mb-1">시도</div>
              <select
                class="w-full rounded-xl border px-3 py-2 bg-white"
                :value="filters.sido"
                @change="set('sido', ($event.target as HTMLSelectElement).value || undefined)"
              >
                <option value="">선택</option>
                <option v-for="s in sidos" :key="s" :value="s">{{ s }}</option>
              </select>
            </label>

            <label class="text-sm">
              <div class="text-xs text-slate-600 mb-1">지역</div>
              <select
                class="w-full rounded-xl border px-3 py-2 bg-white"
                :value="filters.sigungu"
                :disabled="!filters.sido"
                @change="set('sigungu', ($event.target as HTMLSelectElement).value || undefined)"
              >
                <option value="">선택</option>
                <option v-for="s in sigungus" :key="s" :value="s">{{ s }}</option>
              </select>
            </label>
          </div>

          <div class="mt-3">
            <div class="text-xs text-slate-600 mb-2">단지</div>
            <div class="flex flex-wrap gap-2">
              <button
                type="button"
                class="rounded-full border px-3 py-1 text-xs font-medium"
                :class="(filters.complexes || []).length === 0 ? 'bg-slate-900 text-white border-slate-900' : 'hover:bg-slate-50'"
                @click="set('complexes', [])"
              >
                전체선택
              </button>
              <button
                v-for="c in complexes"
                :key="c"
                type="button"
                class="rounded-full border px-3 py-1 text-xs font-medium hover:bg-slate-50"
                :class="(filters.complexes || []).includes(c) ? 'bg-slate-900 text-white border-slate-900' : ''"
                @click="
                  set(
                    'complexes',
                    (filters.complexes || []).includes(c)
                      ? (filters.complexes || []).filter((x) => x !== c)
                      : [...(filters.complexes || []), c]
                  )
                "
              >
                {{ c }}
              </button>
            </div>
          </div>
        </div>

        <div class="lg:col-span-5 rounded-xl border p-4">
          <div class="text-xs font-semibold text-slate-600">차량 정보</div>
          <div class="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
            <label class="text-sm">
              <div class="text-xs text-slate-600 mb-1">제조사</div>
              <select
                class="w-full rounded-xl border px-3 py-2 bg-white"
                :value="filters.maker"
                @change="set('maker', ($event.target as HTMLSelectElement).value || undefined)"
              >
                <option value="">선택</option>
                <option v-for="m in makers" :key="m" :value="m">{{ m }}</option>
              </select>
            </label>

            <label class="text-sm">
              <div class="text-xs text-slate-600 mb-1">모델</div>
              <select
                class="w-full rounded-xl border px-3 py-2 bg-white"
                :value="filters.model"
                :disabled="!filters.maker"
                @change="set('model', ($event.target as HTMLSelectElement).value || undefined)"
              >
                <option value="">선택</option>
                <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
              </select>
            </label>

            <label class="text-sm">
              <div class="text-xs text-slate-600 mb-1">연료</div>
              <select
                class="w-full rounded-xl border px-3 py-2 bg-white"
                :value="filters.fuel"
                @change="set('fuel', ($event.target as HTMLSelectElement).value || undefined)"
              >
                <option value="">선택</option>
                <option v-for="f in fuels" :key="f" :value="f">{{ f }}</option>
              </select>
            </label>

            <label class="text-sm">
              <div class="text-xs text-slate-600 mb-1">변속기</div>
              <select
                class="w-full rounded-xl border px-3 py-2 bg-white"
                :value="filters.gear"
                @change="set('gear', ($event.target as HTMLSelectElement).value || undefined)"
              >
                <option value="">선택</option>
                <option v-for="g in gears" :key="g" :value="g">{{ g }}</option>
              </select>
            </label>

            <label class="text-sm">
              <div class="text-xs text-slate-600 mb-1">색상</div>
              <select
                class="w-full rounded-xl border px-3 py-2 bg-white"
                :value="filters.color"
                @change="set('color', ($event.target as HTMLSelectElement).value || undefined)"
              >
                <option value="">선택</option>
                <option v-for="c in colors" :key="c" :value="c">{{ c }}</option>
              </select>
            </label>

            <label class="text-sm flex items-center gap-2 mt-6">
              <input
                type="checkbox"
                class="rounded border-slate-300"
                :checked="!!filters.no_accident"
                @change="set('no_accident', ($event.target as HTMLInputElement).checked)"
              />
              <span class="text-sm text-slate-700">무사고</span>
            </label>
          </div>
        </div>

        <div class="lg:col-span-3 rounded-xl border p-4">
          <div class="text-xs font-semibold text-slate-600">범위</div>
          <div class="mt-3 space-y-3">
            <div>
              <div class="text-xs text-slate-600 mb-1">연식</div>
              <div class="grid grid-cols-2 gap-2">
                <input
                  type="number"
                  class="w-full rounded-xl border px-3 py-2"
                  :value="filters.year_from ?? ''"
                  placeholder="부터"
                  @input="set('year_from', ($event.target as HTMLInputElement).value ? Number(($event.target as HTMLInputElement).value) : null)"
                />
                <input
                  type="number"
                  class="w-full rounded-xl border px-3 py-2"
                  :value="filters.year_to ?? ''"
                  placeholder="까지"
                  @input="set('year_to', ($event.target as HTMLInputElement).value ? Number(($event.target as HTMLInputElement).value) : null)"
                />
              </div>
            </div>

            <div>
              <div class="text-xs text-slate-600 mb-1">주행거리(Km)</div>
              <div class="grid grid-cols-2 gap-2">
                <input
                  type="number"
                  class="w-full rounded-xl border px-3 py-2"
                  :value="filters.km_from ?? ''"
                  placeholder="부터"
                  @input="set('km_from', ($event.target as HTMLInputElement).value ? Number(($event.target as HTMLInputElement).value) : null)"
                />
                <input
                  type="number"
                  class="w-full rounded-xl border px-3 py-2"
                  :value="filters.km_to ?? ''"
                  placeholder="까지"
                  @input="set('km_to', ($event.target as HTMLInputElement).value ? Number(($event.target as HTMLInputElement).value) : null)"
                />
              </div>
            </div>

            <div>
              <div class="text-xs text-slate-600 mb-1">가격(만원)</div>
              <div class="grid grid-cols-2 gap-2">
                <input
                  type="number"
                  class="w-full rounded-xl border px-3 py-2"
                  :value="filters.price_from ?? ''"
                  placeholder="부터"
                  @input="set('price_from', ($event.target as HTMLInputElement).value ? Number(($event.target as HTMLInputElement).value) : null)"
                />
                <input
                  type="number"
                  class="w-full rounded-xl border px-3 py-2"
                  :value="filters.price_to ?? ''"
                  placeholder="까지"
                  @input="set('price_to', ($event.target as HTMLInputElement).value ? Number(($event.target as HTMLInputElement).value) : null)"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
