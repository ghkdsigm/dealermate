import { useAuthStore } from "~/stores/auth";

export function useApi() {
  const config = useRuntimeConfig();
  const auth = useAuthStore();

  async function request<T>(path: string, opts: any = {}): Promise<T> {
    const headers: Record<string, string> = {
      ...(opts.headers || {})
    };
    if (auth.token) headers.Authorization = `Bearer ${auth.token}`;

    return await $fetch<T>(`${config.public.apiBase}${path}`, {
      ...opts,
      headers
    });
  }

  return { request };
}
