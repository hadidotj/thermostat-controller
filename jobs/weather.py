from scheduler import Job
import logging
import requests
import state
import tracker

log = logging.getLogger('Weather')


class Weather(Job):
    def process(self):
      weatherAPI = state.settings['weather']
      URL = 'https://api.openweathermap.org/data/2.5/weather'
      PARAMS = {
        'units': 'imperial',
        'lat': weatherAPI['lat'],
        'lon': weatherAPI['lon'],
        'appid': weatherAPI['appid']
      }
	  
      resp = requests.get(url = URL, params = PARAMS)
      data = resp.json()
      tracker.trackTemp('outside', data['main']['temp'], data['main']['humidity'])
      state.weather = data

Weather(300)
