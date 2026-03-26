import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error
from scipy.stats import spearmanr
from data import DataParser

raceData = pd.read_csv("1500mData.csv")
raceData["Date"] = pd.to_datetime(raceData["Date"])


def timeToSeconds(timeStr):
    if pd.isna(timeStr):
        return None
    minSeconds = str(timeStr).split(":")
    if len(minSeconds) == 2:
        return int(minSeconds[0]) * 60 + float(minSeconds[1])
    return float(minSeconds[0])


raceData["Time"] = raceData["Time"].apply(timeToSeconds)
raceData = DataParser.AdditionalColumns(raceData)

gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train, test = next(
    gss.split(raceData, raceData["Target_Rank"], groups=raceData["Race_ID"])
)
train = raceData.iloc[train]
test = raceData.iloc[test]
X_train = train.drop(columns=["Time", "Target_Rank", "Date", "Athlete_ID"])
Y_train = train["Time"]
X_test = test.drop(columns=["Time", "Target_Rank", "Date", "Athlete_ID"])
Y_test = test["Time"]

randForest = RandomForestRegressor(n_estimators=100, random_state=42)
randForest.fit(X_train, Y_train)

Y_prediction = randForest.predict(X_test)

spearmanScores = []

testDataFrame = pd.DataFrame(
    {
        "Race_ID": test["Race_ID"],
        "Target_Rank": test["Target_Rank"],
        "Predicted_Time": Y_prediction,
    }
)
for race_id, group in testDataFrame.groupby("Race_ID"):
    ranks = group["Target_Rank"].tolist()
    predictedRanks = group["Predicted_Time"].rank(method="min").tolist()
    correlation = spearmanr(ranks, predictedRanks)[0]
    if not np.isnan(correlation):
        spearmanScores.append(correlation)
averageSpearman = sum(spearmanScores) / len(spearmanScores)
print(averageSpearman)
