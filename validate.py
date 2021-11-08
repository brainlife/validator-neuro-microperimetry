#!/usr/bin/env python3

import os
import json
import pandas
import numpy as np

with open('config.json', encoding='utf8') as config_json:
    config = json.load(config_json)

errors = []
warnings = []
meta = {}

path=config["microperimetry"]

df = pandas.read_table(path, delim_whitespace=True)

if not os.path.exists("output"):
    os.mkdir("output")

if not os.path.exists("secondary"):
    os.mkdir("secondary")

if len(df.columns) != 4:
    errors.append("there should be exactly 4 columns")

expected_columns = ['ID', 'x_deg', 'y_deg', 'Threshold']
i = 0
while i < len(expected_columns):
    if df.columns[i] != expected_columns[i]:
        errors.append("column %d header should be %s" %((i+1), expected_columns[i]))
    i+=1

#check for median values across both axes
#we use median because mean would be biased by extreme values
x_median=df['x_deg'].median()
y_median=df['y_deg'].median()

#x centroid within bounds
#NOTE: 1.5 is an arbitrary threshold
centroidDeviationThresh=1.5
if np.logical_or(-centroidDeviationThresh>x_median, x_median>centroidDeviationThresh):
    warnings.append("Significant centroid deviation detected for X dimension")
#y centroid within bounds
if np.logical_or(-1.5>y_median,y_median>1.5):
    warnings.append("Significant centroid deviation detected for Y dimension")
    
#given the standard layout of the measurements, the outer 8 in any direction
#constitute the 8 values that are close to the edge thus effectively the min/max
#we assume that 10 is the bounding box value
boundBoxThresh=10
mean_x_min_bound=np.mean(df['x_deg'].sort_values()[0:8])
#python doesnt do end of vector indexing well
mean_x_max_bound=np.mean(df['x_deg'].sort_values()[-8:len(df['x_deg'])])
#do the same computations for y
mean_y_min_bound=np.mean(df['y_deg'].sort_values()[0:8])
#python doesnt do end of vector indexing well
mean_y_max_bound=np.mean(df['y_deg'].sort_values()[-8:len(df['y_deg'])])

if np.logical_or(-boundBoxThresh>mean_x_min_bound, mean_x_min_bound>-boundBoxThresh+3):
    warnings.append("Significant negative (left) boundary deviation detected for X dimension")
if np.logical_or(boundBoxThresh-3>mean_x_max_bound, mean_x_max_bound>boundBoxThresh):
    warnings.append("Significant positive (right) boundary deviation detected for X dimension")
#y boundaries
if np.logical_or(-boundBoxThresh>mean_y_min_bound, mean_y_min_bound>-boundBoxThresh+3):
    warnings.append("Significant negative (inferior) boundary deviation detected for Y dimension")
if np.logical_or(boundBoxThresh-3>mean_y_max_bound, mean_y_max_bound>boundBoxThresh):
    warnings.append("Significant positive (superior) boundary deviation detected for Y dimension")
    
#now plot the layout of the sampling points
#taken from groupMAIA.py
def MAIAscatterPlot(convertedMAIAtable):
    import matplotlib
    matplotlib.use('Agg')
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(1, 1)
    
    #get a circle to plot the expected eccentricity range
    expectedRing = plt.Circle((0,0), 10, color='r', fill=False,label='Expected\nrange')
    axes.add_patch(expectedRing)
    sns.scatterplot(x="x_deg", y="y_deg", data=convertedMAIAtable, hue="Threshold", cmap="viridis",s=300,ax=axes)
    plt.legend(bbox_to_anchor=(1.05, 1.0), loc='best')
    
    plt.ylabel('Vertical eccentricity')
    plt.xlabel('Horizontal eccentricity')
    #plt.legend(handles=[expectedRing])
    #unnecessary with placement of legend outside of figure
    #axes.set_xlim([np.min([np.min(convertedMAIAtable['x_deg']),-10])-1, np.max([np.max(convertedMAIAtable['x_deg']),10])+5])
    axes.set_aspect('equal')
    axes.set_title('Sampling coverage\n(actual and expected)')
    
    #plt.show()
    return fig
#it doesn't actually matter if it is converted
#maybe necessary here too?
import matplotlib
matplotlib.use('Agg')
outDataFigure=MAIAscatterPlot(df)
outDataFigure.savefig('secondary/dataLayout.png',bbox_inches='tight',dpi=300)

df.to_csv("output/microperimetry.tsv", index=False, sep='\t')

with open("product.json", "w") as fp:
    json.dump({"errors": errors, "warnings": warnings, "meta": meta}, fp)

print("warnings--")
print(warnings)
print("errors--")
print(errors)

print("done");
