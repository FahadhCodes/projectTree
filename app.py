from flask import Flask, render_template
import pandas as pd
import numpy as np
import re
import json

Df = pd.read_csv('dataset1.csv')
targetColumn = 'Attend?'


def tree(targetColumn, dataset):
    attributes = []
    S = 0
    tree = {}
    counts = {}
    entrophy = {}
    weighted_avg = {}
    gain = {}
    for c in dataset.columns:
        if c != targetColumn:
            attributes.append(c)
    # Boolean Array of target attribute each values
    target = [dataset[targetColumn].values == x for x in dataset[targetColumn].unique()]
    for t in range(len(target)):
        S -= (len(dataset[target[t]])/len(dataset))*np.log2(len(dataset[target[t]])/len(dataset))
    for a in range(len(attributes)):
        weighted_average = 0
        gAin = 0
        for p in range(len(dataset[attributes[a]].unique())):
            target_counting = []
            for q in range(len(target)):
                val = len(dataset.loc[(dataset[attributes[a]] == dataset[attributes[a]].unique()[p]) & (target[q])])
                # counting-preview
                # print(f"{attributes[a]}|{dataset[attributes[a]].unique()[p]} && {targetColumn}|{dataset[targetColumn].unique()[q]}={val}")
                target_counting.append(val)
                counts[f"{attributes[a]}/{dataset[attributes[a]].unique()[p]}/{dataset[targetColumn].unique()[q]}"] = val
            entro = 0
            # target_counting ---> count of one of target column value and other columns
            for i in target_counting:
                probability = i/sum(target_counting)
                # Calulating entrophy
                if (probability == 0 or probability == 1):  # perfect pure ex: 4 "Yes" and 0 "No"
                    entro = 0
                else:
                    entro -= (probability)*np.log2(probability)
            entrophy[f"{attributes[a]}/{dataset[attributes[a]].unique()[p]}"] = entro
            weighted_average += entro * sum(target_counting)/len(dataset)
        weighted_avg[f"{attributes[a]}"] = weighted_average
        gAin = S-weighted_average
        gain[f"{attributes[a]}"] = gAin
    tree["dataset_total_entophy"] = S
    tree["counts"] = counts
    tree["entrophy"] = entrophy
    tree["weighted_avg"] = weighted_avg
    tree["gain"] = gain
    tree["main_node"] = [x for x, y in gain.items() if max(gain.values()) == y][0]
    tree["restof_nodes"] = [col for col in dataset.columns if col != tree["main_node"]]
    return tree


def treeConstr(targetColumn, Df):
    str1 = ""
    dFs = []
    mixeddFs = []
    data = {}
    val = 0
    current_main_node = tree(targetColumn, Df)["main_node"]
    for x in Df[tree(targetColumn, Df)["main_node"]].unique():
        Df1 = Df.loc[Df[tree(targetColumn, Df)["main_node"]] == x].loc[:, [
            col for col in Df.columns if col != tree(targetColumn, Df)["main_node"]]]
        # Df1 is splited version of Df (filtering based same valued main_node column  {main_node=high infomation gain column} )
        found = [True if value != Df1[targetColumn].values[0] else False for value in Df1[targetColumn].values]
        is_mixed = True in found
        dFs.append(Df1)
        if is_mixed:
            mixeddFs.append(Df1)
            str1 += f"{current_main_node}[{x}]-->{treeConstr(targetColumn, Df1)['struct']}"
            # print(treeConstr(Df1)['struct'])
        else:
            str1 += f"{tree(targetColumn, Df)["main_node"]}[{x}]-->{Df1[targetColumn].values[0]}|"
        data["DataFrames"] = dFs  # all dataframes
        data["struct"] = str1  # tree structure for certain main_node
        data["mixedDf"] = mixeddFs  # mixed target values percists dataframes
    return data


def tree_json(targetColumn, Df):
    current_main_node = tree(targetColumn, Df)["main_node"]
    jsonData = {"name": current_main_node,
                "branches": {}}

    for x in Df[current_main_node].unique():
        Df1 = Df.loc[Df[current_main_node] == x].loc[:, [
            col for col in Df.columns if col != current_main_node]]
        # Df1 is splited version of Df (filtering based same valued current_main_node column  {main_node=high infomation gain column} )
        found = [True if value != Df1[targetColumn].values[0] else False for value in Df1[targetColumn].values]
        is_mixed = True in found
        if is_mixed:
            jsonData['branches'][x] = tree_json(targetColumn, Df1)
            # print(treeConstr(Df1)['struct'])
        else:
            jsonData['branches'][x] = Df1[targetColumn].values[0]
    return jsonData


with open('tree.json', 'w') as f:
    json.dump(tree_json(targetColumn, Df), f)


info = tree('Attend?', Df)
tRee = treeConstr('Attend?', Df)

root_node = info['main_node']
other_nodes = info['restof_nodes']
tree_structure = tRee['struct']


pattern = re.compile(r'([A-Za-z_]+)\[([A-Za-z]+)\]-->(Yes|No)?')
Node = [x.group(1) for x in pattern.finditer(tree_structure)]
NodeValue = [x.group(2) for x in pattern.finditer(tree_structure)]
LeafValue = [x.group(3) for x in pattern.finditer(tree_structure)]
count = len(Node)
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('test.html')


if __name__ == "__main__":
    app.run(debug=True)
