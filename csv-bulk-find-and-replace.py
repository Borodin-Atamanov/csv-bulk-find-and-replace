import os
import csv
import shutil
import datetime
from configparser import ConfigParser, ExtendedInterpolation
#from config import config
import jsonpickle

#Debug function for printing complex data in human-readable format
def print_json (data):
    jsonpickle.set_preferred_backend('json')
    jsonpickle.set_encoder_options('json', ensure_ascii=False)
    json_str = jsonpickle.encode(data, unpicklable=False, fail_safe=None, indent=2, separators=(',', ':'))
    print (json_str)
    return json_str

#hardcoded default configuration
config_str = '''
[Common]
    #Application verbosity level. 0 - quet. 3 - very verbose
    verbose = 1

[file_paths]
    #Application create <work_dir> in current directory. Changing <work_dir> in the config will not give any effect
    work_dir = output-csv-bulk-find-and-replace

    #Name of the config file. If it's not exists, it will create in <work_dir>
    #You can change the config file, or delete it. If you delete this config file - application will create a new one. But changing name of the config_file will not give any effect.
    config_file = ${work_dir}/config.cfg

    #Input filename. Which file to process?
    input_file = input.csv

    #File with a pairs of "find and replace" strings.
    #In the first column - which substring to search for. In the second column - which substring to replace.
    find_replace_file = findreplace.csv

    #Output filename. Where to save results of the application work?
    output_file = ${work_dir}/output.csv

    #Save pairs of "find and replace", sorted by "find" strings lenghts in this file. It will not affect further work, but it may contain useful statistics.
    find_replace_sorted_file = ${work_dir}/findreplace.csv

'''

def main():
    #Start!
    #Create new configparser object
    config = ConfigParser (interpolation=ExtendedInterpolation())
    #Load configuration from inline hardcoded string
    config.read_string(config_str)
    if config.getint('Common', 'verbose') >= 2: print ("Load default configuration from inline hardcoded string")
    if config.getint('Common', 'verbose') >= 3: print_json (config._sections)

    #create <work_dir> if it is not exists
    os.makedirs(config['file_paths']['work_dir'], exist_ok=True)

    #Create config-file if it is not exists
    if (not os.path.isfile(config['file_paths']['config_file'])):
        config_file_handler = open(config['file_paths']['config_file'], "w")
        written_bytes = config_file_handler.write(config_str)
        config_file_handler.close()
        if config.getint('Common', 'verbose') >= 2: print ("Create new config file \"{0}\". Writed {1} bytes. ".format(config['file_paths']['config_file'], written_bytes))
    else:
        if config.getint('Common', 'verbose') >= 2: print ("Config file \"{0}\" is already exists.".format(config['file_paths']['config_file']))
        loaded_filenames = config.read(config['file_paths']['config_file'])
        if config.getint('Common', 'verbose') >= 2: print ("Load configuration from config file \"{0}\".".format(config['file_paths']['config_file']))
        if config.getint('Common', 'verbose') >= 3: print_json (config._sections)

    #Check that find_replace_file is exist. Will create empty one if not
    if (not os.path.isfile(config['file_paths']['find_replace_file'])):
        file_handler = open(config['file_paths']['find_replace_file'], "w")
        file_handler.write("\n")
        file_handler.close()
        if config.getint('Common', 'verbose') >= 1: print ("\"find_and_replace\"-file \"{0}\" was not exist! I created empty one for you. That's all I can do. Sorry. ".format(config['file_paths']['find_replace_file']))
        #Program termination?
    else:
        #Read CSV-data from find_replace_file and save it to dictionary
        find_replace_dict = dict()
        with open(config['file_paths']['find_replace_file'], mode='r') as input_file:
            #In first column of
            csv_reader = csv.reader(input_file)
            line_count = 0
            for row in csv_reader:
                line_count += 1
                #Обрабатывать ситуацию, когда нет значения по индексу 0 или 1!
                if (len(row) >= 2):
                    find_replace_dict[row[0]] = row[1]
                else:
                    #Ignore rows, if they don't have 2 cells
                    if config.getint('Common', 'verbose') >= 1: print ("Ignore row on line {0} from find_and_replace-file \"{1}\" because it has less than 2 cells! ".format(line_count, config['file_paths']['find_replace_file']))
                    if config.getint('Common', 'verbose') >= 2: print (row)
            #Sort dictionary by key length (biggest key will be a the top of dict)
            find_replace_dict = {k: v for k,v in sorted(find_replace_dict.items(), reverse=True, key=lambda item: len(str(item[0]))) }
            if config.getint('Common', 'verbose') >= 3: print_json(find_replace_dict)
            find_replace_sorted_file = open(config['file_paths']['find_replace_sorted_file'], mode='w', encoding='UTF-8')
            find_replace_sorted_file_writer = csv.writer(find_replace_sorted_file, delimiter=',', doublequote=True, quotechar='"', lineterminator='\r\n', quoting=csv.QUOTE_ALL)
            find_replace_sorted_file_writer.writerows(find_replace_dict.items())
            find_replace_sorted_file.close()

            if config.getint('Common', 'verbose') >= 2: print ("Processed {0} lines from {1}".format(line_count, config['file_paths']['find_replace_file']))

    #Check that input_file is exist. Will create empty one if not
    if (not os.path.isfile(config['file_paths']['input_file'])):
        file_handler = open(config['file_paths']['input_file'], "w")
        file_handler.write("\n")
        file_handler.close()
        if config.getint('Common', 'verbose') >= 1: print ("Input file \"{0}\" was not exist! I created empty one for you. That's all I can do. Sorry. ".format(config['file_paths']['input_file']))
        #Program termination
        return false;
    else:
        #Create output_file
        output_file = open(config['file_paths']['output_file'], mode='w', encoding='UTF-8')
        output_file_writer = csv.writer(output_file, delimiter=',', doublequote=True, quotechar='"', lineterminator='\r\n', quoting=csv.QUOTE_ALL)

        #Read CSV-data from input file...
        with open(config['file_paths']['input_file'], mode='r') as input_file:
            csv_reader = csv.reader(input_file)
            line_count = 0
            for row in csv_reader:
                line_count += 1
                #пройтись по списку row, каждое значение списка подвергнуть преобразованию, ради которого и затевалась эта программа
                col=0   #current column number
                row_new = []
                #Пройдёмся по каждой колонке в строке
                for cell in row:
                    cell_new = cell
                    #Cycle throw all find_replace_dict pairs
                    #Search and replace every substring, starting from longest strings to shortest
                    for find_str in find_replace_dict:
                        cell_new = cell_new.replace(find_str, find_replace_dict[find_str])
                    col += 1
                    row_new.append(cell_new)
                #Write new line to output_file
                output_file_writer.writerow(row_new)
            if config.getint('Common', 'verbose') >= 2: print ("Processed {0} lines from {1}".format(line_count, config['file_paths']['input_file']))

        output_file.close()

if __name__ == "__main__":
    main()

