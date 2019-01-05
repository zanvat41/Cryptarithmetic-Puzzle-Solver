import sys
import math
import time
import copy
from collections import deque


# Define all operators
OPs = ['+', '-']
#  number of search
global search
#  number arc pruning calls
global prune
search = 0
prune = 0

# Functions for plain DFSB
def Select_Unassigned_Var(Vars, assignment):
    # var is a letter
    for var in Vars:
        if not var in assignment:
            return var
    return -1


# Algorithm from lecture slide
def Plain_Backtracking(assignment,Domains, Cons):
    global search
    if len(assignment) == len(Domains):
        if finalEval(assignment, Cons):
            return assignment
        else:
            return 'failure'
    Vars = list(Domains.keys())
    var = Select_Unassigned_Var(Vars, assignment)
    if var == -1:
        return 'failure'
    for digit in Domains[var]:
        if is_Consistent(var, digit, assignment, Cons):
            search += 1
            assignment[var] = digit
            result = Plain_Backtracking(assignment, Domains, Cons)
            if result != 'failure':
                return result
            assignment.pop(var)
    return 'failure'


# Functions for DFSB++
# Count constraints for a variable
# The AC-3 function modified from the algorithm in lecture slides
def AC3(assignment, l, Cons, domainsNew):
    while len(l) != 0:
        a = l.popleft()
        [remove, domainsNew] = Remove_Inconsistent_Values(a, assignment, Cons, domainsNew)

        # If you remove anythingfrom a variable, then
        # add all arcs that go into that variable back
        # into the queue
        if remove:
            global prune
            prune += 1
            if len(domainsNew[a[0]]) == 0:
                #print("fff")
                #print(domainsNew)
                return (False, domainsNew)

            # List of neighbors of a[0] except a[1]
            neighborList = []
            for con in Cons:
                if a[0] in con:
                    con1 = con.replace('+', ' ')
                    con1 = con1.replace('*', ' ')
                    con1 = con1.replace('==', ' ')
                    conList = con1.split()
                    if '10' in conList:
                        conList.remove('10')
                    conList.remove(a[0])
                    for conVar in conList:
                        if conVar not in neighborList:
                            neighborList.append(conVar)

            if a[0][0] != '$':
                for key in domainsNew:
                    if key != a[0] and key[0] != '$' and key not in neighborList:
                        neighborList.append(key)

            neighborList = [item for item in neighborList if item != a[1]]
            neighborList = [item for item in neighborList if item != a[0]]
            #print("var:"+a[0])
            #print("ne:"+str(neighborList))

            for var in neighborList:
                b = [var, a[0]]
                if not var in assignment and var != a[0]:
                    l.append(b)

    return (True, domainsNew)


def Remove_Inconsistent_Values(a, assignment, Cons, domainsNew):
    removed = False
    if a[0] == a[1]:
        #print("hello")
        return (removed, domainsNew)
    for digit in domainsNew[a[0]]:
        isPossible = False
        assignment[a[0]] = digit
        for digit2 in domainsNew[a[1]]:
            if is_Consistent(a[1], digit2, assignment, Cons):
                #print("here")
                isPossible = True
                break
        if not isPossible:
            #print("a0:"+a[0]+":"+str(digit))
            #print("a1:"+a[1] + ":" + str(digit2))
            #print(assignment)
            #print(domainsNew)
            domainsNew[a[0]].remove(digit)
            removed = True
        assignment.pop(a[0])
    return (removed, domainsNew)



def Count_Constraints(var, Cons):
    consNum = 0
    for con in Cons:
        if var in con:
            consNum += 1
    return consNum


# Pick the most constrained variable
def Select_Unassigned_Plus(assignment, Vars, Cons, Domains, mode):
    res = -1
    min = math.inf
    if mode == 1:
        for var in Vars:
            consNum = Count_Constraints(var, Cons)
            if (consNum < min) and (var not in assignment):
                min = consNum
                res = var
    else:
        for var in Vars:
            if len(Domains[var]) < min and var not in assignment:
                min = len(Domains[var])
                res = var
    return res


