function updateESGCharts() {
  const companySelect = document.getElementById("companySelect");

  // ✅ 1. 获取 value → 用于拼接图表文件名
  const company = companySelect.value;

  // ✅ 2. 获取 text → 用于页面展示
  const companyName = companySelect.options[companySelect.selectedIndex].text;

  // ✅ 3. 设置 iframe 的 src（使用 value）
  document.getElementById("barChart").src = `charts/${company}_bar.html`;
  document.getElementById("lineChart").src = `charts/${company}_line.html`;
  document.getElementById("heatmapChart").src = `charts/${company}_heatmap.html`;

  // ✅ 4. 页面显示当前公司（使用 text）
  document.getElementById("selectedCompanyText").textContent = `You selected: ${companyName}`;
}
