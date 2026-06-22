import os
os.environ["MPLBACKEND"] = "Agg"
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 页面配置
st.set_page_config(
    page_title="电影风向标｜豆瓣Top250多维度深度分析看板",
    layout="wide",
    initial_sidebar_state="expanded"
)
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 缓存加载数据
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_douban.csv", encoding="utf-8-sig")
    df["排名"] = df["排名"].astype(int)
    df["评分"] = df["评分"].astype(float)
    df["评价人数"] = df["评价人数"].astype(int)
    df["年份"] = df["年份"].astype(int)
    # 新增年代分层标签
    def get_period(y):
        if y < 1990:
            return "1930-1989 萌芽期"
        elif y <= 2010:
            return "1990-2010 黄金期"
        elif y <= 2018:
            return "2011-2018 平稳期"
        else:
            return "2019至今 新生代"
    df["年代分层"] = df["年份"].apply(get_period)
    return df

df = load_data()

# 页面标题
st.title("🎬 电影风向标 —— 豆瓣Top250多维度深度交互式分析")
st.divider()

# 侧边筛选面板
st.sidebar.header("🔍 多条件筛选")
min_year, max_year = df["年份"].min(), df["年份"].max()
year_range = st.sidebar.slider("上映年份区间", min_year, max_year, (min_year, max_year))
min_score = st.sidebar.slider("最低评分", 8.0, 9.7, 8.0, 0.1)
min_pop = st.sidebar.slider("最低评价人数(万人)", 0, int(df["评价人数"].max()/10000), 0)
search_name = st.sidebar.text_input("电影名称搜索")

# 筛选逻辑
filter_df = df[(df["年份"] >= year_range[0]) & (df["年份"] <= year_range[1]) & (df["评分"] >= min_score) & (df["评价人数"] >= min_pop*10000)]
if search_name:
    filter_df = filter_df[filter_df["电影名"].str.contains(search_name, na=False)]

# 综合KPI指标
st.subheader("📊 全局数据指标总览")
if len(filter_df) > 0:
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("筛选影片总数", len(filter_df))
    c2.metric("平均评分", round(filter_df["评分"].mean(),2))
    c3.metric("评分中位数", round(filter_df["评分"].median(),2))
    c4.metric("评分标准差", round(filter_df["评分"].std(),2))

    c5,c6,c7,c8 = st.columns(4)
    total_people = round(filter_df["评价人数"].sum()/10000, 1)
    avg_people = round(filter_df["评价人数"].mean()/10000, 1)
    max_people = round(filter_df["评价人数"].max()/10000, 1)
    max_score = filter_df["评分"].max()
    c5.metric("总评价人次(万)", total_people)
    c6.metric("单部平均热度(万)", avg_people)
    c7.metric("最热影片人数(万)", max_people)
    c8.metric("筛选最高评分", max_score)
else:
    st.warning("无匹配数据，请放宽筛选条件！")
st.divider()

# 图表1：评分分布直方图（口碑整体分布）
st.subheader("1. 全筛选影片评分分布直方图｜口碑分层")
fig1, ax1 = plt.subplots(figsize=(12,4),dpi=100)
ax1.hist(filter_df["评分"], bins=14, color="#409EFF", alpha=0.7, edgecolor="white")
ax1.set_xlabel("豆瓣评分")
ax1.set_ylabel("影片数量")
ax1.grid(axis="y", alpha=0.3)
st.pyplot(fig1)
st.divider()

# 图表2：评价人数分布直方图（热度分层）
st.subheader("2. 影片评价人数分布直方图｜热度划分")
fig2, ax2 = plt.subplots(figsize=(12,4),dpi=100)
wan = filter_df["评价人数"] / 10000
ax2.hist(wan, bins=15, color="#F56C6C", alpha=0.7)
ax2.set_xlabel("评价人数（万人）")
ax2.set_ylabel("影片数量")
st.pyplot(fig2)
st.divider()

