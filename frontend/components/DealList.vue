<script setup lang="ts">
const props = defineProps<{ items: any[]; selectedId: number | null }>();
const emit = defineEmits<{ (e: "select", id: number): void }>();
</script>

<template>
  <div class="space-y-2">
    <div
      v-for="d in props.items"
      :key="d.id"
      class="rounded-2xl border p-3 cursor-pointer hover:bg-slate-50 transition"
      :class="props.selectedId === d.id ? 'border-slate-900 bg-slate-50 shadow-sm' : ''"
      @click="emit('select', d.id)"
    >
      <div class="flex items-center justify-between">
        <div class="text-sm font-semibold text-slate-900">Deal #{{ d.id }}</div>
        <div
          class="text-xs font-semibold px-2 py-1 rounded-full"
          :class="d.status === 'open' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-600'"
        >
          {{ d.status }}
        </div>
      </div>
      <div class="mt-1 text-xs text-slate-600 truncate">
        {{ d.customer_token }}
      </div>
    </div>

    <div v-if="!props.items?.length" class="text-sm text-slate-600">
      상담 이력이 없습니다. 오른쪽에서 질문을 시작하면 자동 생성됩니다.
    </div>
  </div>
</template>
