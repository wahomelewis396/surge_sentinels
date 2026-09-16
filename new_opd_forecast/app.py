import streamlit as st
import pandas as pd
import joblib
from datetime import date 

#load the saved model
st.set_page_config(page_title="Kijabe OPD Visit Forecast", layout="centered")

#page colour layout
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #d9e4f5 100%);
    }
    </style>
""", unsafe_allow_html=True)

#passing the model and lookup table to the app
@st.cache_resource
def load_model():
    return joblib.load('daily_model2.pkl')

@st.cache_data
def load_lookup():
    return pd.read_csv('feature_lookup2.csv')

model=load_model()
lookup=load_lookup()
    
#The visible part of the app
st.title("Kijabe OPD Visit Forecast")
st.write("This app forecasts expected daily Outpatient Visits by department. ")

#The dropdown menu for collecting user input
department=st.selectbox("Select Department", sorted(lookup['Department'].unique()))
selected_date=st.date_input("Selected Forecast Date", value=date.today())

#Turning picked date into features the model requires
dayofweek=selected_date.weekday()
month=selected_date.month
is_weekend= 1 if dayofweek in [5,6] else 0

# look up historical reference numbers for the department.
dept_lookup=lookup[(lookup['Department'] == department) & (lookup['dayofweek'] == dayofweek)]

if dept_lookup.empty:
    st.warning("No historical data available for this department on the selected day of the week.")
else:
    avg_visits=dept_lookup['avg_visits'].values[0]
    last_known_lag_7=dept_lookup['last_known_lag_7'].values[0]
    
#Assembling the feature rows and predicting the expected visits
input_features=pd.DataFrame([{
    'Department': department,
    'dayofweek': dayofweek,
    'month': month,
    'is_weekend': is_weekend,
    'lag_1': avg_visits,
    'lag_7': last_known_lag_7,
    'rolling_mean_7': avg_visits
}])
input_features['Department'] = input_features['Department'].astype('category')


if st.button("Forecast Visits"):
    prediction=model.predict(input_features)[0]
    
    delta = prediction -avg_visits
    st.metric(label=f"Predicted Outpatient Visits - {department}", value=f"{prediction:.0f} patients",
              delta=f"{delta:+.0f} vs typical {selected_date.strftime('%A')}"
    )
    st.caption(f"Based on historical patterns for {selected_date.strftime('%A')}s in {department}.")
    
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(5,3))
    ax.bar(['Historical Avg', 'Forecast'], [avg_visits, prediction], color=['#94A3B8', '#2563EB'])
    ax.set_ylabel('Visits')
    st.pyplot(fig)    
    
#Weekly forecast section (low-Volume Departments)
st.markdown("---")
st.header("Weekly Forecast for Low-Volume Departments")
st.write("Some low-volume departments have low daily visit volumes, making daily forecasts less reliable. For these departments, we provide a weekly forecast instead.") 


weekly_model = joblib.load('weekly_model2.pkl')
weekly_lookup = pd.read_csv('weekly_feature_lookup2.csv')

sparse_depts = ['SPECIALITY CLINIC', 'RENAL', 'ONCOLOGY', 'CHRONIC CARE CLINIC (DM/HTN/TB/CCC)']
weekly_department = st.selectbox("Select Department (Weekly Forecast)", sparse_depts)
weekly_month = st.selectbox("Select Month", list(range(1, 13)),
                             format_func=lambda m: date(2000, m, 1).strftime('%B'))

if st.button("Forecast Weekly Visits"):
    dept_weekly_lookup = weekly_lookup[weekly_lookup['Department'] == weekly_department]
    avg_weekly = dept_weekly_lookup['avg_weekly_visits'].values[0]

    weekly_input = pd.DataFrame([{
        'Department': weekly_department,
        'month': weekly_month,
        'lag_1': avg_weekly,
        'lag_4': avg_weekly,
        'rolling_mean_4': avg_weekly
    }])
    weekly_input['Department'] = weekly_input['Department'].astype('category')

    weekly_prediction = weekly_model.predict(weekly_input)[0]
    st.metric(
        label=f"Predicted Weekly Visits — {weekly_department}",
        value=f"{weekly_prediction:.0f} patients"
    )
st.caption(f"Based on historical weekly patterns for {weekly_department}.")