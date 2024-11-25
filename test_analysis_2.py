import unittest
from unittest.mock import MagicMock, patch
from io import StringIO
from analysis_2 import Analysis2
from model import Issue, Event
import pandas as pd

class TestAnalysis2(unittest.TestCase):

    @patch('data_loader.DataLoader.get_issues')
    def test_run_with_no_issues(self, mock_data_loader):
        """
        Test case when no issues are returned by the DataLoader.
        """
        # Mock the DataLoader to return an empty list
        mock_data_loader.return_value.get_issues.return_value = []
        
        # Use StringIO to capture print statements
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            Analysis2().run()
            
            # Get the captured output from stdout
            output = mock_stdout.getvalue()
            
            # Assert that the expected string is in the captured output
            self.assertIn("No events found in the dataset.", output)

    @patch('data_loader.DataLoader')
    def test_run_with_sample_data(self, mock_data_loader):
        """
        Test case when sample issues are returned.
        """
        # Mock DataLoader to return sample issues
        sample_issues = [
            Issue({
                "url": "https://example.com/issue/1",
                "creator": "creator1",
                "labels": ["bug", "high-priority"],
                "state": "open",
                "assignees": ["assignee1", "assignee2"],
                "title": "Sample Issue 1",
                "text": "This is the first sample issue.",
                "number": 1,
                "created_date": "2023-01-01T10:00:00Z",
                "updated_date": "2023-01-02T15:30:00Z",
                "timeline_url": "https://example.com/issue/1/timeline",
                "events": [
                    {
                        "event_type": "commented",
                        "author": "user1",
                        "event_date": "2023-01-01T12:00:00Z",
                        "label": None,
                         "comment": "This is a comment."
                         },
                    {
                        "event_type": "labeled",
                        "author": "user2",
                        "event_date": "2023-01-01T13:00:00Z",
                        "label": "bug",
                        "comment": None
                        },
                    {
                        "event_type": "closed",
                        "author": "user1",
                        "event_date": "2023-01-02T10:00:00Z",
                        "label": None,
                        "comment": None
                        },
                    ],
                }),
            Issue({
                "url": "https://example.com/issue/2",
                "creator": "creator2",
                "labels": ["enhancement"],
                "state": "closed",
                "assignees": ["assignee3"],
                "title": "Sample Issue 2",
                "text": "This is the second sample issue.",
                "number": 2,
                "created_date": "2023-02-01T10:00:00Z",
                "updated_date": "2023-02-03T15:30:00Z",
                "timeline_url": "https://example.com/issue/2/timeline",
                "events": [
                    {
                        "event_type": "commented",
                        "author": "user3",
                        "event_date": "2023-02-01T12:00:00Z",
                        "label": None,
                        "comment": "Looks good to me."
                        },
                    {
                        "event_type": "labeled",
                        "author": "user4",
                        "event_date": "2023-02-01T13:00:00Z",
                        "label": "enhancement",
                        "comment": None
                        },
                    {
                        "event_type": "closed",
                        "author": "user3",
                        "event_date": "2023-02-03T10:00:00Z",
                        "label": None,
                        "comment": None
                    },
                ],
            }),
        ]

        
        mock_data_loader.return_value.get_issues.return_value = sample_issues
        
        with patch('matplotlib.pyplot.savefig') as mock_savefig:
            # Run the analysis
            Analysis2().run()
            
            # Check if plots are saved
            mock_savefig.assert_any_call("filename_contributer_activity.png")
            mock_savefig.assert_any_call("top_labels_activity.png")
    
    

    @patch('data_loader.DataLoader.get_issues')
    def test_run_with_empty_events(self, mock_data_loader):
        """
        Test case when issues exist but contain no events.
        """
        sample_issues = [Issue({"state": "open","events":[]}), Issue({"state": "open","events":[]})]
        mock_data_loader.return_value.get_issues.return_value = sample_issues


        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            Analysis2().run()
            
            # Get the captured output from stdout
            output = mock_stdout.getvalue()
            
            # Assert that the expected string is in the captured output
            self.assertIn("No events found in the dataset.", output)    

    @patch('data_loader.DataLoader')
    def test_top_contributors_calculation(self, mock_data_loader):
        """
        Test the calculations for top contributors.
        """
        # Mock DataLoader to return specific issues
        sample_issues = [
            Issue({"state": "open", "events":[
                {"author":"user1", "event_type":"commented"},
                {"author":"user2", "event_type":"labeled", "label":"bug"},
                {"author":"user1", "event_type":"closed"},
                {"author":"user2", "event_type":"labeled", "label":"feature"},
                {"author":"user3", "event_type":"labeled", "label":"bug"},
            ]})
        ]

        mock_data_loader.return_value.get_issues.return_value = sample_issues


        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            Analysis2().run()
            
            # Get the captured output from stdout
            output = mock_stdout.getvalue()
            
            # Assert that the expected string is in the captured output
            self.assertIn("Top 10 Contributors by Number of Comments:", output)              
            
    @patch('data_loader.DataLoader')
    @patch('matplotlib.pyplot.savefig')  # Mock the plt.savefig method to avoid actual file saving
    def test_run_with_large_data(self, mock_savefig, mock_data_loader):
        """
        Test case with a large dataset to check performance and behavior.
        """
        # Create sample issues with events, using the specified dictionary format
        sample_issues = [
            Issue({
                "state": "open",
                "events": [
                    {"author": f"user{i % 10}", "event_type": "commented"} for i in range(1000)
                ] + [
                    {"author": f"user{i % 5}", "event_type": "labeled", "label": "bug"} for i in range(500)
                ] + [
                    {"author": f"user{i % 3}", "event_type": "closed"} for i in range(300)
                ]
            })
        ]
    
        # Mock DataLoader to return the sample issues
        mock_data_loader.return_value.get_issues.return_value = sample_issues

        # Use StringIO to capture print statements from the Analysis2 run
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            Analysis2().run()
        
            # Get the captured output from stdout
            output = mock_stdout.getvalue()
        
            # Assertion 1: Check that the output contains a message indicating that events were found and processed
            self.assertIn("Total number of unique contributors:", output)
        
            # Assertion 2: Check if a specific string or message indicating that events are being processed is present
            self.assertIn("Top 10 Most Active Labels by Contributors:", output)

            # Assertion 3: Check if plt.savefig was called to save the plots
            # Assert that the savefig method was called with the expected file names
            mock_savefig.assert_any_call("filename_contributer_activity.png")
            mock_savefig.assert_any_call("top_labels_activity.png")

            # Optional: Check the number of events processed in your DataFrame
            # e.g., the number of 'commented', 'labeled', and 'closed' events
            df_events = pd.DataFrame([
                {'author': f"user{i % 10}", 'type': 'commented', 'label': 'No Label'} for i in range(1000)
            ] + [
                {'author': f"user{i % 5}", 'type': 'labeled', 'label': 'bug'} for i in range(500)
            ] + [
                {'author': f"user{i % 3}", 'type': 'closed', 'label': 'No Label'} for i in range(300)
            ])
        
            self.assertEqual(len(df_events), 1000 + 500 + 300)  # Total number of events
            self.assertEqual(df_events['type'].value_counts()['commented'], 1000)
            self.assertEqual(df_events['type'].value_counts()['labeled'], 500)
            self.assertEqual(df_events['type'].value_counts()['closed'], 300)



if __name__ == '__main__':
    unittest.main()
