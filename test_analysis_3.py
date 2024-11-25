import unittest
from unittest.mock import patch, MagicMock
from analysis_3 import Analysis3

class TestAnalysis3(unittest.TestCase):
    @patch('analysis_3.config.get_parameter', return_value='test_user')
    @patch('analysis_3.plt')
    @patch('analysis_3.DataLoader')
    def test_run_analysis_with_various_issues(self, mock_data_loader, mock_plt, mock_get_parameter):
        #Case: Closed issue with closed event

        issue_with_closed_event = MagicMock()
        issue_with_closed_event.state = 'open'
        issue_with_closed_event.created_date = '2023-01-01T00:00:00'
        event_closed = MagicMock()
        event_closed.event_type = 'closed'
        event_closed.event_date = '2023-01-02T00:00:00'
        issue_with_closed_event.events = [event_closed]
        issue_with_closed_event.labels = ['bug']

        #Case: Closed issue with no closed event
        issue_closed_no_event = MagicMock()
        issue_closed_no_event.state = 'closed'
        issue_closed_no_event.created_date = '2023-01-05T00:00:00'
        issue_closed_no_event.events = []
        issue_closed_no_event.labels = ['enhancement']

        #Case: Issue that is still open
        issue_open = MagicMock()
        issue_open.state = 'open'
        issue_open.created_date = '2023-01-10T00:00:00'
        issue_open.events = []
        issue_open.labels = []

        mock_data_loader.return_value.get_issues.return_value = [
            issue_with_closed_event,
            issue_closed_no_event,
            issue_open
        ]

        analysis = Analysis3()
        analysis.run()

        self.assertEqual(mock_plt.savefig.call_count, 3)
        self.assertEqual(mock_plt.show.call_count, 3)



if __name__ == '__main__':
    unittest.main()