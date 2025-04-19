import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from prophet import Prophet
from prophet.plot import plot_plotly
import matplotlib.pyplot as plt
import seaborn as sns

print("✅ Python 脚本开始运行")
# ✅ 设置当前目录为脚本本身所在目录（最关键）
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 确认当前路径
print("📁 当前工作目录：", os.getcwd())

# 只检查 charts 文件夹是否存在（你手动创建）
if not os.path.exists("charts"):
    print("❌ 错误：charts 文件夹不存在，请手动创建一个！")
    exit()

print("📂 charts 文件夹已找到，准备生成图表...")

# ========== Step 1: 模拟数据 ==========
years = [2019, 2020, 2021, 2022, 2023]
esg_rating = ['BBB', 'A', 'A', 'AA', 'AA']
esg_score = [7, 8, 8, 9, 9]
e_score = [68, 71, 73, 76, 79]
s_score = [65, 67, 70, 73, 76]
g_score = [75, 74, 76, 78, 80]
price = [42.5, 44.2, 45.5, 47.0, 49.0]

df = pd.DataFrame({
    'year': years,
    'esg_rating': esg_rating,
    'esg_score': esg_score,
    'e_score': e_score,
    's_score': s_score,
    'g_score': g_score,
    'price': price
})

print("✅ Step 1：数据准备完毕")

# ========== Step 2: ESG 趋势图 ==========
fig_trend = px.line(df, x='year', y='esg_score', title='ESG Score Trend - Pfizer', markers=True)
fig_trend.write_html("charts/Pfizer_trend.html")
print("✅ Step 2：趋势图已生成")

# ========== Step 3: ESG 预测图 ==========
df_prophet = pd.DataFrame({
    'ds': pd.date_range(start='2019', periods=5, freq='Y'),
    'y': esg_score
})
model = Prophet()
model.fit(df_prophet)
future = model.make_future_dataframe(periods=3, freq='Y')
forecast = model.predict(future)
fig_forecast = plot_plotly(model, forecast)
fig_forecast.update_layout(title="ESG Score Forecast - Pfizer")
fig_forecast.write_html("charts/Pfizer_forecast.html")
print("✅ Step 3：预测图已生成")

# ========== Step 4: ESG 雷达图 ==========
radar_data = go.Figure()
radar_data.add_trace(go.Scatterpolar(
    r=[e_score[-1], s_score[-1], g_score[-1]],
    theta=['Environmental', 'Social', 'Governance'],
    fill='toself',
    name='2023'
))
radar_data.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[60, 100])),
    title="E/S/G Score Radar - 2023"
)
radar_data.write_html("charts/Pfizer_radar.html")
print("✅ Step 4：雷达图已生成")

# ========== Step 5: ESG vs 股价相关性 ==========
corr_df = df[['esg_score', 'e_score', 's_score', 'g_score', 'price']]
corr_matrix = corr_df.corr()

plt.figure(figsize=(6, 5))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
plt.title("Correlation: ESG vs Price - Pfizer")
plt.tight_layout()
plt.savefig("charts/Pfizer_correlation.png")  # 注意这是 PNG 图
print("✅ Step 5：相关性图已生成")

print("🎉 所有图表已成功保存到 charts/ 文件夹！")
