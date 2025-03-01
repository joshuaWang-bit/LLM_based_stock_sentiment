<script setup>
import { ref } from 'vue'
import RadarChart from './RadarChart.vue'
import TopicBreakdown from './TopicBreakdown.vue'

const props = defineProps({
  topicAnalysis: {
    type: Object,
    required: true
  },
  showDetails: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close-details'])

const activeTab = ref('radar')
</script>

<template>
  <div>
    <!-- 简略视图 -->
    <div v-if="!showDetails">
      <RadarChart :topic-analysis="topicAnalysis" />
    </div>

    <!-- 详细视图 -->
    <div v-else class="space-y-4">
      <!-- 关闭按钮 -->
      <div class="flex justify-end">
        <el-button type="info" size="small" @click="emit('close-details')">
          关闭详情
        </el-button>
      </div>

      <!-- 标签页 -->
      <el-tabs v-model="activeTab" class="custom-tabs">
        <el-tab-pane label="雷达图" name="radar">
          <RadarChart :topic-analysis="topicAnalysis" />
        </el-tab-pane>
        <el-tab-pane label="详细分析" name="breakdown">
          <TopicBreakdown :topic-analysis="topicAnalysis" />
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<style scoped>
.custom-tabs :deep(.el-tabs__item) {
  color: #ffffff80;
}

.custom-tabs :deep(.el-tabs__item.is-active) {
  color: #00F0FF;
}

.custom-tabs :deep(.el-tabs__active-bar) {
  background-color: #00F0FF;
}
</style>