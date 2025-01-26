<script setup>
import { computed } from 'vue'

const props = defineProps({
  events: {
    type: Array,
    default: () => []
  }
})

// 计算事件类型的图标
const getEventIcon = (event) => {
  // 获取事件标题（兼容新旧格式）
  const title = typeof event === 'string' ? event : event.title

  if (title.toLowerCase().includes('涨停') || title.toLowerCase().includes('上涨')) {
    return '📈'
  } else if (title.toLowerCase().includes('下跌') || title.toLowerCase().includes('跌停')) {
    return '📉'
  } else if (title.toLowerCase().includes('概念') || title.toLowerCase().includes('行业')) {
    return '🔍'
  } else {
    return '📌'
  }
}

// 格式化事件（兼容新旧格式）
const formatEvent = (event) => {
  if (typeof event === 'string') {
    return {
      title: event,
      description: ''
    }
  }
  return event
}
</script>

<template>
  <div class="space-y-2">
    <div v-for="(event, index) in events" :key="index"
      class="flex items-start gap-2 p-2 rounded-lg bg-black/10 backdrop-blur-sm hover:bg-black/20 transition-all">
      <span class="text-lg">{{ getEventIcon(event) }}</span>
      <div class="flex flex-col">
        <span class="text-sm font-medium text-white/90">{{ formatEvent(event).title }}</span>
        <span v-if="formatEvent(event).description" class="text-xs text-white/70">{{ formatEvent(event).description
          }}</span>
      </div>
    </div>
  </div>
</template>