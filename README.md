# Overview
This program contains a model used to predict the winner of the World Athletics Ultimate Championships 2026

`data.py` contains the class DataParser that parses the CSV file `1500mData.csv` containing 1000 rows of self-curated 1500m time and event data

`RandomForest.py` contains the logic for the modelling and testing of a Random Forest Regressor used to predict rankings with a Spearman correlation of 0.496

## Running this program

Ensure both Pandas, NumPy, and Scikit-learn are installed using:
`pip install numpy`
`pip install pandas`
`pip install -U scikit-learn`

To run the program use: 
`python RandomForest.py`

## Results and Analysis

The model has an overall Spearman correlation ($\rho$) of 0.496, meaning:

The model distinguishes between podium finishes (1-3) versus the bottom-tier (9-12)

The model faces challenges with mid-pack finishes due to the difference in finishing times often being <0.5 seconds 
