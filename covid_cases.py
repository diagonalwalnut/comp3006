import csv, logging, argparse, sys
import matplotlib.pyplot as plt, numpy as np
from collections import defaultdict


class StateCounty:
    """Hashable objects with attributes state, county, pop (population), month,
     and case_num (number of cases)"""

    def __init__(self, state, county, pop, month, case_num):
        # sets up the StateCounty object
        self.state = str(state)
        self.county = str(county)
        self.pop = int(pop)
        self.month = str(month)
        self.case_num = int(case_num)

    def __repr__(self):
        return f'StateCounty(\'{self.state}\', \'{self.county}\', {self.pop}, \'{self.month}\', {self.case_num})'

    def __str__(self):
        # repr and str methods return the same string
        return repr(self)

    def __eq__(self, other):
        # all attributes must match for equality
        if type(self) == type(other):
            return (self.state, self.county, self.pop, self.month, self.case_num) \
            == (other.state, other.county, other.pop, other.month, other.case_num)
        else:
            return NotImplemented

    def __lt__(self, other):
        # attributes are compared in the order given below
        if type(self) == type(other):
            return (self.state, self.county, self.pop, self.month, self.case_num) \
            < (other.state, other.county, other.pop, other.month, other.case_num)
        else:
            return NotImplemented

    def __hash__(self):
        # must be used to keep this class hashable because of the eq method.
        return hash((self.state, self.county, self.pop, self.month,
                    self.case_num))

class StateCountyData:
    """Iterable class of StateCounty objects"""

    def __init__(self, data=[]):
        # set up the StateCountyData list
        self.data = data
        if self.data == []:
            self._build_object_1()

    # the methods iter and next set up the iterator and counter
    def __iter__(self):
        self.counter = 0
        return self

    def __next__(self):
        if self.counter >= len(self.data):
            raise StopIteration
        else:
            x = self.counter
            self.counter += 1
            return x

    def _build_object_1(self):
        # set up the state, county and pop attributes of StateCounty objects
        with open('covid_county_population_usafacts.csv', 'r') as file_1:
            dialect1 = csv.Sniffer().sniff(file_1.read(2))
            reader1 = csv.reader(file_1, dialect1)
            fips_state_dict = defaultdict(list)
            fips_county_dict = defaultdict(list)
            fips_pop_dict = defaultdict(list)
            next(reader1)
            for row in reader1:
                if len(row) > 1:
                    row = ['c'.join(row)]
                split_string = row[0].split(',')
                x = split_string[0]
                if int(x) > 0:
                    fips_state_dict[x].append(str(split_string[2]))
                    fips_county_dict[x].append(str(split_string[1]))
                    fips_pop_dict[x].append(int(split_string[3]))

        #logging.debug('state dictionary: %s' % fips_state_dict)

        self._build_object_2(fips_state_dict, fips_county_dict, fips_pop_dict)

    def _build_object_2(self, fips_state_dict, fips_county_dict, fips_pop_dict):
        # set up the num_cases attribute of StateCounty objects
        with open('covid_confirmed_usafacts.csv', 'r') as file_2:
            dialect2 = csv.Sniffer().sniff(file_2.read(2))
            reader2 = csv.reader(file_2, dialect2)
            mar_dict = defaultdict(list)
            apr_dict = defaultdict(list)
            may_dict = defaultdict(list)
            jun_dict = defaultdict(list)
            jul_dict = defaultdict(list)
            next(reader2)
            for row in reader2:
                if len(row) > 1:
                    row = ['c'.join(row)]
                split_record = row[0].split(',')
                y = split_record[0]
                if int(y) > 0:
                    mar_dict[y].append(int(split_record[73]) - \
                                        int(split_record[42]))
                    apr_dict[y].append(int(split_record[103]) -\
                                        int(split_record[73]))
                    may_dict[y].append(int(split_record[134]) -\
                                        int(split_record[103]))
                    jun_dict[y].append(int(split_record[164]) -\
                                        int(split_record[134]))
                    jul_dict[y].append(int(split_record[195]) -\
                                        int(split_record[164]))

        #logging.debug('may dictionary: %s' % may_dict)

        self._build_object_3(fips_state_dict, fips_county_dict, fips_pop_dict,
                            mar_dict, apr_dict, may_dict, jun_dict, jul_dict)

    def _build_object_3(self, fips_state_dict, fips_county_dict, fips_pop_dict,
                        mar_dict, apr_dict, may_dict, jun_dict, jul_dict):
        # take the attributes from build_object_1 and build_object_2 and
        # create the StateCounty objects, then build the StateCountyData
        # object
        for j in fips_state_dict:
            self.data.append(StateCounty(fips_state_dict[j][0],
                            fips_county_dict[j][0], fips_pop_dict[j][0],
                            'March', mar_dict[j][0]))
            self.data.append(StateCounty(fips_state_dict[j][0],
                            fips_county_dict[j][0], fips_pop_dict[j][0],
                            'April', apr_dict[j][0]))
            self.data.append(StateCounty(fips_state_dict[j][0],
                            fips_county_dict[j][0], fips_pop_dict[j][0],
                            'May', may_dict[j][0]))
            self.data.append(StateCounty(fips_state_dict[j][0],
                            fips_county_dict[j][0], fips_pop_dict[j][0],
                            'June', jun_dict[j][0]))
            self.data.append(StateCounty(fips_state_dict[j][0],
                            fips_county_dict[j][0], fips_pop_dict[j][0],
                            'July', jul_dict[j][0]))

    def sort_by_state(self):
        month_dict = {'March' : 3, 'April' : 4, 'May' : 5, 'June' : 6,
                        'July' : 7}
        self.data.sort(key=lambda StateCounty : (StateCounty.state, \
                        StateCounty.pop, StateCounty.county, \
                        month_dict[StateCounty.month], StateCounty.case_num))
        logging.debug('sorted by state %s' % self.data)
        return self.data

