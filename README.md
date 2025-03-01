# Excel Data Optimizer Tool

This is a web-based tool that allows users to upload an Excel file containing product data (product names, profit, and cost). The tool performs optimization to select products that maximize profit while staying within a specified budget.

## Features
- Upload Excel files containing product data.
- Optimize product selection using linear programming.
- Download the optimized results as a new Excel file.

## How to Run the Project

1. Clone this repository:
    ```bash
    git clone <repository_url>
    cd excel_optimization_tool
    ```

2. Create a virtual environment (optional):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the Flask app:
    ```bash
    python app.py
    ```

5. Open your browser and go to `http://127.0.0.1:5000/` to use the tool.

## License
This project is licensed under the MIT License.
