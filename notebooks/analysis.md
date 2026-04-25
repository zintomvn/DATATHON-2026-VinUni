# Phân tích Chi tiết Notebook: preprocess_eda.ipynb

## Mục tiêu tổng thể
Notebook này thực hiện **Data Preprocessing & Exploratory Data Analysis (EDA)** cho dataset E-Commerce Fashion Operations (Vietnam). Mục tiêu chính:
1. Nạp và chuẩn hóa dữ liệu từ thư mục `data/`
2. Kiểm tra chất lượng dữ liệu (missing, duplicates, outliers, business rules)
3. Tạo các bảng phân tích bằng cách join nhiều bảng
4. Thực hiện EDA theo 4 tầng: **Descriptive → Diagnostic → Predictive → Prescriptive**
5. Chuẩn bị dữ liệu cho Tableau/Power BI

---

## PHẦN 1: Khởi tạo và Cấu hình

### Hàm định dạng số (thousands separator)
**Hàm `_fmt_thousands(x, pos)`**:
- Format trục số với dấu phân cách hàng nghìn (1,000).
- **Ý nghĩa**: Biểu đồ dễ đọc, hiển thị số lớn (doanh thu, quantity).

**Hàm `format_axis_thousands(ax, axis="y")`**:
- Format trục tọa độ (x/y/both) đồng bộ.
- **Ý nghĩa**: Professional visualization consistency.

**Hàm `beautify_ax(ax, grid=True)`**:
- Thêm grid, set font size, loại bỏ spines.
- **Ý nghĩa**: Làm đẹp trục cho tất cả plots.

### Hàm xử lý Date columns
**Hàm `_parse_dates_inplace(df)`**:
- Tự động nhận diện cột có tên chứa "date" (order_date, Date, v.v.)
- Dùng `pd.to_datetime(errors="coerce")` → lỗi thành NaT.
- **Ý nghĩa**: Đảm bảo tất cả cột ngày có kiểu datetime, sẵn sàng cho time-series và joins.

### Hàm làm sạch Text columns
**Hàm `_strip_object_columns_inplace(df)`**:
- Trim whitespace với `.str.strip()`
- Empty string → `pd.NA`
- **Ý nghĩa**: Giảm noise, tránh categorical "  " khác với "".

### Hàm profiling cột
**Hàm `profile_table(df, table_name)`**:
**Output columns**:
- `table`, `column`, `dtype`, `n` (tổng dòng)
- `missing_n`, `missing_pct` (tỷ lệ missing)
- `nunique` (số giá trị unique)
- `sample_values` (3 giá trị mẫu)

**Ý nghĩa**:
- Quick data quality overview mỗi bảng
- Phát hiện cột nhiều missing, high-cardinality
- Spot noise qua sample values
- Sort theo `missing_pct` để ưu tiên xử lý.

---

## PHẦN 2: Data Loading & Preprocessing

### Hàm `load_all_tables(data_dir)`
**Mục đích**: Load toàn bộ CSV files vào dict `tables`.

**Các bước**:
1. `glob("*.csv")` lấy tất cả CSV files.
2. Đọc từng file với `pd.read_csv`.
3. Áp dụng `_parse_dates_inplace` và `_strip_object_columns_inplace`.
4. Lưu vào dict với key = filename stem.

**Output**: Dict chứa 12 bảng: customers, orders, products, promotions, v.v.

**Ý nghĩa Business**:
- Single source of truth cho toàn bộ dataset.
- Chuẩn hóa Date columns → sẵn sàng time-series.
- Làm sạch text → giảm noise cho categorical analysis.

**Console Output**:
```
Loaded tables
customers        shape=(121930, 7)
geography        shape=(39948, 4)
inventory        shape=(60247, 17)
order_items      shape=(714669, 7)
orders           shape=(646945, 8)
...
```

---

## PHẦN 3: Data Quality & Integrity Checks

### 3.1 Column Profiling Summary
- **File output**: `outputs/column_profile_all_tables.csv`
- **Ý nghĩa**: Document data quality cho team và judges.
- Dùng làm input cho Tableau/Power BI dashboard.

### 3.2 Missingness Hotspots
- Show top 25 columns có `missing_pct > 0`.
- **Ý nghĩa**: Ưu tiên treatment (imputation vs drop), phát hiện missing pattern.

### 3.3 Duplicate Rows
- Kiểm tra toàn bộ row trùng lặp trong mỗi bảng.
- **Ý nghĩa**: Đảm bảo data integrity, nếu có duplicate → ETL lỗi hoặc double entry.

