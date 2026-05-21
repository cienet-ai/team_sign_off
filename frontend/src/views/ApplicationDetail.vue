<template>
  <div>
    <div class="page-header">
      <h2>申请详情 #{{ app?.id }}</h2>
      <el-button @click="$router.push('/applications')">返回列表</el-button>
    </div>

    <el-card v-if="app" v-loading="loading">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="标题">{{ app.title }}</el-descriptions-item>
        <el-descriptions-item label="事由">{{ app.reason }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="STATUS_TAG_MAP[app.status]">
            {{ STATUS_LABEL_MAP[app.status] }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="申请人">
          {{ app.applicant?.display_name }}
        </el-descriptions-item>
        <el-descriptions-item label="审批人">
          {{ app.approver?.display_name }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ new Date(app.created_at).toLocaleString() }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间" v-if="app.updated_at !== app.created_at">
          {{ new Date(app.updated_at).toLocaleString() }}
        </el-descriptions-item>
        <el-descriptions-item label="驳回原因" v-if="app.reject_reason" :span="2">
          <span style="color: #f56c6c">{{ app.reject_reason }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="详细内容" :span="2">
          <pre class="content">{{ app.content }}</pre>
        </el-descriptions-item>
      </el-descriptions>

      <div class="actions">
        <!-- 审批人操作 -->
        <template v-if="isApprover && app.status === 'pending'">
          <el-popconfirm
            title="确认通过该申请？"
            @confirm="handleApprove"
          >
            <template #reference>
              <el-button type="success">通过</el-button>
            </template>
          </el-popconfirm>
          <el-button type="danger" @click="showRejectDialog = true">驳回</el-button>
        </template>

        <!-- 申请人操作 -->
        <template v-if="isApplicant && app.status === 'rejected'">
          <el-button type="primary" @click="showResubmitDialog = true">
            修改并重提交
          </el-button>
          <el-popconfirm title="确认作废该申请？" @confirm="handleVoid">
            <template #reference>
              <el-button type="info">作废</el-button>
            </template>
          </el-popconfirm>
        </template>
        <template v-if="isApplicant && app.status === 'pending'">
          <el-popconfirm title="确认作废该申请？" @confirm="handleVoid">
            <template #reference>
              <el-button type="info">作废</el-button>
            </template>
          </el-popconfirm>
        </template>
      </div>
    </el-card>

    <!-- 驳回弹窗 -->
    <el-dialog v-model="showRejectDialog" title="驳回申请" width="500px">
      <el-form :model="rejectForm">
        <el-form-item label="驳回原因" required>
          <el-input
            v-model="rejectForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请填写驳回原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRejectDialog = false">取消</el-button>
        <el-button type="danger" :loading="actionLoading" @click="handleReject">
          确认驳回
        </el-button>
      </template>
    </el-dialog>

    <!-- 修改重提交弹窗 -->
    <el-dialog v-model="showResubmitDialog" title="修改并重提交" width="600px">
      <el-form :model="resubmitForm" label-width="100px">
        <el-form-item label="标题">
          <el-input v-model="resubmitForm.title" />
        </el-form-item>
        <el-form-item label="事由">
          <el-input v-model="resubmitForm.reason" />
        </el-form-item>
        <el-form-item label="详细内容">
          <el-input v-model="resubmitForm.content" type="textarea" :rows="6" />
        </el-form-item>
        <el-form-item label="审批人">
          <el-select v-model="resubmitForm.approver_id" filterable style="width: 100%">
            <el-option
              v-for="u in users"
              :key="u.id"
              :label="`${u.display_name} (${u.username})`"
              :value="u.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showResubmitDialog = false">取消</el-button>
        <el-button type="primary" :loading="actionLoading" @click="handleResubmit">
          提交
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "@/stores/auth";
import { getUsers } from "@/api/auth";
import {
  getApplication,
  approveApplication,
  rejectApplication,
  voidApplication,
  updateApplication,
} from "@/api/applications";
import { STATUS_TAG_MAP, STATUS_LABEL_MAP } from "@/types";
import type { Application, User } from "@/types";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const app = ref<Application | null>(null);
const loading = ref(false);
const actionLoading = ref(false);
const showRejectDialog = ref(false);
const showResubmitDialog = ref(false);
const users = ref<User[]>([]);

const rejectForm = reactive({ reason: "" });
const resubmitForm = reactive({
  title: "",
  reason: "",
  content: "",
  approver_id: null as number | null,
});

const isApprover = computed(
  () => app.value && app.value.approver_id === authStore.user?.id,
);
const isApplicant = computed(
  () => app.value && app.value.applicant_id === authStore.user?.id,
);

async function load() {
  loading.value = true;
  try {
    const id = Number(route.params.id);
    app.value = await getApplication(id);
  } finally {
    loading.value = false;
  }
}

async function handleApprove() {
  if (!app.value) return;
  actionLoading.value = true;
  try {
    await approveApplication(app.value.id);
    ElMessage.success("已通过");
    await load();
  } finally {
    actionLoading.value = false;
  }
}

async function handleReject() {
  if (!app.value || !rejectForm.reason) return;
  actionLoading.value = true;
  try {
    await rejectApplication(app.value.id, rejectForm.reason);
    ElMessage.success("已驳回");
    showRejectDialog.value = false;
    rejectForm.reason = "";
    await load();
  } finally {
    actionLoading.value = false;
  }
}

async function handleVoid() {
  if (!app.value) return;
  actionLoading.value = true;
  try {
    await voidApplication(app.value.id);
    ElMessage.success("已作废");
    await load();
  } finally {
    actionLoading.value = false;
  }
}

async function handleResubmit() {
  if (!app.value) return;
  actionLoading.value = true;
  try {
    const newApp = await updateApplication(app.value.id, {
      title: resubmitForm.title || undefined,
      reason: resubmitForm.reason || undefined,
      content: resubmitForm.content || undefined,
      approver_id: resubmitForm.approver_id || undefined,
    });
    ElMessage.success("已重新提交");
    showResubmitDialog.value = false;
    router.replace(`/applications/${newApp.id}`);
  } finally {
    actionLoading.value = false;
  }
}

onMounted(async () => {
  await load();
  if (app.value) {
    resubmitForm.title = app.value.title;
    resubmitForm.reason = app.value.reason;
    resubmitForm.content = app.value.content;
    resubmitForm.approver_id = app.value.approver_id;
  }
  users.value = await getUsers();
});
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.content {
  white-space: pre-wrap;
  font-family: inherit;
  margin: 0;
}
.actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
}
</style>