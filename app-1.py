from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load the dataset once when the app starts
data = pd.read_excel('JaundiceTH.xlsx')

# Function to get thresholds for a given age
def get_threshold(age):
    if age > 169:
        age = 169
    
    thresholds = data[data['Age in hours'] == age]
    if not thresholds.empty:
        thresholds = thresholds.iloc[0]
    else:
        thresholds = data[data['Age in hours'] == data['Age in hours'].max()].iloc[0]

    return {
        'with_risk_factors': thresholds['with risk factors'],
        'without_risk_factors': thresholds['without risk factors']
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        option = request.form.get('option')
        age_input = request.form.get('age')
        
        try:
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

@app.route('/new', methods=['GET'])
def new_entry():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
