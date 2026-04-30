import pandas as pd
import numpy as np
import os
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
DATA_RAW_PATH = os.path.join(ROOT_DIR, "data", 'raw')

def load_data():
    sales = pd.read_csv(os.path.join(DATA_RAW_PATH, 'sales.csv'))
    sales['Date'] = pd.to_datetime(sales['Date'])
    
    promotions = pd.read_csv(os.path.join(DATA_RAW_PATH, 'promotions.csv'))
    promotions['start_date'] = pd.to_datetime(promotions['start_date'])
    promotions['end_date'] = pd.to_datetime(promotions['end_date'])
    
    web_traffic = pd.read_csv(os.path.join(DATA_RAW_PATH, 'web_traffic.csv'))
    web_traffic['date'] = pd.to_datetime(web_traffic['date'])
    
    products = pd.read_csv(os.path.join(DATA_RAW_PATH, 'products.csv'))
    
    orders = pd.read_csv(os.path.join(DATA_RAW_PATH, 'orders.csv'))
    orders['order_date'] = pd.to_datetime(orders['order_date'])
    
    order_items = pd.read_csv(os.path.join(DATA_RAW_PATH, 'order_items.csv'))
    
    return sales, promotions, web_traffic, products, orders, order_items

def analyze():
    sales, promotions, web_traffic, products, orders, order_items = load_data()
    
    res = {}
    
    # Q1.1: Doanh thu tăng trong tháng 4-6 có ảnh hưởng bởi chương trình khuyến mãi?
    sales['month'] = sales['Date'].dt.month
    sales['year'] = sales['Date'].dt.year
    
    # Check promotions in month 4-6
    promotions['start_month'] = promotions['start_date'].dt.month
    promotions_46 = promotions[promotions['start_month'].isin([4,5,6])]
    res['promo_46_count'] = len(promotions_46)
    res['promo_total_count'] = len(promotions)
    
    # Q1.2: Peak tháng 4-6 có lặp lại mỗi năm không?
    monthly_revenue = sales.groupby(['year', 'month'])['Revenue'].sum().reset_index()
    peaks = {}
    for y in monthly_revenue['year'].unique():
        y_data = monthly_revenue[monthly_revenue['year'] == y]
        peaks[int(y)] = int(y_data.loc[y_data['Revenue'].idxmax()]['month'])
    res['yearly_peak_months'] = peaks
    
    # Q1.3: Doanh thu phụ thuộc traffic?
    sales_traffic = sales.merge(web_traffic, left_on='Date', right_on='date', how='inner')
    res['revenue_traffic_corr'] = sales_traffic['Revenue'].corr(sales_traffic['sessions'])
    
    # Q2.1 & Q2.2: Vì sao doanh thu giảm rõ rệt sau 2018?
    yearly_revenue = sales.groupby('year')['Revenue'].sum().to_dict()
    res['yearly_revenue'] = {k: float(v) for k, v in yearly_revenue.items()}
    yearly_traffic = web_traffic.groupby(web_traffic['date'].dt.year)['sessions'].sum().to_dict()
    res['yearly_traffic'] = {k: float(v) for k, v in yearly_traffic.items()}
    
    # Check marketing budget or promo counts by year
    promotions['start_year'] = promotions['start_date'].dt.year
    yearly_promos = promotions.groupby('start_year').size().to_dict()
    res['yearly_promos'] = {k: int(v) for k, v in yearly_promos.items()}
    
    # Q3.1: Products có phải đồ mùa hè?
    cat_counts = products['category'].value_counts().to_dict()
    res['product_categories'] = cat_counts
    
    # Q3.2: Ngành hàng theo tháng
    order_details = orders.merge(order_items, on='order_id').merge(products, on='product_id')
    order_details['month'] = order_details['order_date'].dt.month
    cat_monthly = order_details.groupby(['month', 'category'])['quantity'].sum().unstack().fillna(0)
    res['cat_monthly_sales'] = cat_monthly.to_dict()
    
    with open('eda_results.json', 'w') as f:
        json.dump(res, f, indent=4)
        
if __name__ == '__main__':
    analyze()
