import pandas as pd
import argparse
import logging
from collections import defaultdict
from covid_deaths import StateCovidData, StateCovid
from covid_cases import StateCountyData, StateCounty

def plot_data(x: list, y: list):
    import matplotlib.pyplot as plt
    plt.scatter(x, y)
    plt.xticks(rotation=90)
    plt.show()


def group_counties_to_states(period):
    cases = StateCountyData()
    cases_sorted = cases.sort_by_state()

    month_dict = {'3' : 'March', '4' : 'April', '5' : 'May', '6' : 'June',
                    '7' : 'July'}
    period_as_month = month_dict[str(period)]

    cases_dict = defaultdict(list)
    # pop_dict = defaultdict(list)

    for i in cases_sorted:
        if i.month == period_as_month:
            if i.state not in cases_dict:
                cases_dict[i.state] = i.case_num
                # pop_dict[i.state] = i.pop
                continue

            cases_dict[i.state] = cases_dict[i.state] + i.case_num
            # pop_dict[i.state] = pop_dict[i.state] + i.pop

    return cases_dict


def covid_for_states(period, sort_order):
    deaths = StateCovidData("covid.data.txt")
    
    cases = group_counties_to_states(period)
    
    deaths_for_period = deaths.get_deaths_for_period(period)
    df = pd.DataFrame(deaths_for_period, columns=["state", "population", "median_age", "deaths"])
    df = df.sort_values(by="state")

    df["cases"] = cases.values()

    df = df.sort_values(by=sort_order)

    return df


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

    rate = plot_data_df["deaths"]/plot_data_df["cases"]

    plot_data(plot_data_df["state"], rate)

if __name__ == '__main__':
    main()
