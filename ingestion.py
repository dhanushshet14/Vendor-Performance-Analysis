import pandas as pd
import os
from sqlalchemy import create_engine
import logging
import time
from sqlalchemy.exc import OperationalError

logging.basicConfig(
    filename="logs/ingestion_db.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"

)

engine = create_engine('sqlite:///inventory.db', 
                      connect_args={'timeout': 60, 'check_same_thread': False},
                      pool_pre_ping=True, pool_recycle=300)

def ingest_db(df, table_name, engine):
    ''''this function will ingest the dataframe into table'''
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                df.to_sql(table_name, con = conn, if_exists='replace', index=False)
            break
        except OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                logging.warning(f"Database locked, retrying in 2 seconds... (attempt {attempt + 1})")
                time.sleep(2)
            else:
                raise


def load_raw_data():
    ''''this function will load the CSVs as dataframe and ingest into db'''
    start = time.time()
    for file in os.listdir('data'):
        if '.csv' in file:
            df = pd.read_csv('data/'+file)
            logging.info(f'Ingesting {file} in db')
            ingest_db(df, file[:-4], engine)

    end = time.time()
    total_time = ( end - start ) / 60
    logging.info('-----------------Ingestion Complete-----------------')


    logging.info(f'\n Total Time Taken:  {total_time} minutes')

if __name__ == '__main__':
    load_raw_data()