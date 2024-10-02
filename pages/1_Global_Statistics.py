import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st


# Page configuration
st.set_page_config(layout='wide', page_title='COVID-19: Global')


# Read in data:
## Global data
url_global = 'https://raw.githubusercontent.com/jamesinjune/COVID_19_Data_Exploration/refs/heads/main/visualization_data/covid_daily_global.csv'
df_global = pd.read_csv(url_global)

df_global['date'] = pd.to_datetime(df_global['date'])
df_global = df_global.sort_values(['date']).reset_index(drop=True)


# Constants
metric_list = [
    'Total Cases',
    'Total Deaths',
    'Total Recoveries',
    'Total Active Cases',
    'Daily New Cases',
    'Daily New Deaths',
    'Daily New Recoveries',
    'Cases Breakdown: Deaths, Recoveries, and Active Cases',
    'Case Fatality Rate',
]


# Functions
def graph_area_global(measure, color):
    df = df_global[['date', measure]].dropna()
    fig = px.area(
        df,
        x='date',
        y=measure,
        color_discrete_sequence=[color],
        hover_data={'date': True, measure: True},
    )
    fig.update_layout(
        xaxis_title='date',
        yaxis_title='count',
        xaxis_rangeslider_visible=True,
        width=800,
        height=600,
    )
    return fig


def graph_stacked_global_case():
    df_glob_filtered = df_global.dropna(subset=['active'])[
        ['date', 'recovered', 'deaths', 'active']
    ]
    df_glob_melted = df_glob_filtered.melt(
        id_vars='date', var_name='Measure', value_name='val'
    )

    fig = px.area(
        df_glob_melted,
        x='date',
        y='val',
        color='Measure',
        color_discrete_sequence=['#10cf51', '#ec1342', '#ff9c00'],
    )
    fig.update_layout(
        title='Total Cases Split by Recoveries, Deaths, and Active Cases',
        xaxis_title='date',
        yaxis_title='count',
        xaxis_rangeslider_visible=True,
        width=800,
        height=600,
    )
    return fig


def graph_global_case_fatality():
    fig = px.line(
        df_global, x='date', y='case_fatality_rate', color_discrete_sequence=['#b50f33']
    )
    fig.update_layout(
        title='Global Case Fatality Rate per 100,000 population',
        xaxis_title='date',
        yaxis_title='rate (per 100,000)',
        xaxis_rangeslider_visible=True,
        width=800,
        height=600,
    )
    return fig


def main():

    st.sidebar.markdown(
        '''
        ### About

        The global analysis tool allows you to examine various COVID-19 metrics on a global scale.

        To get started, please select a metric to examine.
        '''
    )

    st.title('Global Statistics on COVID-19')

    st.markdown(
        '''
        The COVID-19 pandemic has had a substantial impact all across the globe since the early days of 2020. Below is a series of charts that track the worldwide progression of COVID-19 from 2020-2023.

        - **Note**: This data was aggregated by summing country-level data to estimate worldwide numbers. Due to inconsistencies in the accurate 
        reporting of COVID-19 numbers by governments across the world, as well as missing data from various other countries, the figures below are lower than the true metric.
        - The dataset used can be viewed [here](https://github.com/jamesinjune/COVID_19_Data_Exploration/blob/main/visualization_data/covid_daily_global.csv).
        '''
    )

    metric_select = st.selectbox('Select a metric', options=metric_list)

    if metric_select == 'Total Cases':
        st.markdown(
            f'''
            The **raw case count** of COVID-19 worldwide. The true value may differ due to inconsistencies in data collection as well as missing country data.
            '''
        )
        global_cases_fig = graph_area_global('cases', '#6f6fe7')
        st.plotly_chart(global_cases_fig)

    if metric_select == 'Total Deaths':
        st.markdown(
            f'''
            The raw death count of COVID-19 worldwide. The true value may differ due to inconsistencies in data collection as well as missing country data.
            '''
        )
        global_deaths_fig = graph_area_global('deaths', '#ec1342')
        st.plotly_chart(global_deaths_fig)

    if metric_select == 'Total Recoveries':
        st.markdown(
            f'''
            The raw recovery count from COVID-19 worldwide. The true value may differ due to inconsistencies in data collection as well as missing country data.
            '''
        )
        global_recovered_fig = graph_area_global(
            'recovered', '#12ed5d'
        )
        st.plotly_chart(global_recovered_fig)

    if metric_select == 'Total Active Cases':
        st.markdown(
            f'''
            The active case count of COVID-19 worldwide on a given date. The true value may differ due to inconsistencies in data collection as well as missing country data.
            '''
        )
        global_active_fig = graph_area_global('active', '#ff9c00')
        st.plotly_chart(global_active_fig)

    if metric_select == 'Daily New Cases':
        st.markdown(
            f'''
            The count of new COVID-19 cases worldwide on a given date. The true value may differ due to inconsistencies in data collection as well as missing country data.
            '''
        )
        global_new_cases_fig = graph_area_global(
            'new_cases', '#6f6fe7'
        )
        st.plotly_chart(global_new_cases_fig)

    if metric_select == 'Daily New Deaths':
        st.markdown(
            f'''
            The count of new COVID-19 deaths worldwide on a given date. The true value may differ due to inconsistencies in data collection as well as missing country data.
            '''
        )
        global_new_deaths_fig = graph_area_global(
            'new_deaths', '#ec1342'
        )
        st.plotly_chart(global_new_deaths_fig)

    if metric_select == 'Daily New Recoveries':
        st.markdown(
            f'''
            The count of new COVID-19 recoveries worldwide on a given date. The true value may differ due to inconsistencies in data collection as well as missing country data.
            '''
        )
        global_new_recovered_fig = graph_area_global(
            'new_recovered', '#11de57'
        )
        st.plotly_chart(global_new_recovered_fig)

    if metric_select == 'Cases Breakdown: Deaths, Recoveries, and Active Cases':
        st.markdown(
            f'''
            The total case count of COVID-19 worldwide, split between current active cases, recoveries, and deaths. The purpose is to investigate the proportions of each metric in relation to each other.
            '''
        )
        global_case_stacked_fig = graph_stacked_global_case()
        st.plotly_chart(global_case_stacked_fig)

    if metric_select == 'Case Fatality Rate':
        st.markdown(
            f'''
            The total number of people per 100,000 infected by COVID-19 that have died so far, on a given date.
            '''
        )
        global_case_fatality_fig = graph_global_case_fatality()
        st.plotly_chart(global_case_fatality_fig)


if __name__ == '__main__':
    main()
