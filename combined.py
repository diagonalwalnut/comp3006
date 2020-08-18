import pandas as pd
import numpy as np
import argparse
import logging
import matplotlib.pyplot as plt
import sys
from collections import defaultdict
from covid_deaths import StateCovidData, StateCovid
from covid_cases import StateCountyData, StateCounty

def plot_data(x: list, y: list):
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


def covid_for_states(sort_order, period):
    deaths = StateCovidData("covid.data.txt")
    
    if period is None:
        start = 3
        end = 8
    else:
        start = period
        end = period + 1

    df = None

    for i in range(start, end):
        cases = group_counties_to_states(i)
        deaths_for_period = deaths.get_deaths_for_period(i)
        if df is None:
            df = pd.DataFrame(deaths_for_period, columns=["state", "population", "median_age", "deaths-" + str(i)])
            df = df.sort_values(by="state")
            df["cases-" + str(i)] = cases.values()
            continue
    
        temp = pd.DataFrame(deaths_for_period, columns=["state", "population", "median_age", "deaths"])
        temp = temp.sort_values(by="state")
        temp["cases"] = cases.values()

        df[str("cases-" + str(i))] = temp["cases"]
        df[str("deaths-" + str(i))] = temp["deaths"]
        
    
    df = df.sort_values(by=sort_order)
    
    rtnDf = pd.DataFrame()
    rtnDf["state"] = df["state"]
    rtnDf["population"] = df["population"]
    rtnDf["median_age"] = df["median_age"]
    rtnDf["cases"] = 0
    rtnDf["deaths"] = 0

    for i in range(start, end):
        rtnDf["cases"] = rtnDf["cases"] + df["cases-" + str(i)]
        rtnDf["deaths"] = rtnDf["deaths"] + df["deaths-" + str(i)]

    return rtnDf

def state_to_total_comparison(df, state):
    tot_pop = sum(df["population"])
    tot_cases = sum(df["cases"])
    tot_deaths = sum(df["deaths"])
    st = df[df.state == state]

    vals_pop = np.array([tot_pop, st["population"].sum()])
    vals_cases = np.array([tot_cases, st["cases"].sum()])
    vals_deaths = np.array([tot_deaths, st["deaths"].sum()])
    pop_radius = 1.50
    cases_radius = 1
    deaths_radius = .50

    outer_label = [f'Total population:\n{tot_pop}', f'{state} population:\n{st["population"].sum()}']
    middle_label = [f'{tot_cases}', f'{st["cases"].sum()}']
    inner_label = [f'{tot_deaths}', f'{st["deaths"].sum()}']

    fig, ax = plt.subplots()
    ax.axis('equal')

    a, b =[plt.cm.Blues, plt.cm.Greens]

    pop_pie, _ = ax.pie(vals_pop, radius=pop_radius,
                        wedgeprops=dict(width=.3, edgecolor='w'),
                        labels=outer_label,
                        labeldistance=0.8,
                        colors=[a(0.6), b(0.6)])
    plt.setp(pop_pie, width=0.5, edgecolor='white')

    cases_pie, _ = ax.pie(vals_cases, radius=cases_radius, 
                          wedgeprops=dict(width=.3, edgecolor='w'),
                          labels=middle_label,
                          labeldistance=0.6,
                          colors=[a(0.4), b(0.4)])
    plt.setp(cases_pie, width=0.5, edgecolor='white')

    deaths_pie, _ = ax.pie(vals_deaths, radius=deaths_radius,
                           wedgeprops=dict(width=.3, edgecolor='w'),
                           labels=inner_label,
                           labeldistance=0.3,
                           colors=[a(0.2), b(0.2)])
    plt.setp(deaths_pie, width=0.5, edgecolor='white')

    plt.margins(0,0)
    ax.set_title(f"Population, Cases, Deaths for {state}",
                 loc="center")

    plt.show()


def plot_bar_chart(cases, deaths, state):
    labels = state

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, deaths, width, label='Deaths')
    rects2 = ax.bar(x + width/2, cases, width, label='Cases')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Scores')
    ax.set_title('Scores by group and gender')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    plt.xticks(rotation=90)
    plt.show()

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

    parser.add_argument("-p", "--plot", dest="plot",
                        type=str,
                        choices=["pie", "scatter", "bar"],
                        default="scatter",
                        help="")

    parser.add_argument("-l", "--location", dest="state",
                        type=str, help="")

    args = parser.parse_args()

    sort_order = args.sort_order
    period = args.month
    state = args.state
    plot = args.plot

    plot_data_df = covid_for_states(sort_order, period)

    if plot == "pie":
        if state is None:
            print("To create a pie chart, I need a state. Use the '-l' argument and supply a 2 letter state code.")
            sys.exit()
           
        state_to_total_comparison(plot_data_df, state)
    elif plot == "bar":
        death_rate = plot_data_df["deaths"]/plot_data_df["population"]
        case_rate = plot_data_df["cases"]/plot_data_df["population"]
        plot_bar_chart(case_rate, death_rate, plot_data_df["state"])
    else:
        rate = plot_data_df["deaths"]/plot_data_df["cases"]
        plot_data(plot_data_df["state"], rate)

if __name__ == '__main__':
    main()
