<template>
  <div>
    <h2>待我审批</h2>

    <el-card>
      <el-table :data="items" stripe v-loading="loading" @row-click="goDetail">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="reason" label="事由" width="200" />
        <el-table-column label="申请人" width="120">
          <template #default="{ row }">
            {{ row.applicant?.display_name }}
          </template>
        </el-table-column>
        <el-table-column label="提交时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="success"
              size="small"
              @click.stop="approve(row.id)"
              :loading="approvingIds.has(row.id)"
            >
              通过
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click.stop="openReject(row)"
            >
              驳回
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && items.length === 0" description="暂无待审批申请" />

      <el-pagination
        v-if="total > 0"
        class="pagination"
        v-model:current-page="pageNum"
        :page-size="limit"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="load"
      />
    </el-card>

    <!-- 快速驳回弹窗 -->
    <el-dialog v-model="rejectVisible" title="驳回申请" width="500px">
      <el-form>
        <el-form-item label="驳回原因" required>
          <el-input
            v-model="rejectReason"
            type="textarea"
            :rows="4"
            placeholder="请填写驳回原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectVisible = false">取消</el-button>
        <el-button type="danger" :loading="rejecting" @click="doReject">
          确认驳回
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { listPendingApprovals, approveApplication, rejectApplication } from "@/api/applications";
import type { Application } from "@/types";

const router = useRouter();
const items = ref<Application[]>([]);
const total = ref(0);
const loading = ref(false);
const pageNum = ref(1);
const limit = 20;

const rejectVisible = ref(false);
const rejectReason = ref("");
const rejecting = ref(false);
const rejectingId = ref<number | null>(null);
const approvingIds = ref(new Set<number>());

async function load() {
  loading.value = true;
  try {
    const res = await listPendingApprovals({
      limit,
      offset: (pageNum.value - 1) * limit,
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

async function approve(id: number) {
  approvingIds.value.add(id);
  try {
    await approveApplication(id);
    ElMessage.success("已通过");
    await load();
  } finally {
    approvingIds.value.delete(id);
  }
}

function openReject(row: Application) {
  rejectingId.value = row.id;
  rejectReason.value = "";
  rejectVisible.value = true;
}

async function doReject() {
  if (!rejectingId.value || !rejectReason.value) return;
  rejecting.value = true;
  try {
    await rejectApplication(rejectingId.value, rejectReason.value);
    ElMessage.success("已驳回");
    rejectVisible.value = false;
    await load();
  } finally {
    rejecting.value = false;
  }
}

onMounted(load);
</script>

<style scoped>
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>