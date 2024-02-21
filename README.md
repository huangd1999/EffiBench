---
license: apache-2.0
---

# Workflow of Efficiency Testing for Code Generation Models


## Installation

```
git clone git@github.com:huangd1999/EffiBench.git
cd EffiBench
pip install -r requirements.txt
```

## convert json to py file

```py
python json_to_py_file.py
```

## execute py file and save execution dat

```bash
bash run.sh
```

## report efficiency metrics

```
python calculate_memory_usage.py
```