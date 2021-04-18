from json import JSONDecodeError

from flask import Flask
from flask import request
from flask import jsonify
from flask import make_response
import requests
import json
from constants import iso3_codes, states_and_districts, countries_hi
from constants import faqs_hi
from constants import faqs_en
from constants import states
from constants import states_hindi

app = Flask(__name__)


@app.route("/")
def home():
    return "<h3>Source Code at <a href='https://github.com/prateekKrOraon/covid-19-tracker-api'>GitHub</a></h3><h3>COVID-19 Tracker Flutter Application - <a href='https://github.com/prateekKrOraon/covid19_tracker'>GitHub</a></h3>"


@app.route("/india/state_data/")
def india_state_data_error():
    return jsonify({"error_message": "State code unavailable.", "example_link": "https://api-covid19-tracker.herokuapp.com/india/state_data/JH"})


@app.route("/india/state_data/<state_code>")
def india_state_data(state_code):
    from constants import state_codes
    if state_code not in state_codes.keys():
        return jsonify({"message": "Invalid State Code"})

    response = {}
    res = requests.get("https://api.covid19india.org/v2/state_district_wise.json")
    state_district_wise = res.json()

    for i in range(len(state_district_wise)):
        state = state_district_wise[i]
        if state['statecode'] == state_code:
            response['district_wise'] = state['districtData']
            break

    res = requests.get("https://api.covid19india.org/states_daily.json")
    states_daily = res.json()
    state_time_series = []
    for i in range(len(states_daily['states_daily'])):
        states = states_daily['states_daily'][i]
        key = state_code.lower()
        state_time_series.append({'date': states['date'], key: states[key]})

    response['timeseries'] = state_time_series

    res = requests.get("https://api.covid19india.org/zones.json")
    zones_data = res.json()
    zones_res = {}
    for i in range(len(zones_data['zones'])):
        district = zones_data['zones'][i]
        if district['statecode'] == state_code:
            value = district['zone']
            key = district['district'].lower().replace(" ", "_")
            zones_res[key] = value

    response['zones'] = zones_res

    res = requests.get("https://api.covid19india.org/state_test_data.json")
    tested_data = res.json()
    list_data = tested_data['states_tested_data']

    test_info = {}
    for i in range(len(list_data)-1, -1, -1):
        if state_code in state_codes.keys() and list_data[i]['state'] == state_codes[state_code]:
            test_info['total_tested'] = list_data[i]['totaltested']
            test_info['last_update'] = list_data[i]['updatedon']
            test_info['source'] = list_data[i]['source1']
            break

    if len(test_info) == 0:
        response['test_data'] = {"last_update": "", "total_tested": "0", "source": ""}
    else:
        response['test_data'] = test_info

    return jsonify(response)


@app.route("/india/state_wise")
def india_state_wise():
    res = requests.get("https://api.covid19india.org/data.json")
    data = res.json()
    state_wise = data['statewise']
    for i in range(len(state_wise)):
        key = state_wise[i]['state'].lower().replace(" ", "_")
        if key in states_and_districts.keys():
            state_wise[i]['state_hi'] = states_and_districts[key]
        else:
            state_wise[i]['state_hi'] = state_wise[i]['state']

    response = {'statewise': state_wise, 'total_tested': data['tested'][len(data['tested']) - 1]}
    return jsonify(response)


@app.route("/india/on_date/")
def india_state_wise_on_date_error():
    return jsonify({'message': 'Specify date as YYYY-MM-DD', 'example_link' : 'api-covid19-tracker.herokuapp.com/india/on_date/2020-06-07'})


