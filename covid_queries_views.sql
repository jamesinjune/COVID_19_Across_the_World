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
	TOP 200 *
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
		cc.cases,
		cc.[year],
		cd.deaths,
		cr.recovered,
		CASE
			WHEN cr.recovered IS NULL THEN NULL
			WHEN (cc.cases - cd.deaths - cr.recovered) < 0 THEN NULL
			ELSE (cc.cases - cd.deaths - cr.recovered)
		END AS active
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
	ac.country,
	date,
	cases,
	deaths,
	recovered,
	active,
	(active / pop.population) * 100000 AS active_case_rate
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
	cc.cases,
	cd.deaths,
	(cd.deaths / NULLIF(cc.cases, 0)) * 100000 AS case_fatality_rate
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
	cc.date,
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
	cc.cases,
	cc.new_cases_smoothed,
	cc.new_cases_growth_rate,
	cv.people_vaccinated,
	cv.people_fully_vaccinated,
	cv.daily_people_vaccinated,
	cv.daily_people_fully_vaccinated,
	pop.population,
	(cc.cases / pop.population) * 100000 AS infection_rate,
	(cv.people_vaccinated / pop.population) * 100000 AS people_vaccinated_rate ,
	(cv.people_fully_vaccinated / pop.population) * 100000 AS fully_vaccinated_rate ,
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
		SUM(cc.cases) AS global_case_count,
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
		SUM(cc.cases) AS cases,
		SUM(cd.deaths) AS deaths,
		CASE
			WHEN COUNT(cr.recovered) < COUNT(cr.country) THEN NULL
			ELSE SUM(cr.recovered)
		END AS recovered,
		SUM(cc.new_cases_smoothed) AS new_cases,
		SUM(cd.new_deaths_smoothed) AS new_deaths,
		CASE
			WHEN COUNT(cr.new_recovered_smoothed) < COUNT(cr.country) THEN NULL
			ELSE SUM(cr.new_recovered_smoothed)
		END AS new_recovered
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
	cases,
	deaths,
	recovered,
	new_cases,
	new_deaths,
	new_recovered,
	CASE
		WHEN recovered IS NULL THEN NULL
		ELSE (cases - deaths - recovered)  
	END AS active,
	(deaths / cases) * 100000 AS case_fatality_rate
FROM
	global_data
;


-- COVID daily data on the country-level
CREATE VIEW covid_daily_country AS
WITH active_cases AS (
	SELECT
		cc.country,
		cc.date,
		CASE
			WHEN cr.recovered IS NULL THEN NULL
			WHEN (cc.cases - cd.deaths - cr.recovered) < 0 THEN NULL
			ELSE (cc.cases - cd.deaths - cr.recovered)
		END AS active
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
	cc.cases,
	cc.new_cases_smoothed,
	cc.new_cases_growth_rate,
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
	(cc.cases / pop.population) * 100000 AS infection_rate,
	(cv.people_vaccinated / pop.population) * 100000 AS people_vaccinated_rate,
	(cv.people_fully_vaccinated / pop.population) * 100000 AS fully_vaccinated_rate,
	(cc.new_cases_smoothed / pop.population) * 100000 AS case_incidence_rate,
	(cd.deaths / NULLIF(cc.cases, 0)) * 100000 AS case_fatality_rate,
	(ac.active / pop.population) * 100000 AS active_case_rate
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