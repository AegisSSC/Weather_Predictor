#https://thecleverprogrammer.com/2020/08/30/predict-weather-with-machine-learning/
#TO DO List:
# Rebuild the broken code
# Build a Visualizer 
# Build a Scraper to read in data
# Properly Segment and Generalize the Code
# Add SQL/Database Support

import pandas as pd
global_temp = pd.read_csv("GlobalTemperatures.csv")
print(global_temp.shape)
print(global_temp.columns)
print(global_temp.info())
print(global_temp.isnull().sum())

#Data Preparation
def wrangle(df):
    df = df.copy()
    df = df.drop(columns=["LandAverageTemperatureUncertainty", "LandMaxTemperatureUncertainty",
                          "LandMinTemperatureUncertainty", "LandAndOceanAverageTemperatureUncertainty"], axis=1)

    def converttemp(x):
        x = (x * 1.8) + 32
        return float(x)
    df["LandAverageTemperature"] = df["LandAverageTemperature"].apply(converttemp)
    df["LandMaxTemperature"] = df["LandMaxTemperature"].apply(converttemp)
    df["LandMinTemperature"] = df["LandMinTemperature"].apply(converttemp)
    df["LandAndOceanAverageTemperature"] = df["LandAndOceanAverageTemperature"].apply(converttemp)
    df["dt"] = pd.to_datetime(df["dt"])
    df["Month"] = df["dt"].dt.month
    df["Year"] = df["dt"].dt.year
    df = df.drop("dt", axis=1)
    df = df.drop("Month", axis=1)
    #df = df[df.Year &gt;= 1850]
    df = df.set_index(["Year"])
    df = df.dropna()
    return df
global_temp = wrangle(global_temp)
print(global_temp.head())

#Show the correlation Matrix. 
import seaborn as sns
import matplotlib.pyplot as plt
corrMatrix = global_temp.corr()
sns.heatmap(corrMatrix, annot=True)
plt.show()


#Now we need to separate the data into features and targets. 
#The target, also called Y, is the value we want to predict, in this case, 
#The actual average land and ocean temperature and features are all the columns the model uses to make a prediction:
target = "LandAndOceanAverageTemperature"
y = global_temp[target]
x = global_temp[["LandAverageTemperature", "LandMaxTemperature", "LandMinTemperature"]]

from sklearn.model_selection import train_test_split

#Split the data into the training sets for X and Y
xtrain, xval, ytrain, yval = train_test_split(x, y, test_size=0.25, random_state=42)
#Print the Results
print(xtrain.shape)
print(xval.shape)
print(ytrain.shape)
print(yval.shape)

#Baseline Mean Absolute Error
#Before we can make and evaluate any predictions on our machine learning model to predict weather,
#we need to establish a baseline, a sane metric that we hope to beat with our model. 
#If our model cannot improve from the baseline then it will fail and we should try a different model or admit 
#that machine learning is not suitable for our problem:
from sklearn.metrics import mean_squared_error
ypred = [ytrain.mean()] * len(ytrain)
print("Baseline MAE: ", round(mean_squared_error(ytrain, ypred), 5))

#Training Model To Predict Weather
#Now to predict weather with Machine Learning 
#I will train a Random Forest algorithm which is capable of 
#performing both the tasks of Classification as well as Regression:
from sklearn.feature_selection import SelectKBest
from sklearn.ensemble import RandomForestRegressor
forest = make_pipeline(
    SelectKBest(k="all"),
    StandardScaler(),
    RandomForestRegressor(
        n_estimators=100,
        max_depth=50,
        random_state=77,
        n_jobs=-1
    )
)
forest.fit(xtrain, ytrain)


#Model Evaluation of Machine Learning model to Predict Weather
#To put our predictions in perspective, we can calculate a precision using the average percentage error subtracted from 100%:

import numpy as np
errors = abs(ypred - yval)
mape = 100 * (errors/ytrain)
accuracy = 100 - np.mean(mape)
print("Random Forest Model: ", round(accuracy, 2), "%")