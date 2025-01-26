<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  trend: {
    type: Array,
    default: () => []
  }
})

const chartRef = ref(null)
let chart = null

// 计算图表数据
const chartData = computed(() => {
  return {
    dates: props.trend.map(item => item.date),
    scores: props.trend.map(item => item.score)
  }
})

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return

  chart = echarts.init(chartRef.value)
  updateChart()
}

// 更新图表
const updateChart = () => {
  if (!chart) return

  const option = {
    grid: {
      top: 40,
      right: 40,
      bottom: 40,
      left: 60,
      containLabel: true
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    xAxis: {
      type: 'category',
      data: chartData.value.dates,
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.3)'
        }
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.7)'
      }
    },
    yAxis: {
      type: 'value',
      min: -1,
      max: 1,
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.3)'
        }
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.7)',
        formatter: '{value}'
      }
    },
    series: [
      {
        name: '情感得分',
        type: 'line',
        smooth: true,
        data: chartData.value.scores,
        symbolSize: 8,
        itemStyle: {
          color: '#00F0FF'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {
              offset: 0,
              color: 'rgba(0, 240, 255, 0.3)'
            },
            {
              offset: 1,
              color: 'rgba(0, 240, 255, 0)'
            }
          ])
        }
      }
    ]
  }

  chart.setOption(option)
}

// 监听数据变化
watch(() => props.trend, () => {
  updateChart()
}, { deep: true })

// 监听窗口大小变化
const handleResize = () => {
  chart?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

defineExpose({
  updateChart
})
</script>

<template>
  <div ref="chartRef" class="w-full h-64 rounded-lg bg-black/20 backdrop-blur-sm"></div>
</template>