# Algorithm from lecture slide
def Backtracking_Plus(assignment, Domains, Cons, mode):
    global search
    if len(assignment) == len(Domains):
        if finalEval(assignment, Cons):
            return assignment
        else:
            return 'failure'

    Vars = list(Domains.keys())
    var = Select_Unassigned_Plus(assignment, Vars, Cons, Domains, mode)

    if var == -1:
        #print("helloaa")
        return 'failure'

    #for digit in Domains[var]:
    #    if is_Consistent(var, digit, assignment, Cons):
    #        search += 1
    #        assignment[var] = digit
    #        result = Plain_Backtracking(assignment, Domains, Cons)
    #        if result != 'failure':
    #            return result
    #        assignment.pop(var)

    for digit in Domains[var]:
        #if var == 'A':
         #   print("Var:"+var+",d:"+str(digit))
         #   print(assignment)
         #   print(Domains)
        domainsNew = copy.deepcopy(Domains)
        if is_Consistent(var, digit, assignment, Cons):
            domainsNew[var] = [item for item in Domains[var] if item == digit]
            #print("Var1:" + var + ",d:" + str(digit))
            #print(domainsNew)
            array = []

            neighborList = []
            for con in Cons:
                if var in con:
                    con1 = con.replace('+', ' ')
                    con1 = con1.replace('*', ' ')
                    con1 = con1.replace('==', ' ')
                    conList = con1.split()
                    if '10' in conList:
                        conList.remove('10')
                    conList.remove(var)
                    for conVar in conList:
                        if conVar not in neighborList:
                            neighborList.append(conVar)

            if var[0] != '$':
                for key in domainsNew:
                    if key != var and key[0] != '$' and key not in neighborList:
                        neighborList.append(key)

            neighborList = [item for item in neighborList if item != var]
            for var2 in neighborList:
                a = [var2, var]
                if not var2 in assignment:
                    array.append(a)
                l = deque(array)
            [inference, dlist] = AC3(assignment, l, Cons, domainsNew)
            if inference:
                domainsNew[var] = [item for item in Domains[var] if item == digit]
                #print("Var2:" + var + ",d:" + str(digit))
                #print(domainsNew)
                search += 1
                assignment[var] = digit
                domainsNew = dlist
                result = Backtracking_Plus(assignment, domainsNew, Cons, mode)
                if result != 'failure':
                    return result
                assignment.pop(var)
    #print("hello")
    return 'failure'


# Other helper functions
# Get the constraints for addition equations
def addCons(op1, op2, res, Domains):
    Cons = []
    # Swap op1 and op2 if len(op2) > len(op1)
    if len(op2) > len(op1):
        temp = op1
        op1 = op2
        op2 = temp

    for i in range(len(res)):
        # Auxiliary variable
        newAux = '$' + str(i)
        if i == 0:
            Con = op1[-1]+'+'+op2[-1]+'=='+res[-1]+'+10*'+newAux
            Cons.append(Con)
            Domains[newAux] = [0, 1]
        if i > 0:
            oldAux = '$' + str(i - 1)
            if i < len(op2):
                Con = oldAux+'+'+op1[-i-1]+'+'+op2[-i-1]+'=='+res[-i-1]+'+10*'+newAux
                Cons.append(Con)
                Domains[newAux] = [0, 1]
            elif i < len(op1):
                Con = oldAux+'+'+op1[-i-1]+'=='+res[-i-1]+'+10*'+newAux
                Cons.append(Con)
                Domains[newAux] = [0, 1]
            else:
                Con = oldAux+'=='+res[-i-1]
                Cons.append(Con)

    return Cons


