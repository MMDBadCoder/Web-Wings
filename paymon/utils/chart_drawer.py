from datetime import datetime
from typing import List, Optional
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from models import DataPoint


# Function to generate the multi-line cumulative chart
def generate_multi_cumulative_chart(data_lists: List[List[DataPoint]],
                                    output_file: str,
                                    titles: Optional[List[str]] = None,
                                    colors: Optional[List[str]] = None):
    # Create a new figure for the plot
    plt.figure(figsize=(10, 6))

    # Iterate over each data list and plot them
    for i, data in enumerate(data_lists):
        # Sort the data by timestamp
        sorted_data = sorted(data, key=lambda x: x.timestamp)

        # Extract timestamps and values
        timestamps = [datetime.fromtimestamp(point.timestamp) for point in sorted_data]
        values = [point.value for point in sorted_data]

        # Calculate cumulative sum of values
        cumulative_values = []
        cumulative_sum = 0
        for value in values:
            cumulative_sum += value
            cumulative_values.append(cumulative_sum)

        # Set the title and color for the current line
        line_title = titles[i] if titles and i < len(titles) else f'Line {i + 1}'
        line_color = colors[i] if colors and i < len(colors) else None

        # Plot the current line
        plt.plot(timestamps, cumulative_values, marker='o', linestyle='-', linewidth=2, markersize=6,
                 label=line_title, color=line_color)

    # Add legend to differentiate between the lines
    plt.legend(loc='upper left', fontsize=10)

    # Beautify the plot
    plt.title('Cumulative Value Over Time', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Cumulative Value', fontsize=14)  # General label for cumulative value
    plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

    # Format the x-axis to show human-readable dates
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator())
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=30))  # Limiting to 30 ticks

    # Rotate date labels on x-axis for better readability
    plt.gcf().autofmt_xdate()

    # Save the chart as an image file
    plt.savefig(output_file, dpi=300, bbox_inches='tight')

    # Show the plot
    plt.show()