# 图表3：各年份上榜数量折线（产出趋势）
st.subheader("3. 历年上榜电影数量折线｜影视产出周期")
year_cnt = filter_df.groupby("年份")["排名"].count()
fig3, ax3 = plt.subplots(figsize=(14,4),dpi=100)
ax3.plot(year_cnt.index, year_cnt.values, marker="o", color="#288c28", linewidth=2)
ax3.set_xlabel("上映年份")
ax3.set_ylabel("上榜影片数")
ax3.tick_params(axis="x", rotation=45)
ax3.grid(alpha=0.3)
st.pyplot(fig3)
st.divider()

# 图表4：各年份平均评分折线（年度口碑变化）
st.subheader("4. 历年平均评分折线｜不同时代影片口碑对比")
year_avg_score = filter_df.groupby("年份")["评分"].mean()
fig4, ax4 = plt.subplots(figsize=(14,4),dpi=100)
ax4.plot(year_avg_score.index, year_avg_score.values, marker="s", color="#9370DB", linewidth=2)
ax4.set_xlabel("上映年份")
ax4.set_ylabel("年度平均评分")
ax4.set_ylim(8.3,9.8)
ax4.tick_params(axis="x", rotation=45)
ax4.grid(alpha=0.3)
st.pyplot(fig4)
st.divider()

# 图表5：四大年代区间影片数量柱状（时代分层对比）
st.subheader("5. 四大时代上榜影片总量柱状｜黄金期对比")
period_cnt = filter_df["年代分层"].value_counts()
fig5, ax5 = plt.subplots(figsize=(10,4),dpi=100)
ax5.bar(period_cnt.index, period_cnt.values, color=["#ccc","#67C23A","#ffc53d","#ee6666"])
ax5.set_xlabel("时代分层")
ax5.set_ylabel("影片数量")
st.pyplot(fig5)
st.divider()

# 图表6：评分&评价人数散点图（口碑热度交叉分析）
st.subheader("6. 评分-评价人数散点图｜爆款/小众影片划分")
fig6, ax6 = plt.subplots(figsize=(12,5),dpi=100)
x = filter_df["评价人数"] / 10000
y = filter_df["评分"]
ax6.scatter(x, y, alpha=0.6, color="#009688")
ax6.set_xlabel("评价人数（万人）")
ax6.set_ylabel("电影评分")
ax6.grid(alpha=0.3)
st.pyplot(fig6)
st.divider()

# 图表7：筛选后口碑TOP10横向条形
st.subheader("7. 口碑TOP10高分影片榜单")
top_score = filter_df.sort_values(["评分","评价人数"], ascending=[False,False]).head(10)
fig7, ax7 = plt.subplots(figsize=(11,4),dpi=100)
ax7.barh(top_score["电影名"][::-1], top_score["评分"][::-1], color="#67C23A")
ax7.set_xlim(9.0,9.8)
ax7.set_xlabel("评分")
st.pyplot(fig7)
st.divider()

# 图表8：筛选后热度TOP10横向条形
st.subheader("8. 人气热度TOP10影片榜单")
top_hot = filter_df.sort_values("评价人数", ascending=False).head(10)
hot_wan = top_hot["评价人数"] / 10000
fig8, ax8 = plt.subplots(figsize=(11,4),dpi=100)
ax8.barh(top_hot["电影名"][::-1], hot_wan[::-1], color="#FF9900")
ax8.set_xlabel("评价人数（万人）")
st.pyplot(fig8)
st.divider()

# 图表9：各年代平均评分对比柱状
st.subheader("9. 四大时代平均评分对比")
period_avg = filter_df.groupby("年代分层")["评分"].mean()
fig9, ax9 = plt.subplots(figsize=(10,4),dpi=100)
ax9.bar(period_avg.index, period_avg.values, color="#e06666")
ax9.set_ylabel("平均评分")
ax9.set_ylim(8.5,9.2)
st.pyplot(fig9)
st.divider()

# 数据明细表格
st.subheader("📋 完整电影数据明细")
st.dataframe(filter_df[["排名","电影名","评分","评价人数","年份","年代分层","一句话影评"]], use_container_width=True, hide_index=True)
