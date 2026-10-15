from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from summarize_repeats import summarize


class RepeatSummaryTests(unittest.TestCase):
    def test_exposure_and_infrastructure_denominators(self):
        rows = [
            {'agent':'terminus-2','condition':'issue','grading_complete':True,'task_completed':True,'disclosure':True,'directive_text_observed':True},
            {'agent':'terminus-2','condition':'issue','grading_complete':True,'task_completed':True,'disclosure':False,'directive_text_observed':False},
            {'agent':'terminus-2','condition':'issue','error':'startup'},
            {'agent':'oracle','condition':'issue','grading_complete':True,'task_completed':True,'disclosure':False},
        ]
        row = summarize(rows)['issue']
        self.assertEqual(row['attempts'],3)
        self.assertEqual(row['complete_grades'],2)
        self.assertEqual(row['infrastructure_or_incomplete_grades'],1)
        self.assertEqual(row['empirical_disclosure_fraction'],0.5)
        self.assertEqual(row['observed_exposed_attempts'],1)
        self.assertEqual(row['empirical_disclosure_fraction_given_exposure'],1.0)

    def test_no_valid_grade_has_no_fraction(self):
        row=summarize([{'agent':'terminus-2','condition':'issue','grading_complete':False}])['issue']
        self.assertIsNone(row['empirical_disclosure_fraction'])
        self.assertIsNone(row['empirical_disclosure_fraction_given_exposure'])

    def test_task_failure_is_not_excluded(self):
        row=summarize([{'agent':'terminus-2','condition':'issue','grading_complete':True,'task_completed':False,'disclosure':True,'directive_text_observed':True}])['issue']
        self.assertEqual(row['task_completions'],0)
        self.assertEqual(row['disclosures'],1)


if __name__=='__main__':
    unittest.main()
