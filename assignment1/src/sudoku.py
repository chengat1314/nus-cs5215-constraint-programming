#===============================================================================
# ------------------------------------------------------------------------------
# CONSTRAINT PROGRAMMING: Solving Sudoku via Local Search w/ Simulated Annealing
# ------------------------------------------------------------------------------
# 
# PREREQUISITES
# 
# * Python 2.4+
# 
# RUN
# 
# To run, dump contents into a folder, then run the follow script in this format
# 
# $ python sudoku.py <TEMPERATURE_SEED> <PATH_TO_SUDOKU_TXT_FILE_PUZZLE>
# 
# EXAMPLE
# 
# $ python sudoku.py 0.5 test.txt
# 
# (This will run a sample sudoku puzzle with a seed system temperature of 0.5).
# 
# ABSTRACT
# 
# As described in the header, this solution solves a sudoku puzzle using simulated annealing. Which really means that it tries to pick better and better solutions, but randomly (depending on temerature) decides against that path a short-sighted better neighbourhood that scores better might lead to a dead-end.
# 
# HOW DOES IT EXACTLY WORK?
# 
# 1) Given a puzzle, we fill each subsquare with optimal solutions in that subsquare's context.
# 2) Create a candidate puzzle that swaps 2 positions within a random subsquare.
# 3) Scores the 2 puzzles, gets a delta, and given a comparator with the random seed, we decide whether to use the better puzzle. (More often or not we'd use the better solution)
# 4) Repeat till puzzle is solved.
# 
# SUBTLETIES
# 
# * Steps 1/2 ensures that the 3rd requirement of the puzzle is fulfilled right from the start. Removing an additional constraint makes for less complexity.
# 
# DONE BY: Steven Goh (U087063E)
#===============================================================================

from random import sample, randint
from copy import deepcopy
from math import exp
from random import random
import sys
import time


class Sudoku:
    
    def __init__(self, orig_array, puzzle_array=None):
        self.orig_puzzle_array = orig_array
        self.filled_puzzle = deepcopy(self.orig_puzzle_array) if puzzle_array is None else puzzle_array
        self.slots = self.get_slots()
        self.fill_slots()
        
    @staticmethod
    def new_sudoku_from_file(path):
        f = open(path,'r')
        sstr = f.read().replace('\n',' ').replace('_','0')
        array = sstr.split(' ')
        s = Sudoku(map(int,array))
        return s
        
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
        print "\n"
    
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
    
    i = 0
    timestamp = time.time()
    while current_score > -162:
        
        #swap and make new candidate puzzle
        i += 1
        
        if i % 10000 == 0:
            print "Running %d iteration with the last 10000 iterations in %f seconds." % (i,time.time() - timestamp)
            timestamp = time.time()
        
        candidate_puzzle = current_puzzle.swap_and_new_puzzle()
        candidate_score = candidate_puzzle.score()
        delta_S = float(current_score - candidate_score) #if delta < 0, its better
        
        if (exp((delta_S/T)) - random() > 0):
            current_puzzle = candidate_puzzle
            current_score = candidate_score
        
        T = .9999*T
    
    print "Puzzle solved in %d iterations." % (i)
    return current_puzzle


def main(t_seed, path_to_puzzle_txt):
    puzzle = Sudoku.new_sudoku_from_file(path_to_puzzle_txt)
    solved_puzzle = solve(puzzle,t_seed)
    solved_puzzle.pprint()
    
if __name__ == '__main__':
    sys.exit(main(float(sys.argv[1]), sys.argv[2]))