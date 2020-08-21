import csv
import os
import sys
import requests
import argparse
import logging
import calendar
import codecs
import numpy as np
import pandas as pd
from datetime import timedelta, date
from collections import namedtuple, defaultdict


class StateCovid:
    def __init__(self, state: str, population: int= 0,
                 median_age: float = 0):
        self.state = str(state)
        self.population = population
        self.median_age = median_age
        self.state_data = dict()
    
    def __repr__(self) -> str:
        """
        Returns a string representaion of an instantiation of StateCovid
        """
        return (f"StateCovid('{self.state}','{self.population}'," +
                f"{self.median_age},{self.state_data})")

    def __str__(self) -> str:
        return (f"State: {self.state}, Population: {self.population}, " +
                f"Median Age: {self.median_age}, State Data: {self.state_data}")

    def __iter__(self):
        """
        Returns an iterable of this class.
        """
        yield self.state
        yield self.population
        yield self.median_age
        for key, val in self.state_data.items():
            yield (key, val)

    def add_deaths(self, period: int, number_of_deaths: int):
        # logging.debug(f"{self.state} - {period}: {number_of_deaths}")
        if int(period) not in self.state_data.keys():
            self.state_data[int(period)] = number_of_deaths
            return None

        p_data = self.state_data[int(period)]

        period_data = p_data + number_of_deaths

        self.state_data[period] = period_data
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
        return self.state_data.items()

    def get_death_data_for_period(self, period):
        return self.state_data[period]
    
    def get_total_deaths(self):
        np_array = np.array(list(self.state_data.values()))
        
        return sum(np_array)

    def max_deaths(self):
        np_array = np.array(list(self.state_data.values()))

        return max(np_array)

