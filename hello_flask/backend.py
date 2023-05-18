import boto3
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from io import BytesIO
import base64
import numpy as np

class AWS_Args:
    # Creates a class that will retain the arguments from the user's input
    def __init__(self, start_date, end_date, username, eventname):
        self.start_date = start_date
        self.end_date = end_date
        self.username = username
        self.eventname = eventname
        self.events = []

    # Creates a list of json elements that is filtered by the event the user wants to track
    def get_events(self):
        # set the aws application we are utilizing 
        client = boto3.client('cloudtrail')
        # use paginate on cloudtrail to grab the json event history
        paginator = client.get_paginator('lookup_events')
        response_iterator = paginator.paginate(
            LookupAttributes=[
                {
                    'AttributeKey': 'Username',
                    'AttributeValue': self.username
                }
            ],
            StartTime=self.start_date,
            EndTime=self.end_date
        )
        # Nested for loop that adds the requested events to the class's list 
        for page in response_iterator:
            for event in page['Events']:
                if event['EventName'] == self.eventname:
                    self.events.append(event)

    # Creates a dictionary where the keys are the event dates where the event appears
    # and the the key values are hits recording the frequency
    def count_events_by_date(self):
        event_count = {}
        for event in self.events:
            event_time = event['EventTime'].date().strftime('%Y-%m-%d')
            if event_time not in event_count:
                event_count[event_time] = 1
            else:
                event_count[event_time] += 1
        return event_count

    # Creates a graph using arguments generated in the backend through the user's input
    def plot_data(self):
        # Grabs the dictionary's keys and values to make the x-axis and its measures
        event_count = self.count_events_by_date()
        dates = list(event_count.keys())
        counts = list(event_count.values())
        fig, ax = plt.subplots(figsize=(12, 6))
        bar_width = 0.5
        bar_positions = np.arange(len(dates))
        
        # Customizes the graph's appearance
        ax.bar(bar_positions, counts, width=bar_width, color='#006699', alpha=0.7)
        ax.set_xlabel('Date', fontsize=14)
        ax.set_ylabel('Event Count', fontsize=14)
        ax.set_title(self.username + '\'s '+ 'Event Frequency by Date', fontsize=16)
        ax.set_xticks(bar_positions)
        ax.set_xticklabels(dates, rotation=45, ha='right', fontsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Saves the graph as a png file and encode it so it can be returned as an image
        fig.tight_layout()
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode('utf8')

        return graph_url