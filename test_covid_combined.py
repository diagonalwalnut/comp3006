import unittest
import combined
from covid_deaths import StateCovidData, StateCovid
from covid_cases import StateCountyData, StateCounty

class TestStateCovid(unittest.TestCase):
    def test_calc_case_rates(self):
        rate = combined.calc_case_rate(10, 100)
        self.assertEqual(rate, .1000)

    def test_calc_death_rates(self):
        rate = combined.calc_death_rate(10, 100)
        self.assertEqual(rate, .1000)

    def test_calc_death_to_case_rates(self):
        rate = combined.calc_deaths_to_cases(10, 100)
        self.assertEqual(rate, .1000)
    
    def test_create_dataframe(self):
        data_dict = StateCovidData("no_file.txt", True)
        data_dict._get_covid_data("test_deaths.csv", "http://google.com")

        t = combined.covid_for_states(data_dict, "population", None)
        self.assertEqual(t["deaths"][0], 300)
        self.assertEqual(t["deaths"][1], 1497)
        self.assertEqual(t["cases"][0], 87721)
        self.assertEqual(t["cases"][1], 46789)

        t = combined.covid_for_states(data_dict, "population", 3)
        self.assertEqual(t["deaths"][0], 3)
        self.assertEqual(t["deaths"][1], 27)
        t = combined.covid_for_states(data_dict, "population", 7)
        self.assertEqual(t["deaths"][0], 150)
        self.assertEqual(t["deaths"][1], 300)
