from golem.tools.testwithdatabase import TestWithDatabase
from golem.tools.assertlogs import LogTestCase
from golem.transactions.incomeskeeper import IncomesDatabase, IncomesKeeper, logger, IncomesState


class TestIncomesDatabase(LogTestCase, TestWithDatabase):
    def test_init(self):
        id = IncomesDatabase()
        self.assertIsInstance(id, IncomesDatabase)

    def test_get_income_value(self):
        id = IncomesDatabase()
        with self.assertLogs(logger, level=1) as l:
            self.assertEquals((0, 0), id.get_income_value("xyz", "DEF"))
        self.assertTrue(any(["not exist" in log for log in l.output]))
        id.update_income("xyz", "DEF", "20.0", "30.0", "SOMESTATE")
        self.assertEquals((20, 30), id.get_income_value("xyz", "DEF"))
        id.update_income("xyz", "DEF", "20.0", "30.0", "SOMESTATE")

    def test_change_state(self):
        id = IncomesDatabase()
        id.change_state("xyz", "DEF", "DIFFSTATE")
        id.update_income("xyz", "DEF", "20.0", "30.0", "SOMESTATE")
        id.update_income("abc", "DEF", "20.0", "30.0", "SOMEOTHERSTATE")
        id.update_income("xyz", "GHI", "20.0", "30.0", "SOMEOTHERSTATE")

        incomes = [income for income in id.get_newest_incomes()]
        self.assertEquals(len(incomes), 3)
        self.assertEqual(id.get_state("xyz", "DEF"), "SOMESTATE")
        id.change_state("xyz", "DEF", "DIFFSTATE")
        incomes = [(income.from_node_id, income.state, income.task) for income in id.get_newest_incomes()]
        self.assertEquals(len(incomes), 3)
        self.assertEqual(id.get_state("xyz", "DEF"), "DIFFSTATE")
        self.assertEqual(id.get_state("abc", "DEF"), "SOMEOTHERSTATE")
        self.assertEqual(id.get_state("xyz", "GHI"), "SOMEOTHERSTATE")

        id.change_state("abc", "DEF", "DIFFSTATE2")
        id.change_state("xyz", "GHI", "DIFFSTATE3")
        incomes = [income for income in id.get_newest_incomes()]
        self.assertEquals(len(incomes), 3)
        self.assertEqual(id.get_state("xyz", "DEF"), "DIFFSTATE")
        self.assertEqual(id.get_state("abc", "DEF"), "DIFFSTATE2")
        self.assertEqual(id.get_state("xyz", "GHI"), "DIFFSTATE3")

    def test_get_state(self):
        id = IncomesDatabase()
        self.assertIsNone(id.get_state("xyz", "DEF"))
        id.update_income("xyz", "DEF", 30.0, 20.0, "SOMESTATE")
        self.assertEqual(id.get_state("xyz", "DEF"), "SOMESTATE")

    def test_update_income(self):
        id = IncomesDatabase()
        id.update_income("xyz", "DEF", 30.0, 20.0, "SOMESTATE")
        self.assertEqual(id.get_income_value("xyz", "DEF"), (30, 20))
        id.update_income("xyz", "DEF", 10.0, 30.0, "SOMESTATE", add_income=True)
        self.assertEqual(id.get_income_value("xyz", "DEF"), (40, 50))
        id.update_income("xyz", "DEF", 20.0, 50.0, "SOMESTATE", add_income=True)
        self.assertEqual(id.get_income_value("xyz", "DEF"), (60, 100))
        id.update_income("xyz", "DEF", 10.0, 10.0, "SOMESTATE")
        self.assertEqual(id.get_income_value("xyz", "DEF"), (10, 10))

    def test_get_newest_incomes(self):
        id = IncomesDatabase()
        for i in range(10):
            id.update_income("xyz{}".format(i), "DEF", i, i, "s")

        incomes = [income for income in id.get_newest_incomes(3)]
        self.assertEqual(len(incomes), 3)
        self.assertEqual(incomes[0].task, "xyz9")
        self.assertEqual(incomes[2].task, "xyz7")
        for i in range(20, 11, -1):
            id.update_income("xyz{}".format(i), "DEF", i, i, "s")
        incomes = [income for income in id.get_newest_incomes(3)]
        self.assertEqual(len(incomes), 3)
        self.assertEqual(incomes[0].task, "xyz12")
        self.assertEqual(incomes[2].task, "xyz14")


class TestIncomesKeeper(TestWithDatabase):
    def test_init(self):
        ik = IncomesKeeper()
        self.assertIsInstance(ik, IncomesKeeper)

    def test_add_payment(self):
        ik = IncomesKeeper()
        ik.add_waiting_payment("xyz", "DEF")
        ik.add_waiting_payment("zyx", "FED")
        xyz = filter(lambda x: x["task"] == "xyz", ik.get_list_of_all_incomes())
        self.assertEqual(len(xyz), 1)
        self.assertEqual(xyz[0]["state"], IncomesState.waiting)
        self.assertEqual(xyz[0]["value"], 0)
        ik.add_timeouted_payment("xyz")
        xyz = filter(lambda x: x["task"] == "xyz", ik.get_list_of_all_incomes())
        self.assertEqual(len(xyz), 1)
        self.assertEqual(xyz[0]["state"], IncomesState.timeout)
        ik.add_income("xyz", "DEF", 10)
        ik.add_income("zyz", "FED", 100)
        xyz = filter(lambda x: x["task"] == "xyz", ik.get_list_of_all_incomes())
        self.assertEqual(len(xyz), 1)
        self.assertEqual(xyz[0]["state"], IncomesState.finished)
        self.assertEqual(xyz[0]["value"], 10)
        zyz = filter(lambda x: x["task"] == "zyz", ik.get_list_of_all_incomes())
        self.assertEqual(len(zyz), 1)
        self.assertEqual(zyz[0]["state"], IncomesState.finished)
        self.assertEqual(zyz[0]["value"], 100)
        ik.add_income("xyz", "DEF", 10)
        xyz = filter(lambda x: x["task"] == "xyz", ik.get_list_of_all_incomes())
        self.assertEqual(xyz[0]["state"], IncomesState.finished)
        self.assertEqual(xyz[0]["value"], 20)







