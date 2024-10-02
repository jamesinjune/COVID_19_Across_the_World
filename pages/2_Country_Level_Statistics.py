import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st

from datetime import datetime

# Page configuration
st.set_page_config(layout='wide', page_title='COVID-19: Country')


# Read in data:
## Country data
zip_url_country = 'https://github.com/jamesinjune/COVID_19_Data_Exploration/raw/refs/heads/main/visualization_data/covid_daily_country.zip'
df_country = pd.read_csv(zip_url_country, compression='zip', encoding='latin-1')

df_country['date'] = pd.to_datetime(df_country['date'])
df_country = df_country.sort_values(['country', 'date']).reset_index(drop=True)


# Constants
country_list = df_country['country'].unique()

metric_list = [
    'Total Cases',
    'Total Deaths',
    'Total Recoveries',
    'Total Active Cases',
    'Daily New Cases',
    'Daily New Deaths',
    'Daily New Recoveries',
    'Cases Breakdown: Recoveries, Deaths, and Active Cases',
    'People Vaccinated',
    'People Fully Vaccinated',
    'Total Vaccinations',
    'Total Boosters',
    'Daily People Vaccinated',
    'Daily People Fully Vaccinated',
    'Daily Vaccinations',
    'Daily Boosters',
    'Stringency Index',
]


# Functions
def capitalize_to_title(string):
    string = string.replace('_', ' ')
    string = string.title()
    return string


def graph_area_country(country, measure, color, title):
    df = df_country.dropna(subset=[measure])
    df = df[df['country'] == country]
    fig = px.area(df, x='date', y=measure, color_discrete_sequence=[color])
    fig.update_layout(
        title=title,
        xaxis_title='date',
        yaxis_title='count',
        xaxis_rangeslider_visible=True,
        width=800,
        height=600,
    )
    return fig


def graph_stacked_country_case(country):
    df = df_country[df_country['country'] == country].set_index('country')
    df_filtered = df.dropna(subset=['active'])[
        ['date', 'recovered', 'deaths', 'active']
    ]
    df_melted = df_filtered.melt(id_vars='date', var_name='Measure', value_name='val')

    fig = px.area(
        df_melted,
        x='date',
        y='val',
        color='Measure',
        color_discrete_sequence=['#10cf51', '#ec1342', '#ff9c00'],
    )
    fig.update_layout(
        title=f'Total Cases Split by Recoveries, Deaths, Active Cases in {country}',
        xaxis_title='date',
        yaxis_title='count',
        xaxis_rangeslider_visible=True,
        width=800,
        height=600,
    )
    return fig


def graph_country_stringency(country):
    df = df_country[df_country['country'] == country]
    df = df[['date', 'stringency_value']].dropna()
    fig = px.line(
        df, x='date', y='stringency_value', color_discrete_sequence=['#d97670']
    )
    fig.update_layout(
        title=f'Stringency Index in {country}',
        xaxis_title='date',
        yaxis_title='stringency index',
        xaxis_rangeslider_visible=True,
        width=800,
        height=600,
    )
    return fig


# Creates bar graphs of top/bottom 15 countries in given measure
def graph_bar_country(measure, date, is_top_n=True):
    df = df_country[df_country['population'] > 1000000]
    df = df[df['date'] == date]
    df = df[['country', measure, 'hdi_value']]
    if is_top_n == True:
        df = (
            df.sort_values(by=measure, ascending=False)
            .head(15)
            .sort_values(by=measure, ascending=True)
        )
    else:
        df = (
            df.sort_values(by=measure, ascending=True)
            .head(15)
            .sort_values(by=measure, ascending=False)
        )
    df['hdi_value'] = df['hdi_value'].round(2)
    fig = px.bar(
        df,
        x=measure,
        y='country',
        orientation='h',
        range_color=[0, 1],
        hover_data={'hdi_value': True},
    )
    if is_top_n == True:
        fig.update_layout(
            title=f'Top 15 Countries by {capitalize_to_title(measure)}',
            xaxis_title='country',
            yaxis_title=measure,
            width=1000,
            height=450,
        )
    else:
        fig.update_layout(
            title=f'Bottom 15 Countries by {capitalize_to_title(measure)}',
            xaxis_title='country',
            yaxis_title=measure,
            width=1000,
            height=450,
        )
    return fig


