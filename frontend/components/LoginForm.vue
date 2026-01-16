<script setup lang="ts">
import { useAuthStore } from "~/stores/auth";
import { useApi } from "~/composables/useApi";

const auth = useAuthStore();
const { request } = useApi();

const employee_id = ref("D001");
const password = ref("pass1234");
const loading = ref(false);
const error = ref("");

async function onLogin() {
  error.value = "";
  loading.value = true;
  try {
    const res = await request<any>("/auth/login", {
      method: "POST",
      body: { employee_id: employee_id.value, password: password.value }
    });
    auth.setAuth(res.access_token, { name: res.name, role: res.role, branch_id: res.branch_id });
    await navigateTo("/dashboard");
  } catch (e: any) {
    error.value = e?.data?.detail || "로그인 실패";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <form class="space-y-3" @submit.prevent="onLogin">
    <div>
      <label class="text-sm font-medium">사번/아이디</label>
      <input v-model="employee_id" class="mt-1 w-full rounded-xl border px-3 py-2" placeholder="D001" />
    </div>
    <div>
      <label class="text-sm font-medium">비밀번호</label>
      <input v-model="password" type="password" class="mt-1 w-full rounded-xl border px-3 py-2" placeholder="pass1234" />
    </div>

    <button
      type="submit"
      class="w-full rounded-xl bg-slate-900 text-white py-2 font-medium disabled:opacity-50"
      :disabled="loading"
    >
      {{ loading ? "로그인 중..." : "로그인" }}
    </button>

    <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
  </form>
</template>
