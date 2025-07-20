let fileData = null;

function triggerUpload() {
  document.getElementById('fileInput').click();

  document.getElementById('fileInput').onchange = function () {
    let file = this.files[0];

    if (file) {
      let formData = new FormData();
      formData.append("file", file);

      $.ajax({
        url: '/upload',
        type: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        success: function(response) {
          fileData = response;
          alert('File uploaded successfully!');
        },
        error: function() {
          alert('Error uploading file');
        }
      });
    }
  };
}


function displayDemandForecasting() {
  if (!fileData || !fileData.demand_forecasting) return alert("Please upload a file first.");
  let df = fileData.demand_forecasting;
  let x = df.map(row => row.Date);
  let actual = df.map(row => row.Quantity);
  let predicted = df.map(row => row.Predicted);

  let trace1 = { x, y: actual, mode: 'lines+markers', name: 'Actual' };
  let trace2 = { x, y: predicted, mode: 'lines+markers', name: 'Predicted' };

  let layout = {
    title: 'Demand Forecasting',
    xaxis: { title: 'Date' },
    yaxis: { title: 'Quantity' }
  };

  Plotly.newPlot('output-box', [trace1, trace2], layout);
}

function displayCustomerSegmentation() {
  if (!fileData || !fileData.customer_segments) return alert("Please upload a file first.");
  let segments = fileData.customer_segments;

  let trace = {
    x: segments.map(s => s.Recency),
    y: segments.map(s => s.Monetary),
    text: segments.map(s => `Customer ${s.CustomerID}`),
    mode: 'markers',
    marker: { size: 10, color: segments.map(s => s.Segment) }
  };

  let layout = {
    title: 'Customer Segmentation (Recency vs Monetary)',
    xaxis: { title: 'Recency' },
    yaxis: { title: 'Monetary' }
  };

  Plotly.newPlot('output-box', [trace], layout);
}

function displayProductCategorization() {
  if (!fileData || !fileData.product_categories) return alert("Please upload a file first.");
  let categories = fileData.product_categories;

  let trace = {
    x: categories.map(c => c.Quantity),
    y: categories.map(c => c.TotalAmount),
    text: categories.map(c => c.ProductName),
    mode: 'markers+text',
    textposition: 'top center',
    marker: {
      size: 12,
      color: categories.map(c => c.Category),
      colorscale: 'Viridis',
      showscale: true,
      colorbar: { title: 'Category' }
    }
  };

  let layout = {
    title: 'Product Categorization (by Quantity vs Total Amount)',
    xaxis: { title: 'Total Quantity Sold' },
    yaxis: { title: 'Total Revenue (₹)' }
  };

  Plotly.newPlot('output-box', [trace], layout);
}

function displaySalesPrediction() {
  if (!fileData || !fileData.sales_predictions) return alert("Please upload a file first.");
  let sales = fileData.sales_predictions;
  let x = sales.map(s => s.Date);
  let actual = sales.map(s => s.TotalAmount);
  let predicted = sales.map(s => s.PredictedSales);

  let trace1 = { x, y: actual, mode: 'lines+markers', name: 'Actual Sales' };
  let trace2 = { x, y: predicted, mode: 'lines+markers', name: 'Predicted Sales' };

  let layout = {
    title: 'Sales Prediction',
    xaxis: { title: 'Date' },
    yaxis: { title: 'Sales Amount' }
  };

  Plotly.newPlot('output-box', [trace1, trace2], layout);
}
