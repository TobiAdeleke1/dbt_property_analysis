import os
import logging
import pandas as pd
import pandas_gbq
import requests
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    style="{",  # over default '%'
    format="{asctime}:{levelname}:{message}",
)
load_dotenv()

URL = "https://price-paid-data.publicdata.landregistry.gov.uk/pp-2025.csv"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "datasets")


def test_connection():
    test_df = pd.DataFrame(
        {"test_str": ["a", "b", "c"], "test_dates": pd.date_range("now", periods=3)}
    )

    try:
        pandas_gbq.to_gbq(
            test_df,
            "raw_data.test_connection",
            project_id=os.environ["gc_project_id"],
            #'fail', 'replace' or 'append
            if_exists="replace",
        )
        logging.info("Test table created")
        read_table_sql = "SELECT * FROM raw_data.test_connection LIMIT 1"
        table_data = pandas_gbq.read_gbq(
            read_table_sql, project_id=os.environ["gc_project_id"]
        )
        print(table_data)
    except Exception as err:
        logging.error("Connection to create test table failed with: ", err)


def extract(url, file_name="price_dataset.csv", timeout=10):
    try:
        logging.info(f"Making request to ... {url}")
        response_data = requests.get(url=url, timeout=timeout)
        response_data.raise_for_status()

        os.makedirs(DATASET_DIR, exist_ok=True)
        file_path = os.path.join(DATASET_DIR, file_name)
        logging.info(f"Loading request data to ... {file_path}")
        with open(file_path, "w") as rf:
            rf.write(response_data.text)

        logging.info(f"Request data written.")
        return file_path

    except Exception as err:
        logging.error(f"Request for {file_name} failed due to {err}")
        return ''


def load(file_path):
    logging.info(f"Reading data from ... {file_path}")
    df = pd.read_csv(file_path, header=None) 
    numerical_columnlist = [f'col_{num}' for num in range(len(df.columns))]
    df.columns = numerical_columnlist

    logging.info(f"Reading data from Bigquery")
    pandas_gbq.to_gbq(
        df,
        'raw_data.price_paid',
        project_id=os.environ["gc_project_id"],
        if_exists="append",
    )

    read_price_paid = "SELECT * FROM raw_data.price_paid LIMIT 5"
    table_data = pandas_gbq.read_gbq(
        read_price_paid, project_id=os.environ["gc_project_id"]
    )
    print(table_data)


def cleanup(file_path):
    pass


if __name__ == "__main__":
    test_connection()
    file_path = extract(URL, 'price_paid.csv')
    load('./datasets/price_paid.csv')
