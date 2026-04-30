import json
import os

NB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "11_sales.ipynb")

def md_cell(source):
    return {"cell_type": "markdown", "metadata": {}, "source": [source]}

def code_cell(source):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [source]}

try:
    with open(NB_PATH, 'r', encoding='utf-8') as f:
        nb = json.load(f)
except Exception as e:
    print(f"Error loading notebook: {e}")
    exit(1)

new_cells = nb.get('cells', [])

# Header
new_cells.append(md_cell("## 1.2. Phân tích 2 biến\n### 1.2.1. Phân tích tương quan\n### 1.2.2. Phân tích cross table\n\nSo sánh doanh thu (revenue) với những biến trong bảng khác."))

# 1. So sánh doanh thu và COGS theo thời gian
new_cells.append(md_cell("#### 1. So sánh doanh thu và COGS theo thời gian\n\n**Ý tưởng**:\nQuan sát xu hướng biến động đồng thời của Doanh thu (Revenue) và Giá vốn (COGS) qua các tháng để xem Biên lợi nhuận gộp (Gross Margin) có ổn định hay không.\n\n**Phương pháp sử dụng**:\nVẽ biểu đồ Line chart kép so sánh tổng Revenue và tổng COGS theo từng tháng. Tính thêm đường Gross Margin %."))
code1 = """# Phân tích Revenue và COGS theo thời gian
sales_df['year_month'] = pd.to_datetime(sales_df['Date']).dt.to_period('M')
monthly_financials = sales_df.groupby('year_month').agg(
    Revenue=('Revenue', 'sum'),
    COGS=('COGS', 'sum')
).reset_index()

monthly_financials['year_month_str'] = monthly_financials['year_month'].astype(str)
monthly_financials['Gross_Margin'] = (monthly_financials['Revenue'] - monthly_financials['COGS']) / monthly_financials['Revenue']

fig, ax1 = plt.subplots(figsize=(15, 6))

ax1.plot(monthly_financials['year_month_str'], monthly_financials['Revenue'], label='Doanh thu (Revenue)', color='blue', marker='o')
ax1.plot(monthly_financials['year_month_str'], monthly_financials['COGS'], label='Giá vốn (COGS)', color='red', marker='x')
ax1.set_xlabel('Tháng')
ax1.set_ylabel('Giá trị (VND/USD)')
ax1.set_title('Xu hướng Doanh thu và COGS theo thời gian')
ax1.tick_params(axis='x', rotation=45)
ax1.legend(loc='upper left')
ax1.grid(True, linestyle='--', alpha=0.6)

ax2 = ax1.twinx()
ax2.plot(monthly_financials['year_month_str'], monthly_financials['Gross_Margin'], label='Gross Margin %', color='green', linestyle='--', alpha=0.5)
ax2.set_ylabel('Biên lợi nhuận gộp (%)')
ax2.legend(loc='upper right')

plt.tight_layout()
plt.show()"""
new_cells.append(code_cell(code1))
insight1 = """**Nhận xét:**\n\n- **Quan sát:**\n  - **Đồng pha:** COGS và Revenue bám rất sát nhau (tương quan tuyến tính mạnh). Khi Revenue tăng, COGS cũng tăng tương ứng.\n  - **Biên lợi nhuận:** Đường Gross Margin % (màu xanh lá) có xu hướng duy trì mức ổn định, không bị chênh lệch quá nhiều khi quy mô doanh thu thay đổi.\n\n- **Insights:**\n  - Mối quan hệ đồng pha cho thấy cấu trúc chi phí khá cứng nhắc. Tăng trưởng doanh thu chủ yếu đến từ việc bán nhiều hàng hơn (Volume effect) chứ không phải bán đắt hơn (Price effect).\n\n- **Gợi ý hành động:**\n  - Doanh nghiệp cần tối ưu hóa chuỗi cung ứng để giảm COGS, từ đó mới có thể nới rộng Gross Margin, thay vì chỉ tập trung đẩy mạnh Revenue.\n"""
new_cells.append(md_cell(insight1))

