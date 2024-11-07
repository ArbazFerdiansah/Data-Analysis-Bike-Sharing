# **Dashboard**

## Setup Environment - Anaconda
```
conda create --name main-ds python=3.12.5
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
mkdir Data-Analysis-Bike-Sharing
cd Data-Analysis-Bike-Sharing
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run Streamlit App
```
streamlit run dashboard/dashboard.py
```
