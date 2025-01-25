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
    <v-chart class="h-full w-full" :option="chartOption" :autoresize="true" @rendered="onChartRendered" />
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
  // 后端返回的分数已经是 -1 到 1 的范围，不需要转换
  const normalizedValue = isNaN(value) ? 0 : value
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
          formatter: function (value) {
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
          formatter: function (value) {
            // 将 -1 到 1 的范围转换为百分比显示
            const percentage = Math.round((value + 1) * 50)
            return percentage + '%'
          },
          color: 'inherit'
        },
        data: [{
          value: score,
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
          value: confidence * 100,
          name: '置信度'
        }]
      }
    ]
  }
})
</script>

<style scoped>
.h-64 {
  height: 16rem;
}
</style>