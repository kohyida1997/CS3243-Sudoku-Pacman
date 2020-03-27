import sys, copy, time

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

"""
Represents a cell in the Sudoku Space.
Maintains Domain of the Variable, its current coordiation position
"""
class Variable(object):
    def __init__(self, position_tuple):
        self.position_tuple = position_tuple  # position is a tuple (i, j) representing i-j coordinates
        self.domain = set(range(1, 10))  # domain of variable is from 1..9 incl. initially
        self.neighbours = set() #set of position_tuple(s) that it has arc consistency with (rows/cols/grid)

    # Remove all items in elements_to_remove (a set) from this variable's domain
    def reduce_domain(self, elements_to_remove):
        self.domain = self.domain.difference(elements_to_remove)
    
    #remove a value from the domain. Called by AC3
    def remove_from_domain(self, value):
        self.domain.remove(value)

    def add_value_to_domain(self, value) :
        self.domain.add(value)

    def domain_empty(self):
        return len(self.domain) == 0
    
    def add_neighbours(self, postion_tuple):
        self.neighbours.add(postion_tuple)

    def __lt__(self, other): #override less-than method
        return len(self.domain) < len(other.domain)

    def __gt__(self, other): #override greater-than method
        return len(self.domain) > len(other.domain)

    def __eq__(self, other):
        return len(self.domain) == len(other.domain) 

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return str(self.position_tuple)

"""
Assignment represents the state of the current CSP assignment. 
If number of unassigned variables = 0, it is complete
"""
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

"""
Encapsulates all variables that needs to be assigned
Single Instance only - stored as an attribute in Sudoku Object
"""
class CSP(object):
    def __init__(self, list_of_cells):
        self.unassigned_dict = dict()  # maps tuple (i, j) to a Variable object (of corresponding position)
        for i in range(0, 9):
            for j in range(0, 9):
                if list_of_cells[i][j] == 0:  # 0 means unassigned initially, is a variable to consider
                    self.unassigned_dict[(i, j)] = Variable((i, j))

    def size(self):
        return len(self.unassigned_dict)

    def get_variable(self, position):
        return self.unassigned_dict[position]
    
    """
    Pre-processing Step to add 
    """
    def gen_binary_constraints(self):
        #Create Arcs to add to constraint sets and neighbours to add to Variables
        def create_arc_neighbour(current_tuple, neighbour_tuple):
            #neighbour is also unassigned, hence common arc
            if neighbour_tuple in self.unassigned_dict: 
                #add neighbours
                curr_var = self.unassigned_dict[current_tuple]
                neighbour_var = self.unassigned_dict[neighbour_tuple]
                curr_var.add_neighbours(neighbour_tuple)
                neighbour_var.add_neighbours(current_tuple)
                
        for (row, col) in self.unassigned_dict: #loop through all positions that are unassigned - they will have arcs
            #Check through row
            for i in range(0, 9):
                if i != col:
                    current_pos = (row, i)
                    create_arc_neighbour((row, col), current_pos)
            
            #Check through columns
            for j in range(0, 9):
                if j != row:
                    current_pos = (j, col)
                    create_arc_neighbour((row, col), current_pos)

            #Check through 3x3 grid
            temp = int(row / 3)
            temp2 = int(col / 3)
            for i in range(temp * 3, (temp + 1) * 3):
                for j in range(temp2 * 3, (temp2 + 1) * 3):
                    current_pos = (i,j)
                    if current_pos != (row, col):
                        create_arc_neighbour((row, col), current_pos)


    """
    Returns a set of tuples representing the positions of the unassigned cells that have arcs with the given cell.
    Called by AC-3 Algorithm
    """
    def get_neighbours_of_cell(self, cell):
        neighbour_set = list()
        return neighbour_set


class Sudoku(object):
    def __init__(self, puzzle):
        self.puzzle = puzzle  # self.puzzle is a 2D List of Integers.
        self.ans = copy.deepcopy(puzzle)  # self.ans is a 2D list of Integers. Will be returned to driver method for output
        self.assignment = Assignment(puzzle)  # initialize assignment based on given input
        self.csp = CSP(puzzle) #
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
        
        #Alternate method to get min_value: Warning: May perform worse, need more research
        # min_variable_key_other = min(self.csp.unassigned_dict, key=self.csp.unassigned_dict.get)
        mrv_variable = self.csp.unassigned_dict[min_variable_key]
        return mrv_variable

    # Inference is forward checking only, returns False if some domain reduced to empty set
    """
    Inference is forward checking only. 
    If some domain of its neighbour is reduced to an empty set, then current value to variable assignment is illegal,
    will return false.
    Else, will return the set of tuples of positions whose domains have their value removed
    """
    def inference(self, csp, var, value):
        failure_flag = False
        set_of_tuples_with_value_removed = set()

        for neighbour_position in var.neighbours:
            if failure_flag:
                break
            if neighbour_position in csp.unassigned_dict: #prevent loop through those neighbours already deleted
                neighbour_var = csp.unassigned_dict[neighbour_position]
                neighbours_domain = neighbour_var.domain #will potentially be reduced
                if value in neighbours_domain:
                    neighbour_var.remove_from_domain(value)
                    set_of_tuples_with_value_removed.add(neighbour_position)
                    if len(neighbours_domain) == 0:
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
        curr_var = self.select_unassigned_variable()  # Returns a Variable object
        del csp.unassigned_dict[curr_var.position_tuple]

        # Counting how constraining a certain value is
        def count_collisions(x):
            count = 0
            curr_row, curr_col = curr_var.position_tuple

            # check row
            for i in range(0, 9):
                if (curr_row, i) in self.csp.unassigned_dict:
                    var = self.csp.unassigned_dict[(curr_row, i)]
                    if x in var.domain:
                        count += 1

            # check col
            for j in range(0, 9):
                if (j, curr_col) in self.csp.unassigned_dict:
                    var = self.csp.unassigned_dict[(j, curr_col)]
                    if x in var.domain:
                        count += 1

            # check 3x3 grid
            temp = int(curr_row / 3)
            temp2 = int(curr_col / 3)
            for a in range(temp * 3, (temp + 1) * 3):
                for b in range(temp2 * 3, (temp2 + 1) * 3):
                    if (a, b) in self.csp.unassigned_dict:
                        var = self.csp.unassigned_dict[(a, b)]
                        if x in var.domain:
                            count += 1

            return count

        # Creating order for domain values
        ordered_values = sorted(list(curr_var.domain), key=count_collisions)

        # x is an integer value from domain of curr_var
        for x in ordered_values:  # No ordering established yet for choosing domain values
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
        start_time = time.time() * 1000
        # Pre-processing to reduce domains
        self.initial_domain_reduction()
        self.csp.gen_binary_constraints()
        # Actual backtracking
        valid_assignment = self.backtrack_search(self.csp)
        print("Inference + MRV + Value Ordering Variant: Time Taken (in ms) = {}, Steps = {}".format(time.time()*1000 - start_time, str(self.steps_taken)))

        # Writing assignment to self.ans for output
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
