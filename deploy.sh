#!/bin/bash
conda create --name politbot python
eval "$(conda shell.bash hook)"
conda activate politbot
pip install -r requirements.txt