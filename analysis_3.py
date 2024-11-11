
from typing import List
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime

from data_loader import DataLoader
from model import Issue,Event
import config

class Analysis3:
    """
    Implements an example analysis of GitHub
    issues and outputs the result of that analysis.
    """
    
    def __init__(self):
        """
        Constructor
        """
        # Parameter is passed in via command line (--user)
        self.USER:str = config.get_parameter('user')
    
    def run(self):
        """
        Starting point for this analysis.
        
        Note: this is just an example analysis. You should replace the code here
        with your own implementation and then implement two more such analyses.
        """
        issues:List[Issue] = DataLoader().get_issues()

        label_closure_times: dict[str, List[float]] = {}
        monthly_closure_times: dict[str, List[float]] = {}
        yearly_closure_times: dict[str, List[float]] = {}

        # Calculate average time it takes to close an issue 
        #   By month, year
        #   By label type
        for issue in issues:
            # Check if issue is closed
            is_closed = (issue.state == 'closed') 
            closed_date = None
            created_date = datetime.fromisoformat(str(issue.created_date)) 

            # Find closed event is exists
            for event in issue.events:
                if event.event_type == 'closed':
                    closed_date = datetime.fromisoformat(str(event.event_date)) 
                    is_closed = True 
                    break

            # Calculate closed time
            if is_closed and closed_date:
                open_duration = (closed_date - created_date).total_seconds() / 86400  # in days

                # Label Type Data Collection
                for label in issue.labels:
                    label_closure_times.setdefault(label, []).append(open_duration)
                    if label not in label_closure_times:
                        label_closure_times[label] = []
                    label_closure_times[label].append(open_duration)
                
                # Monthly + Yearly Data Collection
                month = closed_date.strftime('%m')
                monthly_closure_times.setdefault(month, []).append(open_duration)

                year = closed_date.strftime('%Y')
                yearly_closure_times.setdefault(year, []).append(open_duration)

                if month not in monthly_closure_times:
                    monthly_closure_times[month] = []
                monthly_closure_times[month].append(open_duration)                
                
                if year not in yearly_closure_times:
                    yearly_closure_times[year] = []
                yearly_closure_times[year].append(open_duration)
                
        # Print Results
        # Calculate and display average closure times per label type
        avg_closure_times_by_label = {label: np.mean(times) for label, times in label_closure_times.items()}
        print("\nAverage Closure Time by Label Type (in days):")
        for label, avg_time in avg_closure_times_by_label.items():
            print(f"{label}: {avg_time:.2f} days")

        # Calculate and display average monthly closure times
        avg_monthly_times = {month: np.mean(times) for month, times in monthly_closure_times.items()}
        print("\nAverage Monthly Closure Times (in days):")
        for month, avg_time in avg_monthly_times.items():
            print(f"{month}: {avg_time:.2f} days")

        # Calculate and display average yearly closure times
        avg_yearly_times = {year: np.mean(times) for year, times in yearly_closure_times.items()}
        print("\nAverage Yearly Closure Times (in days):")
        for year, avg_time in avg_yearly_times.items():
            print(f"{year}: {avg_time:.2f} days")

        self.plot_bar_chart(avg_closure_times_by_label, "Label Type", "Average Closure Time by Label Type", "closureTimeByLabel.png")
        self.plot_bar_chart(avg_monthly_times, "Month", "Average Monthly Closure Time", "closureTimeByMonth.png")
        self.plot_bar_chart(avg_yearly_times, "Year", "Average Yearly Closure Time", "closureTimeByYear.png")

    def plot_bar_chart(self, data: dict[str, float], xlabel: str, title: str, filename: str):
        labels = list(data.keys())
        avg_times = list(data.values())
        
        plt.figure(figsize=(10, 6))
        plt.bar(labels, avg_times, color='skyblue')
        plt.xlabel(xlabel)
        plt.ylabel("Average Closure Time (days)")
        plt.title(title)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(filename)
        plt.show() 

if __name__ == '__main__':
    # Invoke run method when running this module directly
    Analysis3().run()