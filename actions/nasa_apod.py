#!/usr/bin/env python
import json
import requests
from st2common.runners.base_action import Action

API_URL = "https://api.nasa.gov/planetary/apod"


class Apod(Action):

    def run(api_key, date, hd):
        params = {'api_key': api_key}
        if date is not None:
            params['date'] = date
        if hd is not None:
            params['hd'] = hd

        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        return response.json()
