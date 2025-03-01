import os
import uuid
from flask import Flask, render_template, request, send_file
import pandas as pd
from scipy.optimize import linprog

app = Flask(__name__)

# Folder to store uploaded files and results
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'

# Ensure the folders exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(RESULT_FOLDER):
    os.makedirs(RESULT_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

# Function to perform the optimization
def optimize_products(data, budget):
    data.columns = data.columns.str.strip()  # Clean column names

    # Check if the required columns exist
    required_columns = ['Product', 'Profit', 'Cost']
    if not all(col in data.columns for col in required_columns):
        return None, f"Missing required columns. Ensure your file contains: {', '.join(required_columns)}"
    
    profits = data['Profit'].values
    costs = data['Cost'].values

    # Negating profits because linprog does minimization
    c = -profits  # Objective function: maximize profit

    # Constraints: cost should not exceed the budget
    A = [costs]  # Coefficients for cost constraint
    b = [budget]  # Budget constraint

    # Variable bounds: each product can either be selected or not
    x_bounds = [(0, 1) for _ in range(len(profits))]  # 0 or 1 for each product

    # Step 3: Solve the optimization problem
    result = linprog(c, A_ub=A, b_ub=b, bounds=x_bounds, method='highs')

    if result.success:
        selected_products = data.iloc[result.x > 0.5]  # Products selected (x > 0.5)
        selected_products['Selected'] = result.x[result.x > 0.5]
        total_profit = -result.fun  # Since we negated profits for minimization
        return selected_products, total_profit
    else:
        return None, "Optimization failed."

# Home page route
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file upload and optimization
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file", 400
    
    # Ensure the file is an Excel file
    if not file.filename.endswith('.xlsx'):
        return "Only .xlsx files are allowed.", 400
    
    # Generate a unique file name
    unique_filename = str(uuid.uuid4()) + '.xlsx'
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

    try:
        # Save the uploaded file with the unique name
        file.save(file_path)
    except PermissionError:
        return "Permission denied: Unable to save the file.", 403
    
    # Load data from the uploaded Excel file
    data = pd.read_excel(file_path)

    # Set the budget (you can make this dynamic)
    budget = 500

    # Perform optimization
    optimized_data, result = optimize_products(data, budget)

    if isinstance(optimized_data, pd.DataFrame):
        # Save the optimized result to a new Excel file
        result_file = os.path.join(app.config['RESULT_FOLDER'], 'optimized_result.xlsx')
        optimized_data.to_excel(result_file, index=False)

        # Return the result to the template for rendering
        return render_template('index.html', result=optimized_data.to_dict(orient='records'), result_file=result_file)
    else:
        return result

# Route for downloading the result
@app.route('/download')
def download_result():
    # Assuming the result file is the latest generated one
    result_file = os.path.join(app.config['RESULT_FOLDER'], 'optimized_result.xlsx')
    return send_file(result_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
