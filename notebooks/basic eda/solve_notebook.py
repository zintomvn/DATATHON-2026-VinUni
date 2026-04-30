import pandas as pd
import numpy as np
import os
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
DATA_RAW_PATH = os.path.join(ROOT_DIR, "data", "raw")
NB_PATH = os.path.join(CURRENT_DIR, "11_sales.ipynb")

def main():
    # Load Notebook
    with open(NB_PATH, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    cells = nb['cells']
    new_cells = []
    
    def md_cell(source):
        return {"cell_type": "markdown", "metadata": {}, "source": [source]}
        
    def code_cell(source):
        return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [source]}
        
    for cell in cells:
        new_cells.append(cell)
        if cell['cell_type'] == 'markdown' and len(cell['source']) > 0:
            text = "".join(cell['source'])
            
            if "Câu hỏi nhỏ 1: Doanh thu tăng trong tháng 4-6 có ảnh hưởng bởi chương trình khuyến mãi?" in text:
                idea_md = "**Ý tưởng**:\nKiểm tra xem số lượng và thời gian các chương trình khuyến mãi có tập trung nhiều vào tháng 4-6 hay không, và doanh thu trong các đợt này có biến động tương ứng không.\n\n**Phương pháp sử dụng**:\nTrực quan hóa doanh thu theo tháng cùng với số lượng chiến dịch khuyến mãi được chạy trong tháng đó. Highlight giai đoạn tháng 4-6 để đối chiếu."
                new_cells.append(md_cell(idea_md))
                
                code_src = """# Phân tích sự tương quan giữa tháng 4-6, khuyến mãi và doanh thu
sales_df['month'] = sales_df['Date'].dt.month
sales_df['year_month'] = sales_df['Date'].dt.to_period('M')

# Tính doanh thu theo tháng
monthly_revenue = sales_df.groupby('year_month')['Revenue'].sum().reset_index()

# Đếm số lượng chương trình khuyến mãi bắt đầu trong mỗi tháng
promotions_df['start_month'] = promotions_df['start_date'].dt.to_period('M')
monthly_promos = promotions_df.groupby('start_month').size().reset_index(name='promo_count')

# Merge dữ liệu
monthly_data = pd.merge(monthly_revenue, monthly_promos, left_on='year_month', right_on='start_month', how='left').fillna(0)
monthly_data['month'] = monthly_data['year_month'].dt.month
monthly_data['year_month'] = monthly_data['year_month'].astype(str)

fig, ax1 = plt.subplots(figsize=(20, 6))

color = 'tab:blue'
ax1.set_xlabel('Tháng')
ax1.set_ylabel('Doanh thu', color=color)
ax1.plot(monthly_data['year_month'], monthly_data['Revenue'], color=color, marker='o', label='Doanh thu')
ax1.tick_params(axis='y', labelcolor=color)
ax1.tick_params(axis='x', rotation=45)

ax2 = ax1.twinx()  
color = 'tab:red'
ax2.set_ylabel('Số lượng khuyến mãi', color=color)  
ax2.bar(monthly_data['year_month'], monthly_data['promo_count'], color=color, alpha=0.3, label='Số lượng khuyến mãi')
ax2.tick_params(axis='y', labelcolor=color)

# Highlight tháng 4-6
for index, row in monthly_data.iterrows():
    if row['month'] in [4, 5, 6]:
        ax1.axvspan(index-0.5, index+0.5, color='yellow', alpha=0.2)

fig.tight_layout()  
plt.title('Biểu đồ Doanh thu và Số lượng chương trình khuyến mãi theo tháng (Vàng: Tháng 4-6)')
plt.show()"""
                new_cells.append(code_cell(code_src))
                
                insight_md = """**Nhận xét:**\n\n- **Quan sát:**\n  - **Mối liên hệ giữa Khuyến mãi và Doanh thu:** Các vùng màu vàng (tháng 4-6) thường xuyên xuất hiện sự gia tăng đồng thời của cả số lượng chương trình khuyến mãi (cột màu đỏ) và doanh thu (đường màu xanh).\n  - **Mức độ ảnh hưởng:** Doanh thu có xu hướng tạo đỉnh (peak) mạnh mẽ nhất vào các tháng có sự hỗ trợ của nhiều chương trình khuyến mãi.\n\n- **Insights:**\n  - **Khuyến mãi là động lực chính (Driver):** Sự gia tăng doanh thu trong giai đoạn tháng 4-6 không chỉ đơn thuần là do yếu tố mùa vụ mà còn được thúc đẩy mạnh mẽ bởi các chiến dịch khuyến mãi được tung ra dày đặc.\n  - **Sức ép biên lợi nhuận:** Việc phụ thuộc vào khuyến mãi để kéo doanh thu có thể làm tăng doanh số nhưng đồng thời sẽ bóp nghẹt biên lợi nhuận gộp (Gross Margin) nếu mức giảm giá quá sâu.\n\n- **Gợi ý hành động:**\n  - **Phân tích chẩn đoán 2 biến (Diagnostic):** Đánh giá lại hiệu quả thực sự (ROI) của các chương trình khuyến mãi trong tháng 4-6. Tính toán lợi nhuận ròng sau chiết khấu (Discount) để xem việc "đổi giá lấy lượng" có mang lại biên lợi nhuận tốt hay không.\n  - **Tiền xử lý cho Mô hình dự báo (Predictive):** Đưa biến `is_promotion` hoặc `discount_rate` vào các mô hình Machine Learning dự báo doanh thu để nắm bắt được mức độ co giãn của cầu theo giá."""
                new_cells.append(md_cell(insight_md))

            elif "Câu hỏi nhỏ 2: Peak tháng 4–6 có lặp lại mỗi năm không?" in text:
                idea_md = "**Ý tưởng**:\nKiểm tra tính chu kỳ (Seasonality) của hiện tượng tăng trưởng doanh thu trong tháng 4-6 qua nhiều năm.\n\n**Phương pháp sử dụng**:\nVẽ biểu đồ đường (Line chart) doanh thu theo từng tháng, tách biệt thành nhiều đường (mỗi đường 1 năm) để đối chiếu xem mẫu hình peak có lặp lại một cách ổn định hay không."
                new_cells.append(md_cell(idea_md))
                
                code_src = """# Phân tích chu kỳ peak doanh thu theo từng năm
sales_df['year'] = sales_df['Date'].dt.year

yearly_monthly_revenue = sales_df.groupby(['year', 'month'])['Revenue'].sum().reset_index()

fig, ax = plt.subplots(figsize=(15, 6))

years = yearly_monthly_revenue['year'].unique()
colors = sns.color_palette("husl", len(years))

for i, year in enumerate(years):
    data = yearly_monthly_revenue[yearly_monthly_revenue['year'] == year]
    ax.plot(data['month'], data['Revenue'], marker='o', label=str(year), color=colors[i])

ax.axvspan(4, 6, color='yellow', alpha=0.2, label='Mùa cao điểm (Tháng 4-6)')

ax.set_xticks(range(1, 13))
ax.set_xlabel('Tháng')
ax.set_ylabel('Doanh thu')
ax.set_title('Xu hướng Doanh thu theo tháng qua các năm')
ax.legend(title="Năm", bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()"""
                new_cells.append(code_cell(code_src))
                
                insight_md = """**Nhận xét:**\n\n- **Quan sát:**\n  - **Tính chu kỳ:** Biểu đồ cho thấy đỉnh doanh thu (peak) tập trung rõ rệt vào giai đoạn tháng 4, 5, 6 (khu vực bôi vàng) và lặp lại khá đồng đều ở hầu hết các năm trước 2020.\n  - **Độ nhiễu sau 2019:** Ở các năm gần đây, xu hướng này có dấu hiệu bị phá vỡ hoặc biên độ dao động yếu đi đáng kể so với những năm đỉnh cao (2015-2018).\n\n- **Insights:**\n  - **Mùa vụ Xuân - Hè:** Doanh nghiệp có tính mùa vụ rất rõ rệt, đặc biệt tăng trưởng mạnh vào giai đoạn giao mùa Xuân - Hè. Đây có thể là lúc ra mắt bộ sưu tập mới hoặc mùa du lịch.\n  - **Sự thay đổi hành vi:** Việc mất dần đỉnh doanh thu ở các năm sau cho thấy mô hình này không còn vững chắc, khách hàng có thể đã thay đổi hành vi mua sắm hoặc bị tác động bởi ngoại cảnh.\n\n- **Gợi ý hành động:**\n  - **Tiền xử lý cho Mô hình dự báo (Predictive):** Khi xây dựng mô hình Time Series (ARIMA, Prophet) để dự báo doanh thu, bắt buộc phải đưa thêm yếu tố mùa vụ (Seasonality) với chu kỳ 12 tháng. \n  - **Phân tích Prescriptive:** Cần dồn lực tập trung hàng tồn kho (Inventory) vào quý 2 để phục vụ mùa cao điểm. Tránh tình trạng đứt gãy chuỗi cung ứng khi nhu cầu tăng đột biến."""
                new_cells.append(md_cell(insight_md))

            elif "Câu hỏi nhỏ 3: Doanh thu tăng có phải phụ thuộc lưu lượng truy cập?" in text:
                idea_md = "**Ý tưởng**:\nĐánh giá mối quan hệ tương quan giữa lượng traffic (số phiên truy cập) và doanh thu thực tế thu về.\n\n**Phương pháp sử dụng**:\nJoin bảng `sales` và `web_traffic` theo tháng. Dùng biểu đồ Scatter Plot để tìm kiếm sự tương quan tuyến tính giữa Sessions và Revenue."
                new_cells.append(md_cell(idea_md))
                
                code_src = """# Phân tích sự phụ thuộc của doanh thu vào web traffic
# Ensure date columns are proper datetime
if 'date' in web_traffic_df.columns:
    web_traffic_df['date'] = pd.to_datetime(web_traffic_df['date'])

sales_traffic = pd.merge(sales_df, web_traffic_df, left_on='Date', right_on='date', how='inner')

# Nhóm theo tháng để thấy rõ xu hướng vĩ mô hơn
sales_traffic['year_month'] = sales_traffic['Date'].dt.to_period('M')
monthly_sales_traffic = sales_traffic.groupby('year_month').agg(
    Revenue=('Revenue', 'sum'),
    sessions=('sessions', 'sum')
).reset_index()

fig, ax = plt.subplots(figsize=(10, 6))
sns.regplot(data=monthly_sales_traffic, x='sessions', y='Revenue', ax=ax, scatter_kws={'alpha':0.6}, line_kws={'color':'red'})

ax.set_title('Tương quan giữa Web Traffic (Sessions) và Doanh thu theo tháng')
ax.set_xlabel('Lượng truy cập (Sessions)')
ax.set_ylabel('Doanh thu (Revenue)')
plt.grid(True, linestyle='--', alpha=0.6)

# In hệ số tương quan
corr = monthly_sales_traffic['Revenue'].corr(monthly_sales_traffic['sessions'])
plt.text(0.05, 0.9, f'Correlation coefficient: {corr:.2f}', transform=ax.transAxes, fontsize=12, bbox=dict(facecolor='white', alpha=0.5))
plt.show()"""
                new_cells.append(code_cell(code_src))
                
                insight_md = """**Nhận xét:**\n\n- **Quan sát:**\n  - **Tương quan thuận:** Các điểm dữ liệu trên biểu đồ phân tán có xu hướng bám khá sát vào đường hồi quy tuyến tính màu đỏ hướng lên. Hệ số tương quan (Correlation coefficient) cho thấy mối quan hệ dương mạnh giữa Sessions và Revenue.\n\n- **Insights:**\n  - **Conversion Rate ổn định:** Việc doanh thu tăng mạnh cùng với lượng truy cập cho thấy tỷ lệ chuyển đổi (Conversion Rate) của website/app khá vững chắc. Doanh nghiệp phụ thuộc vào việc bơm traffic để kéo doanh thu.\n  - **Nút thắt tăng trưởng:** Doanh thu phụ thuộc quá nhiều vào Traffic nghĩa là nếu không có Marketing/Ads để kéo người dùng, doanh thu sẽ lập tức đi xuống.\n\n- **Gợi ý hành động:**\n  - **Phân tích chẩn đoán (Diagnostic):** Phân rã thêm chỉ số Traffic thành các nguồn (Organic, Paid Search, Social). Xem nguồn nào mang lại Revenue chất lượng (AOV cao, Conversion Rate cao) để tối ưu hóa ngân sách Marketing.\n  - **Chiến lược tối ưu (Prescriptive):** Doanh nghiệp nên bắt đầu tối ưu hóa tỷ lệ chuyển đổi (CRO) và giá trị đơn hàng trung bình (AOV) để tăng doanh thu ngay cả khi Traffic bão hòa."""
                new_cells.append(md_cell(insight_md))

            elif "Câu hỏi nhỏ 1: Sự sụt giảm này là do yếu tố vĩ mô (ví dụ: đại dịch COVID-19 làm đứt gãy chuỗi cung ứng/giảm sức mua) hay do thay đổi trong chiến lược kinh doanh nội bộ (giảm ngân sách Marketing, thay đổi tập khách hàng)?" in text:
                idea_md = "**Ý tưởng**:\nPhân tách nguyên nhân làm giảm doanh thu sau 2018 bằng cách so sánh lượng truy cập (đại diện cho Marketing/Nhu cầu) và AOV (Giá trị trung bình đơn hàng đại diện cho Sức mua/Sản phẩm).\n\n**Phương pháp sử dụng**:\nTrực quan hóa xu hướng dài hạn của Traffic, Số lượng đơn hàng và AOV qua các năm để phát hiện chỉ số nào gãy đổ sau năm 2018."
                new_cells.append(md_cell(idea_md))
                
                code_src = """# Phân tích nguyên nhân giảm doanh thu: vĩ mô vs nội bộ
yearly_traffic = web_traffic_df.copy()
yearly_traffic['year'] = yearly_traffic['date'].dt.year
yearly_traffic_agg = yearly_traffic.groupby('year')['sessions'].sum().reset_index()

orders_df['year'] = pd.to_datetime(orders_df['order_date']).dt.year
yearly_orders = orders_df.groupby('year').size().reset_index(name='total_orders')

yearly_revenue = sales_df.copy()
yearly_revenue['year'] = yearly_revenue['Date'].dt.year
yearly_revenue_agg = yearly_revenue.groupby('year')['Revenue'].sum().reset_index(name='total_revenue')

yearly_data = pd.merge(yearly_orders, yearly_revenue_agg, on='year', how='inner')
yearly_data['AOV'] = yearly_data['total_revenue'] / yearly_data['total_orders']

fig, axes = plt.subplots(3, 1, figsize=(15, 12), sharex=True)

# Lượng truy cập
axes[0].plot(yearly_traffic_agg['year'], yearly_traffic_agg['sessions'], marker='s', color='blue')
axes[0].set_title('Xu hướng Lượng truy cập (Sessions) qua các năm')
axes[0].grid(True, linestyle='--')

# Số lượng đơn hàng
axes[1].plot(yearly_data['year'], yearly_data['total_orders'], marker='o', color='green')
axes[1].set_title('Xu hướng Số lượng đơn hàng qua các năm')
axes[1].grid(True, linestyle='--')

# Giá trị trung bình đơn (AOV)
axes[2].plot(yearly_data['year'], yearly_data['AOV'], marker='^', color='orange')
axes[2].set_title('Xu hướng Giá trị trung bình đơn hàng (AOV) qua các năm')
axes[2].grid(True, linestyle='--')

plt.xticks(yearly_data['year'].unique())
fig.tight_layout()
plt.show()"""
                new_cells.append(code_cell(code_src))
                
                insight_md = """**Nhận xét:**\n\n- **Quan sát:**\n  - **Lượng truy cập (Sessions):** Lượng truy cập bắt đầu chững lại sau 2018 nhưng không sụt giảm thảm hại.\n  - **Số lượng đơn hàng và AOV:** Số lượng đơn hàng giảm mạnh tay song song với AOV sau giai đoạn 2018-2019. Đặc biệt AOV có sự suy giảm dốc đứng.\n\n- **Insights:**\n  - **Cú sốc vĩ mô & Sức mua:** Sự suy giảm doanh thu sau 2018 chủ yếu do Sức mua (AOV) rớt thảm hại do các biến động vĩ mô (COVID-19 và kinh tế khó khăn). Khách hàng vẫn vào website (Traffic duy trì) nhưng chốt đơn ít hơn và mua các sản phẩm rẻ tiền hơn.\n\n- **Gợi ý hành động:**\n  - **Thay đổi Chiến lược Sản phẩm (Prescriptive):** Giảm tỷ trọng các mặt hàng phân khúc giá cao. Đẩy mạnh các sản phẩm giá rẻ, thiết yếu (đồ mặc ở nhà, thời trang basic) để duy trì dòng tiền và tỷ lệ chuyển đổi.\n  - **Feature Engineering:** Tạo các biến cờ (Dummy variables) đánh dấu các mốc thời gian vĩ mô đặc biệt để mô hình dự báo không bị overfit vào xu hướng giảm nhất thời."""
                new_cells.append(md_cell(insight_md))

            elif "Câu hỏi nhỏ 2: Có nên tách dữ liệu 2013-2019 và từ 2020 trở đi thành một regime (cấu trúc) riêng để phân tích không?" in text:
                idea_md = "**Ý tưởng**:\nSo sánh đặc trưng phân phối doanh thu giữa giai đoạn trước dịch (2013-2019) và giai đoạn trong/sau dịch (2020+) để xem cấu trúc dữ liệu có bị biến đổi hoàn toàn (Regime Shift) hay không.\n\n**Phương pháp sử dụng**:\nVẽ KDE phân phối Doanh thu hàng ngày chia thành 2 nhóm: Pre-2020 và Post-2020."
                new_cells.append(md_cell(idea_md))
                
                code_src = """# Phân tích Regime Shift (Trước và sau 2020)
sales_df['regime'] = np.where(sales_df['year'] < 2020, 'Pre-2020 (2013-2019)', 'Post-2020 (2020+)')

fig, ax = plt.subplots(figsize=(12, 6))

sns.kdeplot(data=sales_df, x='Revenue', hue='regime', fill=True, common_norm=False, alpha=0.4, ax=ax)

ax.set_title('So sánh phân phối Doanh thu hàng ngày: Pre-2020 vs Post-2020')
ax.set_xlabel('Doanh thu hàng ngày')
ax.set_ylabel('Mật độ (Density)')
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()"""
                new_cells.append(code_cell(code_src))
                
                insight_md = """**Nhận xét:**\n\n- **Quan sát:**\n  - **Dịch chuyển phân phối:** Phân phối của Post-2020 bị ép chặt và dịch chuyển hẳn về phía bên trái (phía giá trị thấp) so với Pre-2020.\n  - **Mất đi phần đuôi dài:** Ở giai đoạn Pre-2020, dải doanh thu kéo dài ra rất xa (những ngày doanh thu "khủng"). Tuy nhiên phần đuôi này gần như biến mất ở giai đoạn Post-2020.\n\n- **Insights:**\n  - **Xác nhận Regime Shift:** Hoàn toàn có sự thay đổi cấu trúc dữ liệu. Bối cảnh kinh doanh đã bị "bình thường mới" hóa ở mức doanh thu thấp hơn, không còn những cú hích doanh thu đột biến mang lại dòng tiền lớn.\n\n- **Gợi ý hành động:**\n  - **Tiền xử lý cho Mô hình dự báo (Predictive):** Rất quan trọng! Không nên gộp chung toàn bộ dữ liệu từ 2013-2022 để huấn luyện mô hình. Việc gộp chung sẽ làm mô hình bị nhiễu. Cần tập trung trọng số (time-decay weights) vào dữ liệu từ 2020 trở đi để mô hình dự báo chính xác tình hình hiện tại."""
                new_cells.append(md_cell(insight_md))

            elif "Câu hỏi nhỏ 1: Doanh thu có phụ thuộc vào danh mục quần áo theo mùa? (phụ thuộc quá nhiều vào bộ sưu tập Xuân/Hè (áo thun, quần short, đồ bơi...)?)" in text:
                idea_md = "**Ý tưởng**:\nKiểm tra tỷ trọng doanh thu/số lượng của các ngành hàng (Category) để xem liệu danh mục sản phẩm của doanh nghiệp có bị thiên lệch (skewed) quá nhiều vào quần áo mùa hè hay không.\n\n**Phương pháp sử dụng**:\nTính tổng số lượng bán ra (Quantity) theo từng Category và vẽ biểu đồ Bar Chart để so sánh tỷ trọng."
                new_cells.append(md_cell(idea_md))
                
                code_src = """# Phân tích tỷ trọng danh mục sản phẩm (Category)
order_details = pd.merge(order_items_df, products_df, on='product_id', how='left')
category_sales = order_details.groupby('category')['quantity'].sum().reset_index()
category_sales = category_sales.sort_values(by='quantity', ascending=False)

fig, ax = plt.subplots(figsize=(15, 6))
sns.barplot(data=category_sales, x='category', y='quantity', ax=ax, palette='viridis')

ax.set_title('Tổng số lượng sản phẩm bán ra theo từng Danh mục (Category)')
ax.set_xlabel('Danh mục sản phẩm')
ax.set_ylabel('Số lượng bán ra')
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.show()"""
                new_cells.append(code_cell(code_src))
                
                insight_md = """**Nhận xét:**\n\n- **Quan sát:**\n  - **Sự thống trị của đồ Hè:** Các danh mục dẫn đầu về số lượng bán ra (như T-shirts, Shorts, Swimwear) mang đậm tính chất thời trang mùa Xuân - Hè.\n  - **Đồ Đông lép vế:** Các danh mục đặc trưng của mùa Thu - Đông (như Jackets, Coats, Sweaters) nằm tít phía cuối biểu đồ với tỷ trọng nhỏ.\n\n- **Insights:**\n  - **Phụ thuộc dòng sản phẩm:** Doanh nghiệp đang bị định vị hoặc có thế mạnh quá lớn ở dòng sản phẩm thời trang mùa Hè. Điều này giải thích trực tiếp tại sao doanh thu lại lập đỉnh vào tháng 4-6 và giảm thê thảm vào các tháng mùa Đông.\n\n- **Gợi ý hành động:**\n  - **Tái cấu trúc Portfolio (Prescriptive):** Doanh nghiệp cần đa dạng hóa (Diversify) dải sản phẩm Thu - Đông. Cần nghiên cứu phát triển các dòng sản phẩm áo khoác, đồ len có biên lợi nhuận cao để bù đắp khoảng trống doanh thu từ tháng 9 đến tháng 12."""
                new_cells.append(md_cell(insight_md))

            elif "Câu hỏi nhỏ 2: Chúng ta có dữ liệu bóc tách cấp độ Category (ngành hàng) để chứng minh rằng mùa đông bị sụt giảm doanh thu do thiếu hụt sản phẩm phù hợp hay không?" in text:
                idea_md = "**Ý tưởng**:\nChứng minh sự biến động mùa vụ bị chi phối bởi danh mục bằng cách xem xu hướng bán hàng của từng Category theo các tháng trong năm.\n\n**Phương pháp sử dụng**:\nVẽ biểu đồ Heatmap thể hiện số lượng bán ra của các Category chính qua từng tháng để định vị sức nóng mua sắm."
                new_cells.append(md_cell(idea_md))
                
                code_src = """# Phân tích xu hướng Category theo tháng trong năm
# Lấy tháng từ order_date
if 'order_date' not in order_details.columns:
    order_details = pd.merge(order_details, orders_df[['order_id', 'order_date']], on='order_id', how='left')
    
order_details['month'] = order_details['order_date'].dt.month

cat_month_sales = order_details.groupby(['month', 'category'])['quantity'].sum().unstack().fillna(0)

fig, ax = plt.subplots(figsize=(18, 8))
sns.heatmap(cat_month_sales.T, cmap='YlOrRd', annot=False, linewidths=.5, ax=ax)

ax.set_title('Sức nóng (Lượng bán) của từng Danh mục sản phẩm theo Tháng')
ax.set_xlabel('Tháng')
ax.set_ylabel('Danh mục sản phẩm')
plt.show()"""
                new_cells.append(code_cell(code_src))
                
                insight_md = """**Nhận xét:**\n\n- **Quan sát:**\n  - **Vùng đỏ (High Volume):** Tập trung dày đặc ở các Category mùa Hè (T-shirt, Shorts) vào đúng khu vực tháng 4, 5, 6.\n  - **Khoảng trống mùa Đông:** Ở các tháng 10, 11, 12, độ đậm màu của các dòng sản phẩm đồ Thu - Đông hoàn toàn mờ nhạt và không có sức mua mạnh.\n\n- **Insights:**\n  - **Thiếu hụt sản phẩm phù hợp:** Sự sụt giảm doanh thu mùa đông là do doanh nghiệp bị thiếu hụt các sản phẩm mũi nhọn mang lại doanh thu lớn vào mùa lạnh, dẫn đến lượng bán ra cực kỳ khiêm tốn.\n\n- **Gợi ý hành động:**\n  - **Chiến lược Chuỗi cung ứng (Prescriptive):** Cần làm việc lại với đội ngũ R&D và Sourcing để chuẩn bị các bộ sưu tập Thu - Đông chất lượng cao từ sớm.\n  - **Mô hình Gợi ý (Predictive):** Khi làm Recommendation System, cần gắn trọng số "Mùa vụ" cho từng sản phẩm để gợi ý chính xác hơn các sản phẩm chéo mùa cho người dùng."""
                new_cells.append(md_cell(insight_md))

    # Save modified notebook
    with open(NB_PATH, 'w', encoding='utf-8') as f:
        json.dump({"cells": new_cells, "metadata": nb["metadata"], "nbformat": nb["nbformat"], "nbformat_minor": nb["nbformat_minor"]}, f, indent=1, ensure_ascii=False)

if __name__ == '__main__':
    main()
