---
license: apache-2.0
---

# Workflow of Efficiency Testing for Code Generation Models

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