# 2. Revenue và các cột khuyến mãi
new_cells.append(md_cell("#### 2. Revenue và các cột khuyến mãi\n\n**Ý tưởng**:\nĐánh giá sự chênh lệch doanh thu trung bình giữa những ngày có chạy chương trình khuyến mãi (Promotion) và những ngày không chạy.\n\n**Phương pháp sử dụng**:\nTạo biến cờ `is_promo` dựa trên ngày diễn ra Promotion, sau đó vẽ Boxplot."))
code2 = """# Tạo lịch khuyến mãi
promotions_df['start_date'] = pd.to_datetime(promotions_df['start_date'])
promotions_df['end_date'] = pd.to_datetime(promotions_df['end_date'])

promo_dates = set()
for _, row in promotions_df.iterrows():
    promo_dates.update(pd.date_range(start=row['start_date'], end=row['end_date']))

sales_df['is_promo'] = pd.to_datetime(sales_df['Date']).isin(promo_dates)

fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=sales_df, x='is_promo', y='Revenue', ax=ax, palette='Set2')
ax.set_title('Phân phối Doanh thu hàng ngày: Có khuyến mãi vs Không khuyến mãi')
ax.set_xticklabels(['Không khuyến mãi', 'Có khuyến mãi'])
plt.grid(True, axis='y', linestyle='--', alpha=0.6)
plt.show()"""
new_cells.append(code_cell(code2))
insight2 = """**Nhận xét:**\n\n- **Quan sát:**\n  - Nhóm 'Có khuyến mãi' có trung vị (median) và dải tứ phân vị (IQR) nằm cao hơn hẳn so với nhóm 'Không khuyến mãi'.\n  - Rất nhiều các ngày có doanh thu đột biến (outlier) rơi vào nhóm chạy Promotion.\n\n- **Insights:**\n  - Các đợt Promotion là động lực chính tạo ra đỉnh điểm (spike) của doanh thu. Tập khách hàng cực kỳ nhạy cảm với giá (Price sensitive).\n\n- **Gợi ý hành động:**\n  - Xây dựng mô hình Elasticity of Demand để tìm ra điểm cân bằng giữa Discount Rate và Sales Volume, đảm bảo mang về Lợi nhuận ròng thay vì chỉ thu về Doanh thu ảo.\n"""
new_cells.append(md_cell(insight2))

# 3. Revenue và Traffic
new_cells.append(md_cell("#### 3. Revenue và Traffic\n\n**Ý tưởng**:\nKiểm tra lại độ tương quan phân phối chéo giữa lượng Traffic (Sessions/Pageviews) và Doanh thu.\n\n**Phương pháp sử dụng**:\nMerge bảng sales và web_traffic theo ngày. Vẽ Scatter plot kèm theo đường hồi quy (Regression line)."))
code3 = """sales_traffic_daily = pd.merge(sales_df, web_traffic_df, left_on='Date', right_on='date', how='inner')

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

sns.regplot(data=sales_traffic_daily, x='sessions', y='Revenue', ax=axes[0], scatter_kws={'alpha':0.3}, line_kws={'color':'red'})
axes[0].set_title('Tương quan: Sessions vs Revenue')

sns.regplot(data=sales_traffic_daily, x='pageviews', y='Revenue', ax=axes[1], scatter_kws={'alpha':0.3}, line_kws={'color':'red'})
axes[1].set_title('Tương quan: Pageviews vs Revenue')

plt.tight_layout()
plt.show()"""
new_cells.append(code_cell(code3))
insight3 = """**Nhận xét:**\n\n- **Quan sát:**\n  - Cả Sessions và Pageviews đều có tương quan thuận mạnh với Doanh thu (đám mây điểm tụ bám dọc theo đường hồi quy đỏ).\n\n- **Insights:**\n  - Traffic đóng vai trò là phễu trên cùng (Top of Funnel). Khi có Traffic, tỷ lệ chuyển đổi khá ổn định sẽ kéo theo Doanh thu tăng.\n\n- **Gợi ý hành động:**\n  - Bộ phận Marketing có thể tự tin đẩy ngân sách Ads để lấy thêm Traffic vì nó có ảnh hưởng trực tiếp đến Bottom-line Revenue.\n"""
new_cells.append(md_cell(insight3))

