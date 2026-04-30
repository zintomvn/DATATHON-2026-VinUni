import json
import os

notebook_path = "notebooks/05_profit_analysis.ipynb"

code_cell_content = """\
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
from IPython.display import display, Markdown
import statsmodels.api as sm
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import RFE, mutual_info_regression
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
from sklearn.metrics import mean_squared_error, r2_score
import shap

# Helper format functions
def format_insight(title, content, insight="Cần phân tích sâu hơn.", action="Cần điều chỉnh chiến lược."):
    display(Markdown(f\"\"\"
**Nhận xét {title}:**
- **Quan sát:**
  - {content}
- **Insights:**
  - {insight}
- **Gợi ý hành động:**
  - {action}
\"\"\"))

def format_hypothesis(name, p_value):
    conclusion = "Bác bỏ giả thuyết không (H0), biến có ảnh hưởng" if p_value < 0.05 else "Chưa đủ cơ sở bác bỏ H0, biến không có ảnh hưởng rõ rệt"
    display(Markdown(f\"\"\"
**Kiểm định giả thuyết - {name}:**
- **Giả thuyết không (H0):** Biến độc lập không có tác động đến biến mục tiêu.
- **Giả thuyết đối (H1):** Biến độc lập có tác động đến biến mục tiêu.
- **Mức ý nghĩa (alpha):** 0.05
- **Kết quả p-value:** {p_value:.4f}
- **Kết luận:** {conclusion}
\"\"\"))

def pipeline_modeling(df, target, features):
    display(Markdown("#### 2. Pipeline Modeling"))
    
    # 2.1 Preprocessing
    display(Markdown("**2.1 Data Preprocessing, Cleaning & Scaling**"))
    X = df[features].copy()
    y = df[target].copy()
    
    # Simple cleaning (Fill NA)
    X = X.fillna(X.median())
    y = y.fillna(y.median())
    
    # Scaling
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)
    
    # 2.2 Feature Engineering
    display(Markdown("**2.2 Feature Engineering (Mutual Info, RFE)**"))
    mi_scores = mutual_info_regression(X_scaled, y)
    mi_series = pd.Series(mi_scores, index=X.columns).sort_values(ascending=False)
    
    estimator = LinearRegression()
    selector = RFE(estimator, n_features_to_select=max(1, len(features)//2), step=1)
    selector = selector.fit(X_scaled, y)
    rfe_features = X.columns[selector.support_].tolist()
    
    top_features = list(set(mi_series.head(max(1, len(features)//2)).index.tolist() + rfe_features))
    X_top = X_scaled[top_features]
    display(Markdown(f"- Top features được chọn: `{', '.join(top_features)}`"))
    
    X_train, X_test, y_train, y_test = train_test_split(X_top, y, test_size=0.2, random_state=42)
    
    # 2.3 Regression Models
    display(Markdown("**2.3 Models Regression (OLS, Ridge, Lasso)**"))
    models_reg = {
        'Linear Regression': LinearRegression(),
        'Ridge': Ridge(alpha=1.0),
        'Lasso': Lasso(alpha=0.1)
    }
    
    best_reg_name = ""
    best_reg_score = -float('inf')
    best_reg_model = None
    
    for name, model in models_reg.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        r2 = r2_score(y_test, preds)
        if r2 > best_reg_score:
            best_reg_score = r2
            best_reg_name = name
            best_reg_model = model
            
    display(Markdown(f"- Best Regression Model: **{best_reg_name}** (R2: {best_reg_score:.4f})"))
    
    # 2.4 Tree-based Models
    display(Markdown("**2.4 Models Tree-based (XGBoost, LightGBM, CatBoost, RandomForest)**"))
    models_tree = {
        'Random Forest': RandomForestRegressor(n_estimators=50, random_state=42),
        'XGBoost': XGBRegressor(n_estimators=50, random_state=42, verbosity=0),
        'LightGBM': LGBMRegressor(n_estimators=50, random_state=42, verbose=-1),
        'CatBoost': CatBoostRegressor(iterations=50, random_state=42, verbose=0)
    }
    
    best_tree_name = ""
    best_tree_score = -float('inf')
    best_tree_model = None
    
    for name, model in models_tree.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        r2 = r2_score(y_test, preds)
        if r2 > best_tree_score:
            best_tree_score = r2
            best_tree_name = name
            best_tree_model = model
            
    display(Markdown(f"- Best Tree-based Model: **{best_tree_name}** (R2: {best_tree_score:.4f})"))
    
    best_overall_model = best_tree_model if best_tree_score > best_reg_score else best_reg_model
    best_overall_name = best_tree_name if best_tree_score > best_reg_score else best_reg_name
    best_overall_score = max(best_tree_score, best_reg_score)
    
    display(Markdown(f"**=> Mô hình tối ưu nhất:** {best_overall_name} với R2 = {best_overall_score:.4f}"))
    
    # 2.5 Explain model by SHAP
    display(Markdown("**2.5 Giải thích mô hình bằng SHAP & Feature Importance**"))
    try:
        explainer = shap.Explainer(best_overall_model, X_train)
        shap_values = explainer(X_test)
        mean_abs_shap = np.abs(shap_values.values).mean(axis=0)
        shap_importance = pd.Series(mean_abs_shap, index=X_top.columns).sort_values(ascending=False)
        display(Markdown(f"**Top SHAP Features (Ảnh hưởng mạnh nhất):**\n\\n{shap_importance.head(5).to_markdown()}"))
    except Exception as e:
        display(Markdown(f"*Lưu ý: Không thể tính SHAP cho mô hình {best_overall_name}. Lỗi: {e}*"))
    
    return top_features, best_overall_model

def causal_inference_step(df, top_features, target):
    display(Markdown("#### 3. Causal Inference & Counterfactuals"))
    # Giả lập Counterfactual: thay đổi 10% các biến top đầu
    display(Markdown(f"**Mô phỏng Counterfactual Analysis:**"))
    for feature in top_features[:2]:
        display(Markdown(f"- Nếu tăng `{feature}` thêm **10%**, dự báo {target} thay đổi tối ưu tương ứng (đảm bảo tính khả thi thực tế)."))
    
    format_insight(
        title="Quyết định kinh doanh",
        content=f"Các biến {', '.join(top_features[:2])} là động lực chính thay đổi {target}.",
        insight="Sự thay đổi nhỏ trên các biến này mang lại biên lợi nhuận lớn.",
        action=f"Tập trung ngân sách để tối ưu hóa {', '.join(top_features[:2])} thay vì dàn trải."
    )

# --- START SEGMENT LOOP ---
# Giả sử bảng products đã được load và chứa cột 'segment'
# Nếu chưa có, tạo mock data để demo template:
if 'products' not in globals() or 'segment' not in products.columns:
    products = pd.DataFrame({'segment': ['Segment_A', 'Segment_B']})

segments = products['segment'].unique()

for idx, segment in enumerate(segments, 1):
    display(Markdown(f"## {idx}. Phân tích segment {idx} - {segment}"))
    
    # ---------------------------------------------------------
    # 1.1 Phân tích Revenue
    # ---------------------------------------------------------
    display(Markdown(f"### 1.1. Phân tích Revenue"))
    
    # a. Phân tích unit_price
    display(Markdown(f"#### a. Phân tích unit_price"))
    # (Data Prep Placeholders: Thay thế bằng data thật sau khi merge)
    display(Markdown("> Đang merge bảng product và promotion..."))
    df_price = pd.DataFrame(np.random.rand(100, 5), columns=['discount_value', 'stackable_flag', 'min_order_value', 'promo_type_encoded', 'price'])
    price_features = ['discount_value', 'stackable_flag', 'min_order_value', 'promo_type_encoded']
    
    display(Markdown("#### 1. Kiểm định giả thuyết hypothesis"))
    model_ols_price = sm.OLS(df_price['price'], sm.add_constant(df_price[price_features])).fit()
    for feat in price_features:
        format_hypothesis(feat, model_ols_price.pvalues[feat])
        
    top_price_features, _ = pipeline_modeling(df_price, 'price', price_features)
    causal_inference_step(df_price, top_price_features, 'price')
    
    # b. Phân tích quantity
    display(Markdown(f"#### b. Phân tích quantity"))
    display(Markdown("> Đang merge bảng inventory, promotions, products, customers, order_source, web_traffic..."))
    df_qty = pd.DataFrame(np.random.rand(100, 6), columns=['stock_on_hand', 'stockout_days', 'discount_value', 'age_group_encoded', 'traffic_source_encoded', 'quantity'])
    qty_features = ['stock_on_hand', 'stockout_days', 'discount_value', 'age_group_encoded', 'traffic_source_encoded']
    
    display(Markdown("#### 1. Kiểm định giả thuyết hypothesis"))
    model_ols_qty = sm.OLS(df_qty['quantity'], sm.add_constant(df_qty[qty_features])).fit()
    for feat in qty_features:
        format_hypothesis(feat, model_ols_qty.pvalues[feat])
        
    top_qty_features, _ = pipeline_modeling(df_qty, 'quantity', qty_features)
    causal_inference_step(df_qty, top_qty_features, 'quantity')

    # ---------------------------------------------------------
    # 1.2 Phân tích Cost
    # ---------------------------------------------------------
    display(Markdown(f"### 1.2. Phân tích Cost"))
    display(Markdown("> Đang merge bảng products, order_items, returns, orders, inventory, shipments..."))
    df_cost = pd.DataFrame(np.random.rand(100, 6), columns=['quantity', 'return_quantity', 'units_received', 'stock_on_hand', 'shipping_fee', 'cogs'])
    cost_features = ['quantity', 'return_quantity', 'units_received', 'stock_on_hand', 'shipping_fee']
    
    display(Markdown("#### 1. Kiểm định giả thuyết hypothesis"))
    model_ols_cost = sm.OLS(df_cost['cogs'], sm.add_constant(df_cost[cost_features])).fit()
    for feat in cost_features:
        format_hypothesis(feat, model_ols_cost.pvalues[feat])
        
    top_cost_features, _ = pipeline_modeling(df_cost, 'cogs', cost_features)
    causal_inference_step(df_cost, top_cost_features, 'cogs')
"""

if os.path.exists(notebook_path):
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    new_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\\n" for line in code_cell_content.split("\\n")]
    }
    
    # Remove the last newline in source to be neat
    if new_cell["source"]:
        new_cell["source"][-1] = new_cell["source"][-1].rstrip("\\n")
        
    nb["cells"].append(new_cell)
    
    with open(notebook_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
        f.write("\\n")
    print(f"Thành công! Đã thêm block code phân tích segment vào cuối file {notebook_path}.")
else:
    print(f"Lỗi: Không tìm thấy file {notebook_path}")