### 3.4 Primary Key & Composite Key Checks
**Hàm `check_key(df, key_cols)`**:
- Output: `null_key_rows`, `dup_key_rows`, `unique_ratio`.
- **EXPECTED_KEYS** theo `DATA.md`:
  - Simple PK: `products[product_id]`, `customers[customer_id]`
  - Composite PK: `order_items[order_id, product_id]`, `web_traffic[date, traffic_source]`

**Ý nghĩa quan trọng**:
- PK phải unique & not-null → đảm bảo row identification.
- Nếu `unique_ratio < 1` → data integrity issue, joins sẽ tạo duplicate rows.
- Ví dụ: `order_items` nếu có 2 row cùng `(order_id, product_id)` → duplicate line items.

**Console Output**:
```
Expected key checks
[table, key, null_key_rows, dup_key_rows, unique_ratio]
```

### 3.5 Foreign Key Orphan Check
**Hàm `fk_orphans(child_df, child_col, parent_df, parent_col)`**:
- Tìm child values không tồn tại trong parent.
- `allow_null=True`: bỏ qua NULL (nếu cho phép nullable).
- Output: `orphan_n`, `orphan_pct`.

**Ví dụ**:
- `orders.customer_id` phải tồn tại trong `customers.customer_id`.
- `order_items.product_id` phải tồn tại trong `products.product_id`.

**Ý nghĩa Business**:
- **Orphan orders**: Không biết khách hàng nào → không phân tích customer behavior.
- **Orphan order_items**: Không biết sản phẩm → không phân tích product performance.
- `orphan_pct` cao có thể do data sync delay, entry error.

**Console Output**:
```
Foreign key checks
[relation, child_col, parent_col, child_n, orphan_n, orphan_pct]
```

### 3.6 Business Rule Validation

#### (a) Pricing: `cogs < price`
- **Logic**: COGS phải nhỏ hơn giá bán, nếu không thì lỗ.
- **Check**: `products.query("cogs >= price")`
- **Output**: Số violations.

#### (b) Promotions: `start_date <= end_date`
- **Logic**: Promotion không thể bắt đầu sau khi kết thúc.
- **Check**: `promotions[promotions["start_date"] > promotions["end_date"]]`

#### (c) Shipments
- `shipping_fee >= 0` (không âm).
- `delivery_date >= ship_date` (giao sau khi gửi).

#### (d) Order Items
- `quantity > 0`, `unit_price >= 0`, `discount_amount >= 0`.

#### (e) Discount Formula Sanity Check (PHẦN QUAN TRỌNG)
**Mục đích**: Kiểm tra tính đúng đắn của công thức giảm giá theo `DATA.md`.

**Bước 1**: Chỉ lấy rows có **exactly 1 promo** (có `promo_id` nhưng không có `promo_id_2`).

**Bước 2**: Merge với `promotions` để lấy `promo_type` và `discount_value`.

**Bước 3**: Tính expected discount theo rule:
- `promo_type` chứa "percentage": `expected = quantity * unit_price * (discount_value/100)`
- `promo_type` là fixed amount: `expected = quantity * discount_value`

**Bước 4**: Tính relative error:
```python
discount_rel_err = |actual - expected| / expected
```

**Threshold**: Flag nếu `discount_rel_err > 0.05` (5% error).

**Ý nghĩa**:
- Đảm bảo **accounting accuracy**.
- Phát hiện lỗi trong ETL hoặc business logic implementation.
- Quan trọng cho financial reporting và audit.

**Output Console**:
```
Discount formula check (1 promo only)
Rows checked: 276,110
Potential mismatches (>5% rel err): 0
```
→ Data **clean** theo discount formula.

---

## PHẦN 4: Build Analysis-Ready Datasets (Joins)

### 4.1 Orders Enriched (Order-level Fact Table)
**Base**: `orders` (646,945 rows, 8 columns).

**Các joins**:
1. **Delivery Geography**: `orders.merge(geography, left_on="delivery_zip", right_on="zip")`
   - Rename columns: `city` → `delivery_city_geo`, `region` → `delivery_region`
2. **Customer Info**: `orders.merge(customers, on="customer_id")`
   - Rename: `customers.zip` → `customer_zip`, `city` → `customer_city`
3. **Customer Geography**:Merge `customers_enriched` với `geography` bằng `customer_zip`.
4. **Payments**: `orders.merge(payments, on="order_id")` (1:1 expected).
5. **Shipments**: `orders.merge(shipments, on="order_id")`.
6. **Derived**: `shipping_lead_time_days = delivery_date - ship_date`.

**Kết quả**: `orders_enriched` shape = **(646945, 27)**.

