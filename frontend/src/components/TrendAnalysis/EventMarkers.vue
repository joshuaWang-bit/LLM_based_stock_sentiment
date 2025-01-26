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
  if (event.toLowerCase().includes('涨停') || event.toLowerCase().includes('上涨')) {
    return '📈'
  } else if (event.toLowerCase().includes('下跌') || event.toLowerCase().includes('跌停')) {
    return '📉'
  } else if (event.toLowerCase().includes('概念') || event.toLowerCase().includes('行业')) {
    return '🔍'
  } else {
    return '📌'
  }
}
</script>

<template>
  <div class="space-y-2">
    <div v-for="(event, index) in events" :key="index"
      class="flex items-start gap-2 p-2 rounded-lg bg-black/10 backdrop-blur-sm hover:bg-black/20 transition-all">
      <span class="text-lg">{{ getEventIcon(event) }}</span>
      <span class="text-sm text-white/90">{{ event }}</span>
    </div>
  </div>
</template>