import streamlit as st
import requests
import pandas as pd

# 需要确保中文字体支持（在系统或代码中配置）
# 基本配置
BACKEND_URL = "http://localhost:8000"  # 根据实际后端地址修改
st.set_page_config(page_title="股票舆情分析系统", layout="wide")

# 初始化session状态
if "stock_options" not in st.session_state:
    st.session_state.stock_options = []
if "selected_stock" not in st.session_state:
    st.session_state.selected_stock = None
if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None


def search_stocks(query: str):
    """调用后端搜索股票接口"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/stocks/search",
            params={"query": query}
        )
        response.raise_for_status()
        st.session_state.stock_options = response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"搜索股票失败: {str(e)}")
        st.session_state.stock_options = []


def analyze_stock(stock_code: str):
    """调用股票分析接口"""
    try:
        with st.spinner("正在分析，请稍候..."):
            response = requests.get(
                f"{BACKEND_URL}/api/stock-analysis/{stock_code}"
            )
            response.raise_for_status()
            st.session_state.analysis_data = response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"分析失败: {e.response.json().get('detail', '未知错误')}")
    except requests.exceptions.RequestException as e:
        st.error(f"请求失败: {str(e)}")
    except Exception as e:
        st.error(f"发生错误: {str(e)}")


# 页面布局
st.title("📈 股票舆情分析系统")

# 搜索栏
search_col, analysis_col = st.columns([3, 1])
with search_col:
    search_query = st.text_input(
        "输入股票名称或代码",
        placeholder="输入关键词搜索股票...",
        key="search_input",
        help="支持股票名称或代码模糊搜索"
    )

# 实时搜索（输入变化时触发）
if search_query:
    search_stocks(search_query)

# 股票选择框
if st.session_state.stock_options:
    selected = st.selectbox(
        "选择股票",
        options=st.session_state.stock_options,
        format_func=lambda x: f"{x['name']} ({x['code']})",
        help="从搜索结果中选择要分析的股票"
    )
    st.session_state.selected_stock = selected

# 分析按钮
if st.session_state.selected_stock:
    if st.button("开始分析", type="primary"):
        analyze_stock(st.session_state.selected_stock["code"])

# 显示分析结果
if st.session_state.analysis_data:
    data = st.session_state.analysis_data

    # 总体情况卡片
    with st.container():
        st.subheader("📊 总体分析")
        cols = st.columns(3)
        with cols[0]:
            st.metric("综合评分", f"{data['analysis_summary']['overall_score'] * 100:.1f}分")
        with cols[1]:
            st.metric("市场情绪",
                      data['analysis_summary']['sentiment_label'],
                      f"投资者情绪指数：{data['analysis_summary']['investor_sentiment']}%")
        with cols[2]:
            st.metric("置信指数",
                      f"{data['analysis_summary']['confidence_index'] * 100:.1f}%",
                      f"分析时段：{data['analysis_summary']['analysis_period']['start_date']} 至 {data['analysis_summary']['analysis_period']['end_date']}")

        st.markdown(f"**分析总结**：{data['analysis_summary']['summary']}")
    # 时间趋势分析
    with st.container():
        st.subheader("⏳ 时间趋势分析")
        df_time = pd.DataFrame(data['time_analysis']['trend'])
        print(df_time)

        df_time['date'] = pd.to_datetime(df_time['date'])

        # 趋势图
        tab1, tab2 = st.tabs(["趋势图表", "关键事件"])
        with tab1:
            st.line_chart(df_time.set_index('date')['score'], use_container_width=True)

        with tab2:
            for event in data['time_analysis']['trend']:
                with st.expander(f"{event['date']} - 评分 {event['score']}"):
                    for e in event['key_events']:
                        st.markdown(f"**{e['title']}**  \n{e['description']}")

    # 主题分析
    with st.container():
        st.subheader("🔍 主题分析")
        topics = data['topic_analysis']
        cols = st.columns(3)

        # 主题评分卡片
        with cols[0]:
            st.markdown("### 主题评分")
            topic_scores = {
                '公司运营': topics['company_operation']['score'],
                '财务表现': topics['financial_performance']['score'],
                '市场竞争': topics['market_competition']['score']
            }
            st.bar_chart(pd.DataFrame.from_dict(topic_scores, orient='index'))

        # 关键点分析
        with cols[1]:
            st.markdown("### 重点领域")
            selected_topic = st.selectbox("选择分析主题", list(topic_scores.keys()))
            topic_data = topics[{
                '公司运营': 'company_operation',
                '财务表现': 'financial_performance',
                '市场竞争': 'market_competition'
            }[selected_topic]]
            st.markdown(f"**评分**: {topic_data['score']}  \n**摘要**: {topic_data['summary']}")

        # 关键点列表
        with cols[2]:
            st.markdown("### 关键要点")
            for point in topic_data['key_points'][:3]:
                st.markdown(f"- {point}")

    # 来源、影响、风险分析
    with st.container():
        st.subheader("📌 综合分析")
        cols = st.columns(3)

        # 来源分析
        with cols[0]:
            st.markdown("### 信息来源分析")
            sources = data['source_analysis']
            source_data = {
                '主流媒体': sources['mainstream_media']['score'],
                '行业媒体': sources['industry_media']['score'],
                '官方公告': sources['official_announcement']['score']
            }
            st.bar_chart(pd.DataFrame.from_dict(source_data, orient='index'))

        # 影响分析
        with cols[1]:
            st.markdown("### 市场影响")
            impact = data['impact_analysis']
            st.markdown(f"""
                **重要性级别**: {impact['importance_level']}  
                **影响评分**: {impact['market_impact']['score']}  
                **持续时间**: {impact['market_impact']['duration']}
            """)
            st.write("**关键因素**:")
            for factor in impact['market_impact']['key_factors'][:3]:
                st.markdown(f"- {factor}")

        # 风险分析
        with cols[2]:
            st.markdown("### 风险提示")
            risk = data['risk_analysis']
            st.markdown(f"**风险等级**: {risk['risk_level']}")
            for factor in risk['risk_factors']:
                with st.expander(f"{factor['factor']}（{factor['severity']}）"):
                    st.write(factor['description'])

    # 新闻分析
    with st.container():
        st.subheader("📰 相关新闻")
        for news in data['news_analysis']:
            with st.expander(f"{news['title']} - {news['source']}"):
                st.markdown(f"""
                    **发布时间**: {news['publish_time']}  
                    **来源**: {news['source']}  
                    **内容摘要**: {news['content'][:200]}...  
                    [查看原文]({news['url']})
                """)


