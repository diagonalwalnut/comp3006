import unittest
from covid_deaths import StateCovidData, StateCovid
from covid_cases import StateCountyData, StateCounty

class TestStateCovid(unittest.TestCase):
    def test_create_object(self):
        data_dict = StateCovidData("no_file.txt", True)
        pop_test = data_dict._get_populations("test_population.csv")
        age_test = data_dict._get_median_age("state_median_age.csv")
        data_dict._get_covid_data("test_deaths.csv", "http://google.com")

        # Deaths test data
        al_str = "State: AL, Population: 0, Median Age: 0, State Data: {3: 3, 4: 27, 5: 30, 6: 90, 7: 150}"
        co_str = "State: CO, Population: 0, Median Age: 0, State Data: {3: 27, 4: 420, 5: 450, 6: 300, 7: 300}"

        # Populations from the Test
        self.assertEqual(pop_test["AL"], 400)
        self.assertEqual(pop_test["CO"], 3001)

        # Median Age from the Test
        self.assertEqual(age_test["AL"], 39.4)
        self.assertEqual(age_test["CO"], 37.1)