#!/bin/env python3

"""
Horizontal Bar Chart Distribution from CSV Data
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import argparse


def read_and_aggregate_csv(file_path):
    df = pd.read_csv(file_path)
    aggregated_results = {}
    for question in df.columns:
        counts = df[question].value_counts().sort_index()
        for rating in range(1, 6):
            if rating not in counts:
                counts[rating] = 0
        aggregated_results[question] = counts.sort_index().tolist()
    return aggregated_results


def survey(results, category_names, title):
    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = plt.get_cmap('Spectral')(np.linspace(0.15, 0.85, data.shape[1]))

    fig, ax = plt.subplots(figsize=(9.2, 5))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        ax.barh(labels, widths, left=starts, height=0.5, label=colname, color=color, edgecolor='black', linewidth=0.1)

        xcenters = starts + widths / 2

        for y, (x, c) in enumerate(zip(xcenters, widths)):
            if c > 0:
                ax.text(x, y, str(int(c)), ha='center', va='center', color='black')

    # Calculate and draw a line in the middle
    for label in results.keys():
        total_responses = sum(results[label])
        median_response_count = total_responses / 2
        ax.axvline(x=median_response_count, color='black', linestyle='dotted', zorder=0, linewidth=1)

    # Create the legend
    major_legend = mpatches.Patch(facecolor='none', label='Major', edgecolor='darkgrey', linewidth=2)
    handles = ax.get_legend_handles_labels()[0]
    handles.append(major_legend)
    plt.legend(handles=handles,
               ncol=len(category_names) + 1, bbox_to_anchor=(0.5, -0.025), loc='upper center', fontsize='small',
               edgecolor='darkgrey', facecolor='lightgrey')

    # Calculate and highlight the winner for each question
    for i, label in enumerate(labels):
        responses = np.array(results[label])
        cumulative_responses = np.cumsum(responses)
        total_responses = cumulative_responses[-1]
        median_index = np.where(cumulative_responses >= total_responses / 2)[0][0]

        # Highlighting the winning segment with a black border and no fill
        left_sum = np.sum(responses[:median_index])
        ax.barh(i, responses[median_index], left=left_sum, height=0.5, color="none", edgecolor='darkgrey', linewidth=5)

    # Misc and plot
    ax.set_facecolor("lightgrey")
    plt.title(title, x=0.5, y=1.05, weight='bold')
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a horizontal bar chart from CSV data.')
    parser.add_argument('--csv', required=True, help='Path to the CSV file containing survey data.')
    args = parser.add_argument('-t', '--title', default='Survey Results', help='Title of the chart')

    args = parser.parse_args()

    category_names = ['Strongly disagree', 'Disagree', 'Neither agree nor disagree', 'Agree', 'Strongly agree']
    results = read_and_aggregate_csv(args.csv)
    survey(results, category_names, args.title)
