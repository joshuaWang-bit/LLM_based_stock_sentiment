<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  topicAnalysis: {
    type: Object,
    required: true
  }
})

const chartRef = ref(null)
let chart = null

// 处理主题数据
const processTopicData = () => {
  const topics = {
    company_operation: '公司经营',
    financial_performance: '财务表现',
    market_competition: '市场竞争',
    product_technology: '产品技术',
    industry_policy: '行业政策',
    capital_market: '资本市场'
  }

  const data = []
  const indicators = []

  Object.entries(topics).forEach(([key, label]) => {
    const score = props.topicAnalysis[key]?.score || 0
    data.push(score)
    indicators.push({ name: label, max: 1 })
  })

  return { data, indicators }
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return

  chart = echarts.init(chartRef.value)
  updateChart()
}

// 更新图表
const updateChart = () => {
  if (!chart) return

  const { data, indicators } = processTopicData()

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const value = (params.value || 0) * 100;
        return `${params.name}: ${value.toFixed(0)}%<br/>
                <span style="color: rgba(255,255,255,0.6); font-size: 12px;">
                得分越高表示该维度的新闻情感越积极</span>`;
      },
      backgroundColor: 'rgba(0,0,0,0.8)',
      borderColor: '#00F0FF',
      textStyle: {
        color: '#fff'
      }
    },
    radar: {
      indicator: indicators,
      shape: 'polygon',
      splitNumber: 4,
      name: {
        textStyle: {
          color: '#00F0FF'
        }
      },
      center: ['50%', '55%'],  // 把雷达图往下移一点
      radius: '65%',  // 调整雷达图大小
      axisName: {
        color: '#00F0FF',
        fontSize: 12,
        formatter: (name, indicator) => {
          // 为公司经营添加标题
          const score = data[indicators.findIndex(i => i.name === name)] || 0;
          if (name === '公司经营') {
            return `{title|主题维度分析}\n{subtitle|各维度得分范围：0-100%}\n\n${name}\n{score|${(score * 100).toFixed(0)}%}`;
          }
          return `${name}\n{score|${(score * 100).toFixed(0)}%}`;
        },
        rich: {
          score: {
            color: 'rgba(255,255,255,0.7)',
            fontSize: 10,
            padding: [2, 0, 0, 0]
          },
          title: {
            color: '#00F0FF',
            fontSize: 16,
            fontWeight: 'bold',
            padding: [0, 0, 4, 0]
          },
          subtitle: {
            color: 'rgba(255,255,255,0.5)',
            fontSize: 12,
            padding: [4, 0, 0, 0]
          }
        }
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(0, 240, 255, 0.1)'
        }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(0, 240, 255, 0.02)', 'rgba(0, 240, 255, 0.05)']
        }
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(0, 240, 255, 0.2)'
        }
      }
    },
    series: [{
      type: 'radar',
      data: [{
        value: data,
        name: '主题情感分析',
        symbol: 'none',
        lineStyle: {
          width: 2,
          color: '#7B42FF'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
            offset: 0,
            color: 'rgba(123, 66, 255, 0.5)'
          }, {
            offset: 1,
            color: 'rgba(123, 66, 255, 0.1)'
          }])
        }
      }]
    }]
  }

  chart.setOption(option)
}

// 监听数据变化
watch(() => props.topicAnalysis, () => {
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

// 组件卸载时清理
const onBeforeUnmount = () => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
}
</script>

<template>
  <div ref="chartRef" class="w-full h-[300px]"></div>
</template>