# DisPatch_demo


## Description

This is the package of DisPatch, a patch decomposition system for unraveling individual security patches from entangled code changes. We first introduce a graph representation named PatchGraph to capture the fine-grained code modifications by retaining changed syntax and dependency. Next, we perform a two-stage patch dependency analysis to group the changed statements addressing the same vulnerability into individual security patches. 

## Disclaimer & License

We developed DisPatch, aiming to help developers understand the huge code changes and identify individual security patches. 
We are not responsible for any negative outcomes that may result from using the software package.

DisPatch is released under the MIT License(refer to the [LICENSE](LICENSE) file for details).

## Dependencies

Python >= 3.10 \
tree-sitter >= 0.24.0 \
tree-sitter-c >= 0.23.4 \
networkx >= 2.8.8

**Suggested system configurations:**\
(Our package can run on pure CPU environments)\
RAM: >2GB\
Disk: >30GB\
CPU: >1 core

```shell 
pip install -r requirements.txt
```

## How-to-Run

### 1. Data Preparation

#### 1.1 Use Demo Data

We provide demos in `~/DisPatch/data/`, which includes the previous version source code, post version source code, and the diff file generated with -U0 tag.

```
data/demo
├── a/
│   ├── previous version source code
│   ├── ...
├── b/
│   ├── post version source code
│   ├── ...
├── commits/ (optional)
│   ├── commit between previous version and post version
│   ├── ...
├── diff_clean.txt
├── ground_truth.txt
```
The individual patches in the  `ground_truth.txt` are listed in the following format:
```
Patch [individual_patch_id]:[security tag]
[node_id, file_name, function_name, code]
....
```

#### 1.2 Use Other Data

We provide other data zipped in the DisPatch_data folder.

#### 1.3 Use Your Own Data

To use your own data, please pre-process it to follow the demo data format.

### 2. Run DisPatch

You can run either DisPatch as a whole or its components, namely, generate PatchGraph and generate Individual Patch. The results from running DisPatch are the same as running generate PatchGraph and generate Individual Patch separately.

#### 2.1 Run DisPatch

To get the individual patches from the entangled patch, update the data location and result location in the `main.py` and run 
```shell 
python src/main.py
```

You can find the individual patches under `result/xxx/patch` folder. The `result/xxx/` folder records the intermediate results, and the folder structure is shown below:
```
result/demo
├── graph/
│   ├── control.txt
│   ├── data.txt
│   ├── diff.txt
│   ├── node.txt
│   ├── pg.dot // The PatchGraph
├── patch/
│   ├── ip.txt // decomposed individual patches
├── segment/
│   ├── segment.txt // decomposed patches segments

```

#### 2.2. Run DisPatch's Each Component

##### 2.2.1. Generate PatchGraph

To generate PatchGraph for the entangled patch, update the data location in the `PatchGraph_parser.py` and run

```shell 
python3 src/PatchGraph_parser.py
```

You can find the node and edges, including diff behavior, data dependency, control dependency, under the `result/xxx/graph` folder.

##### 2.2.1. Generate Individual Patch

To generate the individual patches with security labels for the given PatchGraph, update the data location in the `Patch_slicer.py` and run

```shell 
python3 src/Patch_slicer.py
```

You can find the patch segments under `result/xxx/segments` folder and individual patches under the `result/xxx/patch` folder.