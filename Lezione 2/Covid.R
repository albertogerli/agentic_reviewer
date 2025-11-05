library(readr); library(dplyr); library(lubridate)

url <- "https://covid.ourworldindata.org/data/owid-covid-data.csv"
df  <- read_csv(url, col_types = cols(date = col_date()))

countries <- c("Italy","Germany","France","Spain",
               "United Kingdom","Poland")

weekly <- df %>%
  filter(location %in% countries) %>%
  select(location, date, new_cases, new_deaths) %>%
  mutate(week = floor_date(date, unit = "week", week_start = 1)) %>%
  group_by(location, week) %>%
  summarise(cases_weekly  = sum(new_cases,  na.rm = TRUE),
            deaths_weekly = sum(new_deaths, na.rm = TRUE),
            .groups = "drop") %>%
  rename(region = location)

write_csv(weekly, "covid_epi_weekly.csv")
glimpse(weekly)
