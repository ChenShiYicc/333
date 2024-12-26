# 导入所需的库
import streamlit as st
import streamlit.components.v1 as components
import requests
import jieba
from collections import Counter
from pyecharts.charts import WordCloud, Bar, Line, Pie, Scatter, Radar, Funnel
from pyecharts import options as opts
import re

# Streamlit页面设置
st.title('文本分析工具')

# 用户输入URL
url = st.text_input('请输入文章的URL')

# 定义函数
def fetch_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        response.encoding = 'utf-8'  # 强制指定编码为utf-8
        return response.text
    except requests.exceptions.HTTPError as errh:
        st.error(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        st.error(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        st.error(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        st.error(f"Oops: Something Else: {err}")
    return None

def remove_punctuation(text):
    # 只保留中文字符
    return re.sub(r'[^\u4e00-\u9fa5]+', '', text)

def tokenize_and_count(text):
    words = jieba.lcut(text)
    # 过滤空字符串
    words = [word for word in words if word.strip()]
    word_counts = Counter(words)
    return word_counts

def filter_low_freq_words(word_counts, min_freq):
    return Counter({word: count for word, count in word_counts.items() if count >= min_freq})

def generate_wordcloud(word_counts):
    wordcloud = WordCloud()
    wordcloud.add("", word_counts.items(), word_size_range=[20, 100])
    wordcloud.set_global_opts(title_opts=opts.TitleOpts(title="Word Cloud"))
    return wordcloud

def generate_bar_chart(word_counts):
    bar = Bar()
    words, counts = zip(*word_counts.items())
    bar.add_xaxis(list(words))
    bar.add_yaxis("词频", list(counts))
    bar.set_global_opts(title_opts=opts.TitleOpts(title="词频条形图"), xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)))
    return bar

def generate_line_chart(word_counts):
    line = Line()
    words, counts = zip(*word_counts.items())
    line.add_xaxis(list(words))
    line.add_yaxis("词频", list(counts))
    line.set_global_opts(title_opts=opts.TitleOpts(title="词频折线图"), xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)))
    return line

def generate_pie_chart(word_counts):
    pie = Pie()
    words, counts = zip(*word_counts.items())
    pie.add("", [list(z) for z in zip(words, counts)], radius=["30%", "75%"])
    pie.set_global_opts(title_opts=opts.TitleOpts(title="词频饼图"))
    return pie

def generate_scatter_chart(word_counts):
    scatter = Scatter()
    words, counts = zip(*word_counts.items())
    scatter.add_xaxis(list(words))
    scatter.add_yaxis("词频", list(counts))
    scatter.set_global_opts(title_opts=opts.TitleOpts(title="词频散点图"))
    return scatter

def generate_radar_chart(word_counts):
    radar = Radar()
    radar.add_schema(schema=[opts.RadarIndicatorItem(name=word, max_=max(word_counts.values())) for word in word_counts.keys()])
    radar.add("词频", [list(word_counts.values())])
    radar.set_global_opts(title_opts=opts.TitleOpts(title="词频雷达图"))
    return radar

def generate_funnel_chart(word_counts):
    funnel = Funnel()
    words, counts = zip(*word_counts.items())
    funnel.add("", [list(z) for z in zip(words, counts)])
    funnel.set_global_opts(title_opts=opts.TitleOpts(title="词频漏斗图"))
    return funnel

def display_top_words(word_counts, top_n=20):
    top_words = word_counts.most_common(top_n)
    st.write("词频排名前20的词汇：")
    for word, count in top_words:
        st.write(f"{word}: {count}")

def render_pyecharts_chart(chart):
    # 渲染并显示pyecharts图表
    chart_html = chart.render_embed()
    components.html(chart_html, height=600)  # 可以调整height参数

# 如果用户输入了URL，开始处理
if url:
    text = fetch_text_from_url(url)
    if text is None:
        st.error("无法获取文本内容，请检查URL或网络连接。")
    else:
        # 去除文本中的标点符号，只保留中文字符
        text = remove_punctuation(text)

        # 对文本分词，统计词频
        word_counts = tokenize_and_count(text)

        # 过滤低频词
        min_freq = st.sidebar.slider('设置最低词频阈值', 1, 100, 5)
        filtered_word_counts = filter_low_freq_words(word_counts, min_freq)

        # 选择图表类型
        chart_type = st.sidebar.selectbox(
            '选择图表类型',
            ['词云', '条形图', '折线图', '饼图', '散点图', '雷达图', '漏斗图']
        )

        # 根据用户选择的图表类型生成图表
        if chart_type == '词云':
            wordcloud = generate_wordcloud(filtered_word_counts)
            st.subheader('词云')
            render_pyecharts_chart(wordcloud)
        elif chart_type == '条形图':
            bar = generate_bar_chart(filtered_word_counts)
            st.subheader('词频条形图')
            render_pyecharts_chart(bar)
        elif chart_type == '折线图':
            line = generate_line_chart(filtered_word_counts)
            st.subheader('词频折线图')
            render_pyecharts_chart(line)
        elif chart_type == '饼图':
            pie = generate_pie_chart(filtered_word_counts)
            st.subheader('词频饼图')
            render_pyecharts_chart(pie)
        elif chart_type == '散点图':
            scatter = generate_scatter_chart(filtered_word_counts)
            st.subheader('词频散点图')
            render_pyecharts_chart(scatter)
        elif chart_type == '雷达图':
            radar = generate_radar_chart(filtered_word_counts)
            st.subheader('词频雷达图')
            render_pyecharts_chart(radar)
        elif chart_type == '漏斗图':
            funnel = generate_funnel_chart(filtered_word_counts)
            st.subheader('词频漏斗图')
            render_pyecharts_chart(funnel)

        # 展示词频排名前20的词汇
        display_top_words(filtered_word_counts)
