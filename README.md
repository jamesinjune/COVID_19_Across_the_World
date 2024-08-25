# COVID-19 Exploration
Exploration of various COVID-19 metrics, including cases, deaths, recoveries, vaccinations, stringency index, etc.

---

## Visualizations
The notebook with all interactive visualizations can be accessed and interacted with [here in a Binder environment](https://mybinder.org/v2/gh/jamesinjune/COVID_19_Data_Exploration/2168db1c3ce959860f0a10c31fd24865dcaf0ed4?urlpath=lab%2Ftree%2FCOVID_Visualizations.ipynb).

**Important: Please run all cells in the notebook before interacting with the charts to ensure that each chart is fully rendered.**

---

## Project Overview
This exploration aims to visually demonstrate the spread of COVID-19 over the first 2-3 years of the pandemic, as well as explore key metrics on both global and country-levels. 

### Tools Used
- Python (pandas) - [Data cleaning process](https://github.com/jamesinjune/COVID_19_Data_Exploration/tree/main/notebooks)
- SQL Server - [Data querying/merging process](https://github.com/jamesinjune/COVID_19_Data_Exploration/blob/main/covid_queries_views.sql)
- Python (plotly) - [Visualizations](https://github.com/jamesinjune/COVID_19_Data_Exploration/blob/main/COVID_Visualizations.ipynb)

---

### Datasets (GitHub links):
- [Country-Level Dataset](https://github.com/jamesinjune/COVID_19_Data_Exploration/blob/main/visualization_data/covid_daily_country.zip)
- [Global Dataset](https://github.com/jamesinjune/COVID_19_Data_Exploration/blob/main/visualization_data/covid_daily_global.csv)

### Data Sources and Collection:
- Raw data can be found [here](https://github.com/jamesinjune/COVID_19_Data_Exploration/tree/main/raw_data).
- Data cleaning notebooks can be found [here](https://github.com/jamesinjune/COVID_19_Data_Exploration/tree/main/notebooks).
- Original data sources are as follows:
    - https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series
    - https://github.com/owid/covid-19-data/blob/master/public/data/vaccinations/vaccinations.csv
    - https://github.com/OxCGRT/covid-policy-tracker/blob/master/data/timeseries/stringency_index_avg.csv
    - https://data.worldbank.org/indicator/SP.POP.TOTL
    - https://hdr.undp.org/data-center/documentation-and-downloads

## Dataset Descriptions:
COVID-19 data consolidated from multiple data sources at global and country levels.

### Global Daily Dataset:
The global dataset contains daily entries for various COVID-19 measures. Data was acquired by grouping all country-level data by date from the country-level dataset. This dataset contains the following fields:
- `date`: The date in YYYY-MM-DD format.
- `cases`: Total case count of COVID-19 as of date.
- `deaths`: Total death count by COVID-19 as of date.
- `recovered`: Total count of COVID-19 recoveries as of date.
- `new_cases`: Number of new cases of COVID-19 on that date.
- `new_recovered`: Number of new recoveries from COVID-19 on that date.
- `active`: Number of active COVID-19 cases on that date.
- `case_fatality_rate`: Total death count divided by total case count of COVID-19 on that date, per 100,000 population. The number of people per 100,000 infected by COVID-19 that have died.

### Country Daily Dataset:
- `country`: Name of country. Note that there are countries missing from this dataset.
- `date`: Date in YYYY-MM-DD format.
- `cases`: Total case count of COVID-19 as of date.
- `new_cases_smoothed`: Number of new cases of COVID-19 on that date, with a 7-day moving average applied.
- `new_cases_growth_rate`: Percentage change in `new_cases_smoothed`, as a decimal.
- `deaths`: Total death count of COVID-19 as of date.
- `new_deaths_smoothed`: Number of new deaths by COVID-19 on that date, with a 7-day moving average applied.
- `recovered`: Total count of COVID-19 recoveries as of date.
- `new_recovered_smoothed`: Number of new recoveries from COVID-19 on that date, with a 7-day moving average applied.
- `people_vaccinated`: Total number of people who have received at least one dose of a registered vaccine.
- `people_fully_vaccinated`: Total number of people who have received all doses prescribed by vaccination protocol.
- `total_vaccinations`: Total count of vaccination doses administered.
- `total_boosters`: Total count of vaccination boosters administered (doses beyond what is prescribed by vaccination protocol)
- `daily_people_vaccinated`: Number of people receiving their first vaccination on that date.
- `daily_people_fully_vaccinated`: Number of people completing their vaccination protocol on that date.
- `daily_vaccinations`: Number of vaccination doses administered on that date (counts any dose).
- `daily_boosters`: Number of boosters administered on that date.
- `population`: Total population of country on that date. Only updates yearly, unfortunately.
- `stringency_value`: An aggregate of nine measures that quantifies a country's level of strictness of government policies to reduce the spread of COVID-19. These include lockdowns, travel restrictions, school closures, etc. More info can be found [here](https://github.com/OxCGRT/covid-policy-dataset/blob/main/documentation_and_codebook.md).
- `hdi_value`: The human development index of a country. Measures, broadly, the overall development and quality of life of countries by examining health, education, and standards of living. Only updates yearly.
- `active`: Number of active COVID-19 cases on that date.
- `infection_rate`: The total count of cases per 100,000 people in a country.
- `people_vaccinated_rate`: The total count of people vaccinated per 100,000 people in a country.
- `fully_vaccinated_rate`: The total count of people fully vaccinated per 100,000 people in a country.
- `case_incidence_rate`: The number of new cases per 100,000 people in a country, on that date.
- `case_fatality_rate`: Total death count divided by total case count of COVID-19 on that date, per 100,000 population. The number of people per 100,000 infected by COVID-19 that have died.
- `active_case_rate`: The number of active cases per 100,000 people in a country.

## Selected Key Insights
- As we get further into the pandemic, **the HDI of a country seems to have greater association with the infection rate of COVID-19**. Being that the y-axis is on a logarithmic scale, this indicates that infection rate could change exponentially as a function of HDI. Case fatality rate, however, seems to have very little association with HDI.
- Despite having the world's largest population, **after the first few months China does not appear in the top 15 total case count worldwide**.

## Limitations
- As with any data collected from countries across the world, the standard of data quality and the data collection process varies greatly. There are a few instances of sudden shifts in overall data trends that result from such errors. The following are a few examples of such:
  - `recovered` count of Uganda increases suddenly on 2021-03-25, resulting in a sudden decrease in `active` count.
  - `recovered` count was missing for countries including the United Kingdom and Serbia. Those countries now have NULLs in `recovered` column.
- Some calculated fields are not as useful or meaningful for larger countries, especially those calculated using the `population` column, such as `case_incidence_rate`. For countries as large and as spread out as China, we do not have a good understanding of the spread of COVID-19 from this dataset.
