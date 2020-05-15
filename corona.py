import requests
import json
import pyttsx3 
import speech_recognition as sr
import re
from gtts import gTTS
import playsound
import os
import time
import config


API_KEY = config.API_KEY
PROJECT_TOKEN = config.PROJECT_TOKEN


class Corona: 
    def __init__(self, api, proj_token):
        self.api_key = api
        self.proj_token = proj_token
        self.params = {"api_key" : api}
        self.get_data()

    def get_data(self):
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.proj_token}/last_ready_run/data', params=self.params)
        self.data = json.loads(response.text)
        
    def get_total_cases(self):
        data = self.data['total']
        for val in data:
            if val['name'] == 'Coronavirus Cases:':
                return val['value']
    
    def get_total_deaths(self):
        data = self.data['total']
        for val in data:
            if val['name'] == 'Deaths:':
                return val['value']
            return "0"

    def get_data_by_country(self, country):
        data = self.data['country']
        for inst in data:
            if inst['name'].lower() == country.lower():
                return inst
            return "0"

    def get_countries(self):
        countries = []
        for country in self.data['country']:
            countries.append(country['name'])
        return countries

data = Corona(API_KEY, PROJECT_TOKEN)
countries = data.get_countries()
print (countries)

def speak(text):
    tts = gTTS(text=text)
    filename = "voice.mp3"
    tts.save(filename)
    playsound.playsound(filename)

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""
        try:
            said = r.recognize_google(audio)
        except Exception as e:
            print('Exception', str(e))
    return said.lower()




SEARCH_PATTERNS = {
    re.compile("[\w\s]+ total [\w\s]+ cases"): data.get_total_cases,
    re.compile("[\w\s]+ total [\w\s]+ deaths"): data.get_total_deaths
}

COUNTRY_CASES = {
    re.compile('[\w\s]+ cases in [\w\s]'): lambda country: data.get_data_by_country(country)['total_cases'],
    re.compile('[\w\s]+ deaths in [\w\s]'): lambda country: data.get_data_by_country(country)['deaths']
}

def main():
    
    while True:
        print('Listing...')
        text = get_audio()
        result = None


        for search, func in SEARCH_PATTERNS.items():
            if search.match(text):
                result = func()
                break

        for search, func in COUNTRY_CASES.items():
            if search.match(text):
                words = set(text.split(" "))
                for country in countries:
                    if country in words:
                        result = func(country)
                        break
        
        
        if(result):
            speak(result)

        if text.find('quit') != -1:
            break
        




        
# main()
