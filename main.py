import os
import pandas as pd
from flask import Flask, render_template, request, jsonify
import plotly.graph_objs as go
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from mlxtend.preprocessing import TransactionEncoder

app = Flask(__name__)

# Load Excel sheet

def load_data(file):
    return pd.read_excel(file)

# ----------------------------- Demand Forecasting ----------------------------- #
def demand_forecasting(data):
    data['Date'] = pd.to_datetime(data['Date'])
    demand_data = data.groupby(['Date', 'ProductName'])['Quantity'].sum().reset_index()
    demand_data['Day'] = demand_data['Date'].dt.dayofyear
    X = pd.get_dummies(demand_data[['ProductName', 'Day']], drop_first=True)
    y = demand_data['Quantity']

    model = LinearRegression()
    model.fit(X, y)
    demand_data['Predicted'] = model.predict(X)

    return demand_data[['Date', 'ProductName', 'Quantity', 'Predicted']]

# ----------------------------- Customer Segmentation ----------------------------- #
def customer_segmentation(data):
    rfm = data.groupby('CustomerID').agg({
        'Date': lambda x: (data['Date'].max() - x.max()).days,
        'TransactionID': 'nunique',
        'TotalAmount': 'sum'
    }).rename(columns={'Date': 'Recency', 'TransactionID': 'Frequency', 'TotalAmount': 'Monetary'})

    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm)
    kmeans = KMeans(n_clusters=3, random_state=0)
    rfm['Segment'] = kmeans.fit_predict(rfm_scaled)

    return rfm.reset_index()

# ----------------------------- Product Categorization ----------------------------- #
def product_categorization(data):
    pivot = data.groupby('ProductName').agg({
        'Quantity': 'sum',
        'TotalAmount': 'sum'
    }).reset_index()

    scaler = StandardScaler()
    features = scaler.fit_transform(pivot[['Quantity', 'TotalAmount']])
    
    kmeans = KMeans(n_clusters=3, random_state=0)
    pivot['Category'] = kmeans.fit_predict(features)
    
    return pivot


# ----------------------------- Sales Prediction ----------------------------- #
def sales_prediction(data):
    data['Date'] = pd.to_datetime(data['Date'])
    data['Day'] = data['Date'].dt.dayofyear
    X = pd.get_dummies(data[['ProductName', 'Day']], drop_first=True)
    y = data['TotalAmount']

    model = LinearRegression()
    model.fit(X, y)
    data['PredictedSales'] = model.predict(X)

    return data[['Date', 'ProductName', 'TotalAmount', 'PredictedSales']]

# ----------------------------- Flask Routes ----------------------------- #
@app.route("/")
def home():
    return render_template('index.html')


UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create folder at runtime if missing
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    data = load_data(file)
    data['Date'] = pd.to_datetime(data['Date'])

    demand_df = demand_forecasting(data)
    segments_df = customer_segmentation(data)
    sales_df = sales_prediction(data)
    categories_df = product_categorization(data)  

    return jsonify({
        'demand_forecasting': demand_df.to_dict(orient='records'),
        'customer_segments': segments_df.to_dict(orient='records'),
        'sales_predictions': sales_df.to_dict(orient='records'),
        'product_categories': categories_df.to_dict(orient='records')
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7860)
