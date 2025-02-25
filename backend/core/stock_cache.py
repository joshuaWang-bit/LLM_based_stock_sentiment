import os
import json
from pathlib import Path
from typing import Dict, Optional, List
from utils.config import Config


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.stock_info = None


class StockCache:
    """股票数据缓存类"""

    def __init__(self):
        """初始化股票数据缓存"""
        self.cache_dir = Config.STOCKS_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "stocks.json"
        self.root = TrieNode()
        self.stocks_data = self._load_all_stocks()
        self._build_trie()

    def _load_all_stocks(self) -> Dict:
        """加载所有股票数据
        
        Returns:
            Dict: 所有股票数据的字典，如果文件不存在则返回空字典
        """
        if not self.cache_file.exists():
            return {'stocks': []}

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"读取股票数据缓存出错: {e}")
            return {'stocks': []}

    def _save_all_stocks(self):
        """保存所有股票数据到缓存文件"""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.stocks_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存股票数据缓存出错: {e}")

    def _build_trie(self):
        """构建前缀树"""
        for stock in self.stocks_data.get('stocks', []):
            code = stock['code']
            current = self.root
            for char in code:
                if char not in current.children:
                    current.children[char] = TrieNode()
                current = current.children[char]
            current.is_end = True
            current.stock_info = stock

    def _search_in_trie(self, code: str) -> Optional[Dict]:
        """在前缀树中搜索股票
        
        Args:
            code: 股票代码

        Returns:
            Optional[Dict]: 股票信息，如果未找到则返回None
        """
        current = self.root
        for char in code:
            if char not in current.children:
                return None
            current = current.children[char]
        return current.stock_info if current.is_end else None

    def get_stocks(self, query: str, fetch_func) -> Dict:
        """获取股票数据，优先从前缀树获取
        
        Args:
            query: 搜索关键词
            fetch_func: 获取股票数据的函数，当缓存不存在时调用

        Returns:
            Dict: 股票数据
        """
        # 如果是完整的股票代码，先在前缀树中查找
        if query.isdigit() and len(query) == 6:
            result = self._search_in_trie(query)
            if result:
                return {'stocks': [result]}

        # 如果前缀树中未找到或者不是完整代码，则调用fetch_func
        new_data = fetch_func(query)
        if new_data.get('stocks'):
            # 更新缓存和前缀树
            for stock in new_data['stocks']:
                if not self._search_in_trie(stock['code']):
                    self.stocks_data['stocks'].append(stock)
                    current = self.root
                    for char in stock['code']:
                        if char not in current.children:
                            current.children[char] = TrieNode()
                        current = current.children[char]
                    current.is_end = True
                    current.stock_info = stock
            self._save_all_stocks()
        return new_data

    def update_stocks(self, stocks_data: Dict):
        """更新股票数据缓存
        
        Args:
            stocks_data: 新的股票数据
        """
        self.stocks_data = stocks_data
        self.root = TrieNode()
        self._build_trie()
        self._save_all_stocks()