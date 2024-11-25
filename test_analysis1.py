import unittest
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
            MagicMock(labels=['feature'])
        ]

        analysis = Analysis1()
        analysis.list_labels(mock_issues)

        # Ensure the print statement matches exactly
        mock_print.assert_called_with("Available labels:", {'bug', 'enhancement', 'feature'})

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


    @patch('analysis_1.Analysis1.run')
    def test_main_block(self, mock_run):
        """Test the __main__ block."""
        import analysis_1  # Import the module
        with patch('analysis_1.__name__', '__main__'):  # Simulate main block execution
            importlib.reload(analysis_1)  # Reload the module to execute the __main__ block
            mock_run.assert_called_once()  # Verify that run was called once


    @patch('analysis_1.DataLoader')
    @patch('analysis_1.config')
    def test_run_statistics(self, mock_config, mock_data_loader):
        """Test statistical output in run method."""
        mock_config.get_parameter.return_value = 'bug'
        mock_issues = [
            MagicMock(
                state='closed',
                created_date='2023-11-01T00:00:00',
                updated_date='2023-11-03T00:00:00',
                labels=['bug'],
                events=[
                    MagicMock(event_date='2023-11-01T12:00:00', author='user1')
                ]
            )
        ]
        mock_data_loader.return_value.get_issues.return_value = mock_issues

        analysis = Analysis1()
        with patch('builtins.print') as mock_print:
            analysis.run()
            mock_print.assert_any_call("Total number of issues with label 'bug': 1")
            mock_print.assert_any_call("Average time to close issues: 2 days 00:00:00")

if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)
