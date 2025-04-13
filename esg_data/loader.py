# esg_data/loader.py

import os
import pandas as pd

DATA_DIR = "data"  # 你可以把所有公司 CSV 文件放这里，例如：data/Apple.csv

def load_company_data(name):
    filename = f"{name}.csv"
    filepath = os.path.join(DATA_DIR, filename)

    if not os.path.exists(filepath):
        return None

    try:
        df = pd.read_csv(filepath)
        return df
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None
