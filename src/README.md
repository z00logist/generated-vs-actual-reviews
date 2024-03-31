# Foreword

All credits for the "complexity metrics adapted" folder go to **Blinova Olga** and **Tarasov Nikita**, the authors of the [ComplexityModel Repository](https://github.com/PlainDocument/Complexity-models).

We have rewritten some parts of it, adjusting the code to run on CSV files.

## How To Use It On Your Data

To utilize this tool on your data, follow the steps below:

### Step 0: Install Dependencied

Before all, you need to install dependencies through poetry in your local venv:

```bash
poetry install --no-root"
```
### Step 1: Generate Linguistic Features

First, you need to generate linguistic features using `extract_characteristics.py`. Execute the following command in your terminal:

```bash
cd src/complexity_model_adapted/
python extract_characteristics.py --data_path="enter/your/data.csv" --column_name="enter_column_name" --output_path="enter/your/output.csv"
```

### Step 2: Count Metrics

After preprocessing your data, the next step involves counting the metrics with the processed data. To do this, follow the instructions below:

1. **Navigate to the Metrics Directory**: First, change your current working directory to where the `feature_extractor.py` script is located. This is within the `complexity_metrics_adapted/Metrics` folder. You can do this from the command line with the following command:

```bash
cd src/complexity_model_adapted/Metrics
```
2. **Run the Extractor Script**: This script will process the data according to the specified parameters and output the results to the defined CSV file.
```bash
python feature_extractor.py --input-path='your_folder_name' --output-path='your_file.csv' --num-workers=number_of_available_workers
```
> **Note**: *Make sure to replace `'your_folder_name'`, `'your_file.csv'`, and `number_of_available_workers` with the appropriate values for your project setup. The `--num-workers` parameter allows you to define how many worker processes will be spawned for processing, depending on the capabilities of your system.*
