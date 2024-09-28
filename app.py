from flask import Flask, render_template, request, url_for
import pandas as pd
from whitenoise import WhiteNoise

app = Flask(__name__)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

# Load the dataset once when the app starts
data = pd.read_excel('JaundiceTH.xlsx')
bhutani_data = pd.read_excel('Bhutani.xlsx')

# Function to get thresholds for a given age
def get_threshold(age):
    if age > 169:
        age = 169
    
    # Get the closest matching row in the dataset
    thresholds = data[data['Age in hours'] == age]
    if not thresholds.empty:
        thresholds = thresholds.iloc[0]
    else:
        thresholds = data[data['Age in hours'] == data['Age in hours'].max()].iloc[0]

    return {
       'with_risk_factors': round(thresholds['with risk factors'], 2),
        'without_risk_factors': round(thresholds['without risk factors'], 2)
    }

# Function to get Bhutani limits for the relevant age in hours 
def get_risk_limits(age_hours):
    if age_hours>147:
        age_hours=147

    try:
        row = bhutani_data[bhutani_data['AgeHours'] == age_hours].iloc[0]
        low_risk = row['LowRiskLimit']
        intermediate_risk = row['IntermediateRiskLimit']
        high_risk = row['HighRiskLimit']
    except IndexError:
        # Handle the case where the exact age_hours is not found
        return None, None, None

    return low_risk, intermediate_risk, high_risk

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        option = request.form.get('option')
        age_input = request.form.get('age')
        
        try:
            # Convert input to a number and apply conditions
            age = float(age_input)
            if age < 6:
                return render_template('index.html', error="Minimal age is 6 hours")
           
            # If age is between 6 and 12 hours, show message without table
            elif age < 12:
                # Extract the threshold values (with and without risk factors)
                thresholds = get_threshold(age)
                message = "Risk Zones by Bhutani applicable for ages > 12 hours"
                return render_template('result.html', age=age, option=option, 
                                    with_risk=thresholds['with_risk_factors'], 
                                    without_risk=thresholds['without_risk_factors'], message=message)
            else:
                age = round(age)
                thresholds = get_threshold(age)
                # Get the risk limits for the entered age
                low_risk, intermediate_risk, high_risk = get_risk_limits(age)
                return render_template('result.html', option=option, age=age, 
                                       with_risk=thresholds['with_risk_factors'], 
                                       without_risk=thresholds['without_risk_factors'], low_risk=round(low_risk,2), intermediate_risk=round(intermediate_risk,2), high_risk=round(high_risk,2))
        except ValueError:
            return render_template('index.html', error="Please enter a valid number for age.")
    
    return render_template('index.html')

@app.route('/new', methods=['GET'])
def new_entry():
    return render_template('index.html')


if __name__ == '__main__':
    # Turn on debugging to catch errors
    app.run(debug=True)