class StateCovidData:
    def __init__(self, data_file_name: str = "covid.data.txt", test_flag: bool = False):
        self.data = defaultdict()

        if not test_flag:
            self._load_data(data_file_name)

    def __repr__(self) -> str:
        """
        Returns a string representaion of an instantiation of StateCovid
        """
        rtn_str = ""
        for key, value in self.data.items():
            rtn_str = rtn_str + repr(value) + "\n"

        return rtn_str

    def __str__(self) -> str:
        rtn_str = ""
        for key, value in self.data.items():
            rtn_str = rtn_str + str(value) + "\n"

        return rtn_str

    def add_state_data(self, state_data: StateCovid):
        self.data[state_data.state] = state_data

    # from stackoverflow
    def _daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def _format_date_key(self, month: int):
        return str(month) + "/" + str(calendar.monthrange(2020, month)[1]) + \
                "/" + str(20)

    def _load_data(self, data_file_name: str):
        logging.debug(f"_load_data(): Loading data from {data_file_name}.")
        if not os.path.exists(data_file_name):
            logging.debug(f"{data_file_name} not found. Need to create it.")
            self._create_data_files(data_file_name)
            return None

        logging.debug(f"_load_data(): Loading data from {data_file_name}.")
        self._get_data_from_file(data_file_name)
        self._write_object_data_to_file("from_object.csv")

    def _create_data_files(self, data_file_name: str):
        logging.debug("_create_data_files(): Getting population data")
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
        with open(file_name, "w", newline="", encoding="utf-8") as data_file:
            csv_columns = ["State", "Population", "Median Age", "Period", "Deaths"]
            writer = csv.DictWriter(data_file, fieldnames=csv_columns)
            logging.debug(f"_write_object_data_to_file(): Writing data to {file_name}")
            for state, sdata in self.data.items():
                st = state
                pop = sdata.get_population()
                median_age = sdata.get_median_age()
                death_data = sdata.get_death_data()
                # logging.debug(f"{state} - {sdata}")
                for key, value in death_data:
                    period = key
                    deaths = value

                    row_data = {"State": st, "Population": pop,
                                "Median Age": median_age,
                                "Period": period, "Deaths": deaths}
                    writer.writerow(row_data)

    def _get_data_from_file(self, file_name):
        with open(file_name, "r", encoding="utf-8") as data_file:
            logging.debug(f"_get_data_from_file(): Getting data from {file_name}")
            csv_columns = ["State", "Population", "Median Age", "Period", "Deaths"]
            reader = csv.DictReader(data_file, fieldnames=csv_columns)

            for r in reader:
                # logging.debug(r)
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

        logging.debug(f"_get_covid_data(): Read data from {file_name}")
        with open(file_name, "r", encoding="utf-8-sig") as data_file:
            data_file
            reader = csv.DictReader(data_file)

            for row in reader:
                # In testing, I was encountering an encoding issue with the BOM.
                # Specifying the encoding did not correct it in 1 environment.
                # This is a work around in case that surfaces on unknown machines.
                try:
                    state_flag = row["countyFIPS"]
                except KeyError as k:
                    logging.debug(f"_get_median_age: Key error, {k}")
                    state_flag = row["\ufeffcountyFIPS"]

                if state_flag != 0:
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

    def _get_populations(self, pop_file_name) -> dict:
        if not os.path.exists(pop_file_name):
            pop_url = "https://usafactsstatic.blob.core.windows.net/" + \
                      "public/data/covid-19/" + \
                      "covid_county_population_usafacts.csv"
            self._get_web_data(pop_url, pop_file_name)

        state_totals = dict()

        with open(pop_file_name, "r", encoding="utf-8") as data_file:
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

        with open(age_file_name, encoding="utf-8") as data_file:
            reader = csv.DictReader(data_file)

            for p in reader:
                try:
                    state_median[p["State"]] = float(p["Median"])
                except KeyError as k:
                    logging.debug(f"_get_median_age: {k}")
                    state_median[p["\ufeffState"]] = float(p["Median"])
                
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
            with open(file_name, "w", newline="", encoding="utf-8") as data:
                data.write(response.text)
        else:
            logging.critical(f"We have a problem: {response.status_code}")
            sys.exit()

    def _get_file_data(self, data_file_name: str):
        """
        If the files exists, it is opened and the data is loaded into a
        str object and is returned with the data.
        """
        if not os.path.exists(data_file_name):
            raise FileNotFoundError

        with open(data_file_name, "r", encoding="utf-8") as original_file:
            file_stuff = original_file.read()

        return file_stuff

    def get_deaths_for_period(self, period):
        rates = []
        for key, obj in self.data.items():
            rates.append((key, obj.population, obj.median_age, obj.get_death_data_for_period(period)))
        return rates

    def get_max_deaths(self):
        rates = []
        for key, obj in self.data.items():
            rates.append((key, obj.population, obj.median_age, obj.max_deaths()))
        return rates

    def get_state_totals(self):
        rates = []
        for key, obj in self.data.items():
            rates.append((key, obj.population, obj.median_age, obj.get_total_deaths()))
        return rates

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
        with open(outfile, "w", encoding="utf-8") as outfile:
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


def covid_deaths(covid_data_df, sort_order, plot, outfile):
    write_to_file(covid_data_df, outfile)

    if plot:
        plot_data(covid_data_df["state"], covid_data_df["num_deaths"], sort_order)


def state_data(covid_data, state, plot, outfile):
    s_data = covid_data.get_state_data(state)

    headers = f"{s_data.state}, population: {s_data.population}, median age: {s_data.median_age}\n"

    if outfile is None:
        print(headers)
        for key, value in s_data.state_data.items():
            print(f"Deaths in {calendar.month_abbr[int(key)]}: {value}")
    else:
        with open(outfile, "w", encoding="utf-8") as output:
            output.write(headers)
            for key, value in s_data.state_data.items():
                output.write(f"Deaths in {calendar.month_abbr[int(key)]}: {value}\n")
    
    if plot:
        keys = s_data.state_data.keys()
        values = s_data.state_data.values()
        plot_line_chart(keys, values, state, s_data.population, s_data.median_age)


def plot_line_chart(keys, values, state, population, median_age):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()

    month_label = []
    for m in keys:
        month_label.append(calendar.month_name[m])

    values_array = np.array(list(values), dtype=np.float32)

    ax.plot(month_label, values_array)
    
    plot_title = f"{state}\nPopulation: {population}\nMedian Age: {median_age}"
    ax.set_title(plot_title)
    
    plt.xticks(rotation=45)
    plt.show()

