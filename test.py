import unittest
import constraint
import FileManager





"This is a file to unittest. Right now I just made a template"
class Test(unittest.TestCase):

    def test_findday(self,):
        "This will test if our day function returned the day"
        sample_date = "2020-04-26 16:08:08"
        day_name= constraint.findDay(sample_date)
        self.assertEqual(day_name,'Sunday')

    def test_read_file(self,):
        "This will tets if my file returned is excel"
        path = "C:\\Users\\rajwi\\Documents\\Schedule 138 Ancestor.xlsx"
        file = constraint.read_file(path)
        self.assertIsNotNone(file)


    def test_target_block_set(self,):
        path = "C:\\Users\\rajwi\\Documents\\Schedule 138 Ancestor.xlsx"
        file = constraint.read_file(path)
        self.assertIsNotNone(file)
        target_block_set= constraint.get_target_block_set(file)
        self.assertIsInstance(target_block_set, tuple)

    def test_get_ts_tm_combo(self,):
        path = "C:\\Users\\rajwi\\Documents\\Schedule 138 Ancestor.xlsx"
        file = constraint.read_file(path)
        self.assertIsNotNone(file)
        combo_list_2=constraint.get_ts_tm_combo(file)
        self.assertIsInstance(combo_list_2, tuple)

    def test_check_schedule_start_time(self, ):
        "Checks rule #4 Target blocks start and end on a Tuesday DAY shift"
        path = "C:\\Users\\rajwi\\Documents\\Schedule 138 Ancestor.xlsx"
        schedule = constraint.read_file(path)
        valid_schedule = constraint.check_tb_start_time(schedule)
        self.assertTrue(valid_schedule)

    def test_check_integer_weeks(self,):
        "Checks rule #4 Target blocks start and end on a Tuesday DAY shift"
        path = "C:\\Users\\rajwi\\Documents\\Schedule 138 Ancestor.xlsx"
        schedule = constraint.read_file(path)
        valid_schedule = constraint.check_integer_weeks(schedule)
        self.assertIsNotNone(valid_schedule)

    






if __name__ == '__main__':
    unittest.main()
