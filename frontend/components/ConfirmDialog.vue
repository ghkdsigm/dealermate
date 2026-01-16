<script setup lang="ts">
import ModalBase from "~/components/ModalBase.vue";

const props = defineProps<{
  open: boolean;
  title?: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  danger?: boolean;
}>();

const emit = defineEmits<{ (e: "close"): void; (e: "confirm"): void }>();
</script>

<template>
  <ModalBase :open="open" :title="title || '확인'" maxWidthClass="max-w-md" @close="emit('close')">
    <div class="space-y-4">
      <p class="text-sm text-slate-700 whitespace-pre-line">
        {{ message }}
      </p>

      <div class="flex justify-end gap-2">
        <button
          type="button"
          class="rounded-xl border px-4 py-2 text-sm font-medium hover:bg-slate-50"
          @click="emit('close')"
        >
          {{ cancelText || '취소' }}
        </button>
        <button
          type="button"
          :class="[
            'rounded-xl px-4 py-2 text-sm font-semibold text-white',
            danger ? 'bg-red-600 hover:bg-red-700' : 'bg-slate-900 hover:bg-slate-800'
          ]"
          @click="emit('confirm')"
        >
          {{ confirmText || '확인' }}
        </button>
      </div>
    </div>
  </ModalBase>
</template>
