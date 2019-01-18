#!/usr/bin/python
import argparse
import csv
import glob
import os
import shlex
import re
import yaml

def isListEmpty(inList):
    if isinstance(inList, list): # Is a list
        return all( map(isListEmpty, inList) )
    return False # Not a list

#ArgumentParser
parser = argparse.ArgumentParser(description='Test rules against configuration and compile report')
parser.add_argument(
    '--rules',
    help='YAML file containing rules to test'
)
parser.add_argument(
    'config',
    nargs='+',
    help='config files'
)
args = parser.parse_args()

with open(args.rules) as f:
    loadedYaml=yaml.safe_load(f)

listOfFiles=args.config

#LOOP THROUGH CONFIGS
results=[]
for filePath in listOfFiles:
    with open(filePath) as f:
        config=''.join(f.readlines())

    #LOOP THROUGH RULES AND TEST
    rules=[]
    for r in loadedYaml['rules']:
        passMatch=[re.findall(pattern,config,re.MULTILINE) for pattern in r.get('pass_match',[])]
        failMatch=[re.findall(pattern,config,re.MULTILINE) for pattern in r.get('fail_match',[])]

        ruleResults=''
        passFail='N/A'

        if not isListEmpty(passMatch):
            passFail="Pass"
            for pattern in passMatch:
                for m in pattern:
                    ruleResults=ruleResults+m+"\n"
        elif not isListEmpty(r.get('pass_match',[])) and isListEmpty(passMatch):
            passFail="Fail"

        if not isListEmpty(failMatch):
            passFail="Fail"
            for pattern in failMatch:
                for m in pattern:
                    ruleResults=ruleResults+m+"\n"
        elif not isListEmpty(r.get('fail_match',[])) and isListEmpty(failMatch) and passFail is not "Fail":
            passFail="Pass"

        rules.append({
                      'device':      os.path.basename(filePath),
                      'name':        r.get('name','no-name'),
                      'description': r.get('description','n/a'),
                      'passFail':    passFail,
                      'pass_match':  r.get('pass_match','n/a'),
                      'fail_match':  r.get('fail_match','n/a'),
                      'results':     ruleResults
        })
    results=results+rules

#WRITE OUTPUT
with open('output.csv','w') as f:
    writer=csv.DictWriter(f,fieldnames=[
        'device',
        'name',
        'description',
        'passFail',
        'pass_match',
        'fail_match',
        'results'
    ])
    writer.writeheader()
    for row in results:
        writer.writerow(row)