**Ý nghĩa Business**:
- Unified order view: delivery location, customer demographics, payment, shipping.
- Dùng cho: funnel analysis, delivery performance, customer segmentation.

### 4.2 Line Items Enriched (Line-item-level Fact Table)
**Base**: `order_items` (714,669 rows, 7 columns).

**Các joins**:
1. **Products**: `line_items.merge(products, on="product_id")`
   - Thêm: category, segment, size, color, price, cogs.
2. **Promotions × 2**:
   - `promo1`: `.merge(promotions.add_prefix("promo1_"), left_on="promo_id", right_on="promo1_promo_id")`
   - `promo2`: tương tự với `promo_id_2`.
   - **Lý do**: mỗi line-item có thể có 2 promotions (stackable).
3. **Derived Financial Metrics**:
   ```
   list_price = quantity × unit_price
   gross_revenue = list_price
   discount_rate = discount_amount / list_price (nếu list_price > 0)
   returns_amount = sum(refund_amount) by (order_id, product_id)
   sales_allowance = 0 (fallback nếu chưa có cột riêng)
   net_revenue = gross_revenue - returns_amount - discount_amount - sales_allowance
   cogs_total = quantity × cogs
   gross_profit = net_revenue - cogs_total
   gross_margin = gross_profit / net_revenue (nếu net_revenue > 0)
   ```
4. **Order-level Context**: Merge `orders_enriched` (chọn columns quan trọng):
   - Date/status/payment_method/device_type/order_source
   - Geography: `delivery_region`, `delivery_city_geo`, `customer_region`
   - Customer: `gender`, `age_group`, `acquisition_channel`
   - Financial: `payment_value`, `installments`, `shipping_fee`, `shipping_lead_time_days`

**Kết quả**: `line_items` shape = **(714669, 56)**.

**Ý nghĩa Business**:
- **Granular nhất**: mỗi row = 1 product trong 1 order.
- Phân tích được: product performance, discount effectiveness, category trends, customer-product relationship.
- Dùng cho: profitability analysis, inventory forecasting, promotion ROI.

**Sample output row** (order_id=1):
| order_id | product_id | quantity | unit_price | discount_amount | category | segment | list_price | net_revenue | gross_profit | order_date | delivery_region | ... |
|----------|------------|----------|------------|-----------------|----------|---------|------------|-------------|--------------|------------|-----------------|-----|
| 1        | 2400       | 7        | 1,138.22   | 0.00            | GenZ     | Trendy  | 7,967.54   | 7,967.54    | 590.95       | 2012-07-04 | East            | ... |

### 4.3 Returns Enriched
**Base**: `returns` (39,943 rows).

**Join**: `returns.merge(line_items, on=["order_id", "product_id"])`.
- Thêm toàn bộ product info, order info, customer info.

**Kết quả**: `returns_enriched` shape = **(39,943, 61)**.

**Ý nghĩa**:
- Return analysis đầy đủ.
- Tính return rate theo: product (size/color/category), region, payment method, channel.
- Root-cause: Do size? Quality? Late delivery? Wrong item?

**Sample** (return_id=RET-000001):
- Order 2, product 609 (SaigonFlex UC-74), return_reason: `late_delivery`, quantity 6/7.
- Refund amount: 52,458 VND.

### 4.4 Aggregates for BI Tools

#### Daily KPIs
```python
daily_kpis = line_items.groupby("order_date").agg(
    orders=("order_id", "nunique"),
    items=("product_id", "count"),
    units=("quantity", "sum"),
    net_revenue=("net_revenue", "sum"),
    discount_amount=("discount_amount", "sum"),
    gross_profit=("gross_profit", "sum")
)
```
**File**: `outputs/daily_kpis.csv`

**Mẫu**:
| order_date | orders | items | units | net_revenue | discount_amount | gross_profit |
|------------|--------|-------|-------|-------------|-----------------|--------------|
| 2012-07-04 | 162    | 174   | 777   | 5,123,548   | 0               | 1,140,557    |

**Ý nghĩa**: Time-series dataset cho Tableau/Power BI, theo dõi business health theo ngày.

#### Daily KPIs + Web Traffic
- Merge `daily_kpis` với aggregated `web_traffic` (sessions, visitors, bounce_rate).
- **File**: `outputs/daily_kpis_with_traffic.csv`.
- **Ý nghĩa**: Leading indicator analysis (traffic → revenue).

#### Geo Orders
```python
geo_orders = orders_enriched.groupby(["delivery_region", "delivery_city_geo"])\
    .agg(orders=("order_id", "nunique"))
```
**File**: `outputs/geo_orders.csv`