@app.route("/india/on_date/<date>")
def india_state_wise_on_date(date):
    from constants import state_codes
    res = requests.get("https://api.covid19india.org/v3/data-{}.json".format(date))
    data = None
    try:
        data = res.json()
    except JSONDecodeError:
        return jsonify({"message": "Data not available"})

    response = {}
    state_wise = []
    for key in data.keys():
        state = {
            'lastupdatedtime': '{day}/{month}/{year} 23:59:59'.format(
                day=date[8:10],
                month=date[5:7],
                year=date[0:4]),
            'state': state_codes[key],
            'statecode': key
        }
        if state_codes[key].lower().replace(" ", "_") in states_and_districts.keys():
            state['state_hi'] = states_and_districts[state_codes[key].lower().replace(" ", "_")]
        else:
            state['state_hi'] = state_codes[key]

        state['statenotes'] = ""

        if 'confirmed' in data[key]['total'].keys():
            state['confirmed'] = "{}".format(data[key]['total']['confirmed'])
        else:
            state['confirmed'] = "0"

        if 'deceased' in data[key]['total'].keys():
            state['deaths'] = "{}".format(data[key]['total']['deceased'])
        else:
            state['deaths'] = "0"

        if 'recovered' in data[key]['total'].keys():
            state['recovered'] = "{}".format(data[key]['total']['recovered'])
        else:
            state['recovered'] = "0"

        if 'migrated' in data[key]['total'].keys():
            state['migratedother'] = "{}".format(data[key]['total']['migrated'])
        else:
            state['migratedother'] = "0"

        total_tested = {}
        if key == 'TT' and 'tested' in data[key]['total'].keys():
            total_tested['totalsamplestested'] = "{}".format(data[key]['total']['tested'])
            total_tested['totalindividualstested'] = ""
            if 'meta' in data[key].keys():
                if 'tested' in data[key]['meta'].keys():
                    total_tested['updatetimestamp'] = "{day}/{month}/{year} 09:00:00".format(
                        day=data[key]['meta']['tested']['last_updated'][8:10],
                        month=data[key]['meta']['tested']['last_updated'][5:7],
                        year=data[key]['meta']['tested']['last_updated'][0:4])
                    total_tested['source'] = data[key]['meta']['tested']['source']
        else:
            total_tested['totalsamplestested'] = ""
            total_tested['totalindividualstested'] = ""
            total_tested['updatetimestamp'] = ""
            total_tested['source'] = ""

        response['total_tested'] = total_tested

        state['active'] = "{}".format(int(state['confirmed'])-int(state['recovered'])-int(state['deaths']))

        if 'delta' in data[key].keys():
            if 'confirmed' in data[key]['delta'].keys():
                state['deltaconfirmed'] = "{}".format(data[key]['delta']['confirmed'])
            else:
                state['deltaconfirmed'] = "0"

            if 'deceased' in data[key]['delta'].keys():
                state['deltadeaths'] = "{}".format(data[key]['delta']['deceased'])
            else:
                state['deltadeaths'] = "0"

            if 'recovered' in data[key]['delta'].keys():
                state['deltarecovered'] = "{}".format(data[key]['delta']['recovered'])
            else:
                state['deltarecovered'] = "0"
        else:
            state['deltaconfirmed'] = "0"
            state['deltadeaths'] = "0"
            state['deltarecovered'] = "0"

        state_wise.append(state)

    state_wise = sorted(state_wise, key=lambda i: int(i['confirmed']), reverse=True)
    response['statewise'] = state_wise

    return jsonify(response)


@app.route("/india/time_series")
def india_time_series():
    res = requests.get("https://api.covid19india.org/data.json")
    data = res.json()
    response = {'total': data['statewise'][0], 'timeseries': data['cases_time_series']}
    return jsonify(response)


@app.route('/india/states_time_series')
def india_states_time_series():
    res = requests.get("https://api.covid19india.org/states_daily.json")
    data = res.json()
    states_daily = data['states_daily']

    confirm = []
    deaths = []
    recovered = []

    j = 0
    k = 0
    m = 0

    for i in range(len(states_daily)):
        if i % 3 == 0:
            array = {}
            for key, value in states_daily[i].items():
                if i != 0:
                    if key != 'date' and key != 'status':
                        array[key] = int(value) - confirm[j - 1][key]
                    else:
                        array[key] = value
                else:
                    if key != 'date' and key != 'status':
                        array[key] = int(value)
                    else:
                        array[key] = value
            confirm.append(array)
            j = j + 1
        elif i % 3 == 1:
            array = {}
            for key, value in states_daily[i].items():
                if i != 1:
                    if key != 'date' and key != 'status':
                        array[key] = int(value) - recovered[k - 1][key]
                    else:
                        array[key] = value
                else:
                    if key != 'date' and key != 'status':
                        array[key] = int(value)
                    else:
                        array[key] = value
            recovered.append(array)
            k = k + 1
        elif i % 3 == 2:
            array = {}
            for key, value in states_daily[i].items():
                if i != 2:
                    if key != 'date' and key != 'status':
                        array[key] = int(value) - deaths[m - 1][key]
                    else:
                        array[key] = value
                else:
                    if key != 'date' and key != 'status':
                        array[key] = int(value)
                    else:
                        array[key] = value
            deaths.append(array)
            m = m + 1
    response = {'confirmed': confirm, 'recovered': recovered, 'deaths': deaths}
    return jsonify(response)


