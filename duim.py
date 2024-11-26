#!/usr/bin/env python3

import subprocess, sys
import argparse



'''
OPS445 Assignment 2
Program: duim.py 
Author: Jerrico Gomez
The python code in this file (duim.py) is original work written by
Jerrico Gomez. No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or on-line resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: Essentially just a improvement of the du command in linux. Features include color, bar graphs, and percentage

Date: November 30, 2024
'''

class color:
    'Just a simple class called color which stores class attributes/properties.'
    GREEN = '\033[92m'
    RED = '\033[91m'
    END = '\033[0m'
    CYAN = '\033[96m'

def parse_command_args():
    "Set up argparse here. Call this function inside main."
    parser = argparse.ArgumentParser(prog='duim.py', description="DU Improved -- See Disk Usage Report with bar charts", exit_on_error=False, epilog="Copyright 2023")
    parser.add_argument("-H", action=argparse.BooleanOptionalAction, help="Print sizes in human readable format (e.g. 1K 23M 2G)")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    parser.add_argument("-a", action=argparse.BooleanOptionalAction, help="Run this flag if you want files to be included.")
    parser.add_argument("-t", "--threshold", type=str, help="Specify the threshold size to exclude files <threshold. (e.g 10K,2M,1G)")
    parser.add_argument("-s", action=argparse.BooleanOptionalAction, help="Run this flag if you want to sort the output.")
    parser.add_argument("-target", type=str, default=".", help="Specify the directory to scan. If it is not specified, the default is . which is the current directory.")
    args = parser.parse_args()
    return args



def percent_to_graph(percent: int, total_chars: int) -> str:
    "returns a string: eg. '##  ' for 50 if total_chars == 4"
    if percent >=0 and percent <=100:
        #print("The percentage is a valid number from 0-100")
        percentage_decimal = percent / 100
        hash_signs = '#' * int(round(percentage_decimal * total_chars))    #multiplies the # symbol based on the percentage
        space = len(total_chars * " ") - len(hash_signs)
        #print(f"{hash_signs}{space * ' '}")
        return f"{hash_signs}{space * ' '}"
        #print(len(equal_signs))
    else:
        return "The percentage is not a valid number from 0-100"