# Check if this var-color pair consistent with the constraints
def is_Consistent(var, digit, assignment, Cons):
    # Constraint for letter: one letter for one digit
    if var[0] != '$':
        for key in assignment:
            if key[0] != '$'and digit == assignment[key]:
                    return False
    global prune
    for con in Cons:
        prune+=1
        con1 = con.replace('+', ' ')
        con1 = con1.replace('*', ' ')
        con1 = con1.replace('==', ' ')
        conList = con1.split()
        if '10' in conList:
            conList.remove('10')
        allAssign = True
        conEval = con
        for conVar in conList:
            if conVar in assignment:
                conEval = conEval.replace(conVar, str(assignment[conVar]))
            elif conVar==var:
                conEval = conEval.replace(conVar, str(digit))
            else:
                allAssign = False
                break
        if allAssign:
            if not eval(conEval):
                return False
    return True


# Check if the assignments solve the problem
def finalEval(assignment, Cons):
    for con in Cons:
        con1 = con.replace('+', ' ')
        con1 = con1.replace('*', ' ')
        con1 = con1.replace('==', ' ')
        conList = con1.split()
        if '10' in conList:
            conList.remove('10')
        allAssign = True
        conEval = con
        for conVar in conList:
            if conVar in assignment:
                conEval = conEval.replace(conVar, str(assignment[conVar]))
            else:
                allAssign = False
                break
        if allAssign:
            if not eval(conEval):
                return False
        else:
            return False
    return True


if __name__ == '__main__':

    in_file = ''
    out_file = ''
    mode = 0
    # Split two sides of the equation
    # Special vars: sqrt(something)
    # Ops: +, -, *, /
    leftVars = []
    rightVars = []
    Domains = {}
    Letters = []

    if len(sys.argv) == 4:
        in_file = open(sys.argv[1], 'r')
        out_file = open(sys.argv[2], 'w')
        mode = int(sys.argv[3])
    else:
        print('Wrong number of arguments. Usage:\npython dfsb.py <input_file> <output_file> <mode_flag>')
        sys.exit()

    if mode != 0 and mode != 1 and mode != 2:
        print('Illegal argument: <mode_flag> should be 0, 1 or 2')
        sys.exit()

    # Read input question
    isLeft = True
    for line in in_file:
        line = line.replace('\n', '')
        if line == '=':
            isLeft = False

        elif line in OPs:
            if line == OPs[1]:
                isLeft = False
                op = OPs[0]
            else:
                op = line

        else:
            if isLeft:
                leftVars.append(line)
            else:
                rightVars.append(line)



    # Define domain for each letter
    for line in leftVars + rightVars:
        for i in range(len(line)):
            if line[i] not in Domains:
                Domains[line[i]] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                Letters.append(line[i])
            # Remove leading 0
            if i == 0 and (0 in Domains[line[i]]):
                Domains[line[i]].remove(0)

    if len(Domains) > 10:
        print("Too much letters!\n")
        sys.exit()


    # Swap leftVars and rightVars if necessary
    if len(rightVars) > len(leftVars):
        temp = leftVars
        leftVars = rightVars
        rightVars = temp

    #print(leftVars)
    #print(op)
    #print(rightVars)
    #print(list(Domains.keys()))

    # get constraints
    Cons = addCons(leftVars[0], leftVars[1], rightVars[0], Domains)

    #print(Cons)
    #print(Domains)
    result='failure'
    if mode == 0:
        startTime = time.time()
        result = Plain_Backtracking({}, Domains, Cons)
        print('The Algorithm took {0} second !'.format(time.time() - startTime))
    elif mode == 1:
        startTime = time.time()
        result = Backtracking_Plus({}, Domains, Cons, 1)
        print('The Algorithm took {0} second !'.format(time.time() - startTime))
    elif mode == 2:
        startTime = time.time()
        result = Backtracking_Plus({}, Domains, Cons, 2)
        print('The Algorithm took {0} second !'.format(time.time() - startTime))

    print(result)
    #print(search)
    #print(prune)
    #print(Cons)
    #print(Domains)

    if result == 'failure':
        out_file.write(result)
    else:
        Letters.sort()
        for l in Letters:
            output = l+": "
            output += str(result[l])
            output += '\n'
            out_file.write(output)

    in_file.close()
    out_file.close()