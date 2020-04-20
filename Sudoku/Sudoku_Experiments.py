import os
import sys
import csv
import Sudoku_DegreeHeuristic as SudokuDegreeHeuristic
import Sudoku_ValueOrdering as SudokuValueOrdering

"""
Automated Experiment Data Generator

"""

# File/Directory Variables
test_dir = "public_tests_p2_sudoku_exp"
root_output_file = "output.out"
csv_file_name = "./experiments.csv"

solver_variants= {
    1: SudokuDegreeHeuristic,
    2: SudokuValueOrdering
}


def get_input_file_names():
    os.chdir("./" + test_dir)
    files_in_dir = os.listdir(os.curdir)
    input_file_names = list()
    for file in files_in_dir:
        if file.startswith("input"):
            input_file_names.append(file)
    # os.chdir("../")
    return input_file_names

# Will loop through every input text file in the test dir
# returns a list of 3 Element Tuple of (input_file_name, Number of Blank Tiles, 2D Matrix of Puzzle)
def get_sudoku_input_data(input_file_names):
    input_data = list()
    for input_file_name in input_file_names:
        input_data.append(get_sudoku_data(input_file_name))
    os.chdir("../") #go back to root
    return input_data


# Reads input_file_name
# Returns 3-Element Tuple of (input_file_name, Number of Blank Tiles, 2D Matrix of Puzzle)
def get_sudoku_data(input_file_name):
    blank_tiles_count = 0
    try:
        f = open(input_file_name, 'r')
    except IOError:
        raise IOError("Input File not found!")
    
    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()
    
    i, j = 0, 0
    for line in lines:
        for number in line:
            if number == '0':
                blank_tiles_count += 1
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    return (input_file_name, blank_tiles_count, puzzle)

# Takes a 2D list as the sudoku list to solve, run against the sudoku puzzle and get the experiment data
# Returns a list representing the experimental results data for a specific input_file
def extract_experiment_data(input_data_list):
    exp_data = list()
    for sudoku_data in input_data_list:
        input_file_name, blank_tiles_count, puzzle = sudoku_data
        current_row = list([input_file_name, blank_tiles_count])
        for variant in solver_variants.values():
            sudoku = variant.Sudoku(puzzle) #instantiate Sudoku object
            sudoku.solve()
            time_taken = '{0:.2f}'.format(sudoku.time_taken) #max 2 d.p
            steps_taken = sudoku.steps_taken
            current_row.append(time_taken)
            current_row.append(steps_taken)
        exp_data.append(current_row)
    return exp_data


if __name__ == "__main__":
    input_file_names = get_input_file_names()
    input_data_list = get_sudoku_input_data(input_file_names)
    all_exp_data = extract_experiment_data(input_data_list)
    # print(all_exp_data)
    with open(csv_file_name, 'wb') as f:
        w = csv.writer(f)
        w.writerow(["Test File Name", "Number of Blank Cells", "Time Taken (DH Variant)",
                    "Steps Taken (DH Variant)", "Time Taken (VO Variant)", "Steps Taken (VO Variant)"])
        w.writerows(all_exp_data)
    print("CSV File Generated!")
