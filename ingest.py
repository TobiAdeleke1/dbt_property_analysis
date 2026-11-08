import os
import logging
import pandas as pd
import pandas_gbq
import requests
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
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


def extract(url, file_name="price_dataset.csv"):
    try:
        response_data = requests.get(url=url, timeout=30)
        response_data.raise_for_status()

        os.makedirs(DATASET_DIR, exist_ok=True)
        file_path = os.path.join(DATASET_DIR, file_name)
        with open(file_path, "w") as rf:
            rf.write(response_data.text)
        return file_path

    except Exception  as err:
        logging.error(f"Request for {file_name} failed due to {err}")


if __name__ == "__main__":
    test_connection()
    file_path = extract(URL, 'price_paid.csv')
    print(file_path)
