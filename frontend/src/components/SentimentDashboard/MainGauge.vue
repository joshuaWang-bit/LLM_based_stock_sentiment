<template>
  <div class="h-64 relative">
    <!-- Details Panel -->
    <div v-if="showDetails" class="absolute top-0 left-0 right-0 z-10">
      <div class="backdrop-blur-sm bg-black/20 rounded-lg p-3">
        <div class="flex justify-between items-center mb-2">
          <div class="text-xs text-gray-400 font-medium">详细信息</div>
          <el-button type="info" size="small" circle @click="$emit('close-details')">
            <el-icon>
              <Close />
            </el-icon>
          </el-button>
        </div>
        <div class="grid grid-cols-2 gap-x-4 gap-y-1">
          <div class="text-[11px] text-gray-400">
            <span class="opacity-60">原始分数:</span>
            <span class="text-primary">{{ score }}</span>
          </div>
          <div class="text-[11px] text-gray-400">
            <span class="opacity-60">原始置信度:</span>
            <span class="text-primary">{{ confidence }}</span>
          </div>
          <div class="text-[11px] text-gray-400">
            <span class="opacity-60">标准化分数:</span>
            <span class="text-primary">{{ normalizedScore }}</span>
          </div>
          <div class="text-[11px] text-gray-400">
            <span class="opacity-60">标准化置信度:</span>
            <span class="text-primary">{{ normalizedConfidence }}</span>
          </div>
        </div>
      </div>
    </div>
    <!-- Main Gauge -->
    <div class="relative h-full">
      <v-chart class="h-full w-full" :option="chartOption" :autoresize="true" @rendered="onChartRendered" />
      <!-- Extreme Labels -->
      <div class="absolute bottom-[15%] left-[10%] text-xs px-2 py-1">极负面</div>
      <div class="absolute bottom-[15%] right-[10%] text-xs px-2 py-1">极正面</div>

      <!-- Confidence Gauge -->
      <div class="absolute top-2 right-2 w-20 h-20">
        <v-chart class="h-full w-full" :option="confidenceChartOption" :autoresize="true" />
        <div class="absolute top-14 left-0 w-full text-center text-xs">置信度</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, watch, ref, nextTick } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { GaugeChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent } from 'echarts/components'
import VChart, { THEME_KEY } from 'vue-echarts'
import { provide } from 'vue'
import { Close } from '@element-plus/icons-vue'

// 提供暗色主题
provide(THEME_KEY, 'dark')

// 注册必要的组件
use([CanvasRenderer, GaugeChart, TitleComponent, TooltipComponent])

// Debug counters
const updateCount = ref(0)

const props = defineProps({
  score: {
    type: Number,
    required: true,
    default: 0,
    validator: (value) => {
      console.log('[MainGauge/Props] Validating score:', value)
      return !isNaN(value)
    }
  },
  confidence: {
    type: Number,
    required: true,
    default: 0,
    validator: (value) => {
      console.log('[MainGauge/Props] Validating confidence:', value)
      return !isNaN(value)
    }
  },
  showDetails: {
    type: Boolean,
    default: false
  }
})

defineEmits(['close-details'])

// 数据处理
const normalizedScore = computed(() => {
  const value = Number(props.score)
  console.log('[MainGauge] Normalizing score:', {
    input: props.score,
    parsed: value,
    valid: !isNaN(value),
    type: typeof props.score
  })
  // 直接使用0-1范围的分数，转换为-1到1用于显示
  const normalizedValue = isNaN(value) ? 0 : (value * 2 - 1)
  console.log('[MainGauge] Final normalized score:', normalizedValue)
  return Math.max(-1, Math.min(1, normalizedValue))
})

const normalizedConfidence = computed(() => {
  const value = Number(props.confidence)
  console.log('[MainGauge] Normalizing confidence:', {
    input: props.confidence,
    parsed: value,
    valid: !isNaN(value),
    type: typeof props.confidence
  })
  // 确保置信度在 0-1 范围内
  const normalizedValue = isNaN(value) ? 0 : value
  console.log('[MainGauge] Final normalized confidence:', normalizedValue)
  return Math.max(0, Math.min(1, normalizedValue))
})

// 监听属性变化
watch(() => props.score, (newVal, oldVal) => {
  console.log('[MainGauge] Score changed:', {
    old: oldVal,
    new: newVal,
    normalized: normalizedScore.value,
    type: typeof newVal
  })
  updateCount.value++
}, { immediate: true })

