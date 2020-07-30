from datetime import datetime
import json
import random
from flask import Flask, request
from covid import Covid
from iso3166 import countries

app = Flask(__name__)
covid = Covid()
stat_name = {
    'confirmed': 'confirmed cases',
    'deaths': 'confirmed deaths',
    'active': 'active cases',
    'recovered': 'recovered cases'
}


@app.route('/covidbot', methods=['POST'])
def covidbot():
    stat = request.form.get('Field_stat_Value')
    country = request.form.get('Field_country_Value')
    memory = json.loads(request.form['Memory'])
    if stat is None:
        stat = memory.get('stat')
    if country is None:
        country = memory.get('country')

    message = None
    if stat is None or country is None:
        message = 'Sorry, I do not understand. Can you repeat?'

    if message is None:
        try:
            country_name = countries.get(country).name
        except KeyError:
            message = 'Sorry, I do not recognize that country.'
        if country == 'USA':
            country_key = 'US'
        else:
            country_key = country_name

    if message is None:
        results = covid.get_status_by_country_name(country_key)
        last_update = datetime.utcfromtimestamp(
            results['last_update'] / 1000).strftime('%Y-%m-%d')
        message = random.choice([
            (f'As of {last_update}, {country_name} has '
             f'{results[stat]} {stat_name[stat]}.'),
            (f'There are {results[stat]} {stat_name[stat]} in {country_name}, '
             f'as of {last_update}.'),
            (f'{country_name} has {results[stat]} {stat_name[stat]} as of '
             f'{last_update}.')
        ])

    return {
        'actions': [
            {'say': message},
            {'remember': {'stat': stat, 'country': country}},
            {'listen': True},
        ]
    }