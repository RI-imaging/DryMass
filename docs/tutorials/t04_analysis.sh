#!/bin/bash
dm_analyze_sphere --recursive --profile t4edge $1
dm_analyze_sphere --recursive --profile t4proj $1
dm_analyze_sphere --recursive --profile t4rytov $1
dm_analyze_sphere --recursive --profile t4rytov-sc $1
python t04_method_comparison.py $1
