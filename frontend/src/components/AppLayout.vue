<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo">Team Sign-Off</div>
      <el-menu
        :default-active="route.path"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/applications">
          <el-icon><Document /></el-icon>
          <span>我的申请</span>
        </el-menu-item>
        <el-menu-item index="/approvals">
          <el-icon><Checked /></el-icon>
          <span>待审批</span>
        </el-menu-item>
        <el-menu-item index="/audit">
          <el-icon><Search /></el-icon>
          <span>审计日志</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-right">
          <span class="username">{{ authStore.user?.display_name }}</span>
          <el-button text @click="authStore.logout()">退出</el-button>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import { HomeFilled, Document, Checked, Search } from "@element-plus/icons-vue";
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const authStore = useAuthStore();
</script>

<style scoped>
.layout {
  height: 100vh;
}
.aside {
  background-color: #304156;
}
.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.header {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 20px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.username {
  color: #666;
}
.main {
  background: #f0f2f5;
  min-height: calc(100vh - 60px);
}
</style>