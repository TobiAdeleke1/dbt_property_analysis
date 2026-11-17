import os
import logging
from google.cloud import bigquery
from google.oauth2 import service_account
import requests
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    style="{",  # over default '%'
    format="{asctime}:{levelname}:{message}",
)
logger = logging.getLogger(__file__)
load_dotenv()

URL = 'https://price-paid-data.publicdata.landregistry.gov.uk/pp-2025.csv'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, 'datasets')

# Create Authentication
KEY_FILE = os.environ['gc_keyfile']
DATASET_ID = 'raw_data'


def extract(url, file_name="pp.csv", timeout=10):
    try:
        logger.info(f"Making request to ... {url}")
        response_data = requests.get(url=url, timeout=timeout)
        response_data.raise_for_status()

        os.makedirs(DATASET_DIR, exist_ok=True)
        file_path = os.path.join(DATASET_DIR, file_name)
        logger.info(f"Loading request data to ... {file_path}")
        with open(file_path, "w") as rf:
            rf.write(response_data.text)

        logger.info(f"Request data written.")
        return file_path

    except Exception as err:
        logger.error(f"Request for {file_name} failed due to {err}")
        return ''


def load(sa_credentials, file_path=None):
    credentials = service_account.Credentials.from_service_account_file(
        sa_credentials,
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )


    # 2. create client
    client = bigquery.Client(
        credentials=credentials,
        project=credentials.project_id
    )

    #3. set job_config
    schema = [
        bigquery.SchemaField('transaction_id', 'STRING'),
        bigquery.SchemaField('price', 'STRING'),
        bigquery.SchemaField('transfer_date', 'STRING'),
        bigquery.SchemaField('postcode', 'STRING'),
        bigquery.SchemaField('property_type', 'STRING'),
        bigquery.SchemaField('is_new', 'STRING'),
        bigquery.SchemaField('duration', 'STRING'),
        bigquery.SchemaField('primary_address', 'STRING'),
        bigquery.SchemaField('secondary_address', 'STRING'),
        bigquery.SchemaField('street_name', 'STRING'),
        bigquery.SchemaField('local_area_name', 'STRING'),
        bigquery.SchemaField('town_city_name', 'STRING'),
        bigquery.SchemaField('district_name', 'STRING'),
        bigquery.SchemaField('county_name', 'STRING'),
        bigquery.SchemaField('ppd_category_type', 'STRING'),
        bigquery.SchemaField('record_status', 'STRING'),
    ]
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        skip_leading_rows=0,
        source_format=bigquery.SourceFormat.CSV,
        write_disposition='WRITE_TRUNCATE'
    )

    #4. write table
    table_id = f'{credentials.project_id}.{DATASET_ID}.price_paid'
    logger.info(f'Loading {table_id} ...')
    with open(file_path, 'rb') as csv_file:
        job = client.load_table_from_file(
            csv_file,
            table_id,
            job_config=job_config
        )

    job.result()
    table = client.get_table(table_id)
    logger.info(f'Loaded {table.num_rows} and { len(table.schema)} to {table_id}')


def clean(file_path=None):
    if os.path.exists(file_path):
        os.remove(file_path)



if '__main__'==__name__:
    # file_path = extract(URL, 'pp.csv')
    # print(file_path)
    # load(KEY_FILE, file_path)
    load(KEY_FILE, '/mnt/c/Users/damol/OneDrive/Life_After_UNI/Personal_Study/DATA_ENGINEER_2026/Claude_Help/projects_and_certificate/phase_2/projects/p1/v1/datasets/pp.csv')