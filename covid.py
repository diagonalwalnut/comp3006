import csv
import os
import requests
import argparse
import logging
import calendar
import numpy as np
import pandas as pd
from datetime import timedelta, date
from calendar import monthrange
from collections import namedtuple, defaultdict


class StateCovid:
    def __init__(self, state: str):
        self.state = str(state)
        self.median_age = 0
        self.population = 0
        self.data = dict()

    def __repr__(self) -> str:
        """
        Returns a string representaion of an instantiation of StateCovid
        """
        return (f"StateCovid('{self.state}','{self.population}'," +
                f"{self.median_age},{self.data})")

    def __str__(self) -> str:
        return (f"State: {self.state}, Population: {self.population}, " +
                f"Median Age: {self.median_age}, Data: {self.data}")

    def __iter__(self):
        """
        Returns an iterable of this class.
        """
        yield self.state
        yield self.population
        yield self.median_age
        yield self.data.items()

    def add_deaths(self, period: int, number_of_deaths: int):
        if period not in self.data.keys():
            self.data[period] = number_of_deaths
            return None

        p_data = self.data[period]

        period_data = p_data + number_of_deaths

        self.data[period] = period_data
        return None

    def set_population(self, population):
        self.population = population

    def get_population(self):
        return self.population

    def set_median_age(self, median_age):
        self.median_age = median_age

    def get_median_age(self):
        return self.median_age

    def get_death_data(self):
        return self.data.items()

    def max_death_rate_by_month(self):
        max_val = -99999999
        for key, dat in self.data.items():
            if dat > max_val:
                max_val = dat

        return dat


class StateCovidData:
    def __init__(self, data_file_name: str):
        self.data = dict()

        self._load_data(data_file_name)

    # from stackoverflow
    def _daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

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
        median_age = self._get_median_age("state_median_age.csv")

        deaths_url = "https://usafactsstatic.blob.core.windows.net/" + \
                     "public/data/covid-19/covid_deaths_usafacts.csv"
        self._get_covid_data("deaths.csv", deaths_url)

        for state, data in self.data.items():
            self.data[state].set_population(population[state])
            self.data[state].set_median_age(median_age[state])

        self._write_object_data_to_file(data_file_name)

    def _write_object_data_to_file(self, file_name):
        with open(file_name, "w") as data_file:
            csv_columns = ["State", "Population", "Median Age", "Period", "Deaths"]
            writer = csv.DictWriter(data_file, fieldnames=csv_columns)

            for state, sdata in self.data.items():
                st = state
                pop = sdata.get_population()
                median_age = sdata.get_median_age()
                death_data = sdata.get_death_data()
                for key, value in death_data:
                    period = key
                    deaths = value

                    row_data = {"State": st, "Population": pop,
                                "Median Age": median_age,
                                "Period": period, "Deaths": deaths}
                    writer.writerow(row_data)

    def _get_data_from_file(self, file_name):
        with open(file_name, "r") as data_file:
            csv_columns = ["State", "Population", "Median Age", "Period", "Deaths"]
            reader = csv.DictReader(data_file, fieldnames=csv_columns)

            for r in reader:
                if r["State"] not in self.data:
                    self.data[r["State"]] = StateCovid(r["State"])
                    self.data[r["State"]].set_population(int(r["Population"]))
                    self.data[r["State"]].set_median_age(float(r["Median Age"]))

                self.data[r["State"]].add_deaths(r["Period"], int(r["Deaths"]))

    def _get_covid_data(self, file_name, url):
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
    
    def _get_median_age(self, age_file_name):
        if not os.path.exists(age_file_name):
            raise FileNotFoundError

        state_median = defaultdict()

        with open(age_file_name, "r") as data_file:
            reader = csv.DictReader(data_file)

            for p in reader:
                state_median[p['\ufeffState']] = p["Median"]

        return state_median

    def _get_web_data(self, data_url, file_name: str):
        logging.debug("Getting data from remote.")
        file_address = data_url

        response = requests.get(file_address)

        if not response:
            logging.critical("Data source not responding")
            raise FileNotFoundError

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
    
    def get_max_death_rate(self):
        rates = []
        for key, obj in self.data.items():
            rates.append((key, obj.population, obj.median_age, obj.max_death_rate_by_month()))
        return rates
    
    def sort_by_state(self):
        sorted(self.data.items(), key=lambda d: (d.state, d.population))

    def sort_by_population(self):
        sorted(self.data.values(), key=lambda d: (d.population, d.state))
    
    def sort_by_median_age(self):
        sorted(self.data.items(), key=lambda d: (d.median_age, d.state))

    def get_state_data(self, state: str):
        return self.data[state]


