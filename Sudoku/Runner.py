import os
import sys
import filecmp

"""
Runner Script to easily test files
"""

# File/Directory Variables
solver_name = "Sudoku_BT.py"
test_dir = "public_tests_p2_sudoku"
root_output_file = "output.out"

if __name__ == "__main__":
    os.chdir("./" + test_dir)
    files_in_dir = os.listdir(os.curdir)
    os.chdir("../")  # go back to root/parent directory)
    if os.path.exists(root_output_file):
        os.remove(root_output_file)  # deletes output file, if exists
    for file in files_in_dir: 
        if file.startswith("input"):
            dir_input_file = "{}/{}".format(test_dir, file)
            file_int_num = int((file + "")[5:-4])
            output_file_name = "output{}.txt".format(file_int_num)
            output_file_dir = "{}/{}".format(test_dir, output_file_name)
            command = "python Sudoku_BT.py {} {}".format(
                dir_input_file, root_output_file)
            os.system(command)

            if filecmp.cmp(root_output_file, output_file_dir, shallow=False):  # compares both files
                print("Test Case [{}] Pass".format(dir_input_file))
            else:
                print("Test Case [{}] Fail".format(dir_input_file))
                print("Expected:")
                expected_output_file = open(output_file_dir, 'r').read()
                print(expected_output_file)
                print("Actual:")
                actual_output_file = open(root_output_file, 'r').read()
                print(actual_output_file)

            os.remove(root_output_file)  # deletes file
