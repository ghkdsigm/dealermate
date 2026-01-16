export default defineNuxtConfig({
  modules: ["@nuxtjs/tailwindcss", "@pinia/nuxt"],
  css: ["~/assets/css/tailwind.css"],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8001"
    }
  },
  devtools: { enabled: false },
  app: {
    head: {
      title: "DealerMate",
      meta: [{ name: "viewport", content: "width=device-width, initial-scale=1" }]
    }
  }
});
