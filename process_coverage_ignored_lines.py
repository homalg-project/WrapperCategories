#!/usr/bin/python3

#######################################################
# You should only use the coverage annotations for
# a) lines around errors and warnings,
# b) code solely existing for debugging purposes,
# c) calls of `TryNextMethod` leading to external code.
#######################################################

import json
import re
import os
from pathlib import Path

regex_block_start = re.compile("^\s*# COVERAGE_IGNORE_BLOCK_START$")
regex_block_end = re.compile("^\s*# COVERAGE_IGNORE_BLOCK_END$")
regex_next_line = re.compile("^\s*# COVERAGE_IGNORE_NEXT_LINE$")

for coverage_filename in Path(".").glob("**/coverage.json"):
    print("processing coverage file " + str(coverage_filename))
    with open(coverage_filename) as json_file:
        data = json.load(json_file)
        files = data["coverage"]
        for filename, lines_covered in files.items():
            if filename.startswith(os.getcwd()):
                print(" processing code file " + filename)
                line_number = 0
                ignoring = False
                ignored_lines = []
                with open(filename) as file:
                    while True:
                        line_number += 1
                        line = file.readline()
                        
                        if not line:
                            break
                        
                        if regex_block_start.match(line) is not None:
                            if ignoring:
                                print("Error in line " + str(line_number) + ": start ignoring while already ignoring")
                                exit(1)
                            ignoring = True
                        
                        if regex_block_end.match(line) is not None:
                            if not ignoring:
                                print("Error in line " + str(line_number) + ": end ignoring while not ignoring")
                                exit(1)
                            ignoring = False
                        
                        if regex_next_line.match(line) is not None:
                            if ignoring:
                                print("Error in line " + str(line_number) + ": ignoring next line while already ignoring block")
                                exit(1)
                            ignored_lines.append(line_number + 1)
                        
                        if ignoring:
                            ignored_lines.append(line_number)
                
                if ignoring:
                    print("Error: ignoring until the end of the file")
                    exit(1)
                
                for line_number in ignored_lines:
                    if str(line_number) in lines_covered:
                        if lines_covered[str(line_number)] != "0":
                            print("Error in line " + str(line_number) + ": an ignored line is covered")
                            exit(1)
                        del lines_covered[str(line_number)]
    
    with open(coverage_filename, "w") as outfile:
        json.dump(data, outfile, indent=0)
