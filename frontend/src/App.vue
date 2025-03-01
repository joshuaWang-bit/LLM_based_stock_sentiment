<script setup>
import { ref, computed } from 'vue'
import { Search, Refresh, Setting, Close, Monitor, InfoFilled } from '@element-plus/icons-vue'
import { useStockStore } from './stores/stockStore'
import MainGauge from './components/SentimentDashboard/MainGauge.vue'
import TrendAnalysis from './components/TrendAnalysis/TrendAnalysis.vue'
import TopicAnalysis from './components/TopicAnalysis/TopicAnalysis.vue'

// 状态
const searchQuery = ref('')
const store = useStockStore()
const showDebugInfo = ref(false)
const showDetails = ref(false)
const showTrendDetails = ref(false)
const showTopicDetails = ref(false)

// Debug computed properties
const debugInfo = computed(() => ({
  currentStock: store.currentStock,
  storeDebugState: store.debugState,
  sentimentScore: store.sentimentScore,
  confidenceIndex: store.confidenceIndex,
  lastUpdated: store.lastUpdated,
  hasError: !!store.error,
  error: store.error
}))

// 计算属性
const sentimentScore = computed(() => {
  const score = store.sentimentScore
  console.log('[App] Computing sentiment score:', score)
  return score
})

const confidenceIndex = computed(() => {
  const confidence = store.confidenceIndex
  console.log('[App] Computing confidence index:', confidence)
  return confidence
})

const sentimentType = computed(() => {
  const score = sentimentScore.value
  console.log('[App] Computing sentiment type for score:', score)
  if (score >= 0.9) return 'success'
  if (score >= 0.7) return 'success'
  if (score >= 0.5) return ''
  if (score >= 0.3) return 'warning'
  if (score >= 0.1) return 'warning'
  return 'danger'
})

const sentimentLabel = computed(() => {
  const score = store.analysisData?.analysis_summary?.overall_score || 0
  if (score >= 0.9) return '极度正面'
  if (score >= 0.7) return '正面'
  if (score >= 0.5) return '偏正面'
  if (score >= 0.3) return '负面'
  if (score >= 0.1) return '偏负面'
  return '极度负面'
})

const marketExpectationColor = computed(() => {
  const score = store.analysisData?.analysis_summary?.market_expectation || 0
  if (score > 50) return 'text-quantum'
  if (score > 0) return 'text-primary'
  if (score > -50) return 'text-sentiment-neutral'
  return 'text-sentiment-negative'
})

const investorSentimentColor = computed(() => {
  const score = store.analysisData?.analysis_summary?.investor_sentiment || 0
  if (score > 75) return 'text-quantum'
  if (score > 50) return 'text-primary'
  if (score > 25) return 'text-sentiment-neutral'
  return 'text-sentiment-negative'
})

// 趋势分析数据
const timeAnalysis = computed(() => store.analysisData?.time_analysis || {})

// 主题分析数据
const topicAnalysis = computed(() => store.analysisData?.topic_analysis || {})

// 方法
const handleSearch = async (query, cb) => {
  console.log('[App] Search triggered:', query)
  if (query.length < 2) {
    console.log('[App] Query too short, skipping')
    cb([])
    return
  }
  await store.searchStocks(query)
  console.log('[App] Search completed, results:', store.searchResults)
  cb(store.searchResults)
}

const handleSelect = async (item) => {
  console.log('[App] Stock selected:', item)
  store.setCurrentStock(item)
  console.log('[App] Fetching analysis...')
  await store.getStockAnalysis(item.code)
  console.log('[App] Analysis completed:', {
    hasData: !!store.analysisData,
    score: store.sentimentScore,
    confidence: store.confidenceIndex,
    debugState: store.debugState
  })
}

const refreshData = () => {
  if (store.currentStock) {
    store.getStockAnalysis(store.currentStock.code)
  }
}

const formatMarketExpectation = () => {
  const score = store.analysisData?.analysis_summary?.market_expectation
  console.log('[App] Formatting market expectation:', score)
  if (score === undefined || score === null) return '0'
  return `${score > 0 ? '+' : ''}${score}`
}

const formatInvestorSentiment = () => {
  const score = store.analysisData?.analysis_summary?.investor_sentiment
  console.log('[App] Formatting investor sentiment:', score)
  if (score === undefined || score === null) return '0 分'
  return `${score} 分`
}
</script>

