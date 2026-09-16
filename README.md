AIC Kijabe Hospital - OPD Patient Surge Forecasting
Project Overview
Healthcare facilities need to anticipate patient demand to effectively plan staffing, clinic capacity, and other operational resources.
This project analyzes Outpatient Department (OPD) patient visit data from Kijabe Hospital and develops machine learning and time-series forecasting models to predict future patient volumes at the department.
 Problem Statement
Hospitals experience fluctuations in outpatient demand across departments, days of the week, and seasons. Without reliable demand forecasts, healthcare facilities may struggle with appropriate staffing, resource allocation, and operational planning.
The objective of this project is to:
•	Understand historical OPD utilization patterns.
•	Identify factors associated with patient demand.
•	Forecast future patient volumes by department.
•	Compare different forecasting approaches.
•	Identify limitations in forecasting low-volume departments.
•	Develop a practical forecasting strategy that can support hospital operations
 Dataset
The dataset contains approximately 306,000 patient records before data cleaning.
Key variables include:
Variable	Description
PatientNumber	Unique patient identifier
RegistrationDate	Date and time of patient registration
Gender	Patient gender
Age	Original age field
QueuedTo	Department/service the patient was queued to
ConsultDescription	Description of the consultation
After cleaning and filtering, the forecasting analysis focuses on six major OPD departments:
•	General OPD
•	MCH
•	Chronic Care
•	Speciality Clinic
•	Oncology
•	Renal
Admission records and anomalous one-off department values were excluded from the final OPD forecasting dataset.

 Data Cleaning
The following preprocessing steps were performed:
•	Checked the dataset structure and data types.
•	Identified missing values.
•	Removed duplicate records.
•	Removed records with missing gender.
•	Standardized categorical values.
•	Converted patient ages from different units into years.
•	Identified and handled impossible ages above 100 years.
•	Imputed missing age values using the mean age.
•	Created meaningful age groups.
•	Removed records without department information.
•	Standardized department names.
•	Removed anomalous one-off department entries.
•	Excluded admission records from the OPD forecasting dataset.
The cleaned OPD dataset contained 187,501 records across the six selected departments.
 Feature Engineering
Several temporal and demographic features were created to support the analysis and forecasting models.
Temporal Features
•	Day of week
•	Weekend indicator
•	Month
•	Date
•	Year
•	Hour
Forecasting Features
The machine learning models also used historical demand features such as:
•	lag_1 — previous day's/week's demand depending on model resolution
•	lag_7 — demand from the same day one week earlier
•	Rolling averages
•	Month
•	Day of week
•	Department
These features allow the models to learn recurring demand patterns and recent trends.
Exploratory Data Analysis
The analysis revealed several important patterns in OPD utilization.
Department Demand
General OPD accounts for the largest volume of visits, while departments such as Renal, Oncology, Chronic Care, and Speciality Clinic have substantially lower volumes.
The departments show different demand behaviors, supporting the decision to model them individually rather than treating all hospital demand as one homogeneous series.
Weekday vs Weekend Patterns
A strong weekday/weekend pattern was observed across the departments.
General OPD maintains some weekend activity, while several specialized departments experience a substantial reduction in weekend visits.
Patient Demographics
Patient demographics vary considerably across departments.
For example, MCH has a substantially younger patient population, while Renal and Oncology have considerably older patient populations.
Repeat Visits
Repeat-visit behavior differs substantially between departments.
Renal had the highest average visits per patient, at approximately 34.69 visits per patient, followed by Oncology at approximately 6.96 visits per patient.
General OPD had the lowest average at approximately 1.74 visits per patient, suggesting that its high volume is largely driven by serving many different patients rather than frequent repeat visits from the same individuals.
Seasonal Patterns
June and July showed particularly high visit volumes, while December showed noticeably lower activity.
The analysis also found that the weekday/weekend pattern remained consistent across months, suggesting that weekly operational patterns are an important component of demand forecasting.

Statistical Testing
Statistical tests were performed to validate patterns identified during exploratory analysis.
1. Trend Analysis
A Pearson correlation test was used to examine whether daily OPD volume changed over time.
The results indicated a statistically significant but weak upward trend in daily OPD demand.
2. Chi-Square Test
A chi-square test of independence examined the relationship between department and day of the week.
Results:
•	χ² = 14,578.18
•	p < 0.001
•	Cramér's V = 0.127
This provides statistical evidence that departments have different weekly demand patterns.
3. ANOVA — Patient Age
A one-way ANOVA tested whether average patient age differed across departments.
Results:
•	F = 6970.80
•	p < 0.001
This confirms statistically significant differences in patient age distributions across departments.
4. ANOVA — Visits per Patient
A second ANOVA examined whether visits per patient differed between departments.
Results:
•	F = 780.93
•	p < 0.001
This supports the finding that patient return behavior varies substantially by department.

 Forecasting Models
Two main approaches were evaluated for daily OPD demand forecasting.
1. XGBoost
An XGBoost regression model was trained using department-level and temporal features.
The model incorporated historical demand features such as lag variables and rolling averages.
The final daily model achieved:
Metric	Result
MAE	8.04
RMSE	13.11
R²	0.90
The strongest predictor was lag_7, representing demand from the same day one week earlier.
This indicates that weekly demand patterns are highly informative when forecasting daily OPD visits.

