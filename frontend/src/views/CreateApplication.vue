<template>
  <div>
    <div class="page-header">
      <h2>新建申请</h2>
    </div>

    <el-card>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        style="max-width: 700px"
      >
        <el-form-item label="申请标题" prop="title">
          <el-input v-model="form.title" placeholder="如：申请 token plan" />
        </el-form-item>
        <el-form-item label="事由" prop="reason">
          <el-input
            v-model="form.reason"
            placeholder="如：申请 token plan / 申请 token play 加油包 / 申请 xx 模型的 apikey"
          />
        </el-form-item>
        <el-form-item label="详细内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="6"
            placeholder="请详细描述申请内容..."
          />
        </el-form-item>
        <el-form-item label="审批人" prop="approver_id">
          <el-select
            v-model="form.approver_id"
            placeholder="选择审批人"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="`${user.display_name} (${user.username})`"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="submit">
            提交申请
          </el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import { getUsers } from "@/api/auth";
import { createApplication } from "@/api/applications";
import type { User } from "@/types";

const router = useRouter();
const formRef = ref<FormInstance>();
const users = ref<User[]>([]);
const submitting = ref(false);

const form = reactive({
  title: "",
  reason: "",
  content: "",
  approver_id: null as number | null,
});

const rules: FormRules = {
  title: [{ required: true, message: "请输入标题", trigger: "blur" }],
  reason: [{ required: true, message: "请输入事由", trigger: "blur" }],
  content: [{ required: true, message: "请输入详细内容", trigger: "blur" }],
  approver_id: [{ required: true, message: "请选择审批人", trigger: "change" }],
};

async function submit() {
  const valid = await formRef.value!.validate().catch(() => false);
  if (!valid) return;
  submitting.value = true;
  try {
    const app = await createApplication({
      title: form.title,
      reason: form.reason,
      content: form.content,
      approver_id: form.approver_id!,
    });
    ElMessage.success("申请已提交");
    router.replace(`/applications/${app.id}`);
  } finally {
    submitting.value = false;
  }
}

onMounted(async () => {
  users.value = await getUsers();
});
</script>

<style scoped>
.page-header {
  margin-bottom: 16px;
}
</style>