**Mẫu**:
| delivery_region | delivery_city_geo | orders |
|-----------------|-------------------|--------|
| East            | Son Tay           | 22,473 |
| East            | Thai Nguyen       | 21,931 |
| East            | Nam Dinh          | 21,764 |

**Ý nghĩa**: Map visualization, identify key delivery cities.

#### Region KPIs
```python
region_kpis = line_items.groupby("delivery_region").agg(
    orders=("order_id", "nunique"),
    net_revenue=("net_revenue", "sum"),
    gross_profit=("gross_profit", "sum")
)
```
**File**: `outputs/region_kpis.csv`

**Mẫu**:
| delivery_region | orders   | net_revenue    | gross_profit  |
|-----------------|----------|----------------|---------------|
| East            | 294,612  | 7,291,150,819  | 695,648,304   |
| Central         | 184,691  | 4,719,491,268  | 443,060,931   |
| West            | 167,642  | 3,670,227,178  | 378,709,512   |

**Ý nghĩa**: Regional performance summary, strategic planning.

---

## PHẦN 5: UNIVARIATE EDA (Phân tích 1 biến)

### 5.1 Categorical — Orders Overview

#### Order Status Distribution
**Biểu đồ**: Countplot (`order_status`).

**Các trạng thái có thể có**:
- `delivered`: Đã giao thành công.
- `returned`: Đã trả hàng.
- `processing`, `shipped`, `cancelled`: Khác.

**Business Metrics**:
- **Delivery rate** = delivered / total
- **Return rate** = returned / total (KPI quan trọng)

**Actionable insights**:
- Nếu return rate > 10% → investigate returns section.
- Nếu `cancelled` cao → checkout flow problem?

#### Payment Method Distribution
**Biểu đồ**: Countplot (`payment_method`).

**Phương thức có thể có**: credit_card, cod (cash on delivery), e-wallet, bank_transfer.

**Business insights**:
- COD thường có **return rate cao hơn** (khách hàng không trả tiền trước, ít commitment).
- Credit_card users có thể là higher-value customers?
- Fraud detection: chargeback rate theo payment method.

#### Order Source Distribution (Top 10)
**Biểu đồ**: Countplot top 10 `order_source`.

**Nguồn có thể có**: paid_search, direct, social_media, organic_search, email_campaign, referral.

**Business insights**:
- **Conversion rate** theo source: traffic lớn nhưng conversion thấp → waste money.
- **Customer quality**: organic_search có mean payment_value cao? (xem ở bivariate).
- Marketing budget allocation: prioritize high-converting, high-LTV sources.

### 5.2 Numeric — Financial Metrics

#### Distribution of `payment_value` (orders_enriched)
**Biểu đồ**: Histogram + KDE.

**Insight mong đợi**:
- **Right-skewed**: majority small orders, few large orders.
- **Outliers**: orders với payment_value rất cao (VIP? corporate?).
- **Peak modes**: có thể thấy peaks theo price points (psychological pricing: 500K, 1M, 2M VND).

**Business**:
- **Tail pricing strategy**: Sản phẩm nào ở tail (high-value)? Cần personal sales?
- **Customer segmentation**: Dùng payment_value để phân分段 (quartiles): low/medium/high-value.

#### Distribution of `discount_rate` (line_items)
**Biểu đồ**: Histogram (clipped at p99).

**Insight**:
- Nếu histogram tập trung ở 0 → ít discounts.
- Nếu peak ở 10-20% → standard discount depth.
- Nếu có spike ở 50%+ → clearance sale hoặc heavy promotions (margin risk).

**Business**:
- Discount strategy benchmark.
- Nếu discount_rate cao nhưng volume không tăng → không effective.

#### Distribution of `gross_profit` (line_items)
**Biểu đồ**: Histogram (winsorized 1%-99%).

**Insight**:
- **Negative profits**: losing money products/orders → cần review.
- **Bimodal distribution**: có thể là 2 segments (low-margin vs high-margin products).
- Mode (peak) ở đâu? Profitability issue nếu mode < 0.

**Business**:
- Product portfolio optimization: Kill low-profit products.
- **Gross margin %** = gross_profit / net_revenue, cần xem distribution.

### 5.3 Returns Analysis

#### Top 10 Return Reasons
**Biểu đồ**: Countplot (`return_reason`).

**Các reason phổ biến**:
- `wrong_size`, `wrong_color`, `defective`, `late_delivery`, `changed_mind`.

**Business Action**:
1. **wrong_size**: Cải thiện size guide, virtual try-on, customer reviews.
2. **wrong_color**: Better product photos, color description.
3. **defective**: QC improvement, supplier quality.
4. **late_delivery**: Logistics partner negotiation, warehouse efficiency.
5. **changed_mind**: Strict return policy? Better product info?

