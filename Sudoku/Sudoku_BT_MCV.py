import sys
import copy


# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Variable(object):
    def __init__(self, position_tuple):
        self.position_tuple = position_tuple  # position is a tuple (i, j) representing i-j coordinates
        self.domain = set(range(1, 10))  # domain of variable is from 1..9 incl. initially
        self.fixedValue = 0  # 0 indicates value is not fixed yet.

    # Remove all items in elements_to_remove (a set) from this variable's domain
    def reduce_domain(self, elements_to_remove):
        self.domain = self.domain.difference(elements_to_remove)


class Assignment(object):
    def __init__(self, list_of_cells):
        self.assignment_dict = dict()  # maps tuple (i, j) to a value.
        # Initialise the assignments from list of cells (2D array) given
        num_of_fixed_values = 0  # counting number of unassigned variables left
        for i in range(0, len(list_of_cells)):
            for j in range(0, len(list_of_cells[0])):
                curr_variable = list_of_cells[i][j]

                if curr_variable != 0:  # not 0 means variable has been assigned
                    num_of_fixed_values += 1
                self.assignment_dict[(i, j)] = curr_variable
        self.unassigned_count = 81 - num_of_fixed_values
        # inferences_dict maps tuple (i, j) to (set of) ILLEGAL values associated with that (i, j) position

    def is_complete(self):
        return self.unassigned_count == 0

    def assign(self, position_tuple, value):
        self.assignment_dict[position_tuple] = value
        self.unassigned_count -= 1

    def reset(self, position_tuple):
        if self.assignment_dict[position_tuple] != 0:
            self.assignment_dict[position_tuple] = 0
            self.unassigned_count += 1

    def is_consistent_with(self, position_tuple, value):
        row_to_check = position_tuple[0]
        col_to_check = position_tuple[1]

        # Go through same row as position_tuple
        for i in range(0, 9):
            if i != col_to_check:
                if self.assignment_dict[(row_to_check, i)] == value:
                    return False

        # Go through same col as position_tuple
        for j in range(0, 9):
            if j != row_to_check:
                if self.assignment_dict[(j, col_to_check)] == value:
                    return False

        # Go through same 3x3 grid
        temp = int(row_to_check / 3)
        temp2 = int(col_to_check / 3)
        for i in range(temp * 3, (temp + 1) * 3):
            for j in range(temp2 * 3, (temp2 + 1) * 3):
                if (i, j) != position_tuple:
                    if self.assignment_dict[(i, j)] == value:
                        return False

        return True

    # Returns the number of unassigned variables constrained by the variable at the position given
    def get_constraint_num(self, position_tuple):
        row_to_check = position_tuple[0]
        col_to_check = position_tuple[1]
        count = 0
        # Go through same row as position_tuple
        for i in range(0, 9):
            if i != col_to_check:
                if self.assignment_dict[(row_to_check, i)] == 0:
                    count += 1
        
        #if row_to_check == 0 and col_to_check == 8:
            #print("num of 0 in same row: %d" % (count))
        # Go through same col as position_tuple
        for j in range(0, 9):
            if j != row_to_check:
                if self.assignment_dict[(j, col_to_check)] == 0:
                    count += 1
        #if row_to_check == 0 and col_to_check == 8:
            #print("num of 0 in same row+col: %d" % (count))
        # Go through same 3x3 grid
        temp = int(row_to_check / 3)
        temp2 = int(col_to_check / 3)
        for i in range(temp * 3, (temp + 1) * 3):
            for j in range(temp2 * 3, (temp2 + 1) * 3):
                if i != row_to_check and j != col_to_check:
                    if self.assignment_dict[(i, j)] == 0:
                        #if row_to_check == 0 and col_to_check == 8:
                            #print("checking inner square: %d, %d" % (i, j))
                        count += 1 
        #if row_to_check == 0 and col_to_check == 8:
            #print("num of 0 in same row+col+sq: %d" % (count))
        return count

class CSP(object):
    def __init__(self, list_of_cells):
        self.unassigned_dict = dict()  # maps tuple (i, j) to a Variable object (of corresponding position)
        for i in range(0, len(list_of_cells)):
            for j in range(0, len(list_of_cells[0])):
                if list_of_cells[i][j] == 0:  # 0 means unassigned initially, is a variable to consider
                    self.unassigned_dict[(i, j)] = Variable((i, j))

    def size(self):
        return len(self.unassigned_dict)