watch(() => props.confidence, (newVal, oldVal) => {
  console.log('[MainGauge] Confidence changed:', {
    old: oldVal,
    new: newVal,
    normalized: normalizedConfidence.value,
    type: typeof newVal
  })
  updateCount.value++
}, { immediate: true })

// Chart rendered callback
const onChartRendered = () => {
  console.log('[MainGauge] Chart rendered with:', {
    score: normalizedScore.value,
    confidence: normalizedConfidence.value,
    updateCount: updateCount.value
  })
}

// 计算图表配置
const chartOption = computed(() => {
  const score = normalizedScore.value
  const confidence = normalizedConfidence.value

  console.log('[MainGauge] Updating chart with:', {
    score,
    confidence,
    updateCount: updateCount.value
  })

  return {
    backgroundColor: 'transparent',
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
              [0.1, '#FF3860'],   // 极度负面 (<0.1)
              [0.3, '#FF9F43'],   // 偏负面 (0.1-0.3)
              [0.5, '#FFD700'],   // 负面 (0.3-0.5)
              [0.7, '#90EE90'],   // 偏正面 (0.5-0.7)
              [0.9, '#39FF14'],   // 正面 (0.7-0.9)
              [1, '#00F0FF']      // 极度正面 (>0.9)
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
          fontSize: 12,
          distance: -55,
          formatter: function (value) {
            if (value === 0) return '中性'
            return ''  // 不显示极值标签
          }
        },
        title: {
          offsetCenter: [0, '-20%'],
          fontSize: 20,
          color: '#fff'
        },
        detail: {
          fontSize: 30,
          offsetCenter: [0, '20%'],
          valueAnimation: true,
          formatter: function (value) {
            const percentage = Math.round((value + 1) * 50)
            return percentage + '%'
          },
          color: 'inherit',
          rich: {
            value: {
              fontSize: 36,
              fontWeight: 'bold',
              padding: [10, 0]
            }
          }
        },
        data: [{
          value: score,  // 使用转换后的分数
          name: '情感得分'
        }]
      },
      {
        type: 'gauge',
        startAngle: 180,
        endAngle: 0,
        center: ['50%', '75%'],
        radius: '70%',
        min: -1,
        max: 1,
        itemStyle: {
          color: '#7B42FF'
        },
        progress: {
          show: true,
          width: 8,
          itemStyle: {
            color: '#7B42FF'
          }
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
          value: score,
          name: '进度'
        }]
      }
    ]
  }
})

// Add confidence gauge option
const confidenceChartOption = computed(() => {
  return {
    backgroundColor: 'transparent',
    series: [{
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      min: 0,
      max: 1,
      splitNumber: 2,
      axisLine: {
        lineStyle: {
          width: 4,
          color: [
            [0.3, '#FF3860'],  // 低置信度
            [0.7, '#FFD700'],  // 中等置信度
            [1, '#39FF14']     // 高置信度
          ]
        }
      },
      pointer: {
        itemStyle: {
          color: 'inherit'
        }
      },
      axisTick: {
        distance: -12,
        length: 4,
        lineStyle: {
          color: '#fff',
          width: 1
        }
      },
      splitLine: {
        distance: -12,
        length: 8,
        lineStyle: {
          color: '#fff',
          width: 2
        }
      },
      axisLabel: {
        color: '#fff',
        distance: 10,
        fontSize: 10,
        formatter: function (value) {
          if (value === 0) return '0'
          if (value === 0.5) return '0.5'  // 中间值不显示
          if (value === 1) return '1'
          return ''
        }
      },
      detail: {
        valueAnimation: true,
        formatter: '{value}',
        color: '#fff',
        fontSize: 12,
        offsetCenter: [0, '40%']
      },
      data: [{
        value: normalizedConfidence.value,
        name: ''
      }]
    }]
  }
})

// Add sentiment type computed property
const sentimentType = computed(() => {
  const score = props.score // 直接使用原始分数 (0-1范围)
  if (score >= 0.9) return '极度正面'
  if (score >= 0.7) return '正面'
  if (score >= 0.5) return '偏正面'
  if (score >= 0.3) return '负面'
  if (score >= 0.1) return '偏负面'
  return '极度负面'
})
</script>

<style scoped>
.h-64 {
  height: 16rem;
}
</style>