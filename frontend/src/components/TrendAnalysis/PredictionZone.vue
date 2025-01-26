<script setup>
const props = defineProps({
  prediction: {
    type: String,
    default: ''
  }
})
</script>

<template>
  <div class="p-4 rounded-lg bg-black/20 backdrop-blur-sm border border-primary/20">
    <div class="flex items-center gap-2 mb-2">
      <span class="text-lg">🔮</span>
      <span class="text-sm font-bold text-primary">趋势预测</span>
    </div>
    <p class="text-sm text-white/80 leading-6">{{ prediction }}</p>
  </div>
</template>