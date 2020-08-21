import unittest
from covid_deaths import StateCovid, StateCovidData


class TestStateCovid(unittest.TestCase):
    def test_create_object(self):
        test_state = StateCovid("TX", 28000000, 35)
        test_state.add_deaths(3, 100)
        test_state.add_deaths(4, 200)
        test_state_str = "State: TX, Population: 28000000, Median Age: 35, State Data: {3: 100, 4: 200}"
        self.assertEqual(str(test_state), test_state_str)

    def test_add_deaths_no_data(self):
        test_state = StateCovid("TX", 28000000, 35)
        test_state.add_deaths(3, 100)
        test_state_str = "State: TX, Population: 28000000, Median Age: 35, State Data: {3: 100}"
        self.assertEqual(str(test_state), test_state_str)

    def test_add_deathss_add_to_existing_period(self):
        test_state = StateCovid("TX", 28000000, 35)
        test_state.add_deaths(3, 100)
        test_state.add_deaths(3, 50)
        test_state_str = "State: TX, Population: 28000000, Median Age: 35, State Data: {3: 150}"
        self.assertEqual(str(test_state), test_state_str)

    def test_add_deathss_add_to_empty_period(self):
        test_state = StateCovid("TX", 28000000, 35)
        test_state.add_deaths(3, 100)
        test_state.add_deaths(4, 200)
        test_state_str = "State: TX, Population: 28000000, Median Age: 35, State Data: {3: 100, 4: 200}"
        self.assertEqual(str(test_state), test_state_str)

    def test_set_population(self):
        test_state = StateCovid("TX", 28000000, 35)
        test_state.add_deaths(3, 100)
        test_state.set_population(15)
        test_state_str = "State: TX, Population: 15, Median Age: 35, State Data: {3: 100}"
        self.assertEqual(str(test_state), test_state_str)

    def test_get_population(self):
        test_state = StateCovid("TX", 28000000, 35)
        test_state.add_deaths(3, 100)
        pop = test_state.get_population()
        self.assertEqual(pop, 28000000)

    def test_set_median_age(self):
        test_state = StateCovid("TX", 28000000, 35)
        test_state.add_deaths(3, 100)
        test_state.set_median_age(15)
        test_state_str = "State: TX, Population: 28000000, Median Age: 15, State Data: {3: 100}"
        self.assertEqual(str(test_state), test_state_str)

    def test_get_median_age(self):
        test_state = StateCovid("TX", 28000000, 35)
        test_state.add_deaths(3, 100)
        age = test_state.get_median_age()
        self.assertEqual(age, 35)

    def test_get_data_for_period(self):
        test_state = StateCovid("TX", 28000000, 35)
        test_state.add_deaths(3, 100)
        dat = test_state.get_death_data_for_period(3)
        self.assertEqual(dat, 100)

    def test_get_death_data(self):
        test_state = StateCovid("TX", 28000000, 35)
        test_state.add_deaths(3, 100)
        test_state.add_deaths(4, 200)
        dict_items = iter(test_state.get_death_data())

        key, value = next(dict_items)
        self.assertEqual(key, 3)
        self.assertEqual(value, 100)

        key, value = next(dict_items)
        self.assertEqual(key, 4)
        self.assertEqual(value, 200)

    def test_total_deaths(self):
        test_state = StateCovid("TX", 28000000, 35)
        test_state.add_deaths(3, 100)
        test_state.add_deaths(4, 200)
        total = test_state.get_total_deaths()
        self.assertEqual(total, 300)
        total = test_state.get_death_data_for_period(3)
        self.assertEqual(total, 100)

    def test_max_deaths(self):
        test_state = StateCovid("TX", 28000000, 35)
        test_state.add_deaths(3, 100)
        test_state.add_deaths(4, 200)
        test_state.add_deaths(5, 5)
        test_state.add_deaths(6, 1000)
        maximum = test_state.max_deaths()
        self.assertEqual(maximum, 1000)

class TestStateCovidData(unittest.TestCase):
    def test_get_death_data(self):
        test_state_tx = StateCovid("TX", 28000000, 35)
        test_state_tx.add_deaths(3, 100)
        test_state_tx.add_deaths(4, 200)
        test_state_ut = StateCovid("UT", 10000000, 25)
        test_state_ut.add_deaths(3, 1)
        test_state_ut.add_deaths(4, 10)
        data_dict = StateCovidData("no_file.txt", True)
        data_dict.add_state_data(test_state_tx)
        data_dict.add_state_data(test_state_ut)

        self.assertIsNotNone(data_dict.data["TX"])
        self.assertEqual(data_dict.data["TX"].population, 28000000)
        self.assertEqual(data_dict.data["TX"].median_age, 35)
        self.assertIsNotNone(data_dict.data["UT"])
        self.assertEqual(data_dict.data["UT"].population, 10000000)
        self.assertEqual(data_dict.data["UT"].median_age, 25)

        tx = data_dict.get_state_data("TX")
        self.assertEqual(test_state_tx, tx)

        with self.assertRaises(KeyError):
            data_dict.data["NY"]
    
    def test_get_death_data_test_file(self):
        data_dict = StateCovidData("no_file.txt", True)
        data_dict._get_covid_data("test_deaths.csv", "http://google.com")

        al_str = "State: AL, Population: 0, Median Age: 0, State Data: {3: 3, 4: 27, 5: 30, 6: 90, 7: 150}"
    
        self.assertEqual(str(data_dict.data["AL"]), al_str)

    def test_get_population(self):
        data_dict = StateCovidData("no_file.txt", True)
        pop_test = data_dict._get_populations("test_population.csv")

        self.assertEqual(pop_test["AL"], 400)
        self.assertEqual(pop_test["CO"], 3001)
    
    def test_get_median_age(self):
        data_dict = StateCovidData("no_file.txt", True)
        age_test = data_dict._get_median_age("state_median_age.csv")
        
        self.assertEqual(age_test["CO"], 37.1)
        self.assertEqual(age_test["TX"], 35)
    
    def test_get_totals(self):
        data_dict = StateCovidData("no_file.txt", True)
        data_dict._get_covid_data("test_deaths.csv", "http://google.com")
        tp = data_dict.get_deaths_for_period(4)
        self.assertEqual(tp[0][0], 'AL')
        self.assertEqual(tp[0][3], 27)

        tm = data_dict.get_max_deaths()
        self.assertEqual(tm[0][0], 'AL')
        self.assertEqual(tm[0][3], 150)
        
        tst = data_dict.get_state_totals()
        self.assertEqual(tst[0][0], 'AL')
        self.assertEqual(tst[0][3], 300)
        
        ts = data_dict.get_state_data("CO")
        self.assertEqual(ts.state_data[3], 27)
        self.assertEqual(ts.state_data[7], 300)
        

