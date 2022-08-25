#!/bin/env python3

from math import *
from statistics import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import colorConverter

category_names = ['Bad', 'Mediocre', 'Inadequate', 'Passable', 'Good', 'Very Good', 'Excellent']

#############################################
#			1	2	3	4	5	6	7	8	9
#
#Christophe	5	1	5	1	4	1	5	6	5
#Ambre		3	7	2	4	1	1	7	5	3
#Adrien		4	4	4	4	2	2	7	7	5
#Mathieu	2	5	1	4	1	3	7	5	3
#Pascal		3	7	1	7	3	7	6	6	6
#Guillaume	1	1	3	3	4	4	4	7	7
#Clément	2	1	1	1	1	1	5	5	3
#Lydéric	2	1	2	1	2	1	4	5	7
#
#############################################

results = {
    'Choix 1': [1, 3, 2, 1, 1, 0, 0],
    'Choix 2': [4, 0, 0, 1, 1, 0, 2],
    'Choix 3': [3, 2, 1, 1, 1, 0, 0],
    'Choix 4': [3, 0, 1, 3, 0, 0, 1],
    'Choix 5': [3, 2, 1, 2, 0, 0, 0],
    'Choix 6': [4, 1, 1, 1, 0, 0, 1],
    'Choix 7': [0, 0, 0, 2, 2, 1, 3],
    'Choix 8': [0, 0, 0, 0, 4, 2, 2],
    'Choix 9': [0, 0, 3, 0, 2, 1, 2],
}

def get_medians(results):
    medians = []
    for key, values in results.items():
        tmp = []
        grade = 0
        for v in values:
            grade += 1
            for i in range (0, v):
                tmp.append(grade)
        medians.append(median(map(float, tmp)))
    return medians

def get_means(results):
    means = []
    for key, values in results.items():
        tmp = []
        grade = 0
        for v in values:
            grade += 1
            for i in range (0, v):
                tmp.append(grade)
        means.append(mean(map(float, tmp)))
    return means

def get_colors():
    # (red, green, blue, alpha) 0 >= x <= 1
    # Example: red = (1.0, 0.0, 0.0, 0.75)
    grade_1 = colorConverter.to_rgb('darkred')
    grade_2 = colorConverter.to_rgb('tomato')
    grade_3 = colorConverter.to_rgb('orange')
    grade_4 = colorConverter.to_rgb('gold')
    grade_5 = colorConverter.to_rgb('lightgreen')
    grade_6 = colorConverter.to_rgb('mediumseagreen')
    grade_7 = colorConverter.to_rgb('darkgreen')
    alpha = (1.0,)
    colors = [grade_1, grade_2, grade_3, grade_4, grade_5, grade_6, grade_7]
    return [ c + alpha for c in colors ]

def survey(results, category_names):
    """
    Parameters
    ----------
    results : dict
        A mapping from question labels to a list of answers per category.
        It is assumed all lists contain the same number of entries and that
        it matches the length of *category_names*.
    category_names : list of str
        The category labels.
    """
    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = get_colors()

    fig, ax = plt.subplots(figsize=(9.2, 5))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        rects = ax.barh(labels, widths, left=starts, height=0.5,
                        label=colname, color=color)
        r, g, b, _ = color
        color_text = 'white' if colname == 'Bad' or colname == 'Excellent' else 'black'
        ax.bar_label(rects, label_type='center', color=color_text)

    ax.legend(ncol=len(category_names), bbox_to_anchor=(0.5, -0.02),
              loc='upper center', fontsize='medium')
    median_line = sum(results.get(next(iter(results)))) / 2
    plt.axvline(x=median_line, color='grey', linestyle='dotted')
    plt.title("Majority Judgment", y=1.02)

    return fig, ax

# Print results and winners
i = 0
medians = get_medians(results)
means = get_means(results)
for k, v in results.items():
    maj = floor(medians[i])
    cat = category_names[maj - 1]
    print(k, ":")
    print("    Majority:", cat, "(" + str(category_names.index(cat) + 1) + "/7)")
    print("    Median:", medians[i])
    print("    Floor:", floor(medians[i]))
    print("    Ceil:", ceil(medians[i]))
    print("    Mean:", means[i])
    i += 1

# Display graphics
survey(results, category_names)
plt.show()