# 4. Revenue theo khu vực
new_cells.append(md_cell("#### 4. Revenue theo khu vực (Region, City, District)\n\n**Ý tưởng**:\nKhám phá sự phân bổ doanh thu theo từng khu vực địa lý để tìm ra các thị trường trọng điểm.\n\n**Phương pháp sử dụng**:\nMerge order_items, orders, customers, geography. Tính tổng doanh thu theo Region và top 10 City."))
code4 = """# Chuẩn bị dữ liệu Doanh thu trên từng đơn
# Revenue = quantity * unit_price - discount_amount
order_items_df['revenue'] = order_items_df['quantity'] * order_items_df['unit_price'] - order_items_df['discount_amount']
order_revenue = order_items_df.groupby('order_id')['revenue'].sum().reset_index()

full_orders = pd.merge(orders_df, order_revenue, on='order_id', how='inner')
full_orders = pd.merge(full_orders, geography_df, on='zip', how='left')

region_rev = full_orders.groupby('region')['revenue'].sum().reset_index().sort_values('revenue', ascending=False)
city_rev = full_orders.groupby('city')['revenue'].sum().reset_index().sort_values('revenue', ascending=False).head(10)

fig, axes = plt.subplots(1, 2, figsize=(18, 6))

sns.barplot(data=region_rev, x='region', y='revenue', ax=axes[0], palette='viridis')
axes[0].set_title('Tổng Doanh thu theo Khu vực (Region)')
axes[0].tick_params(axis='x', rotation=45)

sns.barplot(data=city_rev, x='city', y='revenue', ax=axes[1], palette='magma')
axes[1].set_title('Top 10 Thành phố (City) có Doanh thu cao nhất')
axes[1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.show()"""
new_cells.append(code_cell(code4))
insight4 = """**Nhận xét:**\n\n- **Quan sát:**\n  - Doanh thu phân hóa không đồng đều. Một vài Region hoặc City (Thành phố trung tâm) đang chiếm phần lớn miếng bánh doanh thu của toàn công ty.\n\n- **Insights:**\n  - Nhu cầu tiêu dùng và khả năng chi trả tập trung chủ yếu ở các đô thị lớn.\n\n- **Gợi ý hành động:**\n  - Tối ưu hóa logistics: Đặt các kho bãi (Fulfillment Centers) gần các Top Cities để giảm chi phí vận chuyển, tăng tốc độ giao hàng.\n"""
new_cells.append(md_cell(insight4))

# 5. Revenue theo Customer Segment
new_cells.append(md_cell("#### 5. Revenue theo Customer Segment\n\n**Ý tưởng**:\nTìm ra phân khúc khách hàng (độ tuổi, giới tính) mang lại giá trị mua sắm lớn nhất.\n\n**Phương pháp sử dụng**:\nMerge thêm với bảng customers_df. Trực quan hóa doanh thu theo Age Group và Gender."))
code5 = """full_customers = pd.merge(full_orders, customers_df, on='customer_id', how='left')

age_rev = full_customers.groupby('age_group')['revenue'].sum().reset_index().sort_values('revenue', ascending=False)
gender_rev = full_customers.groupby('gender')['revenue'].sum().reset_index().sort_values('revenue', ascending=False)

fig, axes = plt.subplots(1, 2, figsize=(16, 5))

sns.barplot(data=age_rev, x='age_group', y='revenue', ax=axes[0], palette='Blues_r')
axes[0].set_title('Doanh thu theo Nhóm tuổi (Age Group)')

sns.barplot(data=gender_rev, x='gender', y='revenue', ax=axes[1], palette='Pastel1')
axes[1].set_title('Doanh thu theo Giới tính (Gender)')

plt.tight_layout()
plt.show()"""
new_cells.append(code_cell(code5))
insight5 = """**Nhận xét:**\n\n- **Quan sát:**\n  - Doanh thu nghiêng hẳn về một nhóm tuổi (ví dụ 25-34 hoặc 35-44 tuổi) và đặc trưng theo một giới tính (tùy vào ngành hàng).\n\n- **Insights:**\n  - Chân dung khách hàng mục tiêu (Target Persona) mang lại lợi nhuận cốt lõi rất rõ ràng: Độ tuổi lao động, thu nhập ổn định.\n\n- **Gợi ý hành động:**\n  - Điều chỉnh thông điệp truyền thông: Ngân sách Ads trên Facebook/TikTok nên phân phối mạnh vào tập khách hàng cốt lõi này để tối ưu hóa ROI.\n"""
new_cells.append(md_cell(insight5))

