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
  }),

  actions: {
    // 搜索股票
    async searchStocks(query) {
      if (!query) {
        this.searchResults = [];
        return;
      }

      try {
        this.loading = true;
        const response = await axios.get(
          `${API_BASE_URL}/stocks/search?query=${encodeURIComponent(query)}`
        );
        this.searchResults = response.data;
        this.error = null;
      } catch (error) {
        this.error = "搜索股票失败";
        console.error("Search error:", error);
      } finally {
        this.loading = false;
      }
    },

    // 获取股票分析数据
    async getStockAnalysis(stockCode) {
      try {
        this.loading = true;
        const response = await axios.get(
          `${API_BASE_URL}/stock-analysis/${stockCode}`
        );
        this.analysisData = response.data;
        this.error = null;
      } catch (error) {
        this.error = "获取分析数据失败";
        console.error("Analysis error:", error);
      } finally {
        this.loading = false;
      }
    },

    // 设置当前股票
    setCurrentStock(stock) {
      this.currentStock = stock;
    },

    // 清除数据
    clearData() {
      this.searchResults = [];
      this.currentStock = null;
      this.analysisData = null;
      this.error = null;
    },
  },
});
