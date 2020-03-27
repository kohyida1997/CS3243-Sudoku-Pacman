import os
import sys
import filecmp

"""
Runner Script to easily test files
3 Ways to Run:
1) Running specific test on a specific variant. Refer to the solver_files_names dict obj for the variant files names
python Runner.py [variant_num] [test_num]
e.g. python Runner.py 1 2  #Runs Variant 1 on input2.txt

2) Running specific variant on all test files
python Runner.py [variant_num]
e.g. python Runner.py 1

3) Running all variants on all test files
python Runner.py [variant_num]
"""

# File/Directory Variables
test_dir = "public_tests_p2_sudoku"
root_output_file = "output.out"

solver_file_names = {
    1: "Sudoku_BT.py",
    2: "Sudoku_ValueOrdering.py",
    3: "Sudoku_VariableOrdering.py",
    4: "Sudoku_Inference.py"
}

"""
Tests a specific file variant on a specific test case
"""
def specific_test(solver_variant_filename, file_int_num):
    input_file_name = "input{}.txt".format(str(file_int_num))
    dir_input_file = "{}/{}".format(test_dir, input_file_name)
    output_file_name = "output{}.txt".format(str(file_int_num))
    output_file_dir = "{}/{}".format(test_dir, output_file_name)
    command = "python {} {} {}".format(
                solver_variant_filename,dir_input_file, root_output_file)
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

"""
Tests a specific file variant on all input{}.txt test files
"""
def variant_test(solver_variant_filename, input_files_in_dir):
    for file in input_files_in_dir:
        if file.startswith("input"):
            file_int_num = int((file + "")[5:-4])
            specific_test(solver_variant_filename, file_int_num)

def test_all(input_files_in_dir):
    for variant in solver_file_names.values():
        variant_test(variant, input_files_in_dir)

if __name__ == "__main__":
    os.chdir("./" + test_dir)
    files_in_dir = os.listdir(os.curdir)
    os.chdir("../")  # go back to root/parent directory)
    if os.path.exists(root_output_file):
        os.remove(root_output_file)  # deletes output file, if exists
<<<<<<< HEAD
    for file in files_in_dir: 
        if file.startswith("input"):
            dir_input_file = "{}/{}".format(test_dir, file)
            file_int_num = int((file + "")[5:-4])
            output_file_name = "output{}.txt".format(file_int_num)
            output_file_dir = "{}/{}".format(test_dir, output_file_name)
            command = "python Sudoku_BT_MCV.py {} {}".format(
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
=======
    
    if len(sys.argv) == 3: #Run specific variant on a specific test case
        solver_variant = solver_file_names[int(sys.argv[1])]
        file_int_num = int(sys.argv[2])
        specific_test(solver_variant, file_int_num)
    elif len(sys.argv) == 2: #Run specific variant on all test cases 
        solver_variant = solver_file_names[int(sys.argv[1])]
        variant_test(solver_variant, files_in_dir)
    elif len(sys.argv) == 1: #Run all variants on all test cases
        test_all(files_in_dir)
    else:
        raise ValueError("Unknown command line arguments!")
    
>>>>>>> d7368a5dae699808a4a9ee79eef740f6d452c1e0
