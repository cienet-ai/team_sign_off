<template>
  <div>
    <div class="page-header">
      <h2>我的申请</h2>
      <el-button type="primary" @click="$router.push('/applications/new')">
        新建申请
      </el-button>
    </div>

    <el-card>
      <el-form :inline="true" :model="filter" class="filter-form">
        <el-form-item label="状态">
          <el-select v-model="filter.status" clearable placeholder="全部" @change="load">
            <el-option
              v-for="opt in STATUS_OPTIONS"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <el-table :data="items" stripe v-loading="loading" @row-click="goDetail">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="180" />
        <el-table-column prop="reason" label="事由" width="180" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="STATUS_TAG_MAP[row.status]">
              {{ STATUS_LABEL_MAP[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="审批人" width="120">
          <template #default="{ row }">
            {{ row.approver?.display_name }}
          </template>
        </el-table-column>
        <el-table-column label="更新时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.updated_at).toLocaleString() }}
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        class="pagination"
        v-model:current-page="pageNum"
        :page-size="filter.limit"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="load"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import { listMyApplications } from "@/api/applications";
import { STATUS_OPTIONS, STATUS_TAG_MAP, STATUS_LABEL_MAP } from "@/types";
import type { Application } from "@/types";

const router = useRouter();
const items = ref<Application[]>([]);
const total = ref(0);
const loading = ref(false);
const pageNum = ref(1);
const filter = reactive({ status: "", limit: 20 });

async function load() {
  loading.value = true;
  try {
    const res = await listMyApplications({
      status: filter.status || undefined,
      limit: filter.limit,
      offset: (pageNum.value - 1) * filter.limit,
    });
    items.value = res.items;
    total.value = res.total;
  } finally {
    loading.value = false;
  }
}

function goDetail(row: Application) {
  router.push(`/applications/${row.id}`);
}

onMounted(load);
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.filter-form {
  margin-bottom: 16px;
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>