from typing import Tuple
import re
from CSP import Assignment, Problem, UnaryConstraint, BinaryConstraint

#TODO (Optional): Import any builtin library or define any helper function you want to use

# This is a class to define for cryptarithmetic puzzles as CSPs
class CryptArithmeticProblem(Problem):
    LHS: Tuple[str, str]
    RHS: str

    # Convert an assignment into a string (so that is can be printed).
    def format_assignment(self, assignment: Assignment) -> str:
        LHS0, LHS1 = self.LHS
        RHS = self.RHS
        letters = set(LHS0 + LHS1 + RHS)
        formula = f"{LHS0} + {LHS1} = {RHS}"
        postfix = []
        valid_values = list(range(10))
        for letter in letters:
            value = assignment.get(letter)
            if value is None: continue
            if value not in valid_values:
                postfix.append(f"{letter}={value}")
            else:
                formula = formula.replace(letter, str(value))
        if postfix:
            formula = formula + " (" + ", ".join(postfix) +  ")" 
        return formula

    @staticmethod
    def from_text(text: str) -> 'CryptArithmeticProblem':
        # Given a text in the format "LHS0 + LHS1 = RHS", the following regex
        # matches and extracts LHS0, LHS1 & RHS
        # For example, it would parse "SEND + MORE = MONEY" and extract the
        # terms such that LHS0 = "SEND", LHS1 = "MORE" and RHS = "MONEY"
        pattern = r"\s*([a-zA-Z]+)\s*\+\s*([a-zA-Z]+)\s*=\s*([a-zA-Z]+)\s*"
        match = re.match(pattern, text)
        if not match: raise Exception("Failed to parse:" + text)
        LHS0, LHS1, RHS = [match.group(i+1).upper() for i in range(3)]

        problem = CryptArithmeticProblem()
        problem.LHS = (LHS0, LHS1)
        problem.RHS = RHS

        #TODO Edit and complete the rest of this function
        # problem.variables:    should contain a list of variables where each variable is string (the variable name)
        # problem.domains:      should be dictionary that maps each variable (str) to its domain (set of values)
        #                       For the letters, the domain can only contain integers in the range [0,9].
        # problem.constaints:   should contain a list of constraint (either unary or binary constraints).

        problem.variables = []
        problem.domains = {}
        problem.constraints = []
        
        # create the set of unique letters
        letters = set(LHS0 + LHS1 + RHS)
        # define the domain for each letter
        # all letters can take values from 0 to 9
        # but leading letters cannot be 0
        leading_letters = {LHS0[0], LHS1[0], RHS[0]}
        for letter in letters:
            problem.variables.append(letter)
            if letter in leading_letters:
                problem.domains[letter] = set(range(1, 10))  # leading letters cannot be 0
            else:
                problem.domains[letter] = set(range(0, 10))
        
        # construct the binary and unary constraints
              
        # add all-different constraint
        # this ensures that all letters have different values
        def all_different_constraint(assignment: Assignment) -> bool:
            assigned_values = [value for value in assignment.values() if value is not None]
            return len(assigned_values) == len(set(assigned_values))
        # single coloumn constraint
        def column_constraint(col: int, carry_in: int, carry_out: int, col_letters: Tuple[str, str, str]) -> BinaryConstraint:
            """
            Creates a constraint for a single column:
                A  (from word1)
            + B  (from word2)
            + carry_in
            = C  (result letter)
            + 10 * carry_out
            """
            LHS0_letter, LHS1_letter, RHS_letter = col_letters
            def constraint(assignment: Assignment) -> bool:
                if (LHS0_letter not in assignment or LHS1_letter not in assignment or RHS_letter not in assignment):
                    return True  # not all variables assigned yet -> no violation
                LHS0_value = assignment[LHS0_letter]
                LHS1_value = assignment[LHS1_letter]
                RHS_value = assignment[RHS_letter]
                if LHS0_value is None or LHS1_value is None or RHS_value is None:
                    return True  # not all variables assigned yet -> no violation
                total = LHS0_value + LHS1_value + carry_in
                return (total % 10 == RHS_value) and (total // 10 == carry_out)
            return constraint
        
        # create carry variables and column constraints
        max_length = max(len(LHS0), len(LHS1), len(RHS))
        carry_vars = [f"carry_{i}" for i in range(max_length + 1)]
        # add carry variables to problem
        # define their domains (0 or 1)
        for carry_var in carry_vars:
            problem.variables.append(carry_var)
            problem.domains[carry_var] = {0, 1}  # carry can only be 0 or 1
        # add column constraints
        # for each column, create a constraint
        for i in range(max_length):
            LHS0_letter = LHS0[-(i+1)] if i < len(LHS0) else None
            LHS1_letter = LHS1[-(i+1)] if i < len(LHS1) else None
            RHS_letter = RHS[-(i+1)] if i < len(RHS) else None
            col_letters = (LHS0_letter, LHS1_letter, RHS_letter)
            carry_in = carry_vars[i]
            carry_out = carry_vars[i+1]
            constraint = column_constraint(i, carry_in, carry_out, col_letters)
            problem.constraints.append(BinaryConstraint([LHS0_letter, LHS1_letter, RHS_letter, carry_in, carry_out], constraint))
            
        # add all-different constraint as a unary constraint
        problem.constraints.append(UnaryConstraint(problem.variables, all_different_constraint))
        
        
        return problem

    # Read a cryptarithmetic puzzle from a file
    @staticmethod
    def from_file(path: str) -> "CryptArithmeticProblem":
        with open(path, 'r') as f:
            return CryptArithmeticProblem.from_text(f.read())