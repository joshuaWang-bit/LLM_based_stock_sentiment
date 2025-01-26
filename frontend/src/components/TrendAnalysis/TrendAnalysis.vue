<script setup>
import { ref, computed } from 'vue'
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

// 当前选中的日期数据
const currentDateData = ref(null)

// 获取要显示的事件
const displayEvents = computed(() => {
  if (currentDateData.value) {
    return currentDateData.value.key_events
  }
  // 如果没有选中的日期，显示最新一天的事件
  if (!props.timeAnalysis?.trend?.length) return []
  return props.timeAnalysis.trend[props.timeAnalysis.trend.length - 1]?.key_events || []
})

// 处理日期悬停事件
const handleDateHover = (dateData) => {
  currentDateData.value = dateData
}
</script>

<template>
  <div class="space-y-4">
    <!-- 时间序列图表 -->
    <TimeSeries :trend="timeAnalysis?.trend || []" @dateHover="handleDateHover" />

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- 关键事件标记 -->
      <EventMarkers :events="displayEvents" />

      <!-- 预测区域 -->
      <PredictionZone :prediction="timeAnalysis?.trend_prediction" />
    </div>
  </div>
</template>