@app.route('/global_data')
def world_data():
    response = {}
    res = requests.get("https://corona.lmao.ninja/v2/all")
    response['total'] = res.json()
    res = requests.get("https://corona.lmao.ninja/v2/countries?sort=cases")
    data = res.json()
    for i in range(len(data)):
        country = data[i]
        key = country['country'].lower().replace(" ", "_")
        if key in countries_hi.keys():
            data[i]['country_hi'] = countries_hi[key]
        else:
            data[i]['country_hi'] = country['country']

    response['country_wise'] = data
    return jsonify(response)


@app.route('/global_time_series')
def global_time_series():
    res = requests.get("https://covidapi.info/api/v1/global/count")
    response = res.json()
    del response['count']
    return jsonify(response)


@app.route('/country')
def country_data_error():
    return jsonify({"error_message": "Country code unavailable.", "example_link": "https://api-covid19-tracker.herokuapp.com/country/USA"})


@app.route('/country/<iso3>')
def country_data(iso3):
    res = requests.get("https://covidapi.info/api/v1/country/{code}".format(code=iso3))
    response = res.json()
    del response['count']
    return jsonify(response)


@app.route('/compare')
def compare_countries():
    country_one = request.args['country_one'].lower().replace(" ", "_")
    country_two = request.args['country_two'].lower().replace(" ", "_")

    if country_one in iso3_codes.keys():
        country_one = iso3_codes[country_one]
    else:
        country_one = "error"

    if country_two in iso3_codes.keys():
        country_two = iso3_codes[country_two]
    else:
        country_two = "error"

    res = requests.get("https://covidapi.info/api/v1/country/{}".format(country_one))
    country_one_data = res.json()

    res = requests.get("https://corona.lmao.ninja/v2/countries/{}".format(country_one))
    country_one_details = res.json()

    res = requests.get("https://covidapi.info/api/v1/country/{}".format(country_two))
    country_two_data = res.json()

    res = requests.get("https://corona.lmao.ninja/v2/countries/{}".format(country_two))
    country_two_details = res.json()

    response = []
    response_one = {}
    response_two = {}

    if country_one == "error":
        response_one['country'] = "error"
    else:
        key = country_one_details['country'].lower().replace(" ", "_")
        if key in countries_hi.keys():
            country_one_details['country_hi'] = countries_hi[key]
        else:
            country_one_details['country_hi'] = country_one_details['country']

        response_one['details'] = country_one_details
        response_one['result'] = country_one_data['result']

    if country_two == "error":
        response_two['country'] = "error"
    else:
        key = country_two_details['country'].lower().replace(" ", "_")
        if key in countries_hi.keys():
            country_two_details['country_hi'] = countries_hi[key]
        else:
            country_two_details['country_hi'] = country_two_details['country']

        response_two['details'] = country_two_details
        response_two['result'] = country_two_data['result']

    response.append(response_one)
    response.append(response_two)

    return jsonify(response)


@app.route('/check_for_updates', methods=['POST'])
def check_for_updates():
    data = request.get_json()
    version = data['version']
    latest = "1.6.0"
    ver_str = version.replace(".", "")
    data = {}
    if int(ver_str) < int(latest.replace(".", "")):
        data['update'] = True
        data['version'] = latest
        data['link'] = "https://github.com/prateekKrOraon/covid-19-tracker/releases"
    else:
        data['update'] = False
        data['version'] = latest
        data['link'] = "https://github.com/prateekKrOraon/covid-19-tracker/releases"

    return make_response(jsonify(data), 200)


@app.route('/faqs/<lang_code>')
def faqs(lang_code):
    if lang_code == "en":
        return jsonify(faqs_en)
    elif lang_code == "hi":
        return jsonify(faqs_hi)
    else:
        return jsonify({"message": "Language not available"})


@app.route('/resources')
def resources():
    res = requests.get("https://api.covid19india.org/resources/resources.json")
    return jsonify(res.json())


@app.route('/sources')
def sources():
    res = requests.get('https://api.covid19india.org/sources_list.json')
    return jsonify(res.json())


