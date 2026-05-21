<template>
  <div>
    <h2>首页</h2>
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="我的申请" :value="stats.myTotal" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="待审批" :value="stats.pendingApprovals" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="已通过" :value="stats.approved" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="已驳回" :value="stats.rejected" />
        </el-card>
      </el-col>
    </el-row>
    <div class="actions">
      <el-button type="primary" @click="$router.push('/applications/new')">
        新建申请
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted } from "vue";
import { listMyApplications, listPendingApprovals } from "@/api/applications";

const stats = reactive({
  myTotal: 0,
  pendingApprovals: 0,
  approved: 0,
  rejected: 0,
});

onMounted(async () => {
  const [myRes, pendingRes, approvedRes, rejectedRes] = await Promise.all([
    listMyApplications({ limit: 1 }),
    listPendingApprovals({ limit: 1 }),
    listMyApplications({ status: "approved", limit: 1 }),
    listMyApplications({ status: "rejected", limit: 1 }),
  ]);
  stats.myTotal = myRes.total;
  stats.pendingApprovals = pendingRes.total;
  stats.approved = approvedRes.total;
  stats.rejected = rejectedRes.total;
});
</script>

<style scoped>
.stats-row {
  margin-bottom: 24px;
}
</style>