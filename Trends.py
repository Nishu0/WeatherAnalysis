from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from scipy.special import softmax

import numpy as np
import pandas as pd 
from taipy.gui import Gui, notify

text = "Original text"

page = """
# IoT Weather Analysis App


## Welcome to IoT Weather Analysis

Welcome to our IoT Weather Analysis App, a powerful tool for exploring weather trends and conducting in-depth analysis of weather data. With this app, you can gain valuable insights into weather conditions using data gathered from IoT devices such as ESP32, DHT11, and BMP180.

### What It Does

Our IoT Weather Analysis App allows you to:

- Monitor Real-time Weather Data: Get access to real-time weather data collected by IoT devices placed in different locations.

- Analyze Historical Trends: Explore historical weather trends and patterns to make informed decisions.

- Visualize Data: Visualize weather data using interactive charts and graphs, making it easier to understand complex weather patterns.

- Predict Future Weather: Utilize data analysis to predict future weather conditions, helping you plan your activities accordingly.

### How It Works

Our app relies on the following IoT devices for data gathering:

- **ESP32:** This versatile microcontroller is used to collect data from various weather sensors.

- **DHT11:** The DHT11 sensor measures temperature and humidity, providing crucial climate information.

- **BMP180:** This barometric pressure sensor helps us gauge atmospheric pressure changes, which can indicate weather shifts.

The IoT devices continuously collect data and transmit it to our app, where it is processed and analyzed using advanced algorithms and machine learning models.

### Key Features

- **Real-time Weather Data:** Access up-to-the-minute weather information from multiple sensors.

- **Historical Analysis:** Dive into historical weather data to uncover trends and patterns.

- **Interactive Visualizations:** Visualize weather data with interactive charts and graphs for better insights.

- **Weather Predictions:** Use data-driven predictions to plan for future weather conditions.

- **User-Friendly Interface:** Our user-friendly interface makes it easy for anyone to explore and understand weather data.

### What We Used

Our IoT Weather Analysis App is built using Python, Taipy GUI, and popular machine learning models for accurate data analysis.

### Get Started

To get started, simply enter a location or select a sensor from the dropdown menu to view weather data. You can also explore historical data, analyze trends, and make data-driven decisions for your weather-related activities.

Discover the power of IoT-driven weather analysis with our app. Start exploring weather trends and making informed decisions today!

---

#### Connect with Us

Follow us on social media for updates and news:

- [Facebook](#) 
- [Twitter](#)
- [Instagram](#)
- [LinkedIn](#)

#### Contact Us

If you have any questions or feedback, feel free to reach out to us at [contact@email.com](mailto:contact@email.com).

#### Privacy Policy

Read our [Privacy Policy](#) to learn about how we handle your data and ensure your privacy.

"""

MODEL = f"cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)

dataframe = pd.DataFrame({"Text":[''],
                          "Score Pos":[0.33],
                          "Score Neu":[0.33],
                          "Score Neg":[0.33],
                          "Overall":[0]})

dataframe2 = dataframe.copy()

def analyze_text(text):
    # Run for Roberta Model
    encoded_text = tokenizer(text, return_tensors='pt')
    output = model(**encoded_text)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    
    return {"Text":text[:50],
            "Score Pos":scores[2],
            "Score Neu":scores[1],
            "Score Neg":scores[0],
            "Overall":scores[2]-scores[0]}


def local_callback(state):
    notify(state, 'Info', f'The text is: {state.text}', True)
    temp = state.dataframe.copy()
    scores = analyze_text(state.text)
    state.dataframe = temp.append(scores, ignore_index=True)
    state.text = ""


path = ""
treatment = 0

page_file = """
<|{path}|file_selector|extensions=.txt|label=Upload .txt file|on_action=analyze_file|> <|{f'Downloading {treatment}%...'}|>

<br/>

<|Table|expandable|
<|{dataframe2}|table|width=100%|number_format=%.2f|>
|>

<br/>

<|{dataframe2}|chart|type=bar|x=Text|y[1]=Score Pos|y[2]=Score Neu|y[3]=Score Neg|y[4]=Overall|color[1]=green|color[2]=grey|color[3]=red|type[4]=line|height=600px|>

"""

def analyze_file(state):
    state.dataframe2 = dataframe2
    state.treatment = 0
    with open(state.path,"r", encoding='utf-8') as f:
        data = f.read()
        
        # split lines and eliminates duplicates
        file_list = list(dict.fromkeys(data.replace('\n', ' ').split(".")[:-1]))
    
    
    for i in range(len(file_list)):
        text = file_list[i]
        state.treatment = int((i+1)*100/len(file_list))
        temp = state.dataframe2.copy()
        scores = analyze_text(text)
        state.dataframe2 = temp.append(scores, ignore_index=True)
        
    state.path = None
    

pages = {"/":"<|toggle|theme|>\n<center>\n<|navbar|>\n</center>",
         "line":page,
         "text":page_file}

Gui(pages=pages).run(use_reloader=True, port=8000)


