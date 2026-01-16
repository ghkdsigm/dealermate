<script setup lang="ts">
import { useAuthStore } from "~/stores/auth";

const auth = useAuthStore();

watchEffect(() => {
  if (auth.token) navigateTo("/dashboard");
});
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-6">
    <div class="w-full max-w-md rounded-2xl bg-white shadow p-6 space-y-4">
      <h1 class="text-xl font-semibold">DealerMate 로그인</h1>
      <p class="text-sm text-slate-600">
        데모 계정: D001 / M001 / A001 (비밀번호: pass1234)
      </p>
      <LoginForm />
    </div>
  </div>
</template>