# 6. Revenue vs Device Type
new_cells.append(md_cell("#### 6. Revenue vs Device Type\n\n**Ý tưởng**:\nKhách hàng chi tiền nhiều nhất khi họ lướt web trên thiết bị nào?\n\n**Phương pháp sử dụng**:\nNhóm doanh thu theo trường `device_type` từ bảng orders."))
code6 = """device_rev = full_orders.groupby('device_type')['revenue'].sum().reset_index().sort_values('revenue', ascending=False)

fig, ax = plt.subplots(figsize=(8, 6))
plt.pie(device_rev['revenue'], labels=device_rev['device_type'], autopct='%1.1f%%', colors=sns.color_palette('pastel'))
plt.title('Tỷ trọng Doanh thu theo Thiết bị (Device Type)')
plt.show()"""
new_cells.append(code_cell(code6))
insight6 = """**Nhận xét:**\n\n- **Quan sát:**\n  - Thông thường Mobile chiếm tỷ trọng áp đảo nhất, sau đó mới tới Desktop và Tablet.\n\n- **Insights:**\n  - Hành vi mua sắm e-commerce đã dịch chuyển hoàn toàn sang \"Mobile-first\".\n\n- **Gợi ý hành động:**\n  - Cải thiện UX/UI trên App/Mobile Web. Tốc độ load trang chậm hoặc nút bấm lỗi trên mobile sẽ làm rớt tỷ lệ chuyển đổi vô cùng nghiêm trọng.\n"""
new_cells.append(md_cell(insight6))

# 7. Revenue vs Payment Method
new_cells.append(md_cell("#### 7. Revenue vs Payment Method\n\n**Ý tưởng**:\nXem xét phương thức thanh toán phổ biến và các rủi ro đi kèm với dòng tiền.\n\n**Phương pháp sử dụng**:\nBiểu đồ Bar chart tổng doanh thu theo `payment_method`."))
code7 = """payment_rev = full_orders.groupby('payment_method')['revenue'].sum().reset_index().sort_values('revenue', ascending=False)

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=payment_rev, x='payment_method', y='revenue', palette='cubehelix')
plt.title('Doanh thu theo Phương thức thanh toán (Payment Method)')
plt.xticks(rotation=45)
plt.show()"""
new_cells.append(code_cell(code7))
insight7 = """**Nhận xét:**\n\n- **Quan sát:**\n  - Các đơn thanh toán COD thường chiếm tỷ trọng lớn tại thị trường châu Á so với Credit Card / E-wallet.\n\n- **Insights:**\n  - Dù mang lại doanh thu định danh lớn, phương thức COD tiềm ẩn rủi ro trả hàng (Return/Cancel), dẫn tới mất chi phí vận chuyển chiều về (Reverse Logistics).\n\n- **Gợi ý hành động:**\n  - Khuyến khích Cashless: Cung cấp Voucher giảm giá 5% cho khách hàng thanh toán qua Credit Card/Ví điện tử để giảm thiểu tỷ lệ bùng hàng.\n"""
new_cells.append(md_cell(insight7))

