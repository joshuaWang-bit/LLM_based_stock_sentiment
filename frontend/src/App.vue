<script setup>
import { ref, computed } from 'vue'
import { Search, Refresh, Setting } from '@element-plus/icons-vue'
import { useStockStore } from './stores/stockStore'
import MainGauge from './components/SentimentDashboard/MainGauge.vue'

// 状态
const searchQuery = ref('')
const store = useStockStore()

// 计算属性
const sentimentType = computed(() => {
  const score = store.analysisData?.overall_sentiment?.score || 0
  if (score > 0.5) return 'success'
  if (score > 0) return ''
  if (score > -0.5) return 'warning'
  return 'danger'
})

const sentimentLabel = computed(() => {
  const score = store.analysisData?.overall_sentiment?.score || 0
  if (score > 0.5) return '极度正面'
  if (score > 0) return '偏正面'
  if (score > -0.5) return '偏负面'
  return '极度负面'
})

const marketExpectationColor = computed(() => {
  const score = store.analysisData?.overall_sentiment?.market_expectation_strength || 0
  if (score > 50) return 'text-quantum'
  if (score > 0) return 'text-primary'
  if (score > -50) return 'text-sentiment-neutral'
  return 'text-sentiment-negative'
})

const investorSentimentColor = computed(() => {
  const score = store.analysisData?.overall_sentiment?.investor_sentiment || 0
  if (score > 75) return 'text-quantum'
  if (score > 50) return 'text-primary'
  if (score > 25) return 'text-sentiment-neutral'
  return 'text-sentiment-negative'
})

// 方法
const handleSearch = async (query, cb) => {
  if (query.length < 2) {
    cb([])
    return
  }
  await store.searchStocks(query)
  cb(store.searchResults)
}

const handleSelect = (item) => {
  store.setCurrentStock(item)
  store.getStockAnalysis(item.code)
}

const refreshData = () => {
  if (store.currentStock) {
    store.getStockAnalysis(store.currentStock.code)
  }
}

const formatMarketExpectation = (value) => {
  if (!value) return '0%'
  return `${value > 0 ? '+' : ''}${value}%`
}

const formatInvestorSentiment = (value) => {
  if (!value) return '0%'
  return `${value}%`
}
</script>

<template>
  <div class="min-h-screen">
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
        <el-autocomplete
          v-model="searchQuery"
          :fetch-suggestions="handleSearch"
          placeholder="输入股票名称或代码"
          class="w-full"
          :prefix-icon="Search"
          :loading="store.loading"
          @select="handleSelect"
        >
          <template #default="{ item }">
            <div class="flex justify-between">
              <span>{{ item.name }}</span>
              <span class="text-gray-400">{{ item.code }}</span>
            </div>
          </template>
        </el-autocomplete>
      </div>

      <!-- 错误提示 -->
      <el-alert
        v-if="store.error"
        :title="store.error"
        type="error"
        class="mb-6"
        show-icon
        closable
      />

      <!-- 数据展示区域 -->
      <div v-if="store.currentStock" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- 主情感仪表盘 -->
        <div class="card p-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-bold">情感分析</h2>
            <el-tag :type="sentimentType" effect="dark" class="glow">
              {{ sentimentLabel }}
            </el-tag>
          </div>
          <div v-if="store.loading" class="flex justify-center items-center h-64">
            <el-loading />
          </div>
          <template v-else>
            <MainGauge
              :score="store.analysisData?.overall_sentiment?.score || 0"
              :confidence="store.analysisData?.overall_sentiment?.confidence_index || 0"
            />
            <div class="mt-4 grid grid-cols-2 gap-4">
              <div class="text-center">
                <div class="text-sm text-gray-400">市场预期</div>
                <div class="text-lg font-bold" :class="marketExpectationColor">
                  {{ formatMarketExpectation(store.analysisData?.overall_sentiment?.market_expectation_strength) }}
                </div>
              </div>
              <div class="text-center">
                <div class="text-sm text-gray-400">投资者情绪</div>
                <div class="text-lg font-bold" :class="investorSentimentColor">
                  {{ formatInvestorSentiment(store.analysisData?.overall_sentiment?.investor_sentiment) }}
                </div>
              </div>
            </div>
          </template>
        </div>

        <!-- 时间趋势图 -->
        <div class="card p-6">
          <h2 class="text-xl font-bold mb-4">趋势分析</h2>
          <div v-if="store.loading" class="flex justify-center items-center h-64">
            <el-loading />
          </div>
          <!-- 这里将添加趋势图表组件 -->
        </div>

        <!-- 主题分析 -->
        <div class="card p-6">
          <h2 class="text-xl font-bold mb-4">主题分析</h2>
          <div v-if="store.loading" class="flex justify-center items-center h-64">
            <el-loading />
          </div>
          <!-- 这里将添加主题分析组件 -->
        </div>
      </div>

      <!-- 欢迎页面 -->
      <div v-else class="card p-6 text-center">
        <el-empty description="请搜索股票开始分析" />
      </div>
    </main>
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
