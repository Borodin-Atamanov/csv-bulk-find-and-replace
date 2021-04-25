#!/usr/bin/env python
"""
© Copyright 2021 Slava Borodin-Atamanov

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import csv
import time
import jsonpickle
from configparser import ConfigParser
from configparser import ExtendedInterpolation

__author__ = "Slava Borodin-Atamanov"
__license__ = "Apache 2.0"
__maintainer__ = "python@Borodin-Atamanov.ru"
__copyright__ = "Copyright 2021, Slava Borodin-Atamanov"
__email__ = "python@Borodin-Atamanov.ru"
__status__ = "Production"

def print_json (data):
    '''Printing complex data in human-readable JSON format with indents and return string with JSON'''
    jsonpickle.set_preferred_backend('json')
    jsonpickle.set_encoder_options('json', ensure_ascii=False)
    json_str = jsonpickle.encode(data, unpicklable=False, fail_safe=None, indent=2, separators=(',', ':'))
    print (json_str)
    return json_str

def str_ireplace(text, old, new):
    '''Function make case-insensitive replace in input text string'''
    idx = 0
    while idx < len(text):
        index_l = text.lower().find(old.lower(), idx)
        if index_l == -1:
            return text
        text = text[:index_l] + new + text[index_l + len(old):]
        idx = index_l + len(new)
    return text

#hardcoded default configuration
config_str = '''
[Common]
    #Application verbosity level. 0 - quiet. 2 - Ok. 4 - very verbose
    verbose = 3

    #Use case insensitive search and replace?
    case_insensitive = On

    #Show work statistics every n-cells
    show_statistics_every_n_lines_of_input_file = 3000


[files]
    #Application create <work_dir> in current directory. Changing <work_dir> in the config will not give any effect
    work_dir = output-csv-bulk-find-and-replace

    #Name of the config file. If it's not exists, it will create in <work_dir>
    #You can change the config file, or delete it. If you delete this config file - application will create a new one. But changing name of the config_file will not give any effect.
    config_file = ${work_dir}/config.ini

    #file encoding
    encoding = utf-8

    #Input filename. Which file to process?
    input_file = input.csv

    #File with a pairs of "find and replace" strings.
    #In the first column - which substring to search for. In the second column - which substring to replace.
    find_replace_file = findreplace.csv

    #Output filename. Where to save results of the application work?
    output_file = ${work_dir}/output.csv

    #Save pairs of "find and replace", sorted by "find" strings lenghts in this file.
    #It will not affect further work, but it may contain useful statistics.
    find_replace_sorted_file = ${work_dir}/findreplace-stat.csv

    default_input_file_content = "You should eat"
        "1 pizza, 1 beer, and 1 ice cream"
        "every day!"
        "CAPS cAseInsEnsitIvE lower"

    default_find_replace_content = "You should","You can"
        "pizza","fruits"
        "beer","vegetables"
        "ice cream","fiber"
        "!","."
        "1 ",""
        "CaSeiNsensitive","CamelCase"

'''

def main():
    #Start!
    time_start = time.time()
    time_main_start = time_start

    #Create new configparser object
    config = ConfigParser (interpolation=ExtendedInterpolation())
    #Load configuration from inline hardcoded string
    config.read_string(config_str)
    if config.getint('Common', 'verbose') >= 2: print ("Load default configuration from inline hardcoded string")
    if config.getint('Common', 'verbose') >= 3: print_json (config._sections)

    #create <work_dir> if it is not exists
    os.makedirs(config['files']['work_dir'], exist_ok=True)

    #Create config-file if it is not exists
    if (not os.path.isfile(config['files']['config_file'])):
        config_file_handler = open(config['files']['config_file'],  mode="w", encoding=config['files']['encoding'])
        written_bytes = config_file_handler.write(config_str)
        config_file_handler.close()
        if config.getint('Common', 'verbose') >= 2: print ("Create new config file \"{0}\". Writed {1} bytes. ".format(config['files']['config_file'], written_bytes))
    else:
        if config.getint('Common', 'verbose') >= 3: print ("Config file \"{0}\" is already exists.".format(config['files']['config_file']))
        loaded_filenames = config.read(config['files']['config_file'])
        if config.getint('Common', 'verbose') >= 2: print ("Load configuration from config file \"{0}\".".format(config['files']['config_file']))
        if config.getint('Common', 'verbose') >= 3: print_json (config._sections)

    #Check that find_replace_file is exist. Will create empty one if not
    if (not os.path.isfile(config['files']['find_replace_file'])):
        file_handler = open(config['files']['find_replace_file'], mode="w", encoding=config['files']['encoding'])
        file_handler.write(config['files']['default_find_replace_content'])
        file_handler.close()
        if config.getint('Common', 'verbose') >= 1: print ("\"find_and_replace\"-file \"{0}\" was not exist! I created empty one for you. That's all I can do. Sorry. ".format(config['files']['find_replace_file']))
        #Program termination?
    else:
        #Read CSV-data from find_replace_file and save it to dictionary
        find_replace_dict = dict()
        with open(config['files']['find_replace_file'], mode='r', encoding=config['files']['encoding']) as input_file:
            #In first column of
            csv_reader = csv.reader(input_file)
            line_count = 0
            for row in csv_reader:
                line_count += 1
                #Обрабатывать ситуацию, когда нет значения по индексу 0 или 1!
                if (len(row) >= 2):
                    find_replace_dict[row[0]] = \
                        {
                            'replacer': row[1],
                            'replacements_count': 0,
                            'original_line_id': line_count,
                        }
                else:
                    #Ignore rows, if they don't have 2 cells
                    if config.getint('Common', 'verbose') >= 1: print ("Ignore row on line {0} from find_and_replace-file \"{1}\" because it has less than 2 cells! ".format(line_count, config['files']['find_replace_file']))
                    if config.getint('Common', 'verbose') >= 2: print (row)
            #Sort dictionary by key length (biggest key will be at the top of dict)
            find_replace_dict = {k: v for k,v in sorted(find_replace_dict.items(), reverse=True, key=lambda item: len(str(item[0]))) }
            if config.getint('Common', 'verbose') >= 2: print ("Loaded {0} lines from {1}".format(line_count, config['files']['find_replace_file']))

    #Check that input_file is exist. Will create empty one if not
    if (not os.path.isfile(config['files']['input_file'])):
        file_handler = open(config['files']['input_file'], mode="w", encoding=config['files']['encoding'])
        file_handler.write(config['files']['default_input_file_content'])
        file_handler.close()
        if config.getint('Common', 'verbose') >= 1: print ("Input file \"{0}\" was not exist! I created empty one for you. That's all I can do. Sorry. ".format(config['files']['input_file']))
        #Program termination
        return False;
    else:
        #Create output_file
        output_file = open(config['files']['output_file'], mode='w', encoding=config['files']['encoding'])
        output_file_writer = csv.writer(output_file, delimiter=',', doublequote=True, quotechar='"', lineterminator='\n', quoting=csv.QUOTE_ALL)

        #Read CSV-data from input file...
        #all_rows = []   #rows to output file
        with open(config['files']['input_file'], mode='r', encoding=config['files']['encoding']) as input_file:
            csv_reader = csv.reader(input_file)
            line_count = 0
            cell_count = 0
            changed_cells_count = 0
            replacements_count = 0
            for row in csv_reader:
                line_count += 1
                #пройтись по списку row, каждое значение списка подвергнуть преобразованию, ради которого и затевалась эта программа
                col=0   #current column number
                row_new = []
                #Пройдёмся по каждой колонке в строке
                for cell in row:
                    cell_count += 1
                    cell_new = cell
                    #Cycle throw all find_replace_dict pairs
                    #Search and replace every substring, starting from longest strings to shortest
                    for find_str in find_replace_dict:
                        cell_before_replacement = cell_new
                        #Try to make case sensitive replace at first
                        #last_cell_replacements_count = cell_new.count(find_str)
                        last_cell_replacements_count = 0
                        #Check lenghts of string. I can not find longer string in the shorter one
                        if (len(find_str) > len(cell_before_replacement)):
                            #This cell is too short, continue with the next one
                            continue

                        last_cell_replacements_count = cell_before_replacement.count(find_str)
                        cell_new = cell_new.replace(find_str, find_replace_dict[find_str]['replacer'])

                        if bool(config._sections['Common']['case_insensitive']) == True:
                            #Try to make case insensitive replace if needed
                            cell_new = str_ireplace(cell_new, find_str, find_replace_dict[find_str]['replacer'])
                            last_cell_replacements_count = cell_before_replacement.upper().count(find_str.upper())
                        if int(config._sections['Common']['verbose']) >= 4:
                            print (f"\ninput=[{cell_before_replacement}]")
                            print (f"search=[{find_str}], replace to=[{find_replace_dict[find_str]['replacer']}]")
                            print (f"result=[{cell_new}]")
                            print (f"last_cell_replacements_count={last_cell_replacements_count}")
                        if cell_before_replacement != cell_new:
                            replacements_count += last_cell_replacements_count
                            find_replace_dict[find_str]['replacements_count'] += last_cell_replacements_count
                    if cell != cell_new:
                        changed_cells_count += 1
                    col += 1
                    row_new.append(cell_new)
                #Write new line to output_file
                #all_rows.append(row_new)
                output_file_writer.writerow(row_new)

                #Show runtime statistics
                if (line_count % int(config._sections['Common']['show_statistics_every_n_lines_of_input_file'])) == 0:
                    time_end = time.time()
                    time_delta = time_end - time_start
                    if 'computed_cells_start' not in vars():
                        computed_cells_start = 0
                    computed_cells_end = cell_count
                    computed_cells_delta = computed_cells_end - computed_cells_start
                    speed_cells_per_sec = computed_cells_delta / time_delta
                    if 'average_speed_cells_per_sec' not in vars():
                        average_speed_cells_per_sec = speed_cells_per_sec * 0.7
                    average_speed_by_how_many_intervals = 9
                    average_speed_cells_per_sec = (average_speed_cells_per_sec * (average_speed_by_how_many_intervals - 1) + speed_cells_per_sec) / average_speed_by_how_many_intervals
                    if int(config._sections['Common']['verbose']) >= 3: print (f"Speed is {average_speed_cells_per_sec:.00f} cells per second. Computed {cell_count} cells. {replacements_count} replacements made.")
                    time_start = time_end
                    computed_cells_start = cell_count

            #output_file_writer.writerows(all_rows)
            #if config.getint('Common', 'verbose') >= 2: print ("\nInput file: {3}\nfind-and-replace file: {4}\n{0} lines processed\n{1} changed cells\n{2} Find-and-replace operations".format(line_count, changed_cells_count, replacements_count, config['files']['input_file'], config['files']['find_replace_file']))
            if config.getint('Common', 'verbose') >= 3: print (f"\nInput file: {config['files']['input_file']}")
            if config.getint('Common', 'verbose') >= 3: print (f"find-and-replace file: {config['files']['find_replace_file']}")
            if config.getint('Common', 'verbose') >= 2: print (f"{line_count} lines processed from input file")
            if config.getint('Common', 'verbose') >= 3: print (f"{cell_count} cells computed")
            if config.getint('Common', 'verbose') >= 3: print (f"{changed_cells_count} cells changed")
            if config.getint('Common', 'verbose') >= 1: print (f"{replacements_count} replacements made")
            if config.getint('Common', 'verbose') >= 3:
                time_main_delta = round(time.time() - time_main_start + 0.5)
                print (f"{time_main_delta:.0f} irrecoverable seconds wasted")
        output_file.close()

        #
        if os.path.exists(config['files']['find_replace_sorted_file']):
            if config.getint('Common', 'verbose') >= 3: print (f"I deleted old file \"{config['files']['find_replace_sorted_file']}\" what has size {os.path.getsize(config['files']['find_replace_sorted_file'])} bytes")
            os.remove(config['files']['find_replace_sorted_file'])
        else:
            if config.getint('Common', 'verbose') >= 4: print (f"{config['files']['find_replace_sorted_file']} is not exist, I will create it")

        #Write sorted find_replace pairs to file, add some statistics
        all_rows = []
        #sort in original line order
        find_replace_dict = {k: v for k,v in sorted(find_replace_dict.items(), reverse=False, key=lambda item: item[1].get('original_line_id', 0)) }
        for find_str in find_replace_dict:
            all_rows.append([find_str, find_replace_dict[find_str]['replacer'],  find_replace_dict[find_str]['replacements_count']])
        find_replace_sorted_file = open(config['files']['find_replace_sorted_file'], mode='w', encoding=config['files']['encoding'])
        find_replace_sorted_file_writer = csv.writer(find_replace_sorted_file, delimiter=',', doublequote=True, quotechar='"', lineterminator='\n', quoting=csv.QUOTE_ALL)
        find_replace_sorted_file_writer.writerows(all_rows)
        find_replace_sorted_file.close()

        if config.getint('Common', 'verbose') >= 2: print (f"I created file \"{config['files']['find_replace_sorted_file']}\" with "+str(os.path.getsize(config['files']['find_replace_sorted_file']))+f" bytes of statistics")

if __name__ == "__main__":
    main()