---

## PHẦN 6: BIVARIATE EDA (Phân tích 2 biến)

### 6.1 Numeric ↔ Numeric: Pearson Correlation Matrix

**Các numeric variables được chọn**:
`quantity, unit_price, discount_amount, discount_rate, list_price, net_revenue, gross_profit, gross_margin, shipping_fee, shipping_lead_time_days, payment_value, installments`

**Correlation Matrix output** (tóm tắt):

| Pair                  | Correlation | Ý nghĩa                                                |
|-----------------------|-------------|--------------------------------------------------------|
| list_price ↔ net_revenue | 0.99    | Vẫn gần tuyến tính vì net bắt đầu từ list, rồi trừ discounts/returns.                |
| list_price ↔ unit_price | 0.76    | Expensive products có unit_price cao.                  |
| unit_price ↔ payment_value | 0.71 | Customer trả nhiều khi mua sản phẩm đắt.              |
| discount_amount ↔ discount_rate | 0.61 | Sản phẩm giảm giá lớn thường có % cao.              |
| gross_profit ↔ gross_margin | 0.70 | Profitable products có good margin %.

**Ý nghĩa Statistical**:
- **Pearson correlation**: đo linear relationship (-1 đến 1).
- **Significance test**: với n=714,669, almost all correlations are statistically significant (p-value ≈ 0).
- **Causation ≠ correlation**: High correlation không có nghĩa cause-effect.

**Business Applications**:
1. **Multicollinearity check** (cho regression):
   - `list_price` và `net_revenue` quá cao (0.99) → nếu dùng cả 2 làm features, sẽ bị multicollinearity.
   - `gross_profit` và `gross_margin` correlation 0.7 → cẩn thận khi chọn features.
   
2. **Pricing strategy**:
   - `unit_price` và `quantity` correlation -0.00 → không có relationship.
   - Có thể tăng giá mà không giảm quantity? (elasticity test cần thêm).

3. **Discount effectiveness**:
   - `discount_rate` và `net_revenue` correlation -0.20 → negative.
   - Discount nhiều → revenue giảm (dù quantity có thể ↑).
   - Trade-off: volume vs margin.

**Heatmap**: Visualize matrix với màu coolwarm (red=positive, blue=negative).

**Top 10 strongest absolute correlations** (output):
```
list_price     net_revenue     1.00
net_revenue    list_price      1.00
payment_value  net_revenue     0.95
net_revenue    payment_value   0.95
payment_value  list_price      0.95
list_price     payment_value   0.95
unit_price     list_price      0.76
unit_price     net_revenue     0.76
net_revenue    unit_price      0.76
unit_price     net_revenue     0.76
```

**Comment**: `payment_value` highly correlated với `list_price` và `net_revenue` → payment_value là proxy cho order total value.

**Scatter Plot Example**: `discount_rate vs net_revenue`
- **Pearson r = -0.20** (moderate negative).
- **Interpretation**: Khi discount rate tăng, net_revenue giảm (discount depth hurts revenue).
- **Outliers**: Có thể có orders với discount cao nhưng net_revenue vẫn cao (large quantity).
- **Business**: Tìm optimal discount rate để maximize profit, không phải revenue.

### 6.2 Numeric ↔ Categorical: Pivot & Boxplot

**Example**: `net_revenue by order_source` (top 8 sources).

**Pivot Table**:
| order_source   | n (orders) | mean (VND) | median (VND) |
|----------------|------------|------------|--------------|
| direct         | 57,329     | 22,049     | 14,657       |
| paid_search    | 156,500    | 21,993     | 14,612       |
| social_media   | 143,306    | 21,919     | 14,422       |
| organic_search | 200,429    | 21,880     | 14,481       |

**Insight**:
- `direct` source có **mean cao nhất** (22,049) → khách hàng trực tiếp chi tiêu nhiều hơn.
- `organic_search` có **volume lớn nhất** (200K orders) nhưng mean thấp → nhiều small orders.
- Median ~14-16K cho tất cả sources → phân phối right-skewed (few large orders).
- Standard deviation (không hiển thị) sẽ cho biết variability.

**Boxplot** (without outliers):
- So sánh median, IQR (interquartile range).
- Source nào có spread lớn? (có thể do promotions hoặc product mix khác nhau).
- Outliers bị hide để focus trên distribution chính.

