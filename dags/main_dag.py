from airflow import DAG
from datetime import datetime
from pandas import json_normalize
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from web_scraping import *


def store_fct_table():
    hook = PostgresHook(postgres_conn_id = 'postgres')
    hook.copy_expert(
        sql = "COPY fct_table FROM stdin WITH DELIMITER as ',' CSV HEADER",
        filename = 'df_fct_table.csv'
    )

def store_stock_dim_table():
    hook = PostgresHook(postgres_conn_id = 'postgres')
    hook.copy_expert(
        sql = "COPY stock_dim_table FROM stdin WITH DELIMITER as ',' CSV HEADER",
        filename = 'stock_dim_table.csv'
    )

def store_company_dim_table():
    hook = PostgresHook(postgres_conn_id = 'postgres')
    hook.copy_expert(
        sql = "COPY company_dim_table FROM stdin WITH DELIMITER as ',' CSV HEADER",
        filename = 'company_dim_table.csv'
    )

with DAG('main_dag', start_date = datetime(2022,1,1), schedule_interval = '@daily', catchup = False) as dag:
    
    create_fct_table = PostgresOperator(
        task_id='create_fct_table',
        postgres_conn_id='postgres',
        sql='''
            CREATE TABLE IF NOT EXISTS fct_table (
                Market_Cap TEXT NOT NULL,
                Last_Price TEXT NOT NULL,
                Price–earnings_ratio TEXT NOT NULL,
                Dividend_yield TEXT NOT NULL,
                Return_on_equity TEXT NOT NULL,
                Company_Key TEXT NOT NULL,
                Stock_Key TEXT NOT NULL
            );
        '''
    )

    create_stock_dim_table = PostgresOperator(
    task_id='create_stock_dim_table',
    postgres_conn_id='postgres',
    sql='''
            CREATE TABLE IF NOT EXISTS stock_dim_table (
                Stock_Short_Name TEXT NOT NULL,
                Stock_Code TEXT NOT NULL,
                Market_Name TEXT NOT NULL,
                Stock_Key TEXT NOT NULL
            );
        '''
    )

    create_company_dim_table = PostgresOperator(
    task_id='create_company_dim_table',
    postgres_conn_id='postgres',
    sql='''
            CREATE TABLE IF NOT EXISTS company_dim_table (
                Company_Full_Name TEXT NOT NULL,
                Shariah TEXT NOT NULL,
                Sector TEXT NOT NULL,
                Company_Key TEXT NOT NULL
            );
        '''
    )


    web_scraping = PythonOperator(
        task_id = 'web_scraping',
        python_callable = main
    )

    store_fct_table = PythonOperator(
        task_id = 'store_fct_table',
        python_callable = store_fct_table
    )

    store_company_dim_table = PythonOperator(
    task_id = 'store_company_dim_table',
    python_callable = store_company_dim_table
    )

    store_stock_dim_table = PythonOperator(
    task_id = 'store_stock_dim_table',
    python_callable = store_stock_dim_table
    )

    web_scraping >> create_fct_table >> store_fct_table >> create_company_dim_table >> store_company_dim_table >> create_stock_dim_table >> store_stock_dim_table