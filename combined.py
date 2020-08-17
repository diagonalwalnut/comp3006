from covid_deaths import StateCovidData, StateCovid
from covid_cases import StateCountyData, StateCounty
import pandas as pd
import argparse
import logging


def plot_data(x: list, y: list):
    import matplotlib.pyplot as plt
    plt.scatter(x, y)
    plt.xticks(rotation=90)
    plt.show()

def covid_for_states(period, sort_order):
    deaths = StateCovidData("covid.data.txt")
    # cases = StateCountyData()
    
    deaths_for_period = deaths.get_deaths_for_period(period)
    df = pd.DataFrame(deaths_for_period, columns=["state", "population", "median_age", "deaths"])
    df = df.sort_values(by="population")

    # df["cases"] = cases.sort_by_state()

    df = df.sort_values(by=sort_order)

    return df

    m =deaths.get_deaths_for_period(period)
    print(m)

def main():
    parser = argparse.ArgumentParser(
        description="Parse command line arguments")

    parser.add_argument("-s", "--sort", dest="sort_order",
                        type=str,
                        choices=["population", "median_age", "state"],
                        default="population",
                        help="")

    parser.add_argument("-m", "--month", dest="month",
                        type=int,
                        choices=[3, 4, 5, 6, 7],
                        help="")

    args = parser.parse_args()

    sort_order = args.sort_order
    period = args.month

    """ 
    We need to add the call to covid_cases here to get the cases.

    We can then add the values to the plot_data_df dataframe. It would
    probably be best to get the caes first, then pass it into covid_for_states()
    which would add the cases as it iterates through "deaths".
    """
    plot_data_df = covid_for_states(period, sort_order)

    rate = plot_data_df["deaths"]
    # rate = plot_data_df["deaths"]/plot_data_df["cases"]

    plot_data(plot_data_df["state"], rate)

if __name__ == '__main__':
    main()
