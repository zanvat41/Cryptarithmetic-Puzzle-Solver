import sys
import math
import time
import random


# Define all operators
OPs = ['+', '-', '*', '/']


def getAddFitness(individual, op1, op2, res):
    #print(op2)
    for i in range(len(op1)):
        if op1[i] in individual:
            op1 = op1.replace(op1[i], str(individual.index(op1[i])))
    for i in range(len(op2)):
        if op2[i] in individual:
            op2 = op2.replace(op2[i], str(individual.index(op2[i])))
    for i in range(len(res)):
        if res[i] in individual:
            res = res.replace(res[i], str(individual.index(res[i])))
    equLeft = int(op1)+int(op2)
    equRight = int(res)
    return abs(equRight-equLeft)


# population size was fix to 10
def ga(population, Domains, op1, op2, res):
    #print(len(population))
    #addcount = 0
    for i in range(10):
        Added = False
        while not Added:
            newIndividual = list(population[i])
            Swapped = False
            while not Swapped:
                m = random.randint(0, 9)
                n = random.randint(0, 9)
                l1 = newIndividual[m]
                l2 = newIndividual[n]
                if l1==l2:
                    continue
                if (l1=='-' or n in Domains[l1]) and (l2=='-' or m in Domains[l2]):
                    newIndividual[m] = l2
                    newIndividual[n] = l1
                    Swapped = True
                    #print(newIndividual)
            #print(newIndividual in population)
            if newIndividual not in population:
                population.append(newIndividual)
                Added = True
                #addcount += 1
                #print(population.index(individual))
                #print("count:"+str(addcount))

    # print("hhh")

    popWithFitness = {}
    for i in range(len(population)):
        fitness = getAddFitness(population[i], op1, op2, res)
        if fitness == 0:
            return population[i]
        if len(popWithFitness) > 10:
            max = -1
            maxIndex = 0
            for key in popWithFitness:
                if popWithFitness[key] > max:
                    max = popWithFitness[key]
                    maxIndex = key
            if fitness < max:
                popWithFitness.pop(maxIndex)
                popWithFitness[i] = fitness
        else:
            popWithFitness[i] = fitness

    newPopulation = []
    for key in popWithFitness:
        newPopulation.append(population[key])

    return ga(newPopulation, Domains, op1, op2, res)


def initIndividual (Letters, Domains):
    result = []
    for i in range(10):
        result.append('-')
    for l in Letters:
        if len(Domains[l]) == 9:
            while l not in result:
                digit = random.randint(1,9)
                if result[digit] == '-':
                    result[digit] = l
        else:
            while l not in result:
                digit = random.randint(0,9)
                if result[digit] == '-':
                    result[digit] = l
    return result


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

    if len(sys.argv) == 3:
        in_file = open(sys.argv[1], 'r')
        out_file = open(sys.argv[2], 'w')
    else:
        print('Wrong number of arguments. Usage:\npython ga.py <input_file> <output_file> ')
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
    if op == OPs[0]:
        # for addition
        Cons = addCons(leftVars[0], leftVars[1], rightVars[0], Domains)
    else:
        # for multiplication
        Cons = []

    #print(Cons)
    #print(Domains)
    startTime = time.time()
    population = []
    while len(population) < 10:
        newIndividual = initIndividual (Letters, Domains)
        if newIndividual not in population:
            #fitness = getAddFitness(newIndividual, leftVars[0], leftVars[1], rightVars[0])
            #print(newIndividual)
            #print(fitness)
            population.append(newIndividual)
    #print(population)
    result = ga(population, Domains, leftVars[0], leftVars[1], rightVars[0])
    print('The Algorithm took {0} second !'.format(time.time() - startTime))

    print(result)
    #print(result.index('B'))
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
            index = str(result.index(l))
            output += index
            output += '\n'
            out_file.write(output)

    in_file.close()
    out_file.close()