def check_dir_exists(directory: str) -> bool:
    "Basically just checks whether a directory exists by using the ls command."
    run_command = subprocess.run(["ls", directory], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if run_command.stdout:     #If the command runs successfully, even with no output it will return True, meaning the directory exists.
        return True
    elif run_command.stderr:   #If the command runs with an error, that means that the directory doesn't exist, returning False.
        return False
def call_du_sub(location: str) -> list:
    "use subprocess to call `du -d 1 + location`, rtrn raw list"
    #file_size = ["K","M","G","T","P","E","Z","Y","R","Q","k","m"]
    if check_dir_exists(location):
        du_command_list = ["du", "-d 1", location]
        du_sub = subprocess.Popen(du_command_list, stdout=subprocess.PIPE) #opens up pipe in stdout
        du_output_list = du_sub.stdout.readlines()    #stdout method of popen object returns a readable stream object returned by open(), hence readlines() works.
                                                    #readlines() here returns a list of class bytes items
        du_output_list = [directory.strip().decode() for directory in du_output_list]   #list comprehension, just strips \n and decodes byte to string item.
        return du_output_list
    else:
        return False    #Returns False if directory does not exist

def call_du_sub_with_flags(du_command_list):
    if du_command_list != True:
        du_sub = subprocess.Popen(du_command_list, stdout=subprocess.PIPE) #opens up pipe in stdout
        du_output_list = du_sub.stdout.readlines()    #stdout method of popen object returns a readable stream object returned by open(), hence readlines() works.
                                                        #readlines() here returns a list of class bytes items
        du_output_list = [directory.strip().decode() for directory in du_output_list]   #list comprehension, just strips \n and decodes byte to string item.
        return du_output_list
    else:
        return True
    
def a_flag(du_command_list):
    "modifies the du_command_list if the -a flag is specified"
    if args.a:      #if -a is set to true, run du with -a flag. This will include files too and not just directories.
        du_command_list.insert(2, "-a")
    return du_command_list

def threshold_flag(du_command_list):
    "modifies the du_command_list if the -t flag is specified"
    file_size = ["K","M","G","T","P","E","Z","Y","R","Q","k","m"]
    if any(x in file_size for x in args.threshold):          #check if threshold argument character is in the file_size list.
        du_command_list.insert(2, "-t " + str(args.threshold))   #Just basic input validation for file size unit, as i'm not allowed to use regex
    else:
        return True        #Returns True if invalid file unit.
    return du_command_list


def create_dir_dict(raw_dat: list) -> dict:
    "get list from du_sub, return dict {'directory': 0} where 0 is size"
    processed_output = {}
    for directory in raw_dat:
        directory_line_list = directory.split("\t")
        processed_output[directory_line_list[1]] = int(directory_line_list[0])
    #print(processed_output)
    return processed_output

def bytes_to_human_r(kibibytes: int, decimal_places: int=2) -> str:
    "turn 1,024 into 1 MiB, for example"
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']  # iB indicates 1024
    suf_count = 0
    result = kibibytes 
    while result > 1024 and suf_count < len(suffixes):
        result /= 1024
        suf_count += 1
    str_result = f'{result:.{decimal_places}f} '
    str_result += suffixes[suf_count]
    return str_result

def usage():
    print("./duim.py -target [directory]")
    print("Optional flags: \nto include files: -a,\nto sort the output from descending order: -s,\nfor human-readable format: -H,\nto include length of bargraph: -l [length]\nto include threshold: -t [threshold]")

if __name__ == "__main__":
    args = parse_command_args()
    #print(args)
    if len(sys.argv) == 1:
        usage()
    du_sub_output_list = call_du_sub(args.target)
    #print(du_sub_output_list)
    if du_sub_output_list == False:
        print(f"{color.RED}The Directory does not exist!{color.END}")
        usage()
    else:
        du_command_list = ["du", "-d 1", args.target]
        if args.a:    #runs the a_flag function which will insert/modify existing command list when the flag is specified.
            du_sub_output_list = call_du_sub_with_flags(a_flag(du_command_list))
        if args.threshold:    #runs the threshold_flag function which will insert/modify existing command list when the flag is specified
            du_sub_output_list = call_du_sub_with_flags(threshold_flag(du_command_list))
        if du_sub_output_list == True:      #the threshold_flag function will return True and store in du_command_list if the user input for threshold contains an invalid character.
            print(f"\n{color.RED}The size unit is invalid.{color.END}")
            print(f"{color.RED}The size units accepted are: ['K','M','G','T','P','E','Z','Y','R','Q','k','m'] {color.END}\n")
            usage()
            pass
        else:
            dir_dict = create_dir_dict(du_sub_output_list)    #continue program since du_sub_output_list does not contain a boolean
            color = color()                                    #Create color object
            #print(dir_dict)
            if dir_dict:
                last_key = list(dir_dict)[-1]                     #Used to stop for loop when it reaches last item. The last item is the target directory.
            if args.s:
                dir_dict = dict(sorted(dir_dict.items(), key=lambda item:item[1]))       #sorts the dictionary by size, lambda here takes a expression, and the sorted function
            if dir_dict.items():                                                  #sorts the tuple by size (item[1]), returning a list. We then convert to dictionary
                for directory, size in dir_dict.items():
                    percentage = round((size/dir_dict[list(dir_dict)[-1]]) * 100)     #calculates percentage
                    width = len(str(percentage)) + 2              #Used for formatting purposes for string
                    if args.H:                     #If -H is set, run the block of code to convert size to human readable size
                        size = bytes_to_human_r(size)
                    if directory == last_key:
                        print(f"{color.CYAN}Total: {size} {directory}{color.END}")
                    else:
                        print(f"{color.RED}{percentage:>3} % {color.END}{color.GREEN}[{percent_to_graph(percentage, args.length)}]{color.END}\t{color.RED}{size:<{width}}{color.END}\t{color.RED}{directory}{color.END}" )
            else:
                print(f"\n{color.RED}There is either no directories or files...{color.RED}")
                print(f"{color.RED}Or there is no output that is greater than the threshold...{color.RED}")
