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


def get_bhutani_limits(age):
    row = bhutani_data.loc[bhutani_data['Age in hours'] == age]
    if not row.empty:
        low_risk = row['Low Risk Limit'].values[0]
        intermediate_risk = row['Intermediate Risk Limit'].values[0]
        high_risk = row['High Risk Limit'].values[0]
        print(f"Low Risk: {low_risk}, Intermediate Risk: {intermediate_risk}, High Risk: {high_risk}")
        return low_risk, intermediate_risk, high_risk
    return None, None, None

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
            else:
                age = round(age)
                thresholds = get_threshold(age)
                return render_template('result.html', option=option, age=age, 
                                       with_risk=thresholds['with_risk_factors'], 
                                       without_risk=thresholds['without_risk_factors'])
        except ValueError:
            return render_template('index.html', error="Please enter a valid number for age.")
    
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    age = int(request.form['age'])
    option = request.form['option']
    with_risk = float(request.form['with_risk'])
    without_risk = float(request.form['without_risk'])
    
    # Get Bhutani limits for the given age
    low_risk, intermediate_risk, high_risk = get_bhutani_limits(age)
    
    # Render result page with Bhutani data
    return render_template('result.html', 
                           option=option, 
                           age=age, 
                           with_risk=with_risk, 
                           without_risk=without_risk, 
                           low_risk=low_risk, 
                           intermediate_risk=intermediate_risk, 
                           high_risk=high_risk)

@app.route('/new', methods=['GET'])
def new_entry():
    return render_template('index.html')


if __name__ == '__main__':
    # Turn on debugging to catch errors
    app.run(debug=True)
