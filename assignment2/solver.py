import itertools
import sys


__author__ = 'Steven Goh Jian Wen'
__matric_no__ = 'U087063E'


class Arc:
    """
    Relationship between 2 blocks
    """

    def __init__(self, block1, block2):
        self.block1 = block1
        self.block2 = block2

    def has_this_arc(self, worklist):
        for arc in worklist:
            if (arc.block1.equals(self.block1) and arc.block2.equals(self.block2)) or (
                arc.block1.equals(self.block2) and arc.block2.equals(self.block1)):
                return True
        return False

    def constraints(self):
        return [lambda x, y: x[self.block2.index] == y[self.block1.index]]


class Block:
    """
    A block on a nonogram, can be either a row or column.
    """

    def __init__(self, type, index, length):
        self.type = type
        self.index = index
        self.slots = list(set((itertools.product(*[range(2) for _ in range(length)]))))

    def equals(self, block):
        return block.type == self.type and self.index == block.index


class Nonogram:
    """
    A nonogram puzzle
    """

    def build(self):
        """
        populate rows and columns of a nonogram puzzle
        """
        self.rows = [Block('row', i, self.row_length) for i in range(self.col_length)]
        self.cols = [Block('col', i, self.col_length) for i in range(self.row_length)]

    def __init__(self, row_length, col_length, row_hints, col_hints):
        self.col_length = col_length
        self.row_length = row_length
        self.row_hints = row_hints
        self.col_hints = col_hints

    def get_hint(self, block):
        """
        fetches hint as per block
        """
        if block.type == 'row':
            return self.row_hints[block.index]
        return self.col_hints[block.index]

    @staticmethod
    def new_nonogram_from_txt(path_to_puzzle_txt):
        def strip(s):
            s = ' '.join(s.split())
            s = s.replace('\n', '')
            return s

        f = open(path_to_puzzle_txt, 'r')
        lines = f.readlines()

        #row/col length
        lines = filter(lambda x: x[0] != '#', lines)
        length_line = strip(lines[0])
        row_length, col_length = int(length_line.split(" ")[0]), int(length_line.split(" ")[1])

        #col hints
        col_hints = []
        for i in range(1, 1 + row_length):
            line = strip(lines[i]).split(" ")
            col_hints += [tuple(map(int, line))]

        #row hints
        row_hints = []
        for i in range(1 + row_length, 1 + row_length + col_length):
            line = strip(lines[i]).split(" ")
            row_hints += [tuple(map(int, line))]

        return Nonogram(row_length, col_length, row_hints, col_hints)

    def pprint(self):
        def value(idx, list_of_tuples):
            possibilities = []
            for t in list_of_tuples:
                possibilities += [t[idx]]
            if len(possibilities) == 1: return str(possibilities[0]).replace("0", ".").replace("1", "*")
            return "_"

        for r in self.rows:
            s = ""
            for idx, _ in enumerate(self.cols):
                s += "%s " % (value(idx, r.slots))
            print s


def matches_hint(slots, hint):
    """
    Checks that a list of slots (block) matches a hint.
    For example: [0,0,1,1,0,1] matches the hint [2,1]
    """
    #using some string tricks to eliminate intermittent 0s and form the hint
    block_str = "".join(map(str, slots))
    while "00" in block_str:
        block_str = block_str.replace("00", "0")
    str_lis = block_str.split('0')
    block_hint = filter(lambda x: x != 0, map(len, str_lis))
    return list(hint) == block_hint


def arc_reduce(arc_obj):
    """
    Reduces an arc's domain given the constraints present between 2 blocks
    """
    block_lis = [arc_obj.block1, arc_obj.block2]
    arg_combs = list(itertools.product(*[b.slots for b in block_lis]))
    arc_obj.constraints = [lambda x, y: x[arc_obj.block2.index] == y[arc_obj.block1.index]]
    constraint_results = [filter(lambda x: c(*x), arg_combs) for c in arc_obj.constraints][0]

    for idx, b in enumerate(block_lis):
        if len(constraint_results) > 0:
            b.slots = list(set(x[idx] for x in constraint_results))
        else: b.slots = []
    return len(arg_combs) != len(constraint_results)


def _get_unary_constraints(block, hint):
    """
    Unary constraint for a single block
    """
    return lambda x: matches_hint(block.slots, hint)


def solve(nonogram):
    """
    Solves nonogram via CSP (AC-3)
    """
    #build variables
    nonogram.build()

    #unary constraints
    for r in nonogram.rows:
        r.slots = filter(lambda x: matches_hint(x, nonogram.get_hint(r)), r.slots)
    for r in nonogram.cols:
        r.slots = filter(lambda x: matches_hint(x, nonogram.get_hint(r)), r.slots)

    #build worklist
    work_list = []
    for r in nonogram.rows:
        for c in nonogram.cols:
            arc = Arc(r, c)
            if not arc.has_this_arc(work_list): work_list += [arc]

    #binary constraints
    while len(work_list) > 0:
        arc = work_list[0]
        del work_list[0]

        if arc_reduce(arc):
            if len(arc.block1.slots) == 0:
                raise Exception("Failure..")
            other_cols = filter(lambda x: x != arc.block2, nonogram.cols)
            for c in other_cols:
                arc = Arc(arc.block1, c)
                if not arc.has_this_arc(work_list):
                    work_list += [arc]

    return nonogram


def test_unary_constraint():
    """
    unit tests for an unary constraint for a block
    """
    puzzle = Nonogram(3, 3, [(1, 1), (1,), (1,)], [(2,), (1,), (1,)])
    puzzle.build()
    row1 = puzzle.rows[0]
    row1.slots = filter(lambda x: matches_hint(x, (1, 1)), row1.slots)
    assert row1.slots == [(1, 0, 1)]


def _test_puzzle_1():
    """
    Helper method for unit tests to generate a simple nonogram
    """
    puzzle = Nonogram(3, 3, [(1, 1), (1,), (1,)], [(2,), (1,), (1,)])
    puzzle.build()
    for r in puzzle.rows:
        r.slots = filter(lambda x: matches_hint(x, puzzle.get_hint(r)), r.slots)
    for r in puzzle.cols:
        r.slots = filter(lambda x: matches_hint(x, puzzle.get_hint(r)), r.slots)
    return puzzle


def test_arc_reduce():
    """
    Unit tests for arc_reduce()
    """
    puzzle = _test_puzzle_1()

    row1 = puzzle.rows[0]
    col3 = puzzle.cols[2]
    arc = Arc(row1, col3, [
        lambda x, y: x[col3.index] == y[row1.index],
        lambda x, y: matches_hint(x, puzzle.get_hint(row1)),
        lambda x, y: matches_hint(y, puzzle.get_hint(col3))])

    assert arc_reduce(arc)
    assert row1.slots == [(1, 0, 1)]
    assert col3.slots == [(1, 0, 0)]


def test1():
    puzzle = Nonogram(3, 3, [(1, 1), (1,), (1,)], [(2,), (1,), (1,)])
    puzzle = solve(puzzle)
    puzzle.pprint()


def main(path_to_puzzle_txt):
    puzzle = Nonogram.new_nonogram_from_txt(path_to_puzzle_txt)
    puzzle = solve(puzzle)
    puzzle.pprint()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))

