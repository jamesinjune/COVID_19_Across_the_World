/* COVID Data Exploration */

-- File Name: covid_queries_views.sql
-- File Description: Queries and views for analyzing COVID data
-- Author: James Li
-- Dependencies: 



/* 1. Double-check imported datasets */

SELECT
	TOP 200 *
FROM
	covid_cases
;

SELECT
	TOP 200*
FROM
	covid_deaths
;

SELECT
	TOP 200 *
FROM
	covid_recovered
;

SELECT
	TOP 200 *
FROM
	covid_vaccinations
;

SELECT
	TOP 200 *
FROM
	human_development_index
;

SELECT
	TOP 200 *
FROM
	population
;

SELECT
	TOP 200 *
FROM
	stringency_index
;




/* 2. Querying Data */

-- Calculate number of active cases and active case to population ratio
WITH active_cases AS (
	SELECT 
		cc.country,
		cc.date,
		cc.confirmed_cases,
		cc.[year],
		cd.deaths,
		cr.recovered,
		(cc.confirmed_cases - cd.deaths - cr.recovered) AS active
	FROM 
		covid_cases AS cc
	INNER JOIN 
		covid_deaths AS cd
		ON cc.country = cd.country
		AND cc.date = cd.date
	INNER JOIN 
		covid_recovered AS cr
		ON cc.country = cr.country
		AND cc.date = cr.date
)
SELECT
	ac.country,
	date,
	confirmed_cases,
	deaths,
	recovered,
	active,
	(active / pop.population) * 100000 AS active_case_ratio
FROM
	active_cases ac
INNER JOIN
	population AS pop
	ON ac.country = pop.country
	AND ac.[year] = pop.[year]
;


-- Case Fatality Rate (per 100,000): The ratio of deaths by COVID to the number of COVID cases of a country
SELECT
	cc.country,
	cc.date,
	cc.confirmed_cases,
	cd.deaths,
	(cd.deaths / NULLIF(cc.confirmed_cases, 0)) * 100000 AS case_fatality_rate
FROM
	covid_cases AS cc
INNER JOIN
	covid_deaths AS cd
	ON cc.country = cd.country
	AND cc.date = cd.date
;


-- Case Incidence Rate (per 100,000): The ratio of new cases to the total population of a country
SELECT
	cc.country,
	cc.[year],
	cc.new_cases_smoothed,
	pop.population,
	(cc.new_cases_smoothed / pop.population) * 100000 AS case_incidence_rate
FROM
	covid_cases AS cc
INNER JOIN
	population AS pop
	ON cc.country = pop.country
	AND cc.[year] = pop.[year]
;


-- Examining cases vs. vaccinations, stringency index, and hdi
SELECT
	cc.country,
	cc.date,
	cc.confirmed_cases,
	cc.new_cases_smoothed,
	cv.people_vaccinated,
	cv.people_fully_vaccinated,
	cv.daily_people_vaccinated,
	cv.daily_people_fully_vaccinated,
	pop.population,
	(cc.confirmed_cases / pop.population) * 100000 AS infected_population_ratio,
	(cv.people_vaccinated / pop.population) * 100000 AS vaccinated_population_ratio ,
	(cv.people_fully_vaccinated / pop.population) * 100000 AS fully_vaccinated_population_ratio ,
	(cc.new_cases_smoothed / pop.population) * 100000 AS case_incidence_rate,
	si.stringency_value,
	hdi.hdi_value
FROM
	covid_cases AS cc
INNER JOIN
	population AS pop
	ON cc.country = pop.country
	AND cc.[year] = pop.[year]
LEFT JOIN
	covid_vaccinations AS cv
	ON cc.country = cv.country
	AND cc.date = cv.date
LEFT JOIN
	stringency_index AS si
	ON cc.country = si.country
	AND cc.date = si.date
LEFT JOIN
	human_development_index AS hdi
	ON cc.country = hdi.country
	AND cc.year = hdi.year
;


-- Global Case Fatality Rate (per 100,000): Estimated by summing all countries' data
WITH global_data AS (
	SELECT
		cc.date,
		SUM(cc.confirmed_cases) AS global_case_count,
		SUM(cd.deaths) AS global_death_count,
		SUM(cr.recovered) AS global_recovery_count
	FROM
		covid_cases AS cc
	LEFT JOIN
		covid_deaths AS cd
		ON cc.country = cd.country
		AND cc.date = cd.date
	LEFT JOIN
		covid_recovered AS cr
		ON cc.country = cr.country
		AND cc.date = cr.date
	GROUP BY
		cc.date
)
SELECT
	date,
	global_case_count,
	global_death_count,
	global_recovery_count,
	(global_death_count / global_case_count) * 100000 AS global_case_fatality
