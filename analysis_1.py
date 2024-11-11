from typing import List
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

from data_loader import DataLoader
from model import Issue
import config

class Analysis1:
    """
    Implements an input-based analysis of GitHub
    issues and outputs the result of that analysis based on the issue label.
    """
    
    def __init__(self):
        """
        Constructor
        """
        # Parameter is passed in via command line (--label)
        self.LABEL: str = config.get_parameter('label')
    
    def run(self):
        """
        Starting point for this analysis.
        
        This analysis focuses on analyzing issues based on a specific label.
        """
        # Load issues using DataLoader
        issues: List[Issue] = DataLoader().get_issues()
        
        # If no label is provided, ask user to choose from available labels
        if not self.LABEL:
            self.list_labels(issues)
            self.LABEL = input("Please enter a label from the above list: ").strip()
            if not self.LABEL:
                print("No label provided. Exiting analysis.")
                return
        
        # Filter issues by label
        filtered_issues = [issue for issue in issues if self.LABEL in issue.labels]
        
        if not filtered_issues:
            print(f"No issues found with the specified label: '{self.LABEL}'.")
            return
        
        ### BASIC STATISTICS
        num_issues = len(filtered_issues)
        total_comments = sum(len(issue.events) for issue in filtered_issues)
        avg_comments = total_comments / num_issues if num_issues > 0 else 0
        
        # Calculate average time to close
        creation_dates = pd.to_datetime([issue.created_date for issue in filtered_issues if issue.created_date])
        closing_dates = pd.to_datetime([issue.updated_date for issue in filtered_issues if issue.state == 'closed'])
        avg_time_to_close = (closing_dates - creation_dates[:len(closing_dates)]).mean() if len(closing_dates) > 0 else pd.NaT
        
        # Calculate time to first response
        first_response_times = []
        for issue in filtered_issues:
            if len(issue.events) > 0:
                first_response_time = pd.to_datetime(issue.events[0].event_date) - pd.to_datetime(issue.created_date)
                first_response_times.append(first_response_time)
        avg_first_response_time = pd.Series(first_response_times).mean() if len(first_response_times) > 0 else pd.NaT
        
        # Count open vs closed issues
        open_issues = len([issue for issue in filtered_issues if issue.state == 'open'])
        closed_issues = len([issue for issue in filtered_issues if issue.state == 'closed'])
        
        # List top contributors by number of comments
        contributor_comments = {}
        for issue in filtered_issues:
            for event in issue.events:
                if event.author not in contributor_comments:
                    contributor_comments[event.author] = 0
                contributor_comments[event.author] += 1
        top_contributors = sorted(contributor_comments.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Calculate average number of labels per issue
        avg_labels_per_issue = np.mean([len(issue.labels) for issue in filtered_issues]) if num_issues > 0 else 0
        
        # Calculate the proportion of issues with more than 5 comments
        issues_with_many_comments = len([issue for issue in filtered_issues if len(issue.events) > 5])
        proportion_many_comments = issues_with_many_comments / num_issues if num_issues > 0 else 0
        
        # Calculate average time between comments for each issue
        avg_time_between_comments = []
        for issue in filtered_issues:
            if len(issue.events) > 1:
                comment_times = pd.to_datetime([event.event_date for event in issue.events])
                time_diffs = comment_times[1:] - comment_times[:-1]
                avg_time_between_comments.append(time_diffs.mean())
        overall_avg_time_between_comments = pd.Series(avg_time_between_comments).mean() if len(avg_time_between_comments) > 0 else pd.NaT
        
        # Calculate median response time for issues with at least 5 comments
        median_response_times = []
        for issue in filtered_issues:
            if len(issue.events) >= 5:
                comment_times = pd.to_datetime([event.event_date for event in issue.events])
                time_diffs = comment_times[1:] - comment_times[:-1]
                median_response_times.append(time_diffs.median())
        overall_median_response_time = pd.Series(median_response_times).median() if len(median_response_times) > 0 else pd.NaT
        
        # Convert median response times to days for plotting
        median_response_times_days = [time_delta.days for time_delta in median_response_times if pd.notna(time_delta)]
        
        # Calculate frequency of issue updates after initial closing
        reopened_issues_count = len([issue for issue in filtered_issues if issue.state == 'closed' and len(issue.events) > 1])
        proportion_reopened_issues = reopened_issues_count / num_issues if num_issues > 0 else 0
        
        # Output statistics
        output = f"Total number of issues with label '{self.LABEL}': {num_issues}\n"
        output += f"Average number of comments per issue: {avg_comments:.2f}\n"
        output += f"Average time to close issues: {avg_time_to_close}\n"
        output += f"Average time to first response: {avg_first_response_time}\n"
        output += f"Number of open issues: {open_issues}\n"
        output += f"Number of closed issues: {closed_issues}\n"
        output += f"Average number of labels per issue: {avg_labels_per_issue:.2f}\n"
        output += f"Proportion of issues with more than 5 comments: {proportion_many_comments:.2f}\n"
        output += f"Average time between comments: {overall_avg_time_between_comments}\n"
        output += f"Median response time for issues with at least 5 comments: {overall_median_response_time}\n"
        output += f"Proportion of reopened issues: {proportion_reopened_issues:.2f}\n"
        output += "Top contributors by number of comments:\n"
        for contributor, count in top_contributors:
            output += f"  {contributor}: {count} comments\n"
        print('\n' + output + '\n')
        
        ### COMBINED BAR CHART
        # Plotting combined statistics for each issue
        issue_numbers = [issue.number for issue in filtered_issues]
        comments = [len(issue.events) for issue in filtered_issues]
        labels_per_issue = [len(issue.labels) for issue in filtered_issues]
        reopen_counts = [1 if issue.state == 'closed' and len(issue.events) > 1 else 0 for issue in filtered_issues]
        
        x = np.arange(len(issue_numbers))  # the label locations
        width = 0.25  # the width of the bars
        
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.bar(x - width, comments, width, label='Number of Comments', color='skyblue')
        ax.bar(x, labels_per_issue, width, label='Number of Labels', color='lightgreen')
        ax.bar(x + width, reopen_counts, width, label='Reopened Issues', color='orange')
        
        # Add labels, title, and legend
        ax.set_xlabel('Issue Number')
        ax.set_ylabel('Count')
        ax.set_title(f'Combined Statistics for Issues with Label "{self.LABEL}"')
        ax.set_xticks(x)
        ax.set_xticklabels(issue_numbers, rotation=90)
        ax.legend()
        plt.tight_layout()
        
        # Ensure output directory exists
        output_dir = os.path.join(os.getcwd(), 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the combined bar chart
        combined_plot_path = os.path.join(output_dir, 'combined_issue_statistics_plot.png')
        plt.savefig(combined_plot_path)
        print(f"Combined plot saved to {combined_plot_path}")
        plt.close()
        
        ### PIE CHART
        # Plotting open vs closed issues
        plt.figure(figsize=(8, 8))
        plt.pie([open_issues, closed_issues], labels=['Open', 'Closed'], autopct='%1.1f%%', startangle=90, colors=['lightcoral', 'lightskyblue'])
        plt.title(f'Proportion of Open vs Closed Issues with Label "{self.LABEL}"')
        plt.tight_layout()
        
        # Save the pie chart
        pie_chart_path = os.path.join(output_dir, 'open_vs_closed_issues_pie_chart.png')
        plt.savefig(pie_chart_path)
        print(f"Pie chart saved to {pie_chart_path}")
        plt.close()
        
        ### HISTOGRAM
        # Plotting median response time for issues with at least 5 comments
        if len(median_response_times_days) > 0:
            plt.figure(figsize=(10, 6))
            plt.hist(median_response_times_days, bins=10, color='green', alpha=0.7)
            plt.xlabel('Median Response Time (Days)')
            plt.ylabel('Frequency')
            plt.title(f'Median Response Time Distribution for Issues with Label "{self.LABEL}" and at Least 5 Comments')
            plt.tight_layout()
            
            # Save the histogram
            histogram_path = os.path.join(output_dir, 'median_response_time_histogram.png')
            plt.savefig(histogram_path)
            print(f"Histogram saved to {histogram_path}")
            plt.close()
        
        ### BAR CHART FOR REOPENED ISSUES
        # Plotting reopened issues proportion
        plt.figure(figsize=(8, 6))
        plt.bar(['Reopened Issues', 'Never Reopened'], [reopened_issues_count, num_issues - reopened_issues_count], color=['orange', 'lightblue'])
        plt.xlabel('Issue Status')
        plt.ylabel('Number of Issues')
        plt.title(f'Reopened vs Never Reopened Issues with Label "{self.LABEL}"')
        plt.tight_layout()
        
        # Save the bar chart for reopened issues
        reopened_issues_chart_path = os.path.join(output_dir, 'reopened_issues_bar_chart.png')
        plt.savefig(reopened_issues_chart_path)
        print(f"Bar chart for reopened issues saved to {reopened_issues_chart_path}")
        plt.close()
    
    def list_labels(self, issues: List[Issue]):
        """
        Lists all unique labels available in the issues dataset.
        """
        labels = set()
        for issue in issues:
            labels.update(issue.labels)
        print("Available labels:", labels)

if __name__ == '__main__':
    # Invoke run method when running this module directly
    Analysis1().run()
