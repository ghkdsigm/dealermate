<script setup lang="ts">
import { useAuthStore } from "~/stores/auth";

const auth = useAuthStore();

watchEffect(() => {
  if (auth.token) navigateTo("/dashboard");
});
</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-slate-50 to-white flex items-center justify-center p-6">
    <div class="w-full max-w-md">
      <div class="rounded-3xl bg-white shadow-xl ring-1 ring-black/5 p-6 md:p-8 space-y-6">
        <div class="flex items-center gap-3">
          <div class="w-11 h-11 rounded-2xl bg-slate-900 text-white flex items-center justify-center">
            <svg viewBox="0 0 24 24" class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
          </div>
          <div>
            <h1 class="text-xl font-semibold text-slate-900">DealerMate</h1>
            <p class="text-sm text-slate-600">상담을 빠르게, 리스크는 확실하게.</p>
          </div>
        </div>

        <div class="rounded-2xl bg-slate-50 border px-4 py-3 text-sm text-slate-700">
          <div class="font-semibold text-slate-900">데모 계정</div>
          <div class="mt-1">D001 / M001 / A001 (비밀번호: pass1234)</div>
        </div>

        <LoginForm />
      </div>
      <p class="mt-4 text-xs text-slate-500 text-center">
        내부 데모용 UI입니다. 실제 연동 시 권한/데이터는 서버 정책에 맞춰 확장하세요.
      </p>
    </div>
  </div>
</template>