FROM
	global_data
ORDER BY
	date
;


-- Stringency index vs. new cases (smoothed)
SELECT
	cc.country,
	cc.date,
	cc.new_cases_smoothed,
	si.stringency_value
FROM
	covid_cases AS cc
INNER JOIN
	stringency_index AS si
	ON cc.country = si.country
	AND cc.date = si.date
;





/* 3. Creating Views */

-- Global daily COVID cases, deaths, recoveries, and active counts
CREATE VIEW covid_daily_global AS
WITH global_data AS (
	SELECT
		cc.date,
		SUM(cc.confirmed_cases) AS global_case_count,
		SUM(cd.deaths) AS global_death_count,
		SUM(cr.recovered) AS global_recovery_count,
		SUM(cc.new_cases_smoothed) AS global_new_cases,
		SUM(cd.new_deaths_smoothed) AS global_new_deaths,
		SUM(cr.new_recovered_smoothed) AS global_new_recovered
	FROM
		covid_cases AS cc
	LEFT JOIN
		covid_deaths AS cd
		ON cc.country = cd.country
		AND cc.date = cd.date
	LEFT JOIN
		covid_recovered AS cr
		ON cc.country = cr.country
		AND cc.date = cr.date
	GROUP BY
		cc.date
)
SELECT
	date,
	global_case_count,
	global_death_count,
	global_recovery_count,
	global_new_cases,
	global_new_deaths,
	global_new_recovered,
	(global_case_count - global_death_count - global_recovery_count)  AS global_active,
	(global_death_count / global_case_count) * 100000 AS global_case_fatality
FROM
	global_data
;


-- COVID daily data on the country-level
CREATE VIEW covid_daily_country AS
WITH active_cases AS (
	SELECT
		cc.country,
		cc.date,
		(cc.confirmed_cases - cd.deaths - cr.recovered) AS active
	FROM
		covid_cases AS cc
	LEFT JOIN
		covid_deaths AS cd
		ON cc.country = cd.country
		AND cc.date = cd.date
	LEFT JOIN
		covid_recovered AS cr
		ON cc.country = cr.country
		AND cc.date = cr.date
)
SELECT
	cc.country,
	cc.date,
	cc.confirmed_cases,
	cc.new_cases_smoothed,
	cd.deaths,
	cd.new_deaths_smoothed,
	cr.recovered,
	cr.new_recovered_smoothed,
	cv.people_vaccinated,
	cv.people_fully_vaccinated,
	cv.total_vaccinations,
	cv.total_boosters,
	cv.daily_people_vaccinated,
	cv.daily_people_fully_vaccinated,
	cv.daily_vaccinations,
	cv.daily_boosters,
	pop.population,
	si.stringency_value,
	hdi.hdi_value,
	ac.active,
	(cc.confirmed_cases / pop.population) * 100000 AS infection_rate,
	(cv.people_vaccinated / pop.population) * 100000 AS people_vaccinated_ratio,
	(cv.people_fully_vaccinated / pop.population) * 100000 AS fully_vaccinated_ratio,
	(cc.new_cases_smoothed / pop.population) * 100000 AS case_incidence_rate,
	(cd.deaths / NULLIF(cc.confirmed_cases, 0)) * 100000 AS case_fatality_rate,
	(ac.active / pop.population) * 100000 AS active_case_ratio
FROM
	covid_cases AS cc
INNER JOIN
	population AS pop
	ON cc.country = pop.country
	AND cc.[year] = pop.[year]
LEFT JOIN
	covid_deaths AS cd
	ON cc.country = cd.country
	AND cc.date = cd.date
LEFT JOIN
	covid_recovered AS cr
	ON cc.country = cr.country
	AND cc.date = cr.date
LEFT JOIN
	covid_vaccinations AS cv
	ON cc.country = cv.country
	AND cc.date = cv.date
LEFT JOIN
	stringency_index AS si
	ON cc.country = si.country
	AND cc.date = si.date
LEFT JOIN
	human_development_index AS hdi
	ON cc.country = hdi.country
	AND cc.[year] = hdi.[year]
LEFT JOIN
	active_cases AS ac
	ON cc.country = ac.country
	AND cc.date = ac.date
;