class Sudoku(object):
    def __init__(self, puzzle):
        self.puzzle = puzzle  # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle)  # self.ans is a list of lists
        self.assignment = Assignment(puzzle)  # initialize assignment based on given input
        self.csp = CSP(puzzle)
        self.steps_taken = 0

    # Use MRV Minimum Remaining Values Heuristic to select variable
    # Finding variable with the smallest domain
    # Returns Variable object corresponding to position with MRV
    def select_unassigned_variable(self):
        min_domain_size = 11
        min_variable_key = (-1, -1)
        for key in self.csp.unassigned_dict:
            curr_domain_size = len(self.csp.unassigned_dict[key].domain)
            if curr_domain_size <= min_domain_size:
                min_domain_size = curr_domain_size
                min_variable_key = key

        mrv_variable = self.csp.unassigned_dict[min_variable_key]
        return mrv_variable
    
    # Use MCV Most Constraining Variable Heuristic to select variable
    # Finding variable with the most constraints on remaining unassigned variables
    # Returns Variable object corresponding to position with MCV
    def select_unassigned_variable_mcv(self):
        most_constraint_num = 0
        mcv_variable_key = (-1, -1)
        for key in self.csp.unassigned_dict:
            curr_constraint_num = self.assignment.get_constraint_num(key)
            if curr_constraint_num > most_constraint_num:
                #if key[0] == 0 and key[1] == 8:
                    #print("constraint num updated from %d to %d" % (most_constraint_num, curr_constraint_num))
                most_constraint_num = curr_constraint_num
                mcv_variable_key = key
        mcv_variable = self.csp.unassigned_dict[mcv_variable_key]
        return mcv_variable

    # Inference is forward checking only, returns False if some domain reduced to empty set
    def inference(self, csp, var, value):
        var_position = var.position_tuple
        var_row = var_position[0]
        var_col = var_position[1]

        failure_flag = False

        set_of_tuples_with_value_removed = set()

        # forward check across same row
        for i in range(0, 9):
            if (var_row, i) in csp.unassigned_dict:
                domain_to_reduce = csp.unassigned_dict[(var_row, i)].domain
                if value in domain_to_reduce:
                    domain_to_reduce.remove(value)
                    set_of_tuples_with_value_removed.add((var_row, i))
                    if len(domain_to_reduce) == 0:
                        failure_flag = True
                        break

        # forward check across same col
        for j in range(0, 9):
            if (j, var_col) in csp.unassigned_dict:
                domain_to_reduce = csp.unassigned_dict[(j, var_col)].domain
                if value in domain_to_reduce:
                    domain_to_reduce.remove(value)
                    set_of_tuples_with_value_removed.add((j, var_col))
                    if len(domain_to_reduce) == 0:
                        failure_flag = True
                        break

        # forward check within same 3x3 grid
        temp = int(var_row / 3)
        temp2 = int(var_col / 3)
        for a in range(temp * 3, (temp + 1) * 3):
            for b in range(temp2 * 3, (temp2 + 1) * 3):
                if (a, b) in csp.unassigned_dict:
                    domain_to_reduce = csp.unassigned_dict[(a, b)].domain
                    if value in domain_to_reduce:
                        domain_to_reduce.remove(value)
                        set_of_tuples_with_value_removed.add((a, b))
                        if len(domain_to_reduce) == 0:
                            failure_flag = True
                            break

        # If a failure is detected, backtrack and add back VALUE into any reduced domains
        if failure_flag:
            for (i, j) in set_of_tuples_with_value_removed:
                csp.unassigned_dict[(i, j)].domain.add(value)
            return False

        # If no failure is detected, return all the positions whose domains have VALUE removed
        return set_of_tuples_with_value_removed

    def backtrack(self, assignment, csp):
        if assignment.is_complete():
            return assignment

        self.steps_taken += 1
        curr_var = self.select_unassigned_variable_mcv()  # Returns a Variable object
        #print(curr_var.position_tuple)
        del csp.unassigned_dict[curr_var.position_tuple]
        # x is an integer value from domain of curr_var
        for x in curr_var.domain:  # No ordering established yet for choosing domain values
            if assignment.is_consistent_with(curr_var.position_tuple, x):
                assignment.assign(curr_var.position_tuple, x)
                inference = self.inference(csp, curr_var, x)
                if inference != False:
                    result = self.backtrack(assignment, csp)
                    # SUCCESS SCENARIO
                    if result != False:
                        return result

                    # Failure in one of the sub-trees, this x value is not chosen, undo domain reduction
                    for (i, j) in inference:
                        csp.unassigned_dict[(i, j)].domain.add(x)

                assignment.reset(curr_var.position_tuple)
        #print("not succcessful")
        csp.unassigned_dict[curr_var.position_tuple] = curr_var
        return False

    def backtrack_search(self, csp):
        return self.backtrack(self.assignment, csp)

    # Method to initially reduce domains of all variables based on already assigned cells
    def initial_domain_reduction(self):
        # Go through every row
        for r in range(0, 9):
            items = set()
            keys_to_reduce = set()
            for c in range(0, 9):
                if self.puzzle[r][c] != 0:
                    items.add(self.puzzle[r][c])
                else:
                    keys_to_reduce.add((r, c))
            for key in keys_to_reduce:
                self.csp.unassigned_dict[key].reduce_domain(items)

        # Go through every column
        for a in range(0, 9):
            items = set()
            keys_to_reduce = set()
            for b in range(0, 9):
                if self.puzzle[b][a] != 0:
                    items.add(self.puzzle[b][a])
                else:
                    keys_to_reduce.add((b, a))
            for key in keys_to_reduce:
                self.csp.unassigned_dict[key].reduce_domain(items)

        # Go through 3x3 grid
        for f in range(0, 7, 3):
            for g in range(0, 7, 3):
                items = set()
                keys_to_reduce = set()
                for i in range(f, f + 3):
                    for j in range(g, g + 3):
                        if self.puzzle[i][j] != 0:
                            items.add(self.puzzle[i][j])
                        else:
                            keys_to_reduce.add((i, j))
                for key in keys_to_reduce:
                    self.csp.unassigned_dict[key].reduce_domain(items)

    def solve(self):

        self.initial_domain_reduction()

        # for key in self.csp.unassigned_dict:
        #     print(str(key) + " " +str(len(self.csp.unassigned_dict[key].domain)))

        # print("START!")

        valid_assignment = self.backtrack_search(self.csp)
        for (i, j) in valid_assignment.assignment_dict:
            self.ans[i][j] = valid_assignment.assignment_dict[(i, j)]

        return self.ans


if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise IOError("Input file not found!")

    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()

    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
