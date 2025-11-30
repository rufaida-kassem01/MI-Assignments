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
        #                       For example, if the constraint is "A != 0", then the constraint should be UnaryConstraint("A", lambda x: x != 0)
        #                       we can use lambda functions to define the constraint functions

        problem.variables = []
        problem.domains = {}
        problem.constraints = []



        # add variables and domains
        for letter in LHS0 + LHS1 + RHS:
            # first make sure that the letter is not already in the problem.variables
            if letter in problem.variables:
                continue
            problem.variables.append(letter) # add all letters to the problem
            problem.domains[letter] = set(range(10)) # add all letters to the problem (domain is 0-9)

        # the constrains are as follows:
        # 1. all letters in LHS0, LHS1 and RHS should be different
        # 2. the first letter of LHS0 and LHS1 should not be 0
        # 3. the sum of LHS0 and LHS1 should be equal to RHS

        # 1.
        # add unary constraints to first letter of LHS0 and LHS1 --> not equal to 0
        problem.constraints.append(UnaryConstraint(LHS0[0], lambda x: x != 0))
        problem.constraints.append(UnaryConstraint(LHS1[0], lambda x: x != 0))
        problem.constraints.append(UnaryConstraint(RHS[0], lambda x: x != 0))


        # 2.
        # to add the constraints that all letters in LHS0, LHS1 and RHS should be different
        # we can loop through all letters in LHS0, LHS1 and RHS, and add binary constraints for each pair of letters
        for var in problem.variables:
            for var2 in problem.variables:
                if var != var2:
                    problem.constraints.append(BinaryConstraint((var, var2), lambda a, b: a != b))


        # add carry variables and domains
        for i in range(len(RHS)):
            # carry_variables.append("CARRY" + str(i)) # add carry variables to the problem
            # carry_domains["CARRY" + str(i)] = set(range(2)) # add carry variables to the problem (domain is 0-1)
            problem.variables.append("CARRY" + str(i)) # add carry variables to the problem
            problem.domains["CARRY" + str(i)] = set(range(2)) # add carry variables to the problem (domain is 0-1)
            

        # the fisrt carry variable should be 0
        problem.constraints.append(UnaryConstraint("CARRY0", lambda x: x == 0))

        # reverse the LHS0, LHS1 and RHS
        LHS0 = LHS0[::-1]
        LHS1 = LHS1[::-1]
        RHS = RHS[::-1]

        # print("LHS0: ", LHS0)
        # print("LHS1: ", LHS1)
        # print("RHS: ", RHS)
    

        dom1 = set()
        for i in range(10):
            for j in range(10):
                for k in range(2):
                    for l in range(10):
                        dom1.add((i, j, k, l))

        dom2 = set()
        for i in range(10):
            for j in range(10):
                for k in range(2):
                    for l in range(2):
                        dom2.add((i, j, k, l))

        dom3 = set()
        for i in range(10):
            for j in range(2):
                for k in range(10):
                    dom3.add((i, j, k))

        dom4 = set()
        for i in range(10):
            for j in range(2):
                for k in range(2):
                    dom4.add((i, j, k))

        
        # now let's add the constraints
        # (LHS0[i] + LHS1[i] + CARRYi) % 10 = RHS[i]
        # (LHS0[i] + LHS1[i] + CARRYi) // 10 = CARRY(i+1)
        for i in range(max(len(LHS0), len(LHS1))):
            if i >= len(LHS1): # len of LHS0 > len of LHS1
                # LHS0[i] + CARRYi = RHS[i]
                # if no corresponding letter in LHS1, then add a constraint with "CARRY"
                # first push the tuple as a variable
                problem.variables.append((LHS0[i], "CARRY" + str(i), RHS[i]))
                # the domain of this tuple will be all combinations of 0-9 and 0-1 and 0-9
                problem.domains[(LHS0[i], "CARRY" + str(i), RHS[i])] = dom3
                problem.constraints.append(UnaryConstraint((LHS0[i], "CARRY" + str(i), RHS[i]), lambda a: (a[0] + a[1]) % 10 == a[2]))
                # now link the mega variabels with each single variable
                problem.constraints.append(BinaryConstraint((LHS0[i], (LHS0[i], "CARRY" + str(i), RHS[i])), lambda a, b: a == b[0]))
                problem.constraints.append(BinaryConstraint(("CARRY" + str(i), (LHS0[i], "CARRY" + str(i), RHS[i])), lambda a, b: a == b[1]))
                problem.constraints.append(BinaryConstraint((RHS[i], (LHS0[i], "CARRY" + str(i), RHS[i])), lambda a, b: a == b[2])) # this will print the lambda_var such that a is the value of RHS[i] and b is the tuple (LHS0[i], "CARRY" + str(i), RHS[i]) so a is of size 1 and b is of size 3

                if i < len(RHS) - 1:
                    problem.variables.append((LHS0[i], "CARRY" + str(i), "CARRY" + str(i+1)))
                    problem.domains[(LHS0[i], "CARRY" + str(i), "CARRY" + str(i+1))] = dom4
                    problem.constraints.append(UnaryConstraint((LHS0[i], "CARRY" + str(i), "CARRY" + str(i+1)), lambda a: (a[0] + a[1]) // 10 == a[2]))
                    # now link the mega variabels with each single variable
                    problem.constraints.append(BinaryConstraint(("CARRY" + str(i+1), (LHS0[i], "CARRY" + str(i), "CARRY" + str(i+1))), lambda a, b: a == b[2]))
                    problem.constraints.append(BinaryConstraint((LHS0[i], (LHS0[i], "CARRY" + str(i), "CARRY" + str(i+1))), lambda a, b: a == b[0]))
                    problem.constraints.append(BinaryConstraint(("CARRY" + str(i), (LHS0[i], "CARRY" + str(i), "CARRY" + str(i+1))), lambda a, b: a == b[1]))
            elif i >= len(LHS0):
                problem.variables.append((LHS1[i], "CARRY" + str(i), RHS[i]))
                # the domain of this tuple will be all combinations of 0-9 and 0-1 and 0-9
                problem.domains[(LHS1[i], "CARRY" + str(i), RHS[i])] = dom3
                problem.constraints.append(UnaryConstraint((LHS1[i], "CARRY" + str(i), RHS[i]), lambda a: (a[0] + a[1]) % 10 == a[2]))
                # now link the mega variabels with each single variable
                problem.constraints.append(BinaryConstraint((RHS[i], (LHS1[i], "CARRY" + str(i), RHS[i])), lambda a, b: a == b[2]))
                problem.constraints.append(BinaryConstraint((LHS1[i], (LHS1[i], "CARRY" + str(i), RHS[i])), lambda a, b: a == b[0]))
                problem.constraints.append(BinaryConstraint(("CARRY" + str(i), (LHS1[i], "CARRY" + str(i), RHS[i])), lambda a, b: a == b[1]))
                if i < len(RHS) - 1:
                    problem.variables.append((LHS1[i], "CARRY" + str(i), "CARRY" + str(i+1)))
                    problem.domains[(LHS1[i], "CARRY" + str(i), "CARRY" + str(i+1))] = dom4
                    problem.constraints.append(UnaryConstraint((LHS1[i], "CARRY" + str(i), "CARRY" + str(i+1)), lambda a: (a[0] + a[1]) // 10 == a[2]))
                    # now link the mega variabels with each single variable
                    problem.constraints.append(BinaryConstraint(("CARRY" + str(i+1), (LHS1[i], "CARRY" + str(i), "CARRY" + str(i+1))), lambda a, b: a == b[2]))
                    problem.constraints.append(BinaryConstraint((LHS1[i], (LHS1[i], "CARRY" + str(i), "CARRY" + str(i+1))), lambda a, b: a == b[0]))
                    problem.constraints.append(BinaryConstraint(("CARRY" + str(i), (LHS1[i], "CARRY" + str(i), "CARRY" + str(i+1))), lambda a, b: a == b[1]))
            else:
                # (LHS0[i] + LHS1[i] + CARRYi) % 10 = RHS[i]  --> this will be a unary constraint and then we will link the mega variable (LHS0[i], LHS1[i], "CARRY" + str(i)) with each single variable
                # first append the tuple as a variable
                problem.variables.append((LHS0[i], LHS1[i], "CARRY" + str(i), RHS[i]))
                # the domain of this tuple will be all combinations of 0-9 and 0-9 and 0-1 and 0-9
                problem.domains[(LHS0[i], LHS1[i], "CARRY" + str(i), RHS[i])] = dom1
                problem.constraints.append(UnaryConstraint((LHS0[i], LHS1[i], "CARRY" + str(i), RHS[i]), lambda a: (a[0] + a[1] + a[2]) % 10 == a[3]))
                # now link the mega variabels with each single variable
                problem.constraints.append(BinaryConstraint((LHS0[i], (LHS0[i], LHS1[i], "CARRY" + str(i), RHS[i])), lambda a, b: a == b[0]))
                problem.constraints.append(BinaryConstraint((LHS1[i], (LHS0[i], LHS1[i], "CARRY" + str(i), RHS[i])), lambda a, b: a == b[1]))
                problem.constraints.append(BinaryConstraint(("CARRY" + str(i), (LHS0[i], LHS1[i], "CARRY" + str(i), RHS[i])), lambda a, b: a == b[2]))
                problem.constraints.append(BinaryConstraint((RHS[i], (LHS0[i], LHS1[i], "CARRY" + str(i), RHS[i])), lambda a, b: a == b[3]))
                # now let's add the constraint for the carry
                # (LHS0[i] + LHS1[i] + CARRYi) // 10 = CARRY(i+1)
                problem.variables.append((LHS0[i], LHS1[i], "CARRY" + str(i), "CARRY" + str(i+1)))
                # the domain of this tuple will be all combinations of 0-9 and 0-9 and 0-1 and 0-1
                problem.domains[(LHS0[i], LHS1[i], "CARRY" + str(i), "CARRY" + str(i+1))] = dom2
                problem.constraints.append(UnaryConstraint((LHS0[i], LHS1[i], "CARRY" + str(i), "CARRY" + str(i+1)), lambda a: (a[0] + a[1] + a[2]) // 10 == a[3]))
                # now link the mega variabels with each single variable
                problem.constraints.append(BinaryConstraint((LHS0[i], (LHS0[i], LHS1[i], "CARRY" + str(i), "CARRY" + str(i+1))), lambda a, b: a == b[0]))
                problem.constraints.append(BinaryConstraint((LHS1[i], (LHS0[i], LHS1[i], "CARRY" + str(i), "CARRY" + str(i+1))), lambda a, b: a == b[1]))
                problem.constraints.append(BinaryConstraint(("CARRY" + str(i), (LHS0[i], LHS1[i], "CARRY" + str(i), "CARRY" + str(i+1))), lambda a, b: a == b[2]))
                problem.constraints.append(BinaryConstraint(("CARRY" + str(i+1), (LHS0[i], LHS1[i], "CARRY" + str(i), "CARRY" + str(i+1))), lambda a, b: a == b[3]))

        # # now let's add the constraint of the last char in the result if exist
        if len(RHS) > max(len(LHS0), len(LHS1)):
            problem.constraints.append(BinaryConstraint((RHS[-1], "CARRY" + str(len(RHS) - 1)), lambda a, b: a == b))
        

        return problem

    # Read a cryptarithmetic puzzle from a file
    @staticmethod
    def from_file(path: str) -> "CryptArithmeticProblem":
        with open(path, 'r') as f:
            return CryptArithmeticProblem.from_text(f.read())