def graph_country_dual(country, measure_y1, measure_y2, title):
    df = df_country[df_country['country'] == country]
    df = df[['date', measure_y1, measure_y2]].dropna()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df[measure_y1],
            fill='tozeroy',
            mode='lines',
            name=f'{measure_y1}',
            line=dict(color='#6f6fe7'),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df[measure_y2],
            mode='lines',
            name=f'{measure_y2}',
            yaxis='y2',
            line=dict(color='#d97670'),
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title='date',
        yaxis_title=f'{measure_y1}',
        yaxis2=dict(title=f'{measure_y2}', overlaying='y', side='right'),
        xaxis_rangeslider_visible=True,
        width=1000,
        height=600,
    )
    return fig


def hdi_dist(date):
    df = df_country[df_country['date'] == date]
    fig = px.box(df, x='hdi_value')
    fig.update_layout(width=1000, height=400)
    return fig


def graph_scatter(measure_x, measure_y, date, log_x=False, log_y=False):
    df = df_country[df_country['date'] == date]
    df = df[df['population'] > 1000000]
    df['date'] = df['date'].astype(str)
    df[measure_x] = df[measure_x] + 1
    df[measure_y] = df[measure_y] + 1
    fig = px.scatter(
        df,
        x=measure_x,
        y=measure_y,
        trendline='ols',
        trendline_options=dict(log_x=log_x, log_y=log_y),
        hover_data={'country': True, 'date': True},
        log_x=log_x,
        log_y=log_y,
    )
    fig.update_layout(width=1000, height=400)
    return fig