@app.route('/update_logs/<lang_code>')
def update_logs(lang_code):
    res = requests.get("https://api.covid19india.org/updatelog/log.json")
    logs = res.json()

    if lang_code == "en":
        return jsonify(logs)
    elif lang_code == "hi":

        response = []

        for i in range(len(logs)):
            update = {}
            splits = logs[i]['update'].split("\n")
            for j in range(len(splits)):
                if (splits[j].find("death") != -1 or splits[j].find("deaths") != -1) and (
                        splits[j].find("recovery") != -1 or splits[j].find("recoveries") != -1) and (
                        splits[j].find("new case") != -1 or splits[j].find("new cases") != -1):
                    words = splits[j].split(" ")
                    if words[len(words) - 1] in states:
                        key = words[len(words) - 1].lower().replace(" ", "_")
                        val = "{state} में {positive} नए संक्रामक, {recovered} स्वस्थ और {deaths} मौत".format(
                            state=states_hindi[key], positive=words[0], recovered=words[3], deaths=words[6]
                        )
                        if "update" not in update.keys():
                            update["update"] = ""

                        update["update"] += val + "\n"
                        update["timestamp"] = logs[i]['timestamp']
                    elif len(words) > 2 and words[len(words) - 2] + " " + words[len(words) - 1] in states:
                        name = "{} {}".format(words[len(words) - 2], words[len(words) - 1])
                        key = name.lower().replace(" ", "_")
                        val = "{state} में {positive} नए संक्रामक, {recovered} स्वस्थ और {deaths} मौत".format(
                            state=states_hindi[key], positive=words[0], recovered=words[3], deaths=words[6]
                        )
                        if "update" not in update.keys():
                            update["update"] = ""

                        update["update"] += val + "\n"
                        update["timestamp"] = logs[i]['timestamp']
                elif (splits[j].find("death") == -1 or splits[j].find("deaths") == -1) and (
                        splits[j].find("recovery") != -1 or splits[j].find("recoveries") != -1) and (
                        splits[j].find("new case") != -1 or splits[j].find("new cases") != -1):
                    words = splits[j].split(" ")
                    if words[len(words) - 1] in states:
                        key = words[len(words) - 1].lower().replace(" ", "_")
                        val = "{state} में {positive} नए संक्रामक, {recovered} स्वस्थ".format(
                            state=states_hindi[key], positive=words[0], recovered=words[4]
                        )
                        if "update" not in update.keys():
                            update["update"] = ""

                        update["update"] += val + "\n"
                        update["timestamp"] = logs[i]['timestamp']
                    elif len(words) > 2 and words[len(words) - 2] + " " + words[len(words) - 1] in states:
                        name = "{} {}".format(words[len(words) - 2], words[len(words) - 1])
                        key = name.lower().replace(" ", "_")
                        val = "{state} में {positive} नए संक्रामक, {recovered} स्वस्थ".format(
                            state=states_hindi[key], positive=words[0], recovered=words[4]
                        )
                        if "update" not in update.keys():
                            update["update"] = ""

                        update["update"] += val + "\n"
                        update["timestamp"] = logs[i]['timestamp']
                elif (splits[j].find("death") != -1 or splits[j].find("deaths") != -1) and (
                        splits[j].find("recovery") == -1 or splits[j].find("recoveries") == -1) and (
                        splits[j].find("new case") != -1 or splits[j].find("new cases") != -1):
                    words = splits[j].split(" ")
                    if words[len(words) - 1] in states:
                        key = words[len(words) - 1].lower().replace(" ", "_")
                        val = "{state} में {positive} नए संक्रामक और {deaths} मौत".format(
                            state=states_hindi[key], positive=words[0], deaths=words[4]
                        )
                        if "update" not in update.keys():
                            update["update"] = ""

                        update["update"] += val + "\n"
                        update["timestamp"] = logs[i]['timestamp']
                    elif len(words) > 2 and words[len(words) - 2] + " " + words[len(words) - 1] in states:
                        name = "{} {}".format(words[len(words) - 2], words[len(words) - 1])
                        key = name.lower().replace(" ", "_")
                        val = "{state} में {positive} नए संक्रामक और {deaths} मौत".format(
                            state=states_hindi[key], positive=words[0], deaths=words[4]
                        )
                        if "update" not in update.keys():
                            update["update"] = ""

                        update["update"] += val + "\n"
                        update["timestamp"] = logs[i]['timestamp']
                elif (splits[j].find("death") != -1 or splits[j].find("deaths") != -1) and (
                        splits[j].find("recovery") != -1 or splits[j].find("recoveries") != -1) and (
                        splits[j].find("new case") == -1 or splits[j].find("new cases") == -1):
                    words = splits[j].split(" ")
                    if words[len(words) - 1] in states:
                        key = words[len(words) - 1].lower().replace(" ", "_")
                        val = "{state} में {recovered} स्वस्थ और {deaths} मौत".format(
                            state=states_hindi[key], recovered=words[0], deaths=words[3]
                        )
                        if "update" not in update.keys():
                            update["update"] = ""

                        update["update"] += val + "\n"
                        update["timestamp"] = logs[i]['timestamp']
                    elif len(words) > 2 and words[len(words) - 2] + " " + words[len(words) - 1] in states:
                        name = "{} {}".format(words[len(words) - 2], words[len(words) - 1])
                        key = name.lower().replace(" ", "_")
                        val = "{state} में {recovered} स्वस्थ और {deaths} मौत".format(
                            state=states_hindi[key], recovered=words[0], deaths=words[3]
                        )
                        if "update" not in update.keys():
                            update["update"] = ""

                        update["update"] += val + "\n"
                        update["timestamp"] = logs[i]['timestamp']
                elif (splits[j].find("death") == -1 or splits[j].find("deaths") == -1) and (
                        splits[j].find("recovery") == -1 or splits[j].find("recoveries") == -1) and (
                        splits[j].find("new case") != -1 or splits[j].find("new cases") != -1):
                    words = splits[j].split(" ")
                    if words[len(words) - 1] in states:
                        key = words[len(words) - 1].lower().replace(" ", "_")
                        val = "{state} में {positive} नए संक्रामक".format(
                            state=states_hindi[key], positive=words[0]
                        )
                        if "update" not in update.keys():
                            update["update"] = ""

                        update["update"] += val + "\n"
                        update["timestamp"] = logs[i]['timestamp']
                    elif len(words) > 2 and words[len(words) - 2] + " " + words[len(words) - 1] in states:
                        name = "{} {}".format(words[len(words) - 2], words[len(words) - 1])
                        key = name.lower().replace(" ", "_")
                        val = "{state} में {positive} नए संक्रामक".format(
                            state=states_hindi[key], positive=words[0]
                        )
                        if "update" not in update.keys():
                            update["update"] = ""

                        update["update"] += val + "\n"
                        update["timestamp"] = logs[i]['timestamp']
                elif (splits[j].find("death") == -1 or splits[j].find("deaths") == -1) and (
                        splits[j].find("recovery") != -1 or splits[j].find("recoveries") != -1) and (
                        splits[j].find("new case") == -1 or splits[j].find("new cases") == -1):
                    words = splits[j].split(" ")
                    if words[len(words) - 1] in states:
                        key = words[len(words) - 1].lower().replace(" ", "_")
                        val = "{state} में {recovered} स्वस्थ".format(
                            state=states_hindi[key], recovered=words[0]
                        )
                        if "update" not in update.keys():
                            update["update"] = ""

                        update["update"] += val + "\n"
                        update["timestamp"] = logs[i]['timestamp']
                    elif len(words) > 2 and words[len(words) - 2] + " " + words[len(words) - 1] in states:
                        name = "{} {}".format(words[len(words) - 2], words[len(words) - 1])
                        key = name.lower().replace(" ", "_")
                        val = "{state} में {recovered} स्वस्थ".format(
                            state=states_hindi[key], recovered=words[0]
                        )
                        if "update" not in update.keys():
                            update["update"] = ""

                        update["update"] += val + "\n"
                        update["timestamp"] = logs[i]['timestamp']
                elif (splits[j].find("death") != -1 or splits[j].find("deaths") != -1) and (
                        splits[j].find("recovery") == -1 or splits[j].find("recoveries") == -1) and (
                        splits[j].find("new case") == -1 or splits[j].find("new cases") == -1):
                    words = splits[j].split(" ")
                    if words[len(words) - 1] in states:
                        key = words[len(words) - 1].lower().replace(" ", "_")
                        val = "{state} में {deaths} मौत".format(
                            state=states_hindi[key], deaths=words[0]
                        )
                        if "update" not in update.keys():
                            update["update"] = ""

                        update["update"] += val + "\n"
                        update["timestamp"] = logs[i]['timestamp']
                    elif len(words) > 2 and words[len(words) - 2] + " " + words[len(words) - 1] in states:
                        name = "{} {}".format(words[len(words) - 2], words[len(words) - 1])
                        key = name.lower().replace(" ", "_")
                        val = "{state} में {deaths} मौत".format(
                            state=states_hindi[key], deaths=words[0]
                        )
                        if "update" not in update.keys():
                            update["update"] = ""

                        update["update"] += val + "\n"
                        update["timestamp"] = logs[i]['timestamp']
            if len(update) != 0:
                response.append(update)

        return jsonify(response)


if __name__ == '__main__':
    app.run(port=8080)