**Business Application**:
- **Marketing ROI**: `direct` likely highest-quality traffic → protect/expand.
- **Paid_search**: Volume cao nhưng mean thấp → optimize bidding for higher-value keywords.
- **Social media**: Volume cao, mean thấp → có thể là awareness channel, không phải revenue driver.

### 6.3 Categorical ↔ Categorical: Chi-square & Cramer's V

**Example**: `order_status` × `payment_method`.

**Chi-square test**:
- **H0 (null hypothesis)**: order_status và payment_method độc lập (không liên quan).
- **H1**: Có association.
- **Output**: chi2=9478.42, dof=20, p-value=0 → **Reject H0** → có statistically significant relationship.

**Cramer's V**: 0.060 → **very weak association** (thang 0-1: 0.1 small, 0.3 medium, 0.5 large).

**Paradox**: p-value rất nhỏ (significant) nhưng effect size (Cramer's V) rất nhỏ.
**Nguyên nhân**: Sample size lớn (n ~ 646K) → dễ detect tiny differences as "significant".

**Heatmap**: Row-normalized confusion matrix → `P(payment_method | order_status)`.
- Cell = % orders trong status X dùng payment method Y.
- Ví dụ: Trong `returned` orders, % COD có cao hơn `delivered` không?

**Business Insight**:
- Mặc dù có statistical significance, association yếu.
- Order status phụ thuộc vào nhiều factors khác (product, shipping speed) hơn payment method.
- **Practical significance** > statistical significance: liệu có đáng để thay đổi business strategy?

---

## PHẦN 7: TIME SERIES & GEOGRAPHY

### 7.1 Daily KPIs Time Series

**Code**: `daily_kpis` grouped by `order_date`, lineplot `net_revenue` theo thời gian.

**Features**:
1. **Daily net_revenue** (tính từ `line_items`).
2. **Overlay official_revenue** (từ `sales.csv`) để validation.
3. **Monthly aggregation**: `dt.to_period('M')` → nhóm theo tháng.
   - X-axis: year-month (interval 6 months để dễ đọc).

**Insight mong đợi**:
- **Overall trend**: Tăng/đi ngang/giảm? (Có seasonality?)
- **Seasonality**: 
  - Peak vào Tết (Jan-Feb)? 
  - Black Friday (November)? 
  - Back-to-school (August)?
- **Weekly pattern**: Có cyclic theo ngày trong tuần? (cần resample weekly).

**Validation check**:
- So sánh `net_revenue` (tính từ line_items) với `official_revenue` (sales.csv).
- Nếu khác biệt lớn → reconciliation issue cần investigate (có thể do return adjustments?).

**Business uses**:
- Forecasting next quarter revenue.
- Seasonality adjustment cho planning (inventory, staffing).
- Detect anomalies (spike/drop) → investigate events.

### 7.2 Web Traffic as Leading Indicator

**Logic**: Web traffic (sessions, visitors) có thể **dẫn đầu** revenue (leading indicator).

**Code**:
1. Aggregate `web_traffic` by date: sum(sessions), sum(unique_visitors), avg(bounce_rate).
2. Merge `traffic_daily` với `daily_kpis` on `order_date`.
3. Tính Pearson correlation: `corr(sessions, net_revenue)`.

**Output**: `Pearson corr(sessions, net_revenue) = 0.328`

**Interpretation**:
- **Moderate positive correlation** (0.3-0.5 là medium).
- Sessions tăng → net_revenue tăng (không phải 1:1).
- **Leading indicator?** Traffic hôm nay có thể lead revenue trong 1-7 ngày tới? Cần **lag analysis** (shift sessions by 1d, 3d, 7d).

**Scatter plot**: Sessions vs net_revenue (sample 2000 points).
- Visualize relationship, outliers.

**Business**:
- **Marketing Attribution**: Traffic nào convert tốt nhất? (sessions → orders)
- Nếu traffic tăng nhưng revenue không tăng → **conversion rate problem** (checkout friction, product issues).
- Budget allocation: Invest in channels với high traffic-revenue correlation.

### 7.3 Geographic Analysis

#### Region KPIs (from `line_items.groupby("delivery_region")`)

**Data**:
| Region  | Orders   | Net Revenue (VND) | Gross Profit (VND) |
|---------|----------|-------------------|--------------------|
| East    | 294,612  | 7,291,150,819     | 695,648,304        |
| Central | 184,691  | 4,719,491,268     | 443,060,931        |
| West    | 167,642  | 3,670,227,178     | 378,709,512        |

**Derived Metrics** (tính thủ công):
- **East**: 
  - Avg order value = 7,291M / 294,612 ≈ 24,740 VND
  - Profit margin = 695M / 7,291M ≈ **9.5%**
- **Central**: Avg order = 25,546 VND, Margin = **9.4%**
- **West**: Avg order = 21,896 VND, Margin = **10.3%** → highest margin!

**Insight**:
1. **East dominates**: ~34% orders, ~39% revenue, ~37% profit.
2. **West có profit margin cao nhất** (10.3%) dù avg order thấp → cost control tốt? Hoặc product mix khác?
3. **Central**: Volume tốt nhưng profit margin thấp nhất → cần cắt giảm cost hoặc tăng price?

**Visualization**: Barplot `net_revenue by region`.

**Business Actions**:
1. **East (Focus market)**: Đảm bảo inventory đầy đủ, marketing aggressive.
2. **Central**: Tìm cách tăng margin (bundling, premium products).
3. **West**: Học tập best practices, replicate成功.
4. **Logistics**: Kiểm tra shipping_cost theo region, tối ưu warehouse locations.

**Further analysis** (chưa thấy trong code):
- **City-level**: Which cities in East are top? (Hanoi, HCMC?)
- **Customer vs Delivery region**: Are they same? (Customer from Hanoi but delivery to other province? → corporate gifts?)

---

## PHẦN 8: 4-TIER INSIGHT TEMPLATE

Notebook cung cấp **template** để ghi insight sau mỗi chart:

```
- **Descriptive (What happened?)**: [Số liệu/trends]
- **Diagnostic (Why did it happen?)**: [Nguyên nhân/hypothesis]
- **Predictive (What is likely to happen?)**: [Forecast nếu trend tiếp tục]
- **Prescriptive (What should we do?)**: [Actionable recommendation]
```

**Ví dụ với return_analysis**:
- **Descriptive**: 15% orders bị return, top reason: wrong_size (40%), late delivery (25%).
- **Diagnostic**: Size chart không chính xác? Logistics partner chậm? Product quality issue?
- **Predictive**: Nếu không cải thiện, return rate sẽ giảm customer satisfaction và tăng cost.
- **Prescriptive**: 
  1. Improve size guide + virtual try-on.
  2. Negotiate với shipper hoặc chuyển partner.
  3. Offer size exchange program.

---

## TỔNG KẾT WORKFLOW

### Data Pipeline
```
Raw CSVs (data/) 
  → load_all_tables() 
  → Cleaning (parse dates, strip text) 
  → Quality Checks (PK/FK/Business rules) 
  → Join Strategy (3 enriched datasets) 
  → EDA (Univariate → Bivariate → Time/Geo) 
  → Export CSV (outputs/) → Tableau/Power BI
```

### Enriched Datasets Produced
1. `orders_enriched` (27 cols): Order-level holistic view.
2. `line_items` (56 cols): Transaction-level granular data với financial metrics.
3. `returns_enriched` (61 cols): Return analysis enriched.
4. `daily_kpis.csv`: Time-series metrics.
5. `geo_orders.csv`, `region_kpis.csv`: Geographic analysis.

### Files Exported to `outputs/`
- `column_profile_all_tables.csv`: Data dictionary + quality metrics.
- `daily_kpis.csv`: Daily aggregated metrics.
- `geo_orders.csv`: Orders by city.
- `region_kpis.csv`: Revenue/profit by region.
- `daily_kpis_with_traffic.csv`: Combined traffic + revenue.

---

## GIÚP GÌ CHO COMPETITION?

### 1. Data Validation
- Đảm bảo data trustworthy trước khi modeling.
- Identify data issues early (missing PK, orphan FK, business rule violations).
- **Output**: Audit trail cho judges → chứng tỏ hiểu data deeply.

### 2. Feature Engineering
- Derived metrics: `gross_profit`, `gross_margin`, `discount_rate`, `shipping_lead_time_days`.
- Các features này **quý giá** cho ML models (predict revenue, predict return, customer segmentation).

### 3. Business Insights (Value Proposition)
- **Regional performance**: Where to allocate resources? (East focus, West high-margin).
- **Return root-cause**: Wrong size → cải thiện sizing guide.
- **Traffic-revenue correlation**: Marketing ROI analysis.
- **Payment method**: COD có return rate cao? → adjust policy.

### 4. Visualization Ready
- CSV files **sẵn sàng import Tableau/Power BI**.
- Đã có geographic aggregation, time-series, KPIs.
- Judges có thể build dashboard nhanh.

### 5. 4-Tier Framework (Rubric Alignment)
- Mỗi chart đều có **Descriptive/Diagnostic/Predictive/Prescriptive** template.
- **Maximize điểm** theo rubric: không chỉ vẽ chart, mà phải có **business meaning + actionable recommendation**.

---

## CÁC BƯỚC TIẾP THEO CẦN LÀM (Theo PLAN.md)

Notebook hiện tại đã hoànành phần data prep và univariate/bivariate. Cần bổ sung:

### Statistical Inference
- **Hypothesis testing**:
  - T-test: So sánh mean net_revenue giữa payment_method (credit_card vs cod).
  - **ANOVA one-way**: So sánh mean revenue giữa 3+ regions (East/Central/West).
  - **ANOVA two-way**: Region × product_category interaction.
  - **MANOVA**: Multiple dependent variables (revenue, profit, quantity).
- **Chi-square test**: đã làm (order_status × payment_method).
- **Regression**: Linear regression predict net_revenue từ features (price, discount, region, channel).
- **Multicollinearity check**: VIF (Variance Inflation Factor) nếu làm regression.

### Post-Modeling (Causal Inference)
- **Counterfactual**: "Nếu không có promotion, revenue sẽ thế nào?" → uplift modeling.
- **A/B test analysis**: So sánh conversion rate giữa 2 versions.
- **Propensity score matching**: Để đánh giá campaign impact.

### Multivariate Analysis (Chưa thấy trong code)
- **Revenue by region × product category** (heatmap).
- **Customer cohort analysis**: Retention rate theo acquisition_channel.
- **RFM segmentation**: Recency, Frequency, Monetary.
- **Market basket analysis**: Association rules (sản phẩm nào hay mua cùng nhau).

---

## ĐÁNH GIÁ CODE HIỆN TẠY

### Strengths (Điểm mạnh)
1. **Modular**: Hàm nhỏ, reusable (format helpers, parsing helpers).
2. **Robust error handling**: `if df is not None`, `.get()` method, try/except cho scipy.
3. **Clear output**: Section headers, save to CSV, display key tables.
4. **Production-ready**: Type hints, docstrings, consistent formatting.
5. **Business-oriented**: Focus trên derived metrics (profit, margin, lead time).

### Weaknesses (Điểm yếu cần bổ sung)
1. **Chưa có EDA cho multivariate** (3+ variables).
2. **Chưa có statistical tests** (t-test, ANOVA) như PLAN.md đề cập.
3. **Time-series analysis surface-level**: Chỉ plot daily revenue, chưa decompose trend/seasonality/residual.
4. **No outlier detection** formal (IQR, Z-score cho numeric variables).
5. **Customer analysis thiếu**: Chỉ join customers nhưng chưa phân tích RFM, CLV.
6. **No hypothesis statements** rõ ràng (Diagnostic → cần đặt câu hỏi, test).

### Recommendations (Đề xuất cải thiện)
1. **Add missing value treatment strategy**: Imputation (mean/median/mode) or drop?
2. **Add outlier detection & handling**: Winsorize, cap, or investigate?
3. **Add hypothesis testing section**:
   ```python
   # ANOVA: Does net_revenue differ by region?
   import scipy.stats as stats
   groups = [line_items[line_items["delivery_region"]==r]["net_revenue"] for r in regions]
   stats.f_oneway(*groups)
   ```
4. **Add time-series decomposition**:
   ```python
   from statsmodels.tsa.seasonal import seasonal_decompose
   result = seasonal_decompose(daily_kpis.set_index("order_date")["net_revenue"], model="additive")
   ```
5. **Add RFM analysis** (nếu có customer_id trong line_items):
   - Recency: days since last purchase.
   - Frequency: count of orders.
   - Monetary: total net_revenue.
6. **Add product category analysis**:
   - Top categories by revenue, profit.
   - Category × region heatmap.
7. **Export to Tableau Data Extract** (.hyper) thay vì CSV for performance.

---

## KẾT LUẬN

Notebook **preprocess_eda.ipynb** là **foundation EDA solid** với:
✅ Data loading & cleaning tốt.
✅ Data quality checks toàn diện (PK, FK, business rules).
✅ Enriched datasets đầy đủ cho analysis.
✅ Univariate & bivariate EDA với visualization.
✅ Time-series và geographic overview.
✅ Output export cho Tableau/Power BI.

**Chưa đủ** (theo PLAN.md):
- Statistical hypothesis testing (t-test, ANOVA, MANOVA).
- Multicollinearity diagnostics.
- Causal inference & counterfactual.
- Advanced multivariate analysis.

**Next steps**: Bổ sung sections 3-4 (Statistical Methods, Post-Modeling) để hoàn thiện 4-tier EDA.

---

**Tác giả analysis**: AI Assistant  
**Ngày**: 2025-04-23  
**Dựa trên**: preprocess_eda.ipynb (3,158 lines)