def main():

    st.sidebar.markdown(
        '''
        ### About

        The country analysis tool allows you to examine various COVID-19 metrics of any given country.

        To get started, please select a country below.
        '''
    )

    country_select = st.sidebar.selectbox('Select a country', country_list)

    st.title('COVID-19 Statistics by Country')

    st.markdown(
        '''
        While COVID-19 can undoubtedly be defined as a global crisis, its impact has varied significantly across different countries. Below is a series of charts that examine various COVID-19 metrics at the country-level.

        - **Note**: Due to inconsistencies in how different countries report COVID-19 data, some countries may be missing values and every existing metric is underreported. While we have attempted to minimize this by using techniques such as interpolation, there are inherent inaccuracies in this dataset.
        - The dataset used can be viewed [here](https://github.com/jamesinjune/COVID_19_Data_Exploration/blob/main/visualization_data/covid_daily_country.zip).
        '''
    )

    # General Metrics Section
    st.header('General Metrics')

    metric_select = st.selectbox('Select a metric', options=metric_list)

    if metric_select == 'Total Cases':
        st.markdown(
            f'''
            Raw case count of COVID-19 in {country_select}. The true value may differ due to underreporting.
            '''
        )
        country_cases_fig = graph_area_country(
            country_select, 'cases', '#6f6fe7', f'Total Cases: {country_select}'
        )
        st.plotly_chart(country_cases_fig)

    if metric_select == 'Total Deaths':
        st.markdown(
            f'''
            Raw death count of COVID-19 in {country_select}. The true value may differ due to underreporting.
            '''
        )
        country_deaths_fig = graph_area_country(
            country_select, 'deaths', '#ec1342', f'Total Deaths: {country_select}'
        )
        st.plotly_chart(country_deaths_fig)

    if metric_select == 'Total Recoveries':
        st.markdown(
            f'''
            Raw recovery count of COVID-19 in {country_select}. The true value may differ due to underreporting.
            '''
        )
        country_recovered_fig = graph_area_country(
            country_select, 'recovered', '#11de57', f'Total Recoverys: {country_select}'
        )
        st.plotly_chart(country_recovered_fig)

    if metric_select == 'Total Active Cases':
        st.markdown(
            f'''
            Active case count of COVID-19 in {country_select} on a given date. The true value may differ due to underreporting.
            '''
        )
        country_active_fig = graph_area_country(
            country_select, 'active', '#ff9c00', f'Total Active Cases: {country_select}'
        )
        st.plotly_chart(country_active_fig)

    if metric_select == 'Daily New Cases':
        st.markdown(
            f'''
            Number of new COVID-19 cases in {country_select} on a given date. The true value may differ due to underreporting.
            '''
        )
        country_new_cases_smoothed_fig = graph_area_country(
            country_select,
            'new_cases_smoothed',
            '#6f6fe7',
            f'Daily New Cases: {country_select}',
        )
        st.plotly_chart(country_new_cases_smoothed_fig)

    if metric_select == 'Daily New Deaths':
        st.markdown(
            f'''
            Number of new COVID-19 deaths in {country_select} on a given date. The true value may differ due to underreporting.
            '''
        )
        country_new_deaths_smoothed_fig = graph_area_country(
            country_select,
            'new_deaths_smoothed',
            '#ec1342',
            f'Daily New Deaths: {country_select}',
        )
        st.plotly_chart(country_new_deaths_smoothed_fig)

    if metric_select == 'Daily New Recoveries':
        st.markdown(
            f'''
            Number of new COVID-19 recoveries in {country_select} on a given date. The true value may differ due to underreporting.
            '''
        )
        country_new_recovered_smoothed_fig = graph_area_country(
            country_select,
            'new_recovered_smoothed',
            '#11de57',
            f'Daily New Recoveries: {country_select}',
        )
        st.plotly_chart(country_new_recovered_smoothed_fig)

    if metric_select == 'Cases Breakdown: Recoveries, Deaths, and Active Cases':
        st.markdown(
            f'''
            Total case count of COVID-19 in {country_select}, split between current active 
            cases, recoveries, and deaths. The purpose is to investigate the proportions of 
            each metric in relation to each other.
            '''
        )
        country_case_stacked_fig = graph_stacked_country_case(country_select)
        st.plotly_chart(country_case_stacked_fig)

    if metric_select == 'People Vaccinated':
        st.markdown(
            f'''
            Total number of people who have received at least one dose of a registered vaccine. 
            The true value may differ due to underreporting.
            '''
        )
        country_people_vaccinated_fig = graph_area_country(
            country_select,
            'people_vaccinated',
            '#6ad2e5',
            f'People Vaccinated: {country_select}',
        )
        st.plotly_chart(country_people_vaccinated_fig)

    if metric_select == 'People Fully Vaccinated':
        st.markdown(
            f'''
            Total number of people who have received all doses prescribed by vaccination 
            protocol. The true value may differ due to underreporting.
            '''
        )
        country_people_fully_vaccinated_fig = graph_area_country(
            country_select,
            'people_fully_vaccinated',
            '#6ad2e5',
            f'People Fully Vaccinated: {country_select}',
        )
        st.plotly_chart(country_people_fully_vaccinated_fig)

    if metric_select == 'Total Vaccinations':
        st.markdown(
            f'''
            Total count of vaccination doses administered. The true value may differ due 
            to underreporting.
            '''
        )
        country_total_vaccinations_fig = graph_area_country(
            country_select,
            'total_vaccinations',
            '#6ad2e5',
            f'Total Vaccinations: {country_select}',
        )
        st.plotly_chart(country_total_vaccinations_fig)

    if metric_select == 'Total Boosters':
        st.markdown(
            f'''
            Total count of vaccination boosters administered (doses beyond what is prescribed 
            by vaccination protocol). The true value may differ due to underreporting.
            '''
        )
        country_total_boosters_fig = graph_area_country(
            country_select,
            'total_boosters',
            '#6ad2e5',
            f'Total Boosters: {country_select}',
        )
        st.plotly_chart(country_total_boosters_fig)

    if metric_select == 'Daily People Vaccinated':
        st.markdown(
            f'''
            Number of people receiving their first vaccination on a given date. 
            The true value may differ due to underreporting.
            '''
        )
        country_daily_people_vaccinated_fig = graph_area_country(
            country_select,
            'daily_people_vaccinated',
            '#6ad2e5',
            f'Daily People Vaccinated: {country_select}',
        )
        st.plotly_chart(country_daily_people_vaccinated_fig)

    if metric_select == 'Daily People Fully Vaccinated':
        st.markdown(
            f'''
            Number of people completing their vaccination protocol on a given date. The true value may differ due to underreporting.
            '''
        )
        country_daily_people_fully_vaccinated_fig = graph_area_country(
            country_select,
            'daily_people_fully_vaccinated',
            '#6ad2e5',
            f'Daily People Fully Vaccinated: {country_select}',
        )
        st.plotly_chart(country_daily_people_fully_vaccinated_fig)

    if metric_select == 'Daily Vaccinations':
        st.markdown(
            f'''
            Number of vaccination doses administered on that date (counts any dose). The true value may differ due to underreporting.
            '''
        )
        country_daily_vaccinations_fig = graph_area_country(
            country_select,
            'daily_vaccinations',
            '#6ad2e5',
            f'Daily Vaccinations: {country_select}',
        )
        st.plotly_chart(country_daily_vaccinations_fig)

    if metric_select == 'Daily Boosters':
        st.markdown(
            f'''
            Number of boosters administered on that date. The true value may differ due to underreporting.
            '''
        )
        country_daily_boosters_fig = graph_area_country(
            country_select,
            'daily_boosters',
            '#6ad2e5',
            f'Daily Boosters: {country_select}',
        )
        st.plotly_chart(country_daily_boosters_fig)

    if metric_select == 'Stringency Index':
        st.markdown(
            f'''
            An aggregate of nine measures that quantifies a country's level of strictness of government 
            policies to reduce the spread of COVID-19. These include lockdowns, travel restrictions, 
            school closures, etc. More info can be found [here](https://github.com/OxCGRT/covid-policy-dataset/blob/main/documentation_and_codebook.md).
            '''
        )
        country_stringency_fig = graph_country_stringency(country_select)
        st.plotly_chart(country_stringency_fig)

    st.markdown(
        'The plot below charts `new_cases_smoothed` alongside `stringency_value`.'
    )

    country_dual_fig = graph_country_dual(
        country_select,
        'new_cases_smoothed',
        'stringency_value',
        f'Comparing New Cases Smoothed and Stringency Index: {country_select}',
    )

    st.plotly_chart(country_dual_fig)

    # Top/Bottom 15 Countries by Metric Section
    st.header('Visualizing Global COVID-19 Trends')

    st.markdown(
        'This section focuses on examining the worldwide effects of and responses to COVID-19 by comparing countries.'
    )

    st.subheader('Top/Bottom 15 Countries by Metric')

    st.markdown(
        '''
        Below is a bar chart showcasing the top/bottom 15 countries by the selected metric. The date slider 
        allows you to examine shifts in the global landscape over time.
        '''
    )

    col1, col2 = st.columns([0.8, 0.2])

    with col1:
        column_select = st.selectbox(
            'Select a column',
            options=[
                'infection_rate',
                'cases',
                'deaths',
                'active',
                'people_vaccinated',
            ],
            format_func={
                'infection_rate': 'Infection Rate',
                'cases': 'Total Cases',
                'deaths': 'Total Deaths',
                'active': 'Active Cases',
                'people_vaccinated': 'People Vaccinated',
            }.__getitem__,
        )

    with col2:
        is_top_n_radio = st.radio(
            'Sort by:',
            options=[True, False],
            format_func={
                True: 'Top 15 Countries',
                False: 'Bottom 15 Countries',
            }.__getitem__,
        )

    min_date = df_country.dropna(subset=column_select)['date'].iloc[0]
    max_date = df_country.dropna(subset=column_select)['date'].iloc[-1]

    date_slider = st.slider(
        'Select a date',
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=datetime(2021, 2, 22),
    )

    country_top_n_fig = graph_bar_country(
        column_select, date_slider, is_top_n=is_top_n_radio
    )

    st.plotly_chart(country_top_n_fig)

    # Scatterplots Section
    scatterplot_list = [
        'HDI vs. Case Fatality Rate',
        'HDI vs. Infection Rate',
        'People Vaccinated Rate vs. Infection Rate',
        'Fully Vaccinated Rate vs. Infection Rate',
    ]

    st.subheader('Examining the Relationship Between Metrics')

    st.markdown(
        '''
        Below are a series of scatterplots showcasing the relationship between various metrics for each available country. 
        The purpose is to determine whether or not some variables, such as the HDI of a country, are highly correlated with 
        other variables, such as the infection rate of COVID-19.
        '''
    )

    scatterplot_select = st.selectbox('Select a scatterplot', options=scatterplot_list)

    if scatterplot_select == 'HDI vs. Case Fatality Rate':
        min_date_scatter = df_country.dropna(subset='hdi_value')['date'].iloc[0]
        max_date_scatter = df_country.dropna(subset='hdi_value')['date'].iloc[-1]
        date_slider_scatter = st.slider(
            'Select a date',
            min_value=min_date_scatter.to_pydatetime(),
            max_value=max_date_scatter.to_pydatetime(),
            value=datetime(2022, 3, 29),
        )
        hdi_case_fatality_scatter_fig = graph_scatter(
            'hdi_value',
            'case_fatality_rate',
            date_slider_scatter,
            log_x=False,
            log_y=True,
        )
        hdi_dist_fig = hdi_dist(date_slider_scatter)
        st.plotly_chart(hdi_case_fatality_scatter_fig)
        st.plotly_chart(hdi_dist_fig)
        st.markdown(
            '''
            #### Explanation: HDI vs. Case Fatality Rate
            The correlation between HDI and the case fatality rate of a country is shown to grow as the pandemic progresses further. 
            From the early stages of the pandemic through to the first two years, HDI has little correlation to the case fatality 
            rate of COVID-19. By mid-2022, however, countries with higher HDI scores generally experienced exponentially lower case 
            fatality rates than countries with lower HDIs. In other words, we can posit that by this time, highly developed countries 
            have established reliable countermeasures against the lethality of COVID-19 while less developed countries have not.
            '''
        )

    if scatterplot_select == 'HDI vs. Infection Rate':
        min_date_scatter = df_country.dropna(subset='hdi_value')['date'].iloc[0]
        max_date_scatter = df_country.dropna(subset='hdi_value')['date'].iloc[-1]
        date_slider_scatter = st.slider(
            'Select a date',
            min_value=min_date_scatter.to_pydatetime(),
            max_value=max_date_scatter.to_pydatetime(),
            value=datetime(2022, 5, 20),
        )
        hdi_case_fatality_scatter_fig = graph_scatter(
            'hdi_value', 'infection_rate', date_slider_scatter, log_x=False, log_y=True
        )
        hdi_dist_fig = hdi_dist(date_slider_scatter)
        st.plotly_chart(hdi_case_fatality_scatter_fig)
        st.plotly_chart(hdi_dist_fig)
        st.markdown(
            '''
            #### Explanation: HDI vs. Infection Rate
            As HDI increases linearly, we see a strong, positive, exponential growth in infection rate throughout all stages of the 
            pandemic. In fact, the correlation seems to grow stronger as the pandemic progresses, with an $R^2$ value of 0.79 by the 
            end of 2022. Essentially, this means that countries that are more developed generally experience exponentially higher infection 
            rates, and this statement becomes increasingly accurate the further along in the pandemic we are.
            '''
        )

    if scatterplot_select == 'People Vaccinated Rate vs. Infection Rate':
        min_date_scatter = df_country.dropna(subset='people_vaccinated_rate')[
            'date'
        ].iloc[0]
        max_date_scatter = df_country.dropna(subset='people_vaccinated_rate')[
            'date'
        ].iloc[-1]
        date_slider_scatter = st.slider(
            'Select a date',
            min_value=min_date_scatter.to_pydatetime(),
            max_value=max_date_scatter.to_pydatetime(),
            value=datetime(2021, 10, 20),
        )
        hdi_case_fatality_scatter_fig = graph_scatter(
            'people_vaccinated_rate',
            'infection_rate',
            date_slider_scatter,
            log_x=False,
            log_y=True,
        )
        st.plotly_chart(hdi_case_fatality_scatter_fig)
        st.markdown(
            '''
            #### Explanation: Vaccination Rates vs. Infection Rate
            Interestingly, the infection rate of COVID-19 in a country generally seems to grow exponentially as the vaccination rate 
            increases linearly. Essentially, as a country's vaccinated population increases, so does its infected population. We see 
            this phenomenon with fully vaccinated rates as well.

            There are a few possible explanations as to why this occurs. Countries with higher vaccination rates may experience less 
            underreporting of COVID-19, as they are generally the more developed countries with better detection for COVID-19 infections.
            Countries with higher vaccination rates by also have lower stringency standards, such as removing the need to quarantine, 
            resulting in greater exposure to COVID-19 for all individuals.
            '''
        )

    if scatterplot_select == 'Fully Vaccinated Rate vs. Infection Rate':
        min_date_scatter = df_country.dropna(subset='fully_vaccinated_rate')[
            'date'
        ].iloc[0]
        max_date_scatter = df_country.dropna(subset='fully_vaccinated_rate')[
            'date'
        ].iloc[-1]
        date_slider_scatter = st.slider(
            'Select a date',
            min_value=min_date_scatter.to_pydatetime(),
            max_value=max_date_scatter.to_pydatetime(),
            value=datetime(2022, 2, 22),
        )
        hdi_case_fatality_scatter_fig = graph_scatter(
            'fully_vaccinated_rate',
            'infection_rate',
            date_slider_scatter,
            log_x=False,
            log_y=True,
        )
        st.plotly_chart(hdi_case_fatality_scatter_fig)
        st.markdown(
            '''
            #### Explanation: Vaccination Rates vs. Infection Rate
            Interestingly, the infection rate of COVID-19 in a country generally seems to grow exponentially as the vaccination rate 
            increases linearly. Essentially, as a country's vaccinated population increases, so does its infected population. We see 
            this phenomenon with fully vaccinated rates as well.
            
            There are a few possible explanations as to why this occurs. Countries with higher vaccination rates may experience less 
            underreporting of COVID-19, as they are generally the more developed countries with better detection for COVID-19 infections.
            Countries with higher vaccination rates by also have lower stringency standards, such as removing the need to quarantine, 
            resulting in greater exposure to COVID-19 for all individuals.
            '''
        )


if __name__ == '__main__':
    main()
