
from typing import List
import matplotlib.pyplot as plt
import pandas as pd

from data_loader import DataLoader
from model import Issue, Event

class Analysis2:
    """
    Analysis2 provides an overview of contributor activities across all issues, 
    highlighting top contributors based on the comments, labeling activities, and issues closed.
    """
    def run(self):
        """
        run() function is used to do the analysis from the list of issues.
        """
        # list of issues
        issues: List[Issue] = DataLoader().get_issues()
        
        # collecting the required data from the list of issuess based on the author and event type
        event_data = []
        for issue in issues:
            for event in issue.events:
                event_data.append({
                    'author': event.author,
                    'type': event.event_type
                })
        
        df_events = pd.DataFrame(event_data)
        
        if df_events.empty:
            print("No events found in the dataset.")
            return
        
        # Top 10 contributors by number of comments
        top_commenters = df_events[df_events['type'] == 'commented'].groupby('author').size().nlargest(10)
        print("\nTop 10 Contributors by Number of Comments:")
        print(top_commenters)
        
        # Top 10 contributors by labeling activities
        top_labelers = df_events[df_events['type'] == 'labeled'].groupby('author').size().nlargest(10)
        print("\nTop 10 Contributors by Labeling Activities:")
        print(top_labelers)
        
        # Top 10 contributors by issue closed
        top_closers = df_events[df_events['type'] == 'closed'].groupby('author').size().nlargest(10)
        print("\nTop 10 Contributors by Issue Closings:")
        print(top_closers)
        
        # Number of unique contributors involved
        unique_contributors_count = df_events['author'].nunique()
        print(f"\nTotal number of unique contributors: {unique_contributors_count}\n")
        
        # Plotting the charts
        plt.figure(figsize=(16, 10))
        
        # Top 10 commenters chart
        plt.subplot(3, 1, 1)
        top_commenters.plot(kind='bar', title='Top 10 Contributors by Comments')
        plt.xlabel('Contributors')
        plt.ylabel('Number of Comments')
        
        # Top 10 labelers chart
        plt.subplot(3, 1, 2)
        top_labelers.plot(kind='bar', title='Top 10 Contributors by Labeling Activities')
        plt.xlabel('Contributors')
        plt.ylabel('Number of Labeling Activities')
        
        # Top 10 issues closers chart
        plt.subplot(3, 1, 3)
        top_closers.plot(kind='bar', title='Top 10 Contributors by Issue Closed')
        plt.xlabel('Contributors')
        plt.ylabel('Number of Issue Closed')
        
        # saving the plot
        plt.tight_layout()
        # TO VIEW
        plt.show()
        # TO SAVE IN A FILE
        filename = "analysis_2.png"
        plt.savefig(filename)
        print(f"Contributor activity overview saved in: '{filename}'.")

if __name__ == '__main__':
    Analysis2().run()