-- ZestRoute main analytics
-- Matches the Snowflake worksheet views used for Power BI reporting.

USE WAREHOUSE ZESTROUTE_WH;
USE DATABASE ZESTROUTE_DB;
USE SCHEMA DELIVERY_ANALYTICS;

-- Overall KPI snapshot
CREATE OR REPLACE VIEW delivery_kpis_view AS
SELECT
  COUNT(*) AS total_orders,
  ROUND(AVG(TIME_TAKEN_MIN), 2) AS avg_delivery_time,
  ROUND(AVG(DELIVERY_PERSON_RATINGS), 2) AS avg_rating,
  ROUND(AVG(PICKUP_LAG_MIN), 2) AS avg_pickup_lag_min,
  SUM(IFF(DELIVERY_PERFORMANCE = 'Fast', 1, 0)) AS fast_deliveries,
  SUM(IFF(DELIVERY_PERFORMANCE = 'Delayed', 1, 0)) AS delayed_deliveries
FROM ORDERS;

-- Delivery agent performance (used by Power BI agent charts)
CREATE OR REPLACE VIEW delivery_agent_view AS
SELECT
  DELIVERY_PERSON_ID,
  ROUND(AVG(DELIVERY_PERSON_RATINGS), 2) AS avg_rating,
  ROUND(AVG(TIME_TAKEN_MIN), 2) AS avg_delivery_time,
  COUNT(*) AS total_deliveries
FROM ORDERS
WHERE DELIVERY_PERSON_ID IS NOT NULL
GROUP BY DELIVERY_PERSON_ID
ORDER BY avg_rating DESC, total_deliveries DESC;

-- Alias view name seen in Snowsight worksheet screenshots
CREATE OR REPLACE VIEW delivery_performance_view AS
SELECT *
FROM delivery_agent_view;

-- Festival impact on delivery times and ratings
CREATE OR REPLACE VIEW festival_impact_view AS
SELECT
  FESTIVAL,
  COUNT(*) AS total_orders,
  ROUND(AVG(TIME_TAKEN_MIN), 2) AS avg_delivery_time,
  ROUND(AVG(DELIVERY_PERSON_RATINGS), 2) AS avg_rating,
  ROUND(
    100.0 * SUM(IFF(DELIVERY_PERFORMANCE = 'Delayed', 1, 0)) / NULLIF(COUNT(*), 0),
    2
  ) AS delayed_pct
FROM ORDERS
GROUP BY FESTIVAL
ORDER BY total_orders DESC;

-- Traffic density impact
CREATE OR REPLACE VIEW traffic_impact_view AS
SELECT
  ROAD_TRAFFIC_DENSITY,
  COUNT(*) AS total_orders,
  ROUND(AVG(TIME_TAKEN_MIN), 2) AS avg_delivery_time,
  ROUND(AVG(DELIVERY_PERSON_RATINGS), 2) AS avg_rating
FROM ORDERS
GROUP BY ROAD_TRAFFIC_DENSITY
ORDER BY avg_delivery_time DESC;

-- Weather impact
CREATE OR REPLACE VIEW weather_impact_view AS
SELECT
  WEATHERCONDITIONS,
  COUNT(*) AS total_orders,
  ROUND(AVG(TIME_TAKEN_MIN), 2) AS avg_delivery_time,
  ROUND(AVG(DELIVERY_PERSON_RATINGS), 2) AS avg_rating
FROM ORDERS
GROUP BY WEATHERCONDITIONS
ORDER BY avg_delivery_time DESC;

-- City-level delivery summary
CREATE OR REPLACE VIEW city_performance_view AS
SELECT
  CITY,
  COUNT(*) AS total_orders,
  ROUND(AVG(TIME_TAKEN_MIN), 2) AS avg_delivery_time,
  ROUND(AVG(DELIVERY_PERSON_RATINGS), 2) AS avg_rating,
  ROUND(
    100.0 * SUM(IFF(DELIVERY_PERFORMANCE = 'Fast', 1, 0)) / NULLIF(COUNT(*), 0),
    2
  ) AS fast_pct
FROM ORDERS
GROUP BY CITY
ORDER BY total_orders DESC;

-- Weekend vs weekday comparison
CREATE OR REPLACE VIEW weekend_impact_view AS
SELECT
  IS_WEEKEND,
  COUNT(*) AS total_orders,
  ROUND(AVG(TIME_TAKEN_MIN), 2) AS avg_delivery_time,
  ROUND(AVG(DELIVERY_PERSON_RATINGS), 2) AS avg_rating
FROM ORDERS
GROUP BY IS_WEEKEND
ORDER BY IS_WEEKEND;

-- Preview queries used in the Snowsight worksheet
SELECT * FROM delivery_performance_view LIMIT 10;
SELECT * FROM festival_impact_view LIMIT 10;
SELECT * FROM delivery_agent_view LIMIT 10;

SELECT * FROM delivery_kpis_view;
SELECT * FROM traffic_impact_view;
SELECT * FROM weather_impact_view;
SELECT * FROM city_performance_view;
SELECT * FROM weekend_impact_view;
