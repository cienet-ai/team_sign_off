import { defineStore } from "pinia";
import { ref } from "vue";
import { UserManager } from "oidc-client-ts";
import { getMe } from "@/api/auth";
import type { User } from "@/types";

const authority = import.meta.env.VITE_OIDC_AUTHORITY;
const proxyOrigin = window.location.origin;

const oidcSettings = {
  authority,
  client_id: import.meta.env.VITE_OIDC_CLIENT_ID,
  client_secret: import.meta.env.VITE_OIDC_CLIENT_SECRET,
  redirect_uri: proxyOrigin + "/callback",
  post_logout_redirect_uri: proxyOrigin,
  response_type: "code",
  scope: "openid profile email",
  metadata: {
    issuer: authority,
    authorization_endpoint: `${authority}/protocol/openid-connect/auth`,
    token_endpoint: `${proxyOrigin}/realms/team-sign-off/protocol/openid-connect/token`,
    userinfo_endpoint: `${proxyOrigin}/realms/team-sign-off/protocol/openid-connect/userinfo`,
    end_session_endpoint: `${authority}/protocol/openid-connect/logout`,
    jwks_uri: `${proxyOrigin}/realms/team-sign-off/protocol/openid-connect/certs`,
  },
};

const userManager = new UserManager(oidcSettings);

export const useAuthStore = defineStore("auth", () => {
  const user = ref<User | null>(null);
  const accessToken = ref<string | null>(null);
  const loading = ref(true);

  async function handleCallback(): Promise<void> {
    const oidcUser = await userManager.signinCallback();
    if (!oidcUser) return;
    accessToken.value = oidcUser.access_token;
    const me = await getMe();
    if (me) user.value = me;
    loading.value = false;
  }

  async function checkAuth(): Promise<void> {
    const oidcUser = await userManager.getUser();
    if (oidcUser && !oidcUser.expired) {
      accessToken.value = oidcUser.access_token;
      try {
        user.value = await getMe();
      } catch {
        await userManager.removeUser();
        accessToken.value = null;
        user.value = null;
      }
    }
    loading.value = false;
  }

  async function login(): Promise<void> {
    await userManager.signinRedirect();
  }

  async function logout(): Promise<void> {
    await userManager.signoutRedirect();
  }

  return { user, accessToken, loading, handleCallback, checkAuth, login, logout };
});