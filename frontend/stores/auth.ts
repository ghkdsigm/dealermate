import { defineStore } from "pinia";

type Profile = {
  name: string;
  role: string;
  branch_id: string;
};

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: "" as string,
    profile: null as Profile | null
  }),
  actions: {
    setAuth(token: string, profile: Profile) {
      this.token = token;
      this.profile = profile;
    },
    logout() {
      this.token = "";
      this.profile = null;
    }
  }
});
