from flask import Flask
from flask import request
from flask import jsonify
from flask import make_response
import requests
import json
from constants import iso3_codes
from constants import faqs_hi
from constants import faqs_en
from constants import states
from constants import states_hindi

app = Flask(__name__)


@app.route("/")
def home():
    return "<h3>Source Code at <a href='https://github.com/prateekKrOraon/covid-19-tracker-api'>GitHub</a></h3><h3>COVID-19 Tracker Flutter Application - <a href='https://github.com/prateekKrOraon/covid19_tracker'>GitHub</a></h3>"


@app.route("/india/state_data/<state_code>")
def india_state_data(state_code):
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
    return jsonify(response)


@app.route("/india/state_wise")
def india_state_wise():
    res = requests.get("https://api.covid19india.org/data.json")
    data = res.json()
    response = {'statewise': data['statewise'], 'total_tested': data['tested'][len(data['tested']) - 1]}
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
    response['country_wise'] = res.json()
    return jsonify(response)


@app.route('/global_time_series')
def global_time_series():
    res = requests.get("https://covidapi.info/api/v1/global/count")
    response = res.json()
    del response['count']
    return jsonify(response)


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
        response_one['details'] = country_one_details
        response_one['result'] = country_one_data['result']

    if country_two == "error":
        response_two['country'] = "error"
    else:
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
    app.run()
