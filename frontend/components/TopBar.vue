<script setup lang="ts">
import { useAuthStore } from "~/stores/auth";

const auth = useAuthStore();

function logout() {
  auth.logout();
  navigateTo("/");
}
</script>

<template>
  <div class="border-b bg-white">
    <div class="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-slate-900 text-white flex items-center justify-center font-bold">DM</div>
        <div>
          <div class="font-semibold">DealerMate</div>
          <div class="text-xs text-slate-600">판매자(딜러/상사)용 AI 업무 에이전트</div>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <div class="text-sm text-slate-700" v-if="auth.profile">
          {{ auth.profile.name }}
        </div>
        <button class="rounded-xl border px-3 py-2 text-sm" @click="logout">로그아웃</button>
      </div>
    </div>
  </div>
</template>
