import os
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import akshare as ak
from backend.utils.config import Config
from collections import defaultdict


class NewsCrawler:
    """新闻爬虫类"""

    def __init__(self):
        """初始化新闻爬虫"""
        self.cache_dir = Config.NEWS_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, stock_code: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{stock_code}.json"

    def _load_cache(self, stock_code: str) -> Optional[Dict]:
        """加载缓存的新闻数据"""
        try:
            cache_path = self._get_cache_path(stock_code)
            if not cache_path.exists():
                return None

            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # 检查缓存是否过期
            cache_date = datetime.strptime(cache_data['date'], '%Y-%m-%d')
            if (datetime.now() - cache_date).days <= Config.CACHE_VALID_DAYS:
                return cache_data
        except Exception as e:
            print(f"读取新闻缓存出错: {e}")
        return None

    def _save_cache(self, stock_code: str, news_list: List[Dict]):
        """保存新闻数据到缓存"""
        try:
            cache_data = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'news': news_list
            }
            with open(self._get_cache_path(stock_code), 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存新闻缓存出错: {e}")

    def get_stock_news(
        self,
        stock_code: str,
        days: int = Config.DEFAULT_DAYS,
        max_news: int = Config.MAX_NEWS_PER_STOCK
    ) -> List[Dict]:
        """获取股票新闻

        Args:
            stock_code: 股票代码
            days: 获取有新闻的天数（默认7天）
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
            # 对缓存的新闻进行日期分组处理
            date_grouped_news = self._group_news_by_date(news_list)
            if len(date_grouped_news) >= days:  # 只有缓存的日期数满足要求才使用缓存
                print(f"使用缓存数据，共{len(date_grouped_news)}个日期的新闻")
                return self._process_grouped_news(date_grouped_news, days)
            else:
                print(f"缓存数据日期数({len(date_grouped_news)})不足，需要重新获取")

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
            for _, row in news_df.iterrows():
                try:
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

                except Exception as e:
                    print(f"处理新闻出错: {e}")
                    continue

            # 按时间排序
            news_list.sort(key=lambda x: x['publish_time'], reverse=True)

            # 按日期分组并处理
            date_grouped_news = self._group_news_by_date(news_list)
            processed_news = self._process_grouped_news(
                date_grouped_news, days)

            # 保存缓存
            self._save_cache(stock_code, processed_news)

            return processed_news

        except Exception as e:
            print(f"爬取新闻出错: {e}")
            return []

    def _group_news_by_date(self, news_list: List[Dict]) -> Dict[str, List[Dict]]:
        """将新闻按日期分组"""
        date_grouped_news = defaultdict(list)
        for news in news_list:
            date = news['publish_time'].split()[0]  # 提取日期部分
            date_grouped_news[date].append(news)
        return dict(date_grouped_news)

    def _process_grouped_news(self, date_grouped_news: Dict[str, List[Dict]], required_days: int) -> List[Dict]:
        """处理分组后的新闻数据"""
        # 按日期排序
        sorted_dates = sorted(date_grouped_news.keys(), reverse=True)

        # 获取指定天数的新闻
        processed_news = []
        days_count = 0

        for date in sorted_dates:
            if days_count >= required_days:
                break

            # 对每天的新闻按时间排序并限制数量
            day_news = sorted(date_grouped_news[date],
                              key=lambda x: x['publish_time'],
                              reverse=True)

            # 每天最多取5条新闻
            day_news = day_news[:5]
            processed_news.extend(day_news)
            days_count += 1

        return processed_news
