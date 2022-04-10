#!/bin/bash
ROOT="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; cd .. ; pwd -P )"
mkdir $ROOT/mipt_algobot/contest
mkdir $ROOT/mipt_algobot/contest/solutions
mkdir $ROOT/mipt_algobot/contest/generators
mkdir $ROOT/mipt_algobot/contest/comparators
mkdir $ROOT/mipt_algobot/temp
mkdir $ROOT/mipt_algobot/temp/user
sudo useradd -s /bin/bash -d $ROOT/mipt_algobot/temp/user -G sudo vitek
sudo chown -R vitek $ROOT/mipt_algobot/temp/user
python3 -m pip install -r $ROOT/requirements.txt
