import csv
import os
import requests
import argparse
import logging
import numpy as np
import pandas as pd
from datetime import timedelta, date
from calendar import monthrange
from collections import namedtuple, defaultdict

Period_Data = namedtuple("Period_Data", ["cases", "deaths"])


class StateCovid:
    def __init__(self, state: str):
        self.state = str(state)
        self.population = 0
        self.data = dict()

    def __repr__(self) -> str:
        """
        Returns a string representaion of an instantiation of StateCovid
        """
        return (f"StateCovid('{self.state}','{self.population}'," +
                f"{self.data})")

    def __str__(self) -> str:
        return (f"State: {self.state}, Population: {self.population}, " +
                f"Data: {self.data}")

    def __iter__(self):
        """
        Returns an iterable of this class.
        """
        yield self.state
        yield self.population
        yield self.data.items()

    def add_cases(self, period: int, number_of_cases: int):
        if period not in self.data.keys():
            self.data[period] = Period_Data(number_of_cases, 0)
            return None

        p_data = self.data[period].cases
        period_data = Period_Data(p_data + number_of_cases,
                                  self.data[period].deaths)
        self.data[period] = period_data
        return None

    def add_deaths(self, period: int, number_of_deaths: int):
        if period not in self.data.keys():
            self.data[period] = Period_Data(0, number_of_deaths)
            return None

        p_data = self.data[period].deaths

        period_data = Period_Data(self.data[period].cases,
                                  p_data + number_of_deaths)

        self.data[period] = period_data
        return None

    def get_cases_for_month(self, month: int):
        month_data = dict(filter(lambda k: k[0] == month,
                          self.data.items()))

        return month_data[month].cases

    def set_population(self, population):
        self.population = population

    def get_population(self):
        return self.population

    def get_case_data(self):
        return self.data.items()


class StateCovidData:
    def __init__(self, data_file_name: str):
        self.data = defaultdict()

        self._load_data(data_file_name)

    # from stackoverflow
    def _daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def _parse_cases_data(self, file_name):
        pass

    def _format_date_key(self, month: int):
        return str(month) + "/" + str(monthrange(2020, month)[1]) + \
                "/" + str(20)

    def _load_data(self, data_file_name: str):
        logging.debug(f"Loading data from {data_file_name}.")
        if not os.path.exists(data_file_name):
            logging.debug(f"{data_file_name} not found. Need to create it.")
            self._create_data_files(data_file_name)
            return None

        logging.debug("Loading data from file.")
        self._get_data_from_file(data_file_name)
        self._write_object_data_to_file("from_object.csv")

    def _create_data_files(self, data_file_name: str):
        logging.debug("Getting population data")
        population = self._get_populations("population.csv")

        caser_url = "https://usafactsstatic.blob.core.windows.net/" + \
                    "public/data/covid-19/covid_confirmed_usafacts.csv"
        self._get_covid_data("cases.csv", caser_url, True)

        deaths_url = "https://usafactsstatic.blob.core.windows.net/" + \
                     "public/data/covid-19/covid_deaths_usafacts.csv"
        self._get_covid_data("deaths.csv", deaths_url, False)

        for state in self.data.items():
            self.data[state].set_population(population[state])

        self._write_object_data_to_file(data_file_name)

    def _write_object_data_to_file(self, file_name):
        with open(file_name, "w") as data_file:
            csv_columns = ["State", "Population", "Period", "Cases", "Deaths"]
            writer = csv.DictWriter(data_file, fieldnames=csv_columns)

            for state, sdata in self.data.items():
                st = state
                pop = sdata.get_population()
                case_data = sdata.get_case_data()
                for k in case_data:
                    period = k[0]
                    cases = k[1].cases
                    deaths = k[1].deaths

                    row_data = {"State": st, "Population": pop,
                                "Period": period, "Cases": cases,
                                "Deaths": deaths}
                    writer.writerow(row_data)

    def _get_data_from_file(self, file_name):
        with open(file_name, "r") as data_file:
            csv_columns = ["State", "Population", "Period", "Cases", "Deaths"]
            reader = csv.DictReader(data_file, fieldnames=csv_columns)

            for r in reader:
                if r["State"] not in self.data:
                    self.data[r["State"]] = StateCovid(r["State"])
                    self.data[r["State"]].set_population(int(r["Population"]))

                self.data[r["State"]].add_cases(r["Period"], int(r["Cases"]))
                self.data[r["State"]].add_deaths(r["Period"], int(r["Deaths"]))

    def _create_state_covid_object(state, population, cases, deaths):
        state_object = StateCovid(state)

        state_object.add_cases(period, cases)
        state_object.add_deaths(period, deaths)

    def _get_covid_data(self, file_name, url, is_cases: bool):
        if not os.path.exists(file_name):
            self._get_web_data(url, file_name)

        start_month = 3
        end_month = 7

        logging.debug("Read data.")
        with open(file_name, "r") as data_file:
            reader = csv.DictReader(data_file)
            for row in reader:
                if row["\ufeffcountyFIPS"] != 0:
                    # the data is cumulative by column, so I will subtract the
                    # last period from the current to get the amount.
                    date_key = self._format_date_key(start_month-1)
                    previous_value = int(row[date_key])

                    for month in range(start_month, end_month+1):

                        date_key = self._format_date_key(month)
                        if row["State"] not in self.data.keys():
                            self.data[row["State"]] = StateCovid(row["State"])

                        state_data = self.data[row["State"]]
                        month_total = int(row[date_key]) - previous_value
                        if is_cases:
                            state_data.add_cases(month, month_total)
                        else:
                            state_data.add_deaths(month, month_total)

                        self.data[row["State"]] = state_data
                        previous_value = int(row[date_key])

    def _get_populations(self, pop_file_name):
        if not os.path.exists(pop_file_name):
            pop_url = "https://usafactsstatic.blob.core.windows.net/" + \
                      "public/data/covid-19/" + \
                      "covid_county_population_usafacts.csv"
            self._get_web_data(pop_url, pop_file_name)

        state_totals = dict()

        with open(pop_file_name, "r") as data_file:
            reader = csv.DictReader(data_file)

            for p in reader:
                if p["State"] in state_totals.keys():
                    state_totals[p["State"]] += int(p["population"])
                    continue

                state_totals[p["State"]] = int(p["population"])

        return state_totals

    def _get_web_data(self, data_url, file_name: str):
        logging.debug("Getting data from remote.")
        file_address = data_url

        response = requests.get(file_address)

        if not response:
            logging.debug("Using alternate data source.")
            response = requests.get(alternate_file_address)

        if response:
            logging.debug(f"Writing data to {file_name}.")
            with open(file_name, 'w') as data:
                data.write(response.text)
        else:
            logging.critical(f("We have a problem: {response.status_code}"))
            sys.exit()

    def _get_file_data(self, data_file_name: str):
        """
        If the files exists, it is opened and the data is loaded into a
        str object and is returned with the data.
        """
        if not os.path.exists(data_file_name):
            raise FileNotFoundError

        with open(data_file_name, "r") as original_file:
            file_stuff = original_file.read()

        return file_stuff


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s" +
                                  " - %(message)s")

    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    fh = logging.FileHandler("covid_log.log", mode="w")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return None


def main():
    setup_logging()

    file_name = "covid_data.csv"

    logging.debug("Create Data class.")
    covid_data = StateCovidData(file_name)


if __name__ == '__main__':
    main()
