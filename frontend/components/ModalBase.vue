<script setup lang="ts">
const props = defineProps<{
  open: boolean;
  title?: string;
  maxWidthClass?: string;
}>();

const emit = defineEmits<{ (e: "close"): void }>();

function onBackdrop(e: MouseEvent) {
  if (e.target === e.currentTarget) emit("close");
}
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-50">
      <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="onBackdrop"></div>
      <div class="relative h-full w-full flex items-center justify-center p-4">
        <div
          :class="[
            'w-full rounded-2xl bg-white shadow-xl ring-1 ring-black/5',
            maxWidthClass || 'max-w-lg'
          ]"
        >
          <div class="px-5 py-4 border-b flex items-center justify-between">
            <div class="font-semibold text-slate-900">
              {{ title }}
            </div>
            <button
              type="button"
              class="rounded-xl px-2 py-1 text-slate-500 hover:text-slate-900 hover:bg-slate-100"
              @click="emit('close')"
              aria-label="닫기"
            >
              <svg viewBox="0 0 24 24" class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="p-5">
            <slot />
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