<template>
  <div class="flex flex-col min-h-screen bg-background text-white">
    <!-- Debug Info -->
    <div v-if="showDebugInfo"
      class="fixed bottom-4 right-4 p-4 bg-black/50 text-xs text-white rounded-lg max-w-md z-50 overflow-auto max-h-96">
      <div class="flex justify-between items-center mb-2">
        <div class="font-bold">Debug Information</div>
        <el-button type="info" size="small" circle @click="showDebugInfo = false">
          <el-icon>
            <Close />
          </el-icon>
        </el-button>
      </div>
      <pre>{{ JSON.stringify(debugInfo, null, 2) }}</pre>
    </div>

    <!-- Debug Toggle Button -->
    <div v-else class="fixed bottom-4 right-4 z-50">
      <el-button type="info" circle @click="showDebugInfo = true">
        <el-icon>
          <Monitor />
        </el-icon>
      </el-button>
    </div>

    <!-- 顶部导航栏 -->
    <header class="card fixed top-0 left-0 right-0 z-50 px-6 py-4 flex items-center justify-between">
      <div class="text-2xl font-bold text-primary glow">
        股票情感分析
      </div>
      <div class="flex items-center space-x-4">
        <el-button type="primary" :icon="Refresh" circle @click="refreshData" :loading="store.loading" />
        <el-button type="info" :icon="Setting" circle />
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="pt-20 px-6">
      <!-- 搜索区域 -->
      <div class="card p-6 mb-6">
        <el-autocomplete v-model="searchQuery" :fetch-suggestions="handleSearch" placeholder="输入股票名称或代码" class="w-full"
          :prefix-icon="Search" :loading="store.loading" @select="handleSelect">
          <template #default="{ item }">
            <div class="flex justify-between">
              <span>{{ item.name }}</span>
              <span class="text-gray-400">{{ item.code }}</span>
            </div>
          </template>
        </el-autocomplete>
      </div>

      <!-- 错误提示 -->
      <el-alert v-if="store.error" :title="store.error" type="error" class="mb-6" show-icon closable />

      <!-- 数据展示区域 -->
      <div v-if="store.currentStock" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- 主情感仪表盘 -->
        <div class="card p-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-bold">情感分析</h2>
            <div class="flex items-center gap-2">
              <el-button v-if="!showDetails" type="info" size="small" @click="showDetails = true">
                查看详情
              </el-button>
              <el-tag :type="sentimentType" effect="dark" class="glow">
                {{ sentimentLabel }}
              </el-tag>
            </div>
          </div>
          <div v-if="store.loading" class="flex justify-center items-center h-64">
            <el-loading />
          </div>
          <template v-else>
            <MainGauge :score="sentimentScore" :confidence="confidenceIndex" :show-details="showDetails"
              @close-details="showDetails = false" />
            <div class="mt-4 grid grid-cols-2 gap-4">
              <div class="text-center">
                <div class="text-xs text-gray-400">市场预期</div>
                <div class="text-sm font-bold" :class="marketExpectationColor">
                  {{ formatMarketExpectation() }}
                </div>
              </div>
              <div class="text-center">
                <div class="text-xs text-gray-400">投资者情绪</div>
                <div class="text-sm font-bold" :class="investorSentimentColor">
                  {{ formatInvestorSentiment() }}
                </div>
              </div>
            </div>
            <!-- 分析摘要 -->
            <div v-if="store.analysisData?.analysis_summary?.summary" class="mt-4">
              <div class="text-xs text-gray-400 mb-1">分析摘要</div>
              <div class="text-[11px] leading-5 text-red-400/80 backdrop-blur-sm bg-black/20 p-3 rounded-lg">
                {{ store.analysisData.analysis_summary.summary }}
              </div>
            </div>
          </template>
        </div>

        <!-- 趋势分析 -->
        <div class="card p-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-bold">趋势分析</h2>
            <div class="flex items-center gap-2">
              <el-button v-if="!showTrendDetails" type="info" size="small" @click="showTrendDetails = true">
                查看详情
              </el-button>
            </div>
          </div>
          <div v-if="store.loading" class="flex justify-center items-center h-64">
            <el-loading />
          </div>
          <template v-else>
            <TrendAnalysis :time-analysis="timeAnalysis" />
          </template>
        </div>

        <!-- 主题分析 -->
        <div class="card p-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-bold">主题分析</h2>
            <el-button v-if="!showTopicDetails" type="info" size="small" @click="showTopicDetails = true">
              查看详情
            </el-button>
          </div>
          <div v-if="store.loading" class="flex justify-center items-center h-64">
            <el-loading />
          </div>
          <template v-else>
            <TopicAnalysis :topic-analysis="topicAnalysis" :show-details="showTopicDetails"
              @close-details="showTopicDetails = false" />
          </template>
        </div>
      </div>

      <!-- 欢迎页面 -->
      <div v-else class="card p-6 text-center">
        <el-empty description="请搜索股票开始分析" />
      </div>
    </main>

    <!-- Details Button -->
    <div v-if="store.currentStock" class="absolute top-4 left-4">
      <el-button type="primary" size="small" class="!bg-quantum/20 hover:!bg-quantum/30 backdrop-blur-sm"
        @click="showDetails = !showDetails">
        <el-icon class="mr-1">
          <InfoFilled />
        </el-icon>
        查看详情
      </el-button>
    </div>

    <!-- Debug Info Toggle -->
    <!-- <div class="absolute bottom-4 right-4">
      <el-button type="info" size="small" circle class="!bg-black/20 hover:!bg-black/30 backdrop-blur-sm"
        @click="showDebugInfo = !showDebugInfo">
        <el-icon>
          <Monitor />
        </el-icon>
      </el-button>
    </div> -->

    <!-- Debug Info Panel -->
    <!-- <div v-if="showDebugInfo" class="absolute bottom-16 right-4 max-w-md">
      <div class="backdrop-blur-sm bg-black/20 rounded-lg p-3">
        <div class="flex justify-between items-center mb-2">
          <div class="text-xs text-gray-400 font-medium">调试信息</div>
          <el-button type="info" size="small" circle @click="showDebugInfo = false">
            <el-icon>
              <Close />
            </el-icon>
          </el-button>
        </div>
        <pre class="text-[11px] text-gray-400 whitespace-pre-wrap">{{ JSON.stringify(debugInfo, null, 2) }}</pre>
      </div>
    </div> -->
  </div>
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}

.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}

.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
