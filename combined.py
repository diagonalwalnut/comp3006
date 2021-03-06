import pandas as pd
import numpy as np
import argparse
import logging
import matplotlib.pyplot as plt
import sys
from collections import defaultdict
from covid_deaths import StateCovidData, StateCovid
from covid_cases import StateCountyData, StateCounty

def plot_data(x: list, y: list, sort_order, period):
    plt.scatter(x, y)
    plt.xticks(rotation=90)

    if period is None:
        period = "March - July"

    if sort_order == 'population':
        plt.title(f'Death rates by state for {period}/2020')
        plt.xlabel('States in order of increasing population')
        plt.ylabel('Ratio of deaths to cases')
    elif sort_order == 'median_age':
        plt.title(f'Death rates by state for {period}/2020')
        plt.xlabel('States in order of increasing median age')
        plt.ylabel('Ratio of deaths to cases')
    else:
        plt.title(f'Death rates by state for {period}/2020')
        plt.xlabel('States in alphabetical order')
        plt.ylabel('Ratio of deaths to cases')

    plt.show()

def group_counties_to_states(period, states):
    cases = StateCountyData()
    cases_sorted = cases.sort_by_state()

    month_dict = {'3' : 'March', '4' : 'April', '5' : 'May', '6' : 'June',
                    '7' : 'July'}
    period_as_month = month_dict[str(period)]

    cases_dict = defaultdict(list)

    for i in cases_sorted:
        if i.month == period_as_month:
            if i.state not in states:
                continue

            if i.state not in cases_dict:
                cases_dict[i.state] = i.case_num
                continue

            cases_dict[i.state] = cases_dict[i.state] + i.case_num

    return cases_dict

def get_covid_deaths(file_name):
    return StateCovidData()

def covid_for_states(deaths, sort_order, period):
    if period is None:
        start = 3
        end = 8
    else:
        start = period
        end = period + 1

    df = None

    for i in range(start, end):
        cases = group_counties_to_states(i, deaths.data.keys())
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

def plot_state_to_total_comparison(df, state, period):
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

    outer_perc = round(st["population"].sum()/tot_pop*100,2)
    middle_perc = round(st["cases"].sum()/tot_cases*100,2)
    inner_perc = round(st["deaths"].sum()/tot_deaths*100,2)

    outer_label = [f'U.S. population:\n{tot_pop}', f'{state} population:\n{st["population"].sum()}\n{outer_perc}%']
    middle_label = [f'U.S. cases:\n{tot_cases}', f'{state} cases:\n{st["cases"].sum()}\n{middle_perc}%']
    inner_label = [f'U.S. deaths:\n{tot_deaths}', f'{state} deaths:\n{st["deaths"].sum()}\n{inner_perc}%']

    fig, ax = plt.subplots()
    ax.axis('equal')

    a, b =[plt.cm.Blues, plt.cm.Greens]

    pop_pie, _ = ax.pie(vals_pop, radius=pop_radius,
                        wedgeprops=dict(width=.3, edgecolor='w'),
                        labels=outer_label,
                        labeldistance=0.8, startangle=0,
                        colors=[a(0.6), b(0.6)])
    plt.setp(pop_pie, width=0.5, edgecolor='white')

    cases_pie, _ = ax.pie(vals_cases, radius=cases_radius,
                          wedgeprops=dict(width=.3, edgecolor='w'),
                          labels=middle_label,
                          labeldistance=0.6, startangle=-45,
                          colors=[a(0.4), b(0.4)])
    plt.setp(cases_pie, width=0.5, edgecolor='white')

    deaths_pie, _ = ax.pie(vals_deaths, radius=deaths_radius,
                           wedgeprops=dict(width=.3, edgecolor='w'),
                           labels=inner_label, startangle=-90,
                           labeldistance=0.3,
                           colors=[a(0.2), b(0.2)])
    plt.setp(deaths_pie, width=0.5, edgecolor='white')

    plt.margins(0,0)
    if period is None:
        period = "March - July"

    ax.set_title(f"Population, Cases, Deaths for {state} in {period}/2020",
                 loc="center")

    plt.show()

def plot_bar_chart(cases, deaths, state, sort_order, period):
    labels = state

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, deaths, width, label='Deaths')
    rects2 = ax.bar(x + width/2, cases, width, label='Cases')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    if period is None:
        period = "March - July"

    if sort_order == 'population':
        ax.set_title(f'Comparison of case rates and death rates for {period}/2020')
        ax.set_ylabel('Ratio of deaths/cases to population')
        ax.set_xlabel('States in order of increasing population')
    elif sort_order == 'median_age':
        ax.set_title(f'Comparison of case rates and death rates for {period}/2020')
        ax.set_ylabel('Ratio of deaths/cases to population')
        ax.set_xlabel('States in order of increasing median_age')
    else:
        ax.set_title(f'Comparison of case rates and death rates for {period}/2020')
        ax.set_ylabel('Ratio of deaths/cases to population')
        ax.set_xlabel('States in alphabetical order')

    plt.xticks(rotation=90)
    plt.show()

def calc_death_rate(deaths, population):
    return round(deaths/population, 4)

def calc_case_rate(cases, population):
    return round(cases/population, 4)

def calc_deaths_to_cases(deaths, cases):
    return round(deaths/cases, 4)

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
                        choices = ['HI','AK','WA','OR','CA','NV','ID','UT',
                        'AZ','MT','WY','CO','NM','ND','SD','NE','KS','OK',
                        'TX','MN','IA','MO','AR','LA','WI','MI','IL','IN',
                        'KY','TN','MS','AL','GA','FL','SC','NC','VA','MD',
                        'DE','DC','WV','OH','PA','NJ','NY','CT','RI','MA',
                        'VT','NH','ME'],
                        type=str, help="")

    args = parser.parse_args()

    sort_order = args.sort_order
    period = args.month
    state = args.state
    plot = args.plot

    death_data = get_covid_deaths("covid.data.txt")
    plot_data_df = covid_for_states(death_data, sort_order, period)

    if plot == "pie":
        if state is None:
            print("To create a pie chart, I need a state. Use the '-l' argument and supply a 2 letter state code.")
            sys.exit()

        plot_state_to_total_comparison(plot_data_df, state, period)
    elif plot == "bar":
        death_rate = calc_death_rate(plot_data_df["deaths"], plot_data_df["population"])
        case_rate = calc_case_rate(plot_data_df["cases"], plot_data_df["population"])
        plot_bar_chart(case_rate, death_rate, plot_data_df["state"], sort_order, period)
    else:
        rate = calc_deaths_to_cases(plot_data_df["deaths"], plot_data_df["cases"])
        plot_data(plot_data_df["state"], rate, sort_order, period)

if __name__ == '__main__':
    main()
