<template>
  <div class="h-64">
    <v-chart class="h-full w-full" :option="chartOption" autoresize />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { GaugeChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'

// 注册必要的组件
use([CanvasRenderer, GaugeChart, TitleComponent, TooltipComponent])

const props = defineProps({
  score: {
    type: Number,
    default: 0
  },
  confidence: {
    type: Number,
    default: 0
  }
})

// 计算图表配置
const chartOption = computed(() => ({
  series: [
    {
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      center: ['50%', '75%'],
      radius: '90%',
      min: -1,
      max: 1,
      splitNumber: 8,
      axisLine: {
        lineStyle: {
          width: 6,
          color: [
            [-0.75, '#FF3860'],  // 极度负面
            [-0.25, '#FF9F43'],  // 偏负面
            [0.25, '#FFD700'],   // 中性
            [0.75, '#39FF14'],   // 偏正面
            [1, '#00F0FF']       // 极度正面
          ]
        }
      },
      pointer: {
        icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
        length: '12%',
        width: 20,
        offsetCenter: [0, '-60%'],
        itemStyle: {
          color: 'inherit'
        }
      },
      axisTick: {
        length: 12,
        lineStyle: {
          color: 'inherit',
          width: 2
        }
      },
      splitLine: {
        length: 20,
        lineStyle: {
          color: 'inherit',
          width: 5
        }
      },
      axisLabel: {
        color: '#fff',
        fontSize: 16,
        distance: -60,
        formatter: function(value) {
          if (value === -1) return '极负面'
          if (value === 0) return '中性'
          if (value === 1) return '极正面'
          return ''
        }
      },
      title: {
        offsetCenter: [0, '-20%'],
        fontSize: 20,
        color: '#fff'
      },
      detail: {
        fontSize: 30,
        offsetCenter: [0, '0%'],
        valueAnimation: true,
        formatter: function(value) {
          return Math.round(value * 100) + '%'
        },
        color: 'inherit'
      },
      data: [{
        value: props.score,
        name: '情感得分'
      }]
    },
    {
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      center: ['50%', '75%'],
      radius: '70%',
      min: 0,
      max: 100,
      itemStyle: {
        color: '#7B42FF'
      },
      progress: {
        show: true,
        width: 8
      },
      pointer: {
        show: false
      },
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      splitLine: {
        show: false
      },
      axisLabel: {
        show: false
      },
      title: {
        show: false
      },
      detail: {
        show: false
      },
      data: [{
        value: props.confidence,
        name: '置信度'
      }]
    }
  ]
}))
</script> 