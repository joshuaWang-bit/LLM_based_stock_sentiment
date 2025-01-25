import json
from pathlib import Path
from datetime import datetime, timedelta
import akshare as ak
from typing import List, Dict, Optional


class NewsCrawler:
    """新闻爬取类"""

    def __init__(self):
        """初始化新闻爬取器"""
        self.cache_dir = Path(
            __file__).parent.parent.parent / 'data' / 'news_cache'
        # 确保缓存目录存在
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, stock_code: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{stock_code}_news.json"

    def _load_cache(self, stock_code: str) -> Optional[List[Dict]]:
        """加载缓存的新闻数据"""
        try:
            cache_path = self._get_cache_path(stock_code)
            if not cache_path.exists():
                return None

            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                cache_date = datetime.strptime(cache_data['date'], '%Y-%m-%d')
                if cache_date.date() == datetime.now().date():
                    return cache_data['news']
        except Exception as e:
            print(f"读取新闻缓存出错: {e}")
        return None

    def _save_cache(self, stock_code: str, news_list: List[Dict]):
        """保存新闻数据到缓存"""
        try:
            # 确保缓存目录存在
            self.cache_dir.mkdir(parents=True, exist_ok=True)

            cache_data = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'news': news_list
            }

            cache_path = self._get_cache_path(stock_code)
            # 确保父目录存在
            cache_path.parent.mkdir(parents=True, exist_ok=True)

            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存新闻缓存出错: {e}")

    def get_stock_news(self, stock_code: str, days: int = 7, max_count: int = 20) -> List[Dict]:
        """获取股票新闻

        Args:
            stock_code: 股票代码
            days: 获取最近几天的新闻
            max_count: 最大新闻条数

        Returns:
            List[Dict]: 新闻列表
        """
        # 尝试从缓存加载
        cached_news = self._load_cache(stock_code)
        if cached_news is not None:
            print("使用缓存数据，共{}条新闻".format(len(cached_news)))
            return cached_news[:max_count]

        try:
            # 获取新闻数据
            df = ak.stock_news_em(symbol=stock_code)

            # 转换为列表
            news_list = []
            for _, row in df.iterrows():
                news_list.append({
                    'title': row['新闻标题'],
                    'content': row['新闻内容'],
                    'source': row['新闻来源'],
                    'publish_time': row['发布时间']
                })

            print(f"成功获取到{len(news_list)}条新闻")

            # 保存到缓存
            self._save_cache(stock_code, news_list)

            return news_list[:max_count]

        except Exception as e:
            print(f"获取新闻出错: {e}")
            return []