def write_to_file(covid_data_df, outfile):
    headers = covid_data_df.columns.values
    if outfile is None:
        import sys
        writer = csv.writer(sys.stdout)
        writer.writerow(headers)
        for index, row in covid_data_df.iterrows():
            writer.writerow(row)
    else:
        logging.debug(f"Writing data to {outfile}.")
        with open(outfile, "w") as outfile:
            writer = csv.writer(outfile)
            writer.writerow(headers)
            for index, row in covid_data_df.iterrows():
                writer.writerow(row)


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s" +
                                  " - %(message)s")

    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    fh = logging.FileHandler("covid.log", mode="w")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return None


def print_data(covid_data, sort_order, outfile):
    logging.debug(f"Sorting data by {sort_order}.")
    if sort_order == "state":
        covid_data.sort_by_state()
    elif sort_order == "age":
        covid_data.sort_by_median_age()
    else:
        covid_data.sort_by_population()

    write_to_file(covid_data, outfile)


def covid_deaths(covid_data, sort_order, plot, outfile):
    death_rates = covid_data.get_max_death_rate()

    df = pd.DataFrame(death_rates, columns=["state", "population", "median_age", "death_rate"])
    df = df.sort_values(by=sort_order)
    write_to_file(df, outfile)

    if plot:
        plot_data(df["state"], df["death_rate"])


def state_data(covid_data, state, outfile):
    state_data = covid_data.get_state_data(state)

    headers = f"{state_data.state}, population: {state_data.population}, median age: {state_data.median_age}\n"

    if outfile is None:
        print(headers)
        for key, value in state_data.data.items():
            print(f"Deaths in {calendar.month_abbr[int(key)]}: {value}")
    else:
        with open(outfile, "w") as output:
            output.write(headers)
            for key, value in state_data.data.items():
                output.write(f"Deaths in {calendar.month_abbr[int(key)]}: {value}\n")


def plot_data(x: list, y: list):
    logging.debug(f"Plotting data.")
    import matplotlib.pyplot as plt
    plt.scatter(x, y)
    plt.xticks(rotation=80)
    plt.show()


def main():
    setup_logging()

    file_name = "covid_data.csv"

    logging.debug("Create Data class.")

    parser = argparse.ArgumentParser(
        description="Parse command line arguments")

    parser.add_argument("command", metavar="<command>",
                        type=str,
                        choices=["print", "deaths", "state"],
                        help="Command to print")

    parser.add_argument("-l", "--location", dest="state",
                        type=str, help="")

    parser.add_argument("-s", "--sort", dest="sort_order",
                        type=str,
                        choices=["population", "median_age"],
                        default="population",
                        help="")

    parser.add_argument("-f", "--file_name", dest="file_name",
                        type=str,
                        help="File name for data file",
                        default="covid.data.txt")

    parser.add_argument("-o", "--ofile", dest="outfile",
                        type=str, default=None,
                        help="The file to which output should be written")

    parser.add_argument("-p", "--plot", dest="plot",
                        action="store_true", default=False,
                        help="Display a matplotlib plot")

    args = parser.parse_args()

    command_param = args.command
    sort_order = args.sort_order
    file_name = args.file_name
    plot = args.plot
    outfile = args.outfile
    state = args.state

    logging.debug(f"Arg command_param = {command_param}")
    logging.debug(f"Arg sort_order = {sort_order}")
    logging.debug(f"Arg file_name = {file_name}")
    logging.debug(f"Arg plot = {plot}")
    logging.debug(f"Arg outfile = {outfile}")
    logging.debug(f"Arg state = {state}")

    covid_data = StateCovidData(file_name)    

    if command_param == "print":
        if sort_order == "population":
            covid_data.sort_by_population()
        else:
            covid_data.sort_by_median_age()
        print_data(covid_data, sort_order, outfile)
        return None

    if command_param == "deaths":
        covid_deaths(covid_data, sort_order, plot, outfile)
        return None
    
    if command_param == "state":
        state_data(covid_data, state, outfile)
        return None

if __name__ == '__main__':
    main()
