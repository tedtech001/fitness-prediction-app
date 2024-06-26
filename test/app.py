from flask import Flask, request, render_template, redirect, url_for
import joblib
import pandas as pd

app = Flask(__name__)

# Load the pre-trained model and encoders
model = joblib.load('fitness_model.pkl')
scaler = joblib.load('scaler.pkl')
le_gender = joblib.load('le_gender.pkl')
le_bmicase = joblib.load('le_bmicase.pkl')

# Define features for scaling
features = ['Weight', 'Height', 'BMI', 'Age']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.form
    weight = float(data['weight'])
    height = float(data['height'])
    bmi = float(data['bmi'])
    gender = data['gender']
    age = int(data['age'])
    bmicase = data.get('bmicase', 'unknown')

    # Handle Gender encoding
    gender_encoded = le_gender.transform([gender])[0]

    # Handle BMIcase encoding with a fallback for 'unknown'
    try:
        bmi_encoded = le_bmicase.transform([bmicase])[0]
    except KeyError:
        bmi_encoded = le_bmicase.transform(['unknown'])[0]

    # Create a DataFrame for the input data
    input_data = pd.DataFrame({
        'Weight': [weight],
        'Height': [height],
        'BMI': [bmi],
        'Gender': [gender_encoded],
        'Age': [age],
        'BMIcase': [bmi_encoded]
    })

    # Scale the features
    input_data[features] = scaler.transform(input_data[features])

    # Make a prediction
    recommendation = model.predict(input_data)

    return redirect(url_for('show_prediction', recommendation=int(recommendation[0])))

@app.route('/prediction/<int:recommendation>')
def show_prediction(recommendation):
    return render_template('predict.html', recommendation=recommendation)

if __name__ == '__main__':
    app.run(debug=True)