def states_write(args, rate_dict, month_dict):
    # writes the output for the 'states' command and makes a plot if '-p'
    # is given in the command line

    # output to be written in order of increasing state population
    sort_keys = sorted(rate_dict.keys(), key=lambda x : x[1])

    logging.debug('sort_keys is %s' % sort_keys)


    if args.o_file is None:
        writer = csv.DictWriter(sys.stdout, fieldnames=['(state, population)',
                f'infection rate in {month_dict[args.which_month]} 2020 (percentage)'])
        writer.writeheader()
        for i in sort_keys:
            writer.writerow({'(state, population)' : i,
                    f'infection rate in {month_dict[args.which_month]} 2020 (percentage)'\
                     : rate_dict[i]})
    else:
        with open(args.o_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['(state, population)',
                f'infection rate in {month_dict[args.which_month]} 2020 (percentage)'])
            writer.writeheader()
            for i in sort_keys:
                writer.writerow({'(state, population)' : i,
                    f'infection rate in {month_dict[args.which_month]} 2020 (percentage)'\
                    : rate_dict[i]})

    if args.plot:
        plt.plot([x[0] for x in rate_dict], [rate_dict[x] for x in rate_dict], 'go')
        plt.title(f'Infection Rates in {month_dict[args.which_month]} 2020')
        plt.xlabel('states in order of increasing population')
        plt.xticks(rotation=90)
        plt.ylabel('infection rate as a percentage of state population')
        plt.show()

