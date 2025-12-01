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
        # -------------------------
        
        # 1. Setup letter variables
        
        # Deterministic order: first-appearance of each letter
        letters = list(dict.fromkeys(LHS0 + LHS1 + RHS))
        problem.variables = list(letters)

        # Domain for each letter is 0-9
        problem.domains = {l: set(range(10)) for l in letters}
        
        # -------------------------
        
        # 2. Constraints for letters
        
        # Leading letters cannot be zero
        # First letter of LHS0, LHS1, and RHS cannot be 0
        # as in the instructions document:
        # The first letter in each string cannot be 0 
        leading = {LHS0[0], LHS1[0], RHS[0]}
        for L in leading:
            problem.constraints.append(UnaryConstraint(L, lambda v: v != 0))

        
        # All letters must be different
        for i in range(len(letters)):
            for j in range(i + 1, len(letters)):
                A, B = letters[i], letters[j]
                problem.constraints.append(BinaryConstraint((A, B), lambda x, y: x != y))

        
        # 3. Prepare for column-wise processing
        
        # Get lengths
        m0, m1, mr = len(LHS0), len(LHS1), len(RHS)
        n = max(m0, m1)  # number of columns to process
        
        # Reverse strings to process from least significant digit (rightmost)
        # A = LHS0 reversed, padded with "_" to length n
        # B = LHS1 reversed, padded with "_" to length n
        # C = RHS reversed
        
        A = LHS0[::-1] + "_" * (n - m0)  # pad with "_" if shorter
        B = LHS1[::-1] + "_" * (n - m1)
        C = RHS[::-1]                    # may have extra leading digit

        
        # 4. Carry variables
        # Carry variables: C0..Cn (n+1 variables). C0 always 0
        carry_vars = [f"C{i}" for i in range(n + 1)]
        for cv in carry_vars:
            problem.variables.append(cv)
            problem.domains[cv] = {0, 1}  # carries are either 0 or 1
        problem.constraints.append(UnaryConstraint("C0", lambda v: v == 0))  # initial carry is 0

        
        # 5. Column-wise constraints
        for i in range(n):
            # Letters for current column, "_" if no letter exists
            # aL is letter from LHS0, bL from LHS1, rL from RHS
            aL = A[i] if i < len(A) else "_"
            bL = B[i] if i < len(B) else "_"
            rL = C[i] if i < len(C) else "_"

            cin = f"C{i}"      # carry in
            cout = f"C{i+1}"   # carry out

            
            # 5a. Valid tuples for this column
            valid_tuples = set()
            for av in (range(10) if aL != "_" else [0]):  # possible value for aL
                for bv in (range(10) if bL != "_" else [0]):  # possible value for bL
                    for rv in (range(10) if rL != "_" else [0]):  # possible value for result digit
                        for cinv in (0, 1):  # possible incoming carry
                            for coutv in (0, 1):  # possible outgoing carry
                                # Valid if sum with carry matches the digit + 10*carry out
                                if av + bv + cinv == rv + 10 * coutv:
                                    valid_tuples.add((av, bv, rv, cinv, coutv))

            
            # 5b. Identify active variables in this column
            # where active means not "_"
            all_vars = [aL, bL, rL, cin, cout]  # potential variables in this column
            positions = [idx for idx, v in enumerate(all_vars) if v != "_"]  # only keep actual variables
            vars_in_column = [all_vars[idx] for idx in positions]

            # Skip trivial columns with <=1 active variable
            if len(vars_in_column) <= 1:
                continue

            
            # 5c. Create auxiliary tuple variable for this column
            aux = f"TUP_{i}"
            problem.variables.append(aux)
            # Project each tuple to active variables only
            problem.domains[aux] = set(tuple(t[pos] for pos in positions) for t in valid_tuples)

            
            # 5d. Constraint linking auxiliary variable to active variables
            for idx, var in enumerate(vars_in_column):
                problem.constraints.append(
                    BinaryConstraint((var, aux), lambda v, tup, idx=idx: v == tup[idx])
                )

        
        # 6. Final carry constraint
        if mr == n + 1:
            # If RHS has extra leading digit, it must equal final carry
            leading_rhs_var = RHS[0]
            problem.constraints.append(BinaryConstraint((leading_rhs_var, f"C{n}"), lambda r, c: r == c))
        else:
            # Otherwise final carry must be zero
            final_carry = f"C{n}"
            problem.constraints.append(UnaryConstraint(final_carry, lambda v: v == 0))

        return problem
    
    # Read a cryptarithmetic puzzle from a file
    @staticmethod
    def from_file(path: str) -> "CryptArithmeticProblem":
        with open(path, 'r') as f:
            return CryptArithmeticProblem.from_text(f.read())
    # @staticmethod
    # def from_text(text: str) -> 'CryptArithmeticProblem':
    #     # Given a text in the format "LHS0 + LHS1 = RHS", the following regex
    #     # matches and extracts LHS0, LHS1 & RHS
    #     # For example, it would parse "SEND + MORE = MONEY" and extract the
    #     # terms such that LHS0 = "SEND", LHS1 = "MORE" and RHS = "MONEY"
    #     pattern = r"\s*([a-zA-Z]+)\s*\+\s*([a-zA-Z]+)\s*=\s*([a-zA-Z]+)\s*"
    #     match = re.match(pattern, text)
    #     if not match: raise Exception("Failed to parse:" + text)
    #     LHS0, LHS1, RHS = [match.group(i+1).upper() for i in range(3)]

    #     problem = CryptArithmeticProblem()
    #     problem.LHS = (LHS0, LHS1)
    #     problem.RHS = RHS

    #     problem.variables = []
    #     problem.domains = {}
    #     problem.constraints = []
        
    #     # -------------------------
    #     # 1. Letter variables
    #     # -------------------------
        
    #     # Identify all unique letters in the puzzle
    #     letters = set(LHS0 + LHS1 + RHS)
    #     problem.variables.extend(letters)
        
    #     # create domains for each letter
    #     for letter in letters:
    #         problem.domains[letter] = set(range(10))
        
    #     # All letters must be different
    #     for i, l1 in enumerate(problem.variables):
    #         for l2 in problem.variables[i+1:]:
    #             problem.constraints.append(BinaryConstraint((l1, l2), lambda x, y: x != y))
        
    #     # Leading letters cannot be 0
    #     for lead in (LHS0[0], LHS1[0], RHS[0]):
    #         problem.constraints.append(UnaryConstraint(lead, lambda x: x != 0))
        
    #     # -------------------------
    #     # 2. Carry variables (auxiliary)
    #     # -------------------------
    #     max_length = max(len(LHS0), len(LHS1), len(RHS))
    #     carries = [f"C{i}" for i in range(max_length)]
    #     problem.variables.extend(carries)
        
    #     # create domains for each carry
    #     for c in carries:
    #         problem.domains[c] = set(range(2))  # 0 or 1
        
    #     # C0 is always 0
    #     problem.constraints.append(UnaryConstraint(carries[0], lambda x: x == 0))
        
    #     # -------------------------
    #     # 3. Reverse for LSB-first processing
    #     # -------------------------
    #     LHS0 = LHS0[::-1]
    #     LHS1 = LHS1[::-1]
    #     RHS = RHS[::-1]
        
    #     # -------------------------
    #     # 4. Domains for mega variables as we will use them in constraints
    #     # -------------------------
    #     first_domain = set((i, j, k, l) for i in range(10) for j in range(10) for k in range(2) for l in range(10))
    #     second_domain = set((i, j, k, l) for i in range(10) for j in range(10) for k in range(2) for l in range(2))
    #     third_domain = set((i, j, k) for i in range(10) for j in range(2) for k in range(10))  # corrected tuple size
    #     fourth_domain = set((i, j, k) for i in range(10) for j in range(2) for k in range(2))
        
    #     # -------------------------
    #     # 5. Helper to add mega variables and constraints
    #     # -------------------------
    #     def add_mega_variable(problem, mega_var, domain, unary_condition, linked_vars):
    #         problem.variables.append(mega_var)
    #         problem.domains[mega_var] = domain
    #         problem.constraints.append(UnaryConstraint(mega_var, unary_condition))
    #         # FIXED: lambda late-binding issue
    #         for i, var in enumerate(linked_vars):
    #             problem.constraints.append(BinaryConstraint(
    #                 (var, mega_var), lambda x, t, i=i: x == t[i]
    #             ))
        
    #     # -------------------------
    #     # 6. Add constraints column by column
    #     # -------------------------
    #     max_len = max(len(LHS0), len(LHS1))
        
    #     for i in range(max_len):
    #         letter0 = LHS0[i] if i < len(LHS0) else None
    #         letter1 = LHS1[i] if i < len(LHS1) else None
    #         rhs_letter = RHS[i] if i < len(RHS) else None
    #         carry_in = f"C{i}"
    #         carry_out = f"C{i+1}" if i+1 < max_length else None
            
    #         # Only letter0
    #         if letter0 and not letter1:
    #             mega_sum = (letter0, carry_in, rhs_letter)
    #             add_mega_variable(problem, mega_sum, third_domain, lambda a: (a[0]+a[1])%10==a[2], [letter0, carry_in, rhs_letter])
    #             if carry_out:
    #                 mega_carry = (letter0, carry_in, carry_out)
    #                 add_mega_variable(problem, mega_carry, fourth_domain, lambda a: (a[0]+a[1])//10==a[2], [letter0, carry_in, carry_out])
            
    #         # Only letter1
    #         elif letter1 and not letter0:
    #             mega_sum = (letter1, carry_in, rhs_letter)
    #             add_mega_variable(problem, mega_sum, third_domain, lambda a: (a[0]+a[1])%10==a[2], [letter1, carry_in, rhs_letter])
    #             if carry_out:
    #                 mega_carry = (letter1, carry_in, carry_out)
    #                 add_mega_variable(problem, mega_carry, fourth_domain, lambda a: (a[0]+a[1])//10==a[2], [letter1, carry_in, carry_out])
            
    #         # Both letters
    #         elif letter0 and letter1:
    #             mega_sum = (letter0, letter1, carry_in, rhs_letter)
    #             add_mega_variable(problem, mega_sum, first_domain, lambda a: (a[0]+a[1]+a[2])%10==a[3], [letter0, letter1, carry_in, rhs_letter])
    #             if carry_out:
    #                 mega_carry = (letter0, letter1, carry_in, carry_out)
    #                 add_mega_variable(problem, mega_carry, second_domain, lambda a: (a[0]+a[1]+a[2])//10==a[3], [letter0, letter1, carry_in, carry_out])
        
    #     # Handle possible last RHS digit (extra carry)
    #     if len(RHS) > max(len(LHS0), len(LHS1)):
    #         last_rhs = RHS[-1]
    #         last_carry = f"C{len(RHS)-1}"
    #         problem.constraints.append(BinaryConstraint((last_rhs, last_carry), lambda r, c: r == c))
        
    #     return problem
