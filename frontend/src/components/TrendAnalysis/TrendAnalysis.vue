<script setup>
import { computed } from 'vue'
import TimeSeries from './TimeSeries.vue'
import EventMarkers from './EventMarkers.vue'
import PredictionZone from './PredictionZone.vue'

const props = defineProps({
  timeAnalysis: {
    type: Object,
    default: () => ({
      trend: [],
      trend_prediction: ''
    })
  }
})

// 获取最新的关键事件
const latestEvents = computed(() => {
  if (!props.timeAnalysis?.trend?.length) return []
  return props.timeAnalysis.trend[props.timeAnalysis.trend.length - 1]?.key_events || []
})
</script>

<template>
  <div class="space-y-4">
    <!-- 时间序列图表 -->
    <TimeSeries :trend="timeAnalysis?.trend || []" />

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- 关键事件标记 -->
      <EventMarkers :events="latestEvents" />
      
      <!-- 预测区域 -->
      <PredictionZone :prediction="timeAnalysis?.trend_prediction" />
    </div>
  </div>
</template> 