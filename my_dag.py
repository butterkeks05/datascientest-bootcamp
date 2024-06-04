from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import json
import os
import time
import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from joblib import dump

url = "https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid=2153979c28e6c33466ea4e4322485a6a"

path_to_data='/app/clean_data/fulldata.csv'

output_folder = "/app/raw_files"

cities = [
    {"name": "Munich", "lat": 48.14, "lon": 11.58},
    {"name": "London", "lat": 51.51, "lon": -0.13},
    {"name": "Rome", "lat": 41.90, "lon": 12.50}
]


my_dag = DAG(
    dag_id='exam_dag',
    description='Airflow Evaluation',
    tags=['tutorial', 'datascientest'],
    schedule_interval=timedelta(seconds=15),
    default_args={
        'owner': 'airflow',
        'start_date': days_ago(2),
    }
)

###### TASK 1 ######

def retreiving_data():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    weather_data = []

    for city in cities:
        city_url = url.format(lat=city["lat"], lon=city["lon"])
        response = requests.get(city_url)
        response_json = response.json()
        weather_data.append(response_json)

    filename = os.path.join(output_folder, f"{current_time}.json")

    with open(filename, 'w') as file:
        json.dump(weather_data, file, indent=2)

    print(f"Weather data for all cities saved to {filename}")

task1 = PythonOperator(
    task_id='task1',
    python_callable=retreiving_data,
    dag=my_dag
)

###### TASK 2 ######

def data_20_to_csv(n_files=20, filename='data.csv'):
    parent_folder = '/app/raw_files'
    files = sorted(os.listdir(parent_folder), reverse=True)[:n_files]

    dfs = []

    for f in files:

        with open(os.path.join(parent_folder, f), 'r') as file:
            data_temp = json.load(file)
        
        for data_city in data_temp:
            dfs.append({                
                'temperature': data_city['main']['temp'],
                'city': data_city['name'],
                'pressre': data_city['main']['pressure'],
                'date': f.split('.')[0]}
            )

    df = pd.DataFrame(dfs)

    print('\n', df.head(10))

    df.to_csv(os.path.join('/app/clean_data', filename), index=False)

task2 = PythonOperator(
    task_id='task2',
    python_callable=data_20_to_csv,
    dag=my_dag
)

###### TASK 3 ######

def data_all_to_csv(filename='fulldata.csv'):
    parent_folder = '/app/raw_files'
    files = sorted(os.listdir(parent_folder), reverse=True)
    n_files = len(files)
    files = (files)[:n_files-1] #without deleting the last file I get an encoding error

    dfs = []

    for f in files:

        with open(os.path.join(parent_folder, f), 'r') as file:
            data_temp = json.load(file)
        
        for data_city in data_temp:
            dfs.append({                
                'temperature': data_city['main']['temp'],
                'city': data_city['name'],
                'pressre': data_city['main']['pressure'],
                'date': f.split('.')[0]}
            )

    df = pd.DataFrame(dfs)

    print('\n', df.head(10))

    df.to_csv(os.path.join('/app/clean_data', filename), index=False)

task3 = PythonOperator(
    task_id='task3',
    python_callable=data_all_to_csv,
    dag=my_dag
)

###### TASK 4 ######

def prepare_data(path_to_data='/app/clean_data/fulldata.csv'):

    df = pd.read_csv(path_to_data)

    df = df.sort_values(['city', 'date'], ascending=True)

    dfs = []

    for c in df['city'].unique():
        df_temp = df[df['city'] == c]

        df_temp.loc[:, 'target'] = df_temp['temperature'].shift(1)

        for i in range(1, 10):
            df_temp.loc[:, 'temp_m-{}'.format(i)
                        ] = df_temp['temperature'].shift(-i)

        df_temp = df_temp.dropna()

        dfs.append(df_temp)

    df_final = pd.concat(
        dfs,
        axis=0,
        ignore_index=False
    )

    df_final = df_final.drop(['date'], axis=1)

    df_final = pd.get_dummies(df_final)

    features = df_final.drop(['target'], axis=1)
    target = df_final['target']

    return features, target


def compute_model_score(model, X, y):
    cross_validation = cross_val_score(
        model,
        X,
        y,
        cv=3,
        scoring='neg_mean_squared_error')

    model_score = cross_validation.mean()

    return model_score


def train_data(task_instance):
    X, y = prepare_data('/app/clean_data/fulldata.csv')

    score_lr = compute_model_score(LinearRegression(), X, y)
    score_dt = compute_model_score(DecisionTreeRegressor(), X, y)

    task_instance.xcom_push(
        key="score_lr_my_xcom",
        value=score_lr
    )
    task_instance.xcom_push(
        key="score_dt_my_xcom",
        value=score_dt
    )

task4 = PythonOperator(
    task_id='task4',
    python_callable=train_data,
    provide_context=True, 
    dag=my_dag
)

###### TASK 5 ######


def train_and_save_model(model, X, y, path_to_model='/app/clean_data/model.pckl'):

    model.fit(X, y)

    print(str(model), 'saved at ', path_to_model)
    dump(model, path_to_model)


def selection_and_retrain(task_instance):
    X, y = prepare_data('/app/clean_data/fulldata.csv')
    
    score_lr = task_instance.xcom_pull(
        key="score_lr_my_xcom",
        task_ids='task4')
    score_dt = task_instance.xcom_pull(
            key="score_dt_my_xcom",
            task_ids='task4')

    if score_lr < score_dt:
        train_and_save_model(
            LinearRegression(),
            X,
            y,
            '/app/clean_data/best_model.pickle'
    )
    else:
        train_and_save_model(
            DecisionTreeRegressor(),
            X,
            y,
            '/app/clean_data/best_model.pickle'
        )


task5 = PythonOperator(
    task_id='task5',
    python_callable=selection_and_retrain,
    provide_context=True,
    dag=my_dag
)

task1 >> task2
task1 >> task3
task3 >> task4
task4 >> task5
