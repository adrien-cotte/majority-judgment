#!/bin/env python3

"""
Majority Judgment Bar Chart Distribution from CSV Data
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import argparse
from argparse import RawTextHelpFormatter
import re


# Supported values_type : 'int' or 'str'
def read_and_aggregate_csv(file_path, category_names, ignore_first_column,values_type="int"):
    df = pd.read_csv(file_path)
    # Deleting the first column of the csv if -I has been called
    if ignore_first_column == True:
        first_column = df.columns[0]
        df = df.drop([first_column], axis=1)
    max_count = len(category_names)

    if values_type == "int":
        # Function to check if a value is out of the desired range
        def is_out_of_range(x):
            return not (1 <= x <= max_count)

        # Check for any value out of range
        if df.map(is_out_of_range).any().any():
            print("Warning: There are values not between 1 and", max_count)

    elif values_type == "str":
        # Convert category names to a set for efficient lookup
        category_names_set = set(category_names)

        # Function to check if a value is out of the desired categories
        def is_out_of_category(x):
            return not (x in category_names_set)

        # Check for any value out of category
        if df.map(is_out_of_category).any().any():
            print("Warning: There are values not in", category_names)
    else:
        raise Exception(
            "values_type='" + values_type + "' is not supported, try 'int' or 'str'"
        )

    aggregated_results = {}
    for question in df.columns:
        # Adjust to map category names to their indices
        mapped_df = df[question].replace(
            {name: i + 1 for i, name in enumerate(category_names)}
        )
        counts = mapped_df.value_counts().sort_index()
        for rating in range(1, max_count + 1):
            if rating not in counts:
                counts[rating] = 0
        aggregated_results[question] = counts.sort_index().tolist()
    return aggregated_results


def survey(results, category_names, title, display_major=True, plot=True):
    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = plt.get_cmap("Spectral")(np.linspace(0.15, 0.85, data.shape[1]))

    fig, ax = plt.subplots(figsize=(9.2, 5))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        ax.barh(
            labels,
            widths,
            left=starts,
            height=0.5,
            label=colname,
            color=color,
            edgecolor="black",
            linewidth=0.1,
        )

        xcenters = starts + widths / 2

        for y, (x, c) in enumerate(zip(xcenters, widths)):
            if c > 0:
                ax.text(x, y, str(int(c)), ha="center", va="center", color="black")

    # Calculate and draw a line in the middle
    if display_major:
        medline_zorder = 0
        medline_linewidth = 1
        medline_linestyle = "dotted"
    else:
        medline_zorder = 1
        medline_linewidth = 1.5
        medline_linestyle = "-"

    for label in results.keys():
        total_responses = sum(results[label])
        median_response_count = total_responses / 2
        ax.axvline(
            x=median_response_count,
            color="black",
            linestyle=medline_linestyle,
            zorder=medline_zorder,
            linewidth=medline_linewidth,
        )

    # Create the legend
    handles = ax.get_legend_handles_labels()[0]
    if display_major:
        major_legend = mpatches.Patch(
            facecolor="none", label="Major", edgecolor="darkgrey", linewidth=2
        )
        handles.append(major_legend)
    plt.legend(
        handles=handles,
        ncol=len(category_names) + 1,
        bbox_to_anchor=(0.5, -0.025),
        loc="upper center",
        fontsize="small",
        edgecolor="darkgrey",
        facecolor="lightgrey",
    )

    # Calculate and highlight the winner for each question
    if display_major:
        for i, label in enumerate(labels):
            responses = np.array(results[label])
            cumulative_responses = np.cumsum(responses)
            total_responses = cumulative_responses[-1]
            median_index = np.where(cumulative_responses >= total_responses / 2)[0][0]

            # Highlighting the winning segment with a black border and no fill
            left_sum = np.sum(responses[:median_index])
            ax.barh(
                i,
                responses[median_index],
                left=left_sum,
                height=0.5,
                color="none",
                edgecolor="darkgrey",
                linewidth=5,
            )

    # Misc and plot
    ax.set_facecolor("lightgrey")
    plt.title(title, x=0.5, y=1.05, weight="bold")

    if plot:
        plt.show()
    else:
        if title == "":
            png_name = "plot.png"
        else:
            # Remove special chars for Windows files
            png_name = re.sub(r'\W', '_', title) + ".png"
        # Save the figure as a PNG file
        plt.savefig(png_name, dpi=300)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
Generate a Majority Judgment bar chart from CSV data.

Examples of CSV files formats:

    Q1,Q2,Q3    Q1,Q2,Q3
    3,3,3       C,C,C
    2,4,1       D,B,E
    5,5,1       A,A,E
    1,2,2       E,D,D

Examples of usages:
    ./majority_judgment.py -c resto.csv
    ./majority_judgment.py -c resto.csv -l fr -t 'Restaurants'
    ./majority_judgment.py -c resto.csv -C 'Too bad' 'Bad' 'Okay' 'Good' 'Very good'
    ./majority_judgment.py -c tier-list.csv -C B- B+ A- A+ S SS -T str -t 'Tier List'""",
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        "-c",
        "--csv",
        required=True,
        help="Path to the CSV file containing survey data.",
    )
    parser.add_argument(
        "-p",
        "--png",
        action='store_true',
        default=False,
        help="Write a PNG file instead of plotting results.",
    )
    parser.add_argument("-t", "--title", default="", help="Title of the chart.")
    parser.add_argument(
        "-l",
        "--lang",
        default="en",
        choices=["en", "fr"],
        help='Change the language. (default: "en")',
    )
    parser.add_argument(
        "-T",
        "--type",
        default="int",
        choices=["int", "str"],
        help='Change the type of the categories values. (default: "int")',
    )
    parser.add_argument(
        "-C",
        "--categories",
        help="""Override the categories list. (ascending order)""",
        nargs="*",
    )
    parser.add_argument(
        "-D",
        "--disable-major",
        help="""Remove major selection display.""",
        action='store_true',
        default=False
    )
    parser.add_argument(
        "-I",
        "--ignore-first-column",
        help="""Ignores the first column of the csv data.""",
        action='store_true',
        default=False
    )

    args = parser.parse_args()

    if args.lang == "en":
        category_names = [
            "Strongly disagree",
            "Disagree",
            "Neither agree nor disagree",
            "Agree",
            "Strongly agree",
        ]
    elif args.lang == "fr":
        category_names = [
            "Fort désaccord",
            "Désaccord",
            "Ni accord ni désaccord",
            "D'accord",
            "Fortement d'accord",
        ]

    if args.categories is not None:
        category_names = args.categories

    if args.png:
        plot = False
    else:
        plot = True

    results = read_and_aggregate_csv(args.csv, category_names, args.ignore_first_column, args.type)
    survey(results, category_names, args.title, not args.disable_major, plot)