import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import akshare as ak
import pandas as pd
from typing import List, Dict, Optional


class NewsCrawler:
    """新闻爬取类"""

    def __init__(self):
        """初始化新闻爬取器"""
        self.cache_dir = Path(
            __file__).parent.parent.parent / 'data' / 'news_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, stock_code: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{stock_code}_news.json"

    def _load_cache(self, stock_code: str) -> Optional[Dict]:
        """加载缓存数据"""
        cache_path = self._get_cache_path(stock_code)
        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                cache_date = datetime.strptime(cache_data['date'], '%Y-%m-%d')
                if cache_date.date() == datetime.now().date():
                    return cache_data
        except Exception as e:
            print(f"读取缓存出错: {e}")
        return None

    def _save_cache(self, stock_code: str, news_list: List[Dict]):
        """保存缓存数据"""
        try:
            cache_data = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'news': news_list
            }
            with open(self._get_cache_path(stock_code), 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存缓存出错: {e}")

    def get_stock_news(self, stock_code: str, days: int = 7, max_news: int = 20) -> List[Dict]:
        """获取股票新闻

        Args:
            stock_code: 股票代码
            days: 获取最近几天的新闻
            max_news: 最大新闻条数

        Returns:
            List[Dict]: 新闻列表，每条新闻包含:
                - title: 标题
                - content: 内容
                - publish_time: 发布时间
                - source: 来源
                - url: 链接
        """
        # 尝试加载缓存
        cache_data = self._load_cache(stock_code)
        if cache_data:
            news_list = cache_data['news']
            print(f"使用缓存数据，共{len(news_list)}条新闻")
            return news_list[:max_news]

        try:
            # 设置pandas显示选项
            pd.set_option('display.max_columns', None)
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_colwidth', None)

            # 获取新闻数据
            news_df = ak.stock_news_em(symbol=stock_code)
            if news_df is None or len(news_df) == 0:
                print(f"未获取到{stock_code}的新闻数据")
                return []

            print(f"成功获取到{len(news_df)}条新闻")

            # 处理新闻数据
            news_list = []
            cutoff_date = datetime.now() - timedelta(days=days)

            for _, row in news_df.iterrows():
                try:
                    # 检查发布时间
                    publish_time = datetime.strptime(
                        row['发布时间'], '%Y-%m-%d %H:%M:%S')
                    if publish_time < cutoff_date:
                        continue

                    # 获取新闻内容
                    content = row['新闻内容'] if '新闻内容' in row and not pd.isna(
                        row['新闻内容']) else ''
                    if not content:
                        content = row['新闻标题']

                    content = content.strip()
                    if len(content) < 10:  # 内容太短的跳过
                        continue

                    # 构建新闻项
                    news_item = {
                        'title': row['新闻标题'].strip(),
                        'content': content,
                        'publish_time': row['发布时间'],
                        'source': row['文章来源'].strip(),
                        'url': row['新闻链接'].strip()
                    }
                    news_list.append(news_item)

                    if len(news_list) >= max_news:
                        break

                except Exception as e:
                    print(f"处理新闻出错: {e}")
                    continue

            # 按时间排序
            news_list.sort(key=lambda x: x['publish_time'], reverse=True)

            # 保存缓存
            self._save_cache(stock_code, news_list)

            return news_list

        except Exception as e:
            print(f"爬取新闻出错: {e}")
            return []