2. SARIMA
A classical time-series approach using SARIMA was also evaluated.
SARIMA models were trained independently for each department using:
order = (1, 1, 1)
seasonal_order = (1, 1, 1, 7)
The overall comparison showed:
Model	MAE	RMSE
XGBoost	8.04	13.11
SARIMA	10.42	13.02
XGBoost produced the lower MAE, while the two approaches produced comparable RMSE values.
For this project, XGBoost was therefore retained as the primary daily forecasting model.

Hyperparameter Tuning
RandomizedSearchCV with TimeSeriesSplit was used to investigate whether XGBoost performance could be improved through hyperparameter optimization.
The search explored parameters including:
•	Number of estimators
•	Learning rate
•	Maximum tree depth
•	Minimum child weight
•	Subsample ratio
•	Column sampling ratio
However, the tuned model produced worse department-level MAPE for most departments.
For example, Speciality Clinic increased from approximately 50.8% MAPE to 61.6%.
This highlighted an important modeling consideration:
Optimizing a global metric such as MAE can favor high-volume departments and fail to improve performance for low-volume departments.
The original XGBoost model was therefore retained as the final daily forecasting model.

The Low-Volume Department Challenge
One of the most important findings of the project was that forecasting accuracy depends strongly on department volume.
The daily XGBoost model produced approximately:
Department	Daily MAPE
General OPD	17.3%
Chronic Care	23.1%
Oncology	31.1%
Renal	33.8%
Speciality Clinic	50.8%
The issue is not necessarily that low-volume departments are inherently unpredictable.
When a department has only a few patients per day, a small absolute forecasting error can become a large percentage error.
This led to the development of a second forecasting approach.

 Weekly Forecasting Model
To address the limitations of daily forecasting for low-volume departments, the following departments were aggregated to weekly demand:
•	Speciality Clinic
•	Renal
•	Oncology
•	Chronic Care
A second XGBoost model was then trained using weekly features including:
•	Department
•	Month
•	Previous week's demand
•	Demand approximately four weeks earlier
•	Four-week rolling mean
Results
Department	Daily MAPE	Weekly MAPE
Speciality Clinic	50.8%	21.0%
Renal	33.8%	10.9%
Oncology	31.1%	16.3%
Chronic Care	23.1%	18.0%
Weekly aggregation substantially reduced forecast error for all four low-volume departments.
This demonstrates that changing the forecasting time resolution can be an effective way to reduce noise in sparse demand series.

 Key Insights
The project produced several operationally relevant insights:
1.	General OPD is the highest-volume department and has a clear upward trend over the analyzed period.
2.	Demand varies significantly by department, meaning hospital-wide forecasting alone may hide important departmental differences.
3.	Weekly patterns are highly important, with strong differences between weekdays and weekends.
4.	Renal and Oncology show strong repeat-visit behavior, indicating recurring patient care patterns.
5.	June and July show high demand, while December shows comparatively lower activity.
6.	General OPD is easier to forecast at daily resolution because its larger volume produces a more stable demand signal.
7.	Low-volume departments experience higher percentage errors at daily resolution because small absolute changes create large proportional errors.
8.	Weekly aggregation improves forecasting performance for low-volume departments, demonstrating the importance of matching forecasting resolution to the characteristics of the department.
9.	Historical demand from the same weekday in the previous week (lag_7) is the strongest predictor in the daily XGBoost model.

 Proposed Forecasting Strategy
Based on the analysis, the project supports a department-specific, multi-resolution forecasting strategy:
High-volume departments
Use daily XGBoost forecasts to support operational decisions such as:
•	Staffing
•	Daily clinic preparation
•	Resource allocation
•	Patient-flow planning
Lower-volume departments
Use weekly XGBoost forecasts to provide a smoother and more reliable estimate of expected demand.
This approach recognizes that different departments have different demand structures rather than forcing every department into the same forecasting framework.

Technologies Used
Programming & Data Analysis
•	Python
•	Pandas
•	NumPy
Visualization
•	Matplotlib
•	Seaborn
Statistical Analysis
•	SciPy
•	ANOVA
•	Chi-square testing
•	Pearson correlation
•	Cramér's V
Machine Learning
•	Scikit-learn
•	XGBoost
•	RandomizedSearchCV
•	TimeSeriesSplit
Time-Series Forecasting
•	SARIMA / Statsmodels
Model Deployment Preparation
•	Joblib
•	CSV feature lookup tables



 Deployment Preparation
The final trained models were saved using joblib:
joblib.dump(xgb_model, 'daily_model2.pkl')
joblib.dump(xgb_weekly_model, 'weekly_model2.pkl')
Feature lookup tables were also created to support future application development:
feature_lookup2.csv
weekly_feature_lookup2.csv
These artifacts can be used as a foundation for building an application that provides department-level OPD demand forecasts.

 Conclusion
This project demonstrates how healthcare data can be transformed into actionable demand forecasting insights.
Rather than relying on a single model or forecasting resolution, the analysis shows the value of combining:
Data Cleaning → EDA → Statistical Testing → Feature Engineering → Model Comparison → Error Analysis → Multi-resolution Forecasting
The final approach uses daily XGBoost forecasting for higher-volume OPD demand and weekly XGBoost forecasting for lower-volume departments, providing a more practical way to handle the different demand characteristics observed across hospital departments.

