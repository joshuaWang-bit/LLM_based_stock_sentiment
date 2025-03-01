<script setup>
import { computed } from 'vue'

const props = defineProps({
  topicAnalysis: {
    type: Object,
    required: true
  }
})

const topics = {
  company_operation: {
    label: '公司经营',
    icon: '🏢',
    description: '公司运营、管理、战略等相关新闻'
  },
  financial_performance: {
    label: '财务表现',
    icon: '📊',
    description: '财务报告、业绩预告、盈利能力等信息'
  },
  market_competition: {
    label: '市场竞争',
    icon: '🔄',
    description: '市场地位、竞争优势、行业对比等信息'
  },
  product_technology: {
    label: '产品技术',
    icon: '🔧',
    description: '产品创新、技术突破、研发进展等信息'
  },
  industry_policy: {
    label: '行业政策',
    icon: '📜',
    description: '政策法规、行业规范、监管动态等信息'
  },
  capital_market: {
    label: '资本市场',
    icon: '💰',
    description: '股价表现、融资并购、股东变动等信息'
  }
}

const getSentimentClass = (score) => {
  if (score >= 0.7) return 'text-quantum'
  if (score >= 0.5) return 'text-primary'
  if (score >= 0.3) return 'text-sentiment-neutral'
  return 'text-sentiment-negative'
}

const topicList = computed(() => {
  return Object.entries(topics).map(([key, info]) => {
    const topicData = props.topicAnalysis[key] || {}
    return {
      key,
      ...info,
      score: topicData.score || 0,
      summary: topicData.summary || '',
      keyPoints: topicData.key_points || []
    }
  }).sort((a, b) => b.score - a.score) // 按得分降序排序
})
</script>

<template>
  <div class="space-y-4">
    <!-- 添加说明信息 -->
    <div class="p-4 rounded-lg backdrop-blur-sm bg-black/20 border border-primary/20">
      <h3 class="text-primary text-sm font-bold mb-2">主题分析说明</h3>
      <p class="text-xs text-gray-300 leading-5">
        主题分析将新闻按不同维度进行分类并分析，得分范围0-100%，得分越高表示该维度的新闻情感越积极。
        通过分析各个维度的得分，可以快速了解不同方面的市场反应。
      </p>
    </div>

    <!-- 图例说明 -->
    <div class="flex items-center justify-center space-x-6 text-xs text-gray-400 mb-2">
      <div class="flex items-center space-x-1">
        <span class="w-2 h-2 rounded-full bg-quantum"></span>
        <span>极度正面 (≥70%)</span>
      </div>
      <div class="flex items-center space-x-1">
        <span class="w-2 h-2 rounded-full bg-primary"></span>
        <span>正面 (≥50%)</span>
      </div>
      <div class="flex items-center space-x-1">
        <span class="w-2 h-2 rounded-full bg-sentiment-neutral"></span>
        <span>中性 (≥30%)</span>
      </div>
      <div class="flex items-center space-x-1">
        <span class="w-2 h-2 rounded-full bg-sentiment-negative"></span>
        <span>负面 (&lt;30%)</span>
      </div>
    </div>

    <!-- 主题列表 -->
    <div v-for="topic in topicList" :key="topic.key"
      class="p-4 rounded-lg backdrop-blur-sm bg-black/20 border border-white/5 hover:border-primary/20 transition-all">
      <div class="flex items-center justify-between mb-2">
        <div class="flex items-center space-x-2">
          <span class="text-xl">{{ topic.icon }}</span>
          <div>
            <span class="font-bold">{{ topic.label }}</span>
            <div class="text-xs text-gray-400">{{ topic.description }}</div>
          </div>
        </div>
        <div :class="getSentimentClass(topic.score)" class="text-sm font-mono">
          {{ (topic.score * 100).toFixed(0) }}%
        </div>
      </div>

      <div class="text-sm text-gray-300 mb-2">{{ topic.summary }}</div>

      <div v-if="topic.keyPoints.length > 0" class="space-y-1">
        <div v-for="(point, index) in topic.keyPoints" :key="index"
          class="text-xs text-gray-400 flex items-start space-x-2">
          <span class="text-primary">•</span>
          <span>{{ point }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bg-quantum {
  background-color: #39FF14;
}

.bg-primary {
  background-color: #00F0FF;
}

.bg-sentiment-neutral {
  background-color: #FFD700;
}

.bg-sentiment-negative {
  background-color: #FF3860;
}
</style>