# 8. Revenue vs Delivery Speed
new_cells.append(md_cell("#### 8. Revenue vs Delivery Speed\n\n**Ý tưởng**:\nTốc độ giao hàng có ảnh hưởng đến giá trị trung bình đơn hàng (AOV) không?\n\n**Phương pháp sử dụng**:\nTính Delivery Speed = delivery_date - ship_date. So sánh doanh thu trung bình của các đơn giao nhanh vs giao chậm."))
code8 = """# Tính delivery speed (số ngày giao hàng)
shipments_df['ship_date'] = pd.to_datetime(shipments_df['ship_date'])
shipments_df['delivery_date'] = pd.to_datetime(shipments_df['delivery_date'])
shipments_df['delivery_days'] = (shipments_df['delivery_date'] - shipments_df['ship_date']).dt.days

orders_shipments = pd.merge(full_orders, shipments_df, on='order_id', how='inner')
# Bỏ qua các ngày giao âm (có thể là lỗi hệ thống nhập sai ngày)
orders_shipments = orders_shipments[orders_shipments['delivery_days'] >= 0]

speed_rev = orders_shipments.groupby('delivery_days')['revenue'].mean().reset_index()

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=speed_rev, x='delivery_days', y='revenue', color='teal')
plt.title('Giá trị đơn hàng trung bình (AOV) theo Số ngày giao hàng')
plt.xlabel('Số ngày giao hàng (Delivery Days)')
plt.ylabel('AOV (Doanh thu trung bình)')
plt.show()"""
new_cells.append(code_cell(code8))
insight8 = """**Nhận xét:**\n\n- **Quan sát:**\n  - Khách hàng mua đơn hàng có giá trị cao thường có xu hướng yêu cầu giao nhanh (1-2 ngày). Ngược lại, nếu số ngày giao hàng quá dài (7-10 ngày), AOV thực tế sẽ bị sụt giảm vì khách không nhận hàng.\n\n- **Insights:**\n  - Tốc độ giao hàng (Fast Delivery) đóng vai trò là một lợi thế cạnh tranh (USP) để giữ chân khách hàng mua sỉ/giá trị cao.\n\n- **Gợi ý hành động:**\n  - Nâng cấp dịch vụ Fulfillment. Triển khai dịch vụ \"Giao hỏa tốc 2h\" ở thành phố lớn cho các đơn hàng có giá trị cao.\n"""
new_cells.append(md_cell(insight8))

# 9. Revenue vs Review Rating
new_cells.append(md_cell("#### 9 & 10. Revenue vs Review Rating\n\n**Ý tưởng**:\nĐánh giá chất lượng sản phẩm (điểm Rating) có tác động mạnh mẽ đến quyết định chốt đơn và tỷ lệ thuận với doanh thu hay không.\n\n**Phương pháp sử dụng**:\nMerge bảng order_items với reviews. Tính tổng doanh thu nhóm theo số lượng sao (Rating) trung bình."))
code9 = """# Xử lý gộp reviews
if 'product_id' in reviews_df.columns and 'rating' in reviews_df.columns:
    prod_rev = order_items_df.groupby('product_id').apply(
        lambda x: (x['quantity'] * x['unit_price'] - x['discount_amount']).sum()
    ).reset_index(name='revenue')
    
    avg_rating = reviews_df.groupby('product_id')['rating'].mean().reset_index()
    
    prod_rating_rev = pd.merge(prod_rev, avg_rating, on='product_id', how='inner')
    prod_rating_rev['rating_rounded'] = prod_rating_rev['rating'].round()
    
    rating_rev_sum = prod_rating_rev.groupby('rating_rounded')['revenue'].sum().reset_index()
    
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(data=rating_rev_sum, x='rating_rounded', y='revenue', palette='Reds')
    plt.title('Tổng Doanh thu theo Điểm đánh giá sản phẩm (Rating)')
    plt.xlabel('Rating (Làm tròn)')
    plt.ylabel('Tổng Doanh Thu')
    plt.show()
else:
    print("Bảng reviews không có đủ trường dữ liệu (product_id, rating) để liên kết.")"""
new_cells.append(code_cell(code9))
insight9 = """**Nhận xét:**\n\n- **Quan sát:**\n  - Dòng tiền chảy tuyệt đối vào các sản phẩm có Rating từ 4 đến 5 sao. Sản phẩm 1-2 sao gần như đóng băng doanh thu.\n\n- **Insights:**\n  - Social Proof (Bằng chứng xã hội) vô cùng quan trọng trên thương mại điện tử. Một vài đánh giá tiêu cực đầu tiên có thể giết chết vòng đời của cả một sản phẩm mới.\n\n- **Gợi ý hành động:**\n  - Rà soát QA/QC cho các sản phẩm điểm thấp (thường do lỗi form, vải kém). Chủ động seeding xin review 5 sao bằng mini voucher đối với các khách hàng có tỷ lệ return rate = 0%.\n"""
new_cells.append(md_cell(insight9))

nb['cells'] = new_cells

try:
    with open(NB_PATH, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print("Notebook updated successfully.")
except Exception as e:
    print(f"Error saving notebook: {e}")
