import unittest
import importlib
from io import StringIO
from unittest.mock import patch, MagicMock
from analysis_1 import Analysis1

class TestAnalysis1(unittest.TestCase):
    @patch('analysis_1.DataLoader')
    @patch('analysis_1.config')
    @patch('matplotlib.pyplot.show')
    def test_run_with_valid_data(self, mock_show, mock_config, mock_data_loader):
        """Test the main run functionality with valid data."""
        mock_config.get_parameter.return_value = 'bug'

        mock_issues = [
            MagicMock(
                state='closed',
                created_date='2023-11-01T00:00:00',
                updated_date='2023-11-03T00:00:00',
                labels=['bug', 'critical'],
                events=[
                    MagicMock(event_date='2023-11-01T12:00:00', author='user1'),
                    MagicMock(event_date='2023-11-02T12:00:00', author='user2'),
                ],
                number=1
            ),
            MagicMock(
                state='open',
                created_date='2023-11-05T00:00:00',
                updated_date=None,
                labels=['bug'],
                events=[
                    MagicMock(event_date='2023-11-05T08:00:00', author='user3'),
                ],
                number=2
            ),
            MagicMock(
                state='open',
                created_date='2023-11-05T00:00:00',
                updated_date=None,
                labels=['ux'],
                events=[
                    MagicMock(event_date='2023-11-05T08:00:00', author='user3'),
                ],
                number=3
            )
        ]
        mock_data_loader.return_value.get_issues.return_value = mock_issues

        analysis = Analysis1()
        analysis.run()

        filtered_issues = [issue for issue in mock_issues if 'bug' in issue.labels]
        self.assertEqual(len(filtered_issues), 2)

    @patch('builtins.print')
    def test_list_labels(self, mock_print):
        """Test list_labels method."""
        mock_issues = [
            MagicMock(labels=['bug', 'enhancement']),
            MagicMock(labels=['feature']),
            MagicMock(labels=['feature']),
            MagicMock(labels=['bug']),
            MagicMock(labels=['other'])
        ]

        analysis = Analysis1()
        analysis.list_labels(mock_issues)

        # Ensure the print statement matches exactly
        mock_print.assert_called_with("Available labels:", {'bug', 'enhancement', 'feature', 'other'})

    @patch('analysis_1.DataLoader')
    @patch('analysis_1.config')
    def test_run_all_issues_filtered(self, mock_config, mock_data_loader):
        """Test run method when no issues match the label."""
        mock_config.get_parameter.return_value = 'bug'
        mock_data_loader.return_value.get_issues.return_value = [
            MagicMock(labels=['feature']),  # No 'bug' label
            MagicMock(labels=['enhancement'])
        ]

        analysis = Analysis1()
        with patch('builtins.print') as mock_print:
            analysis.run()
            mock_print.assert_called_with("No issues found with the specified label: 'bug'.")

    @patch('analysis_1.DataLoader')
    @patch('analysis_1.config')
    def test_run_no_issues(self, mock_config, mock_data_loader):
        """Test run method with an empty issues list."""
        mock_config.get_parameter.return_value = 'bug'
        mock_data_loader.return_value.get_issues.return_value = []

        analysis = Analysis1()
        with patch('builtins.print') as mock_print:
            analysis.run()
            mock_print.assert_any_call("No issues found with the specified label: 'bug'.")

    @patch('matplotlib.pyplot.savefig', side_effect=Exception("Save Error"))
    @patch('analysis_1.DataLoader')
    @patch('analysis_1.config')
    def test_run_plot_save_error(self, mock_config, mock_data_loader, mock_savefig):
        """Test run method when saving plots fails."""
        mock_config.get_parameter.return_value = 'bug'
        mock_data_loader.return_value.get_issues.return_value = [
            MagicMock(
                state='closed',
                created_date='2023-11-01T00:00:00',
                updated_date='2023-11-03T00:00:00',
                labels=['bug'],
                events=[]
            )
        ]

        analysis = Analysis1()
        with patch('builtins.print') as mock_print:
            analysis.run()
            mock_print.assert_any_call("Error saving plot files.")

    @patch('matplotlib.pyplot.show')
    @patch('analysis_1.config')
    @patch('analysis_1.DataLoader')  # Mock DataLoader to control the issues data
    @patch('sys.stdout', new_callable=StringIO)
    def test_output_statistics(self, mock_stdout,mock_data_loader, mock_config, mock_show):
        """Test the output statistics printed by the run method."""
        mock_config.get_parameter.return_value = 'bug'
        # Mock the data loader to return mock issues
        mock_issues = [
            MagicMock(
                labels=['bug', 'critical'],
                created_date='2023-11-01T00:00:00',
                updated_date='2023-11-03T00:00:00',
                state='closed',
                events=[MagicMock(event_date='2023-11-01T12:00:00', author='user1')]
            )
        ]
        
        # Mock the return value of the DataLoader's get_issues method
        mock_data_loader.return_value.get_issues.return_value = mock_issues

        # Create the analysis object
        analysis = Analysis1()

        # Run the analysis
        analysis.run()
        output = mock_stdout.getvalue()

        # The expected statistics output (based on the mock data above)
        expected_output = (
            f"Total number of issues with label 'bug': 1\n"
            f"Average number of comments per issue: 1.00\n"
            f"Average time to close issues: 2 days 00:00:00\n"
            f"Average time to first response: 0 days 12:00:00\n"
            f"Number of open issues: 0\n"
            f"Number of closed issues: 1\n"
            f"Average number of labels per issue: 2.00\n"
            f"Proportion of issues with more than 5 comments: 0.00\n"
            f"Average time between comments: NaT\n"
            f"Median response time for issues with at least 5 comments: NaT\n"
            f"Proportion of reopened issues: 0.00\n"
            f"Top contributors by number of comments:\n"
            f"  user1: 1 comments\n"
        )

        self.assertIn(expected_output, output)

    @patch('analysis_1.DataLoader')
    @patch('analysis_1.config')
    @patch.object(Analysis1,'list_labels')
    @patch('builtins.print')
    @patch('builtins.input')
    def test_no_label_provided(self, mock_input,mock_print, mock_list_labels, mock_config, mock_data_loader):
        mock_config.get_parameter.return_value = ''

        mock_issues = [
            MagicMock(
                state='closed',
                created_date='2023-11-01T00:00:00',
                updated_date='2023-11-03T00:00:00',
                labels=['bug', 'critical'],
                events=[
                    MagicMock(event_date='2023-11-01T12:00:00', author='user1'),
                    MagicMock(event_date='2023-11-02T12:00:00', author='user2'),
                ],
                number=1
            )
        ]
        mock_data_loader.return_value.get_issues.return_value = mock_issues
        mock_input.return_value=""

        analysis = Analysis1()
        analysis.run()
        mock_list_labels.assert_called_once()
        mock_print.assert_called_with("No label provided. Exiting analysis.")
       
    @patch('analysis_1.DataLoader')
    @patch('analysis_1.config')
    @patch('matplotlib.pyplot.show')
    @patch('sys.stdout', new_callable=StringIO)
    def test_median_response_times(self, mock_stdout,mock_show, mock_config, mock_data_loader):
        mock_config.get_parameter.return_value = 'bug'

        mock_issues = [
            MagicMock(
                state='closed',
                created_date='2023-11-01T00:00:00',
                updated_date='2023-11-03T00:00:00',
                labels=['bug', 'critical'],
                events=[
                    MagicMock(event_date='2023-11-01T12:00:00', author='user1'),
                    MagicMock(event_date='2023-11-02T12:00:00', author='user2'),
                    MagicMock(event_date='2023-11-03T12:00:00', author='user2'),
                    MagicMock(event_date='2023-11-04T12:00:00', author='user2'),
                    MagicMock(event_date='2023-11-05T12:00:00', author='user2'),
                ],
                number=1
            ),
            MagicMock(
                state='open',
                created_date='2023-11-05T00:00:00',
                updated_date=None,
                labels=['bug'],
                events=[
                    MagicMock(event_date='2023-11-05T08:00:00', author='user3'),
                ],
                number=2
            ),
            MagicMock(
                state='open',
                created_date='2023-11-05T00:00:00',
                updated_date=None,
                labels=['ux'],
                events=[
                    MagicMock(event_date='2023-11-05T08:00:00', author='user3'),
                ],
                number=3
            )
        ]
        mock_data_loader.return_value.get_issues.return_value = mock_issues

        analysis = Analysis1()
        analysis.run()
        output = mock_stdout.getvalue()
        self.assertIn("Median response time for issues with at least 5 comments: 1 days 00:00:00", output)
        
        

if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)