def months_write(args, rate_dict, month_dict):
    # writes the output for the 'months' command and makes a plot if '-p'
    # is given in the command line
    if args.o_file is None:
        writer = csv.DictWriter(sys.stdout, fieldnames=['(county, population)',
                f'infection rate in {month_dict[args.which_month]} 2020 (percentage) for {args.which_state}'])
        writer.writeheader()
        for i in rate_dict:
            writer.writerow({'(county, population)' : i,
                f'infection rate in {month_dict[args.which_month]} 2020 (percentage) for {args.which_state}'\
                : rate_dict[i]})
    else:
        with open(args.o_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['(county, population)',
                    f'infection rate in {month_dict[args.which_month]} 2020 (percentage) for {args.which_state}'])
            writer.writeheader()
            for i in rate_dict:
                writer.writerow({'(county, population)' : i,
                    f'infection rate in {month_dict[args.which_month]} 2020 (percentage) for {args.which_state}'\
                    : rate_dict[i]})

    if args.plot:
        plt.plot([x[0] for x in rate_dict], [rate_dict[x] for x in rate_dict], 'ro')
        plt.title(f'Infection Rates in {month_dict[args.which_month]} 2020 for {args.which_state}')
        plt.xlabel('counties in order of increasing population')
        plt.xticks(rotation=90)
        plt.ylabel('infection rate as a percentage of county population')
        plt.show()

def states(args):
    # what happens when the command 'states' is given
    month_dict = {'3' : 'March', '4' : 'April', '5' : 'May', '6' : 'June',
                    '7' : 'July'}
    obj = StateCountyData().sort_by_state()
    cases_dict = defaultdict(list)
    pop_dict = defaultdict(list)
    rate_dict = {}
    for i in obj:
        if i.month == month_dict[args.which_month]:
            cases_dict[i.state].append(i.case_num)
            pop_dict[i.state].append(i.pop)

    '''logging.debug('cases_dict is %s' % cases_dict)
    logging.debug('pop_dict is %s' % pop_dict)'''

    # the dictionary from which output and plots are made
    for k in cases_dict:
        rate_dict.update({(k, sum(pop_dict[k])) : (sum(cases_dict[k] * 100) / sum(pop_dict[k]))})

    logging.debug('rate_dict is %s' % rate_dict)

    states_write(args, rate_dict, month_dict)

def months(args):
    # what happens when the command 'months' is given

    month_dict = {'3' : 'March', '4' : 'April', '5' : 'May', '6' : 'June',
                    '7' : 'July'}
    obj = StateCountyData().sort_by_state()
    rate_dict = {}
    for i in obj:
        if i.state == args.which_state and \
            i.month == month_dict[args.which_month] and \
            i.pop > 0:
            rate_dict.update({(i.county, i.pop) : (i.case_num * 100) / i.pop})

    logging.debug('rate_dict is %s' % rate_dict)

    months_write(args, rate_dict, month_dict)

def arguments(args):
    # this function handles the 'command' argument
    if args.command == 'states':
        states(args)
    if args.command == 'months':
        if args.which_state is None:
            print('You must choose a state.')
            sys.exit(1)
        else:
            months(args)

def main():
    # This function sets up logging and argparse

    # setting up the logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # messages that go to a file:
    fh = logging.FileHandler('covid_cases.log', 'w')
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    # messages that go to console:
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    logger.addHandler(sh)

    # setting up the argument parser
    parser = argparse.ArgumentParser(description=\
                        'Covid data for March through July 2020')

    parser.add_argument('command', metavar='<command>',
                        choices=['states','months'],
                        help='choose how to display data')
    parser.add_argument('which_month', metavar='<which_month>',
                        choices=['3','4','5','6','7'],
                        help='choose a month from March to July')
    # must be selected if command is 'months'
    parser.add_argument('-s', '--which_state', metavar='<which_state>',
                        choices = ['HI','AK','WA','OR','CA','NV','ID','UT',
                        'AZ','MT','WY','CO','NM','ND','SD','NE','KS','OK',
                        'TX','MN','IA','MO','AR','LA','WI','MI','IL','IN',
                        'KY','TN','MS','AL','GA','FL','SC','NC','VA','MD',
                        'DE','DC','WV','OH','PA','NJ','NY','CT','RI','MA',
                        'VT','NH','ME'], help='required when <command> is months')
    # optional command to name a csv file for output. if not used, output
    # prints to console
    parser.add_argument('-o', '--o_file', metavar='<outfile>',
                        help='the name of a csv output file')
    # optional command to plot data
    parser.add_argument('-p', '--plot', action='store_true',
                        help='to create a plot')
    args = parser.parse_args()

    arguments(args)


if __name__ == '__main__':
    main()
