<template>
  <div class="callback-page">
    <el-result v-if="error" icon="error" title="登录失败" :sub-title="error">
      <template #extra>
        <el-button type="primary" @click="authStore.login()">重新登录</el-button>
      </template>
    </el-result>
    <div v-else class="loading">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <p>正在登录...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { Loading } from "@element-plus/icons-vue";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();
const error = ref<string | null>(null);

onMounted(async () => {
  try {
    await authStore.handleCallback();
    router.replace("/");
  } catch (e: unknown) {
    console.error("OIDC callback error:", e);
    error.value = (e as Error).message || "OIDC 回调处理失败";
  }
});
</script>

<style scoped>
.callback-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
.loading {
  text-align: center;
  color: #666;
}
</style>