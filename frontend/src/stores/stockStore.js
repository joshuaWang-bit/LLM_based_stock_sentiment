import { defineStore } from "pinia";
import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api";

export const useStockStore = defineStore("stock", {
  state: () => ({
    searchResults: [],
    currentStock: null,
    analysisData: null,
    loading: false,
    error: null,
    lastUpdated: null,
  }),

  getters: {
    sentimentScore: (state) => {
      console.log("[Store/Getter] Raw analysis data:", state.analysisData);
      if (!state.analysisData?.analysis_summary?.overall_score) {
        console.warn("[Store/Getter] No sentiment score available");
        return 0;
      }
      const score = Number(state.analysisData.analysis_summary.overall_score);
      console.log("[Store/Getter] Processed sentiment score:", score);
      return score;
    },

    confidenceIndex: (state) => {
      if (!state.analysisData?.analysis_summary?.confidence_index) {
        console.warn("[Store/Getter] No confidence index available");
        return 0;
      }
      const confidence = Number(
        state.analysisData.analysis_summary.confidence_index
      );
      console.log("[Store/Getter] Processed confidence index:", confidence);
      return confidence;
    },

    // 添加一个用于调试的getter
    debugState: (state) => {
      return {
        hasCurrentStock: !!state.currentStock,
        hasAnalysisData: !!state.analysisData,
        analysisDataStructure: state.analysisData
          ? Object.keys(state.analysisData)
          : [],
        analysisSummary: state.analysisData?.analysis_summary || null,
      };
    },
  },

  actions: {
    // 搜索股票
    async searchStocks(query) {
      console.log("[Store/Action] Starting stock search:", query);
      if (!query) {
        this.searchResults = [];
        return;
      }

      try {
        this.loading = true;
        const response = await axios.get(
          `${API_BASE_URL}/stocks/search?query=${encodeURIComponent(query)}`
        );
        console.log("[Store/Action] Search API response:", response.data);
        this.searchResults = response.data;
        this.error = null;
      } catch (error) {
        console.error("[Store/Action] Search failed:", error);
        this.error = "搜索股票失败";
      } finally {
        this.loading = false;
      }
    },

    // 获取股票分析数据
    async getStockAnalysis(stockCode) {
      console.log("[Store/Action] Starting analysis fetch for:", stockCode);
      try {
        this.loading = true;
        const response = await axios.get(
          `${API_BASE_URL}/stock-analysis/${stockCode}`
        );
        console.log("[Store/Action] Analysis API response:", response.data);

        // 验证数据结构
        if (!response.data?.analysis_summary) {
          console.error(
            "[Store/Action] Invalid data structure:",
            response.data
          );
          throw new Error("Invalid analysis data structure");
        }

        // 数据预处理
        const processedData = {
          ...response.data,
          analysis_summary: {
            ...response.data.analysis_summary,
            overall_score: Number(response.data.analysis_summary.overall_score),
            confidence_index: Number(
              response.data.analysis_summary.confidence_index
            ),
          },
        };

        console.log("[Store/Action] Processed analysis data:", processedData);

        this.analysisData = processedData;
        this.lastUpdated = new Date().toISOString();
        this.error = null;

        // 验证getter的值
        console.log("[Store/Action] Verifying getters after update:", {
          score: this.sentimentScore,
          confidence: this.confidenceIndex,
        });
      } catch (error) {
        console.error("[Store/Action] Analysis failed:", error);
        this.error = "获取分析数据失败";
        this.analysisData = null;
      } finally {
        this.loading = false;
      }
    },

    // 设置当前股票
    setCurrentStock(stock) {
      console.log("[Store/Action] Setting current stock:", stock);
      this.currentStock = stock;
    },

    // 清除数据
    clearData() {
      console.log("[Store/Action] Clearing all data");
      this.searchResults = [];
      this.currentStock = null;
      this.analysisData = null;
      this.error = null;
      this.lastUpdated = null;
    },
  },
});
