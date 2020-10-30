import unittest
import constraint



"This is a file to unittest. Right now I just made a template"
class Test(unittest.TestCase):

    def test_findday(self,):
        "This will test if our day function returned the day"
        sample_date = "2020-04-26 13:02:30"
        day_name= constraint.findDay(sample_date)
        self.assertEqual(day_name,'Sunday')

    def test_combo_targetstation_targetmodule(self):
        "The Target Station / Target Module combination should alternate"
        schedule_path= "C:\\Users\\rajwi\\Documents\\Schedule 138 Ancestor.xlsx"
        schedule = constraint.read_file(schedule_path)
        is_valid, error_msg = constraint.check_constraints(schedule)
        self.assertTrue(is_valid)
        self.assertIsNone(error_msg)
        is_valid, error_msg = constraint.check_constraints(schedule)
        self.assertFalse(is_valid)
        self.assertEqual(error_msg, "This specific error message")


if __name__ == '__main__':
    unittest.main()
