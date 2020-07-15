#!/bin/bash

ulimit -a

cd /opt/DatabaseMonitor/

python3 DatabaseMonitor.py > DatabaseMonitor.out 2>&1
