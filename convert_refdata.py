#!/usr/bin/python3
import os
from collections import defaultdict


def get_steps(rules, steps, item):
    result = {}
    if item in rules:
        for step in rules[item].keys():
            res = get_steps(rules, steps, step)
            for key, val in res.items():
                result[key] = val
    elif item in steps:
        result[item] = steps[item]
    return result

def import_steps(in_dir, ref, import_file, import_data):
    filename = os.path.join(in_dir, ref, import_file)
    import_data = import_data.strip()
    print(filename)
    print('"' + import_data + '"')
    if '#' in import_data:
        import_data = import_data.split('#')[0]
        import_data = import_data.strip()
        print('Clean:"' + import_data + '"')
    if ' ' in import_data:
        import_data = import_data.split()
    else:
        import_data = [import_data, ]
    
    result = {}
    steps = {}
    rules = defaultdict(dict)
    with open(filename, 'r') as infile:
        for line in infile:
            if line.startswith('#'):
                continue
            if line.startswith('all:'):
                continue
            if line.startswith('import'):
                next_file, next_data  = line[7:].split(':')
                for item in import_data:
                    if item in next_data:
                        res = import_steps(in_dir, ref, next_file, next_data)
                        for key, val in res.items():
                            result[key] = val
            elif '\t' in line:
                row = line.rstrip('\n\r').split('\t')
                steps[row[0]] = row[1]
            else:
                row = line.rstrip('\n\r').split()
                if len(row) > 1 and row[0].endswith(':'):
                    for item in row[1:]:
                        rules[row[0][:-1]][item] = 1
    for item in import_data:
        if item in steps:
            print('FOUND STEP', item)
            result[item] = steps[item]
        elif item in rules:
            print('FOUND RULE', item)
            input_steps = get_steps(rules, steps, item)
            for key, val in input_steps.items():
                result[key] = val
        else:
            print('NOT FOUND', import_data)
            print(steps)
            print(rules)
        
    print(result)
    return result

def main():
    in_dir = '/home/aekazakov/tools/GapMind/cgcmc_gapmind/PaperBLAST/gaps'
    refs = ['aa', 'carbon']
    for ref in refs:
        pathways = {}
        steps = defaultdict(dict)
        pathway_file = os.path.join(in_dir, ref, ref + '.table')
        with open(pathway_file, 'r') as infile:
            infile.readline()
            for line in infile:
                row = line.rstrip('\n\r').split('\t')
                pathways[row[0]] = row[1]
        for pathway in pathways.keys():
            steps_file = os.path.join(in_dir, ref, pathway + '.steps')
            if not os.path.exists(steps_file):
                print('File not found:', steps_file)
                continue
            with open(steps_file, 'r') as infile:
                for line in infile:
                    line  = line.rstrip('\n\r')
                    if line.startswith('#'):
                        continue
                    if line.startswith('import'):
                        print(pathway, 'IMPORTS', line)
                        import_file, import_data  = line[7:].split(':')
                        for step, step_desc in import_steps(in_dir, ref, import_file, import_data).items():
                            steps[pathway][step] = step_desc
                    row = line.rstrip('\n\r').split('\t')
                    if len(row) < 2:
                        continue
                    if ':' not in row[0]:
                        steps[pathway][row[0]] = row[1]
        with open(os.path.join('/home/aekazakov/tools/GapMind/cgcmc_gapmind/PaperBLAST/', ref + '.ref.txt'), 'w') as outfile:
            for pathway in sorted(pathways.keys()):
                for step in sorted(steps[pathway].keys()):
                    outfile.write('\t'.join([pathway, pathways[pathway], step, steps[pathway][step]]) + '\n')

if __name__=='__main__':
    main()