def process_all_periods(covid_data, sort_order):
    df = pd.DataFrame(columns=["state", "population", "median_age"])
    for state, sdata in covid_data.data.items():
        state_header = [state, sdata.get_population(), sdata.get_median_age()]
        df_temp = pd.DataFrame([state_header], columns=["state", "population", "median_age"])

        for key, val in sdata.state_data.items():
            df_temp[key] = val

        df = df.append(df_temp, ignore_index=True)
        df.sort_values(by=sort_order)
    return df


def print_all_periods(covid_df, plot, outfile, sort_order):
    write_to_file(covid_df, outfile)

    if plot:
        plot_all(covid_df, sort_order)


def plot_all(covid_df, sort_order):
    import matplotlib.pyplot as plt
    labels = covid_df["state"]
    fig, ax = plt.subplots()

    for m in range(3,8):
        ax.bar(labels, covid_df[m], .2, label=calendar.month_name[m])

    plot_title = f'Deaths per Month by State\nsorted by {sort_order}'

    ax.set_ylabel('COVID-19 Deaths')
    ax.set_xlabel('States')
    ax.set_title(plot_title)
    ax.legend()

    plt.xticks(rotation=90)
    plt.show()


def plot_data(x: list, y: list, sort_order):
    logging.debug(f"Plotting data.")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()

    plot_title = f'Deaths per State\nsorted by {sort_order}'

    ax.set_ylabel('COVID-19 Deaths')
    ax.set_xlabel('States')
    ax.set_title(plot_title)

    plt.scatter(x, y)
    plt.xticks(rotation=90)
    plt.show()


def main():
    setup_logging()

    file_name = "covid_data.csv"

    logging.debug("Create Data class.")
    logging.debug(sys.getdefaultencoding())

    parser = argparse.ArgumentParser(
        description="Parse command line arguments")

    parser.add_argument("command", metavar="<command>",
                        type=str,
                        choices=["print", "deaths", "state"],
                        default="print",
                        help="Command to print")

    parser.add_argument("-l", "--location", dest="state",
                        type=str, help="Two letter state code, e.g., TX or DC.")

    parser.add_argument("-s", "--sort", dest="sort_order",
                        type=str,
                        choices=["population", "median_age", "state"],
                        default="population",
                        help="Sorting can be done by population, median_age, or state.")

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

    parser.add_argument("-a", "--agg", dest="agg",
                        type=str,
                        choices=["total", "max", "all"],
                        default="total",
                        help="The data can be returned as a total of all " +
                             "deaths, maximum value, or all periods separated.")

    args = parser.parse_args()

    command_param = args.command
    sort_order = args.sort_order
    file_name = args.file_name
    plot = args.plot
    outfile = args.outfile
    state = args.state
    agg = args.agg

    logging.debug(f"Arg command_param = {command_param}")
    logging.debug(f"Arg sort_order = {sort_order}")
    logging.debug(f"Arg file_name = {file_name}")
    logging.debug(f"Arg plot = {plot}")
    logging.debug(f"Arg outfile = {outfile}")
    logging.debug(f"Arg state = {state}")

    covid_data = StateCovidData(file_name)

    if agg =="all":
        cd_values = process_all_periods(covid_data, sort_order)
        print_all_periods(cd_values, plot, outfile, sort_order)
        return None

    if agg == "max":
        cd_values = covid_data.get_max_deaths()
    else:
        cd_values = covid_data.get_state_totals()

    covid_data_df = pd.DataFrame(cd_values, 
                                 columns=["state", "population",
                                          "median_age", "num_deaths"])
    covid_data_df = covid_data_df.sort_values(by=sort_order)

    if command_param == "print":
        write_to_file(covid_data_df, outfile)
        return None

    if command_param == "deaths":
        covid_deaths(covid_data_df, sort_order, plot, outfile)
        return None
    
    if command_param == "state":
        if state is None:
            print("To create a pie chart, I need a state. Use the '-l' " +
                  "argument and supply a 2 letter state code.")
            sys.exit()
        state_data(covid_data, state, plot, outfile)
        return None

if __name__ == '__main__':
    main()
