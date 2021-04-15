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
    verbose = 3

[file_paths]
    #Application create <work_dir> in current directory. Changing <work_dir> in the config will not give any effect
    work_dir = output-csv-bulk-find-and-replace

    #Name of the config file. If it's not exists, it will create in <work_dir>
    #You can change the config file, or delete it. If you delete this config file - application will create a new one. But changing name of the config_file will not give any effect.
    config_file = ${work_dir}/config.cfg

    #Input filename. Which file to process?
    input_file = input.csv

    #File with a pairs of "find and replace" strings.
    find_replace_file = findreplace.csv

    #Output filename. Where to save results of the application work?
    output_file = ${work_dir}/output.csv

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

    #Check that input_file is exist. Will create empty one if not
    if (not os.path.isfile(config['file_paths']['input_file'])):
        file_handler = open(config['file_paths']['input_file'], "w")
        file_handler.write("\n")
        file_handler.close()
        if config.getint('Common', 'verbose') >= 1: print ("Input file \"{0}\" was not exist! I created empty one for you. That's all I can do. Sorry. ".format(config['file_paths']['input_file']))
        #Program termination
        return false;
    else:
        #Read CSV-data from input file...
        with open(config['file_paths']['input_file'], mode='r') as input_file:
            csv_reader = csv.reader(input_file)
            line_count = 0
            for row in csv_reader:
                line_count += 1
                print_json(row)
                if line_count > 10: break;
            if config.getint('Common', 'verbose') >= 2: print ("Processed {0} lines from {1}".format(line_count, config['file_paths']['input_file']))

    #if (os.path.isfile(config['db']['sqlite3file'])):


if __name__ == "__main__":
    main()

