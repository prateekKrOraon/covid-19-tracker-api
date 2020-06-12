# COVID-19 Tracker API
This API is used by [COVID-19 Tracker](https://github.com/prateekKrOraon/covid19_tracker)

### Endpoints

|Data|URL|
|----|----|
|India: Time Series|https://api-covid19-tracker.herokuapp.com/india/time_series|
|India: State Data|https://api-covid19-tracker.herokuapp.com/india/state_data/<state_code>|
|India: State Wise Data|https://api-covid19-tracker.herokuapp.com/india/state_wise|
|India: State Wise Time Series|https://api-covid19-tracker.herokuapp.com/india/states_time_series|
|India: State Wise Data (For any particular date.)|https://api-covid19-tracker.herokuapp.com/india/on_date/<{YYYY-MM-DD}>|
|Global Data: Time Series|https://api-covid19-tracker.herokuapp.com/global_time_series|
|Global Data: Country wise information|https://api-covid19-tracker.herokuapp.com/global_data|
|Global Data: Country information|https://api-covid19-tracker.herokuapp.com/country/<iso3_code>|
|MISC: FAQs (English)|https://api-covid19-tracker.herokuapp.com/faqs/en|
|MISC: FAQs (Hindi)|https://api-covid19-tracker.herokuapp.com/faqs/hi|
|MISC: India Update Logs (English)|https://api-covid19-tracker.herokuapp.com/update_logs/en|
|MISC: India Update Logs (Hindi)|https://api-covid19-tracker.herokuapp.com/update_logs/hi|


### Data Sources
|Data|Source|
|----|------|
|India|https://api.covid19india.org|
|Global|https://corona.lmao.ninja|

### Contributions
* Contributions are welcome. Please create a GH issue and discuss there before working on the same.
* Please raise an issue before submitting a pull request.
