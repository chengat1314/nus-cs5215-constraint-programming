from random import sample, randint
from copy import deepcopy
from math import exp
from random import random


class Sudoku:
    
    def __init__(self, orig_array, puzzle_array=None):
        self.orig_puzzle_array = orig_array
        self.filled_puzzle = deepcopy(self.orig_puzzle_array) if puzzle_array is None else puzzle_array
        self.slots = self.get_slots()
        self.fill_slots()
        
    def get_slots(self):
        """
        Returns a list of array indexes representing slots that are unfilled in puzzle. 
        (or represented as 0 in the original puzzle array)
        """
        return [i[0] for i in enumerate(self.orig_puzzle_array) if i[1] == 0]
        
    def fill_slots(self):
        """
        Fill each subsquare with suboptimal solutions
        """
        for i in range(9):
            all_vals = range(1,10)
            values = self.values_for_subsquare(i)
            unfilled_values = [x for x in all_vals if x not in values]
            for v in unfilled_values:
                for idx,k in enumerate(values):
                    if k == 0:
                        values[idx] = v
                        break
            self.subsquare_values(i,values)
        return values
    
    def index_of_subsquare(self,i):
        """
        Returns the indexes to the puzzle array for a given subsquare
        """
        idxes = range(81)
        row_allowed = [j+((i/3)*3) for j in range(3)]
        cols_allowed = [j+((i%3)*3) for j in range(3)]
        
        idx_to_set = []
        for r in row_allowed:
            for c in cols_allowed:
                idx_to_set += idxes[r*9:r*9+9][c::9]
        return idx_to_set
    
    def subsquare_values(self, i, values):
        """
        Returns the values in the filled_puzzle in a given subsquare
        """
        idx_to_set = self.index_of_subsquare(i)
                
        for i,idx in enumerate(idx_to_set):
            self.filled_puzzle[idx] = values[i]
    
    def values_for_row(self,i):
        """
        Return values in the filled_puzzle given a row
        """
        return self.filled_puzzle[i*9:i*9+9]
        
    def values_for_col(self,i):
        """
        Return values in the filled_puzzle given a col
        """
        return self.filled_puzzle[i::9]
    
    def values_for_subsquare(self,i):
        """
        Return values in a given subsquare of the filled_puzzle
        """
        row_allowed = [j+((i/3)*3) for j in range(3)]
        cols_allowed = [j+((i%3)*3) for j in range(3)]
        
        values = []
        for r in row_allowed:
            for c in cols_allowed:
                values += self.values_for_row(r)[c::9]
                
        return values
            
    
    def score(self):
        """
        Scores the puzzle, -1 for each unique value in a row/col.
        -162 for perfect score
        """
        
        score = 0
        for i in range(9):
            score -= len(set(self.values_for_col(i)))
            score -= len(set(self.values_for_row(i)))
        return score
    
    def pprint(self):
        """
        Pretty Print the puzzle, because we're superifical creatures
        """
        print "\n"
        for i in range(9):
            row = self.values_for_row(i)
            print " ".join(map(str,row))
    
    def swap_and_new_puzzle(self):
        """
        Swap 2 values from a random subsquare
        """
        subsquare_idxes = self.index_of_subsquare(randint(0,8))
        subsquare_idxes = [x for x in subsquare_idxes if x in self.slots]
        if len(subsquare_idxes) >= 2:
            idx_a,idx_b = sample(subsquare_idxes,2)
            new_puzzle = deepcopy(self.filled_puzzle)
            new_puzzle[idx_a], new_puzzle[idx_b] = new_puzzle[idx_b], new_puzzle[idx_a]
            return Sudoku(self.orig_puzzle_array,new_puzzle)
        return self
    

def solve(sudoku_puzzle, T=None):
    
    T = .5 if T is None else T
    current_score = sudoku_puzzle.score()
    current_puzzle = sudoku_puzzle
    
    while current_score > -162:
        
        #new swapped puzzle
        candidate_puzzle = current_puzzle.swap_and_new_puzzle()
        candidate_score = candidate_puzzle.score()
        delta_S = float(current_score - candidate_score) #if delta < 0, its better
        
        if (exp((delta_S/T)) - random() > 0):
            current_puzzle = candidate_puzzle
            current_score = candidate_score
        
        T = .9999*T
    
    return current_puzzle


def run():
    f = open('/home/nubela/Workspace/cs5215/assignment1/src/test.txt','r')
    str = f.read().replace('\n',' ').replace('_','0')
    array = str.split(' ')
    s = Sudoku(map(int,array))
    solve(s).pprint()
    
run()