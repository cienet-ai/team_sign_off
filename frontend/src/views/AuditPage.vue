<template>
  <div>
    <h2>审计日志</h2>

    <el-card>
      <el-form :inline="true" :model="filter" class="filter-form">
        <el-form-item label="申请状态">
          <el-select v-model="filter.status" clearable placeholder="全部">
            <el-option
              v-for="opt in STATUS_OPTIONS"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="操作类型">
          <el-select v-model="filter.action" clearable placeholder="全部">
            <el-option
              v-for="opt in ACTION_OPTIONS"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">检索</el-button>
          <el-button @click="reset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="items" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="申请单" width="180">
          <template #default="{ row }">
            <el-link type="primary" @click="$router.push(`/applications/${row.application_id}`)">
              #{{ row.application_id }} {{ row.application?.title }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-tag>{{ ACTION_LABEL_MAP[row.action] || row.action }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="申请人" width="120">
          <template #default="{ row }">
            {{ row.application?.applicant?.display_name }}
          </template>
        </el-table-column>
        <el-table-column label="审批人" width="120">
          <template #default="{ row }">
            {{ row.application?.approver?.display_name }}
          </template>
        </el-table-column>
        <el-table-column label="操作人" width="120">
          <template #default="{ row }">
            {{ row.performed_by?.display_name }}
          </template>
        </el-table-column>
        <el-table-column label="申请状态" width="100">
          <template #default="{ row }">
            <el-tag
              v-if="row.application"
              :type="STATUS_TAG_MAP[row.application.status]"
            >
              {{ STATUS_LABEL_MAP[row.application.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="180">
          <template #default="{ row }">
            {{ row.comment || "-" }}
          </template>
        </el-table-column>
        <el-table-column label="时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && items.length === 0" description="暂无审计记录" />

      <el-pagination
        v-if="total > 0"
        class="pagination"
        v-model:current-page="pageNum"
        :page-size="limit"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="search"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { listAuditLogs } from "@/api/audit";
import {
  STATUS_OPTIONS,
  ACTION_OPTIONS,
  STATUS_TAG_MAP,
  STATUS_LABEL_MAP,
  ACTION_LABEL_MAP,
} from "@/types";
import type { AuditLog } from "@/types";

const items = ref<AuditLog[]>([]);
const total = ref(0);
const loading = ref(false);
const pageNum = ref(1);
const limit = 20;
const dateRange = ref<[string, string] | null>(null);

const filter = reactive({
  status: "",
  action: "",
});

async function search() {
  loading.value = true;
  try {
    const params: Record<string, unknown> = {
      limit,
      offset: (pageNum.value - 1) * limit,
    };
    if (filter.status) params.status = filter.status;
    if (filter.action) params.action = filter.action;
    if (dateRange.value) {
      params.start_date = dateRange.value[0];
      params.end_date = dateRange.value[1];
    }
    const res = await listAuditLogs(params);
    items.value = res.items;
    total.value = res.total;
  } finally {
    loading.value = false;
  }
}

function reset() {
  filter.status = "";
  filter.action = "";
  dateRange.value = null;
  pageNum.value = 1;
  search();
}

search();
</script>

<style scoped>
.filter-form {
  margin-bottom: 16px;
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>