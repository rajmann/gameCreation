# -*- coding: utf-8 -*-
"""
@author: richard mann, nerdle

A solved shuffle puzzle is a 4x4 magic square of numbers.  Each number is 1 or 2 digits.  Each row or column of numbers of digits is separated with 2 mathematical operators and one equals sign to make a valid calculation eg 10+50/5=15
This file then generates a question by playing a game in reverse.  This can create a shuffle sliding puzzle or a 2d 'swapping' puzzle depending on the mode chosen in parameters.

File inputs:
    - There are no inputs required to generate Shuffle puzzles as the file calculates all possible 

Algorithm step 1 - generate solved puzzle:
    - Generate a list of all valid calculations in format nsnsn=n where n=number(0-99) and s=symbol(+-/*)         
    - Generate a magic square by selecting random starting calculation and then attempting to fit other calculation until valid solution found

Algorithm step 2 - generate question from solved puzzle:
    - Play game backwards by 'unshuffling' (for Shuffle) or 'swapping' (for 2d) n times to create question  
    
File output:
    - [fileStem]_[mode]_[number_of_puzzles]_A.json - solved puzzles
    - [fileStem]_[mode]_[number_of_puzzles]_Q.json - starting questions
    - [fileStem]_[mode]_[number_of_puzzles]_S.json - move sequence to solve (not required for game)
    
"""
import random
import numpy as np
import itertools 
import json  
import sys

# setting params

#number of games to be created
questions = 10
filePrefix = 'shufflePuzzles' 

#mode for creating question from give solution
#chose from:
    #shuffle (shuffle numbers), 
    #swapBoth (2d level 2/3), 
    #swapNum (2d level 1),
    #swapSym (not currently used)

mode = 'shuffle' 
fileStem = filePrefix + '_' + mode + '_'+str(questions)

#number of duplicates required.  A few duplicates makes 2d nerdle more interesting. 3-6 used for first generation games for 2d. 0-999 for Shuffle numbers
if mode == 'shuffle':
    duplicatesRequiredMin = 0 #0 if no specific requirement
    duplicatesRequiredMax = 999 #999 if no specific requirement
else:
    duplicatesRequiredMin = 3 #0 if no specific requirement
    duplicatesRequiredMax = 6 #999 if no specific requirement


def permutations(x=4, type="50x4", stripBoring=False):  
    #generate all possible calculations of specifiedformat
    #x = number of digits in calculation (4 or 5 but only '4' used for live puzzles so far)
    #type = type of calculation allowed (see list below) ('50x4' used for Shuffle and '12strict4' used for 2d)
    #stripBoring = if true, remove calculations including *1, /1 or x/x
     
    if type=="50x1":
        
        ns = [str(x+2) for x in range(49)]
        ns0 = ['0','1']+ns
        ss = ['+']

    elif type=="50x2":
        
        ns = [str(x+2) for x in range(49)]
        ns0 = ['0','1']+ns
        ss = ['+','-']

    #default mode for shuffle numbers
    elif type=="50x4":
        
        ns = [str(x+2) for x in range(49)]
        ns0 = ['0','1']+ns
        ss = ['+','-','*','/']

    elif type=="20x4":
        
        ns = ['2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20']
        ns0 = ['0','1']+ns
        ss = ['+','-','*','/']

    ##numbers 1-12
    #not allowing larger answers
    elif type=="12strictx2":
        
        ns = ['1','2','3','4','5','6','7','8','9','10','11','12']
        ns0 = ns.copy()
        ss = ['+','-']

    #default mode for 2d nerdle
    elif type=="12strictx4":
        
        ns = ['1','2','3','4','5','6','7','8','9','10','11','12']
        ns0 = ns.copy()
        ss = ['+','-','*','/']


    ##numbers 1-6
    
    #allowing larger answers
    elif type=="6x4":
        
        ns = ['1','2','3','4','5','6']
        ns0 = [str(x+2) for x in range(49)]
        ns0 = ['0','1']+ns0
        ss = ['+','-','*','/']

    elif type=="6x2":
        
        ns = ['1','2','3','4','5','6']
        ns0 = [str(x+2) for x in range(49)]
        ns0 = ['0','1']+ns0
        ss = ['+','-']

    #not allowing larger answers
    elif type=="6strictx2":
        
        ns = ['1','2','3','4','5','6']
        ns0 = ns.copy()
        ss = ['+','-']

    elif type=="6strictx4":
        
        ns = ['1','2','3','4','5','6']
        ns0 = ns.copy()
        ss = ['+','-','*','/']

    elif type=="6x1":
        
        ns = ['1','2','3','4','5','6']
        ns0 = [str(x+2) for x in range(49)]
        ns0 = ['0','1']+ns0
        ss = ['+']
    
    else:
        print("undefined type")
        sys.exit()

    perms = []
    
    if x==4:
        target=len(ns)**3*len(ss)**2
        for n1 in ns:
            for s1 in ss:
                for n2 in ns:
                    for s2 in ss:
                        for n3 in ns:
                            equation = [n1,s1,n2,s2,n3]
                            try: 
                                answer = eval("".join(equation))
                                if answer in [n1,n2,n3]:
                                    pass
                                if (answer==np.round(answer,0)) & (str(int(answer)) in ns0):
                                    perms.append(equation+['=',str(int(answer))])
                                if len(perms)%10000==0:
                                    print("Permutations progress:",len(perms),len(perms)/target)
        
                            except:
                                #math errors eg division by zero
                                pass

    elif x==5:
        target=len(ns)**4*len(ss)**3
        for n1 in ns:
            for s1 in ss:
                for n2 in ns:
                    for s2 in ss:
                        for n3 in ns:
                            for s3 in ss:
                                for n4 in ns:
                                    equation = [n1,s1,n2,s2,n3,s3,n4]
                                    try: 
                                        answer = eval("".join(equation))
                                        if (answer==np.round(answer,0)) & (str(int(answer)) in ns0):
                                            perms.append(equation+['=',str(int(answer))])
                                        if len(perms)%10000==0:
                                            print("Permutations progress:",len(perms),len(perms)/target)
                                    except:
                                        #math errors eg division by zero
                                        pass

    else:
        print("invalid perms param")
        sys.exit()

    if stripBoring:
        perms = [p for p in perms if "*1" not in "".join(p)]        
        perms = [p for p in perms if "/1" not in "".join(p)]        
        perms = [p for p in perms if "1*" not in "".join(p)]
        for n in ns:
            perms = [p for p in perms if n+"/"+n not in "".join(p)]
            perms = [p for p in perms if "/"+n+"*"+n not in "".join(p)]
            
    return(perms)

#create solved puzzle given the following inputs:
    #perms = allowed calculation list
    #permsLast = allowed calculation list for final row / column (which may be the same as above)
    #minTimesDivide = minimum number of occurrences of a * and / in puzzle
    
#perms are allowed rows and columns other than final row/col.  permsLast are allowed last row/column
def create_game(perms,permsLast,minTimesDivide=2):    

    attempts = 0
    maxAttempts = 1000
    success = False
    
    lengthN = int((len(perms[0])+1)/2)

    if lengthN==4:
        while (attempts<maxAttempts) & (success==False):
            attempts+=1
            print("Attempt",attempts, end=", ")
        
            #calculate grid
            
            #first 3 rows
            [r1,r2,r3] = random.sample(perms,3)
            
            #all possible columns that match
            possible_cs = {}
            
            for x in range(0,len(perms[0]),2):
                column = [r1[x],r2[x],r3[x]]
                
                #final column
                if x==len(perms[0])-1:
                    possible_cs[x] = [p for p in permsLast if ([p[0],p[2],p[4]]==column)]
                #other columns
                else:
                    possible_cs[x] = [p for p in perms if ([p[0],p[2],p[4]]==column)]
                
            #possible final row
            possible_r4 = {}
            possible_r4s = permsLast.copy()
            
            for x in range(0,len(perms[0]),2):
                possible_r4[x] = set([c[-1] for c in possible_cs[x]])
                possible_r4s = [p for p in possible_r4s if p[x] in possible_r4[x]] 
        
            if len(possible_r4s)>0:    
                [r4] = random.sample(possible_r4s,1)
                
                #fit last column to last row
                possible_cs[6] = [p for p in possible_cs[6] if p[-1]==r4[-1]]
                
                
                if any([len(cs)==0 for cs in possible_cs.values()]):
                    #fail
                    pass
                
                if ((r1+r2+r3+r4+possible_cs[0]+possible_cs[2]+possible_cs[4]+possible_cs[6]).count('*') + (r1+r2+r3+r4+possible_cs[0]+possible_cs[2]+possible_cs[4]+possible_cs[6]).count('/'))>minTimesDivide:
                        success=True
        
                
        if success == False:
            print("Not found - step 1")
            return([])
        
        else:    
            success = False
            while success == False:    
                [c1] = random.sample([c for c in possible_cs[0] if c[-1]==r4[0]],1)
                [c2] = random.sample([c for c in possible_cs[2] if c[-1]==r4[2]],1)
                [c3] = random.sample([c for c in possible_cs[4] if c[-1]==r4[4]],1)
                [c4] = random.sample([c for c in possible_cs[6] if c[-1]==r4[6]],1)
                
                sym1 = [c1[1]," ",c2[1]," ",c3[1]," ",c4[1]]
                sym2 = [c1[3]," ",c2[3]," ",c3[3]," ",c4[3]]
                sym3 = [c1[5]," ",c2[5]," ",c3[5]," ",c4[5]]
                
                if ((r1+r2+r3+r4+c1+c2+c3+c4).count('*') + (r1+r2+r3+r4+c1+c2+c3+c4).count('/'))>minTimesDivide:
                        success=True
                    
            grid = [r1,sym1,r2,sym2,r3,sym3,r4]

    elif lengthN==5:
            
        while (attempts<maxAttempts) & (success==False):
            attempts+=1
            print("Attempt",attempts)
        
            #calculate grid
            
            #first 3 rows
            noduplicates = False
            while noduplicates == False:
                [r1,r2,r3,r4] = random.sample(perms,4)
                numbers = [x for x in sum([r1,r2,r3,r4], []) if x not in ['+','-','*','/','=',' ']]
                if len(set(numbers))==len(numbers):
                    print("no duplicates")
                    noduplicates=True
            #all possible columns that match
            possible_cs = {}
            
            for x in range(0,len(perms[0]),2):
                column = [r1[x],r2[x],r3[x],r4[x]]
                possible_cs[x] = [p for p in perms if ([p[0],p[2],p[4],p[6]]==column)]
                
            #possible final row
            possible_r5 = {}
            possible_r5s = perms.copy()
            
            for x in range(0,len(perms[0]),2):
                possible_r5[x] = set([c[-1] for c in possible_cs[x]])
                possible_r5s = [p for p in possible_r5s if p[x] in possible_r5[x]] 
        
            if len(possible_r5s)>0:    
                [r5] = random.sample(possible_r5s,1)
                
                #fit last column to last row
                possible_cs[8] = [p for p in possible_cs[8] if p[-1]==r5[-1]]
                
                
                if any([len(cs)==0 for cs in possible_cs.values()]):
                    #fail
                    pass
                
                elif ((r1+r2+r3+r4+r5+possible_cs[0]+possible_cs[2]+possible_cs[4]+possible_cs[6]+possible_cs[8]).count('*')>2) & ((r1+r2+r3+r4+r5+possible_cs[0]+possible_cs[2]+possible_cs[4]+possible_cs[6]+possible_cs[8]).count('/')>minTimesDivide):
                    success=True
        
        if success == False:
            print("Not found - step 2")
            return([])
        
        else:    
            success = False
            while success == False:    
                [c1] = random.sample([c for c in possible_cs[0] if c[-1]==r5[0]],1)
                [c2] = random.sample([c for c in possible_cs[2] if c[-1]==r5[2]],1)
                [c3] = random.sample([c for c in possible_cs[4] if c[-1]==r5[4]],1)
                [c4] = random.sample([c for c in possible_cs[6] if c[-1]==r5[6]],1)
                [c5] = random.sample([c for c in possible_cs[8] if c[-1]==r5[8]],1)
                
                sym1 = [c1[1]," ",c2[1]," ",c3[1]," ",c4[1]," ",c5[1]]
                sym2 = [c1[3]," ",c2[3]," ",c3[3]," ",c4[3]," ",c5[3]]
                sym3 = [c1[5]," ",c2[5]," ",c3[5]," ",c4[5]," ",c5[5]]
                sym4 = [c1[7]," ",c2[7]," ",c3[7]," ",c4[7]," ",c5[7]]
                
                if ((r1+r2+r3+r4+r5+c1+c2+c3+c4+c5).count('*')>2) & ((r1+r2+r3+r4+r5+c1+c2+c3+c4+c5).count('/')>minTimesDivide):
                    success=True
                
            grid = [r1,sym1,r2,sym2,r3,sym3,r4,sym4,r5]        

    
    return(grid)

def print_grid(grid):
    for g in grid:
        for i in g:
            print(i,end=' '*(3-len(i)))
        print()

def encode_grid(gridQ,grid):
    for r in range(len(grid)):
        for c in range(len(grid)):
            i=gridQ[r][c]
            print(' '+i+' ',end=' '*(3-len(i)))
        print()
        for c in range(len(grid)):
            i=gridQ[r][c]
            j=grid[r][c]
            if i in " +-*/=": 
                print('   ',end=' '*(2))
            elif i==j:
                print('---',end=' '*(2))
                
            else:
                print('XXX',end=' '*(2))
                
        print()
        

#swap numbers only - n times
def random_swap(grid,n):
    gridQ = [g.copy() for g in grid] 
    solveList = []
    minSolve=0
    
    for i in range(n):
        swappable=False
        counter=0
        while (swappable==False) & (counter<100):
            counter+=1
            a = [random.randint(0,3)*2,random.randint(0,3)*2]
            b = [random.randint(0,3)*2,random.randint(0,3)*2]

            #swappable if at least one of the two is currently green
            if grid[a[0]][a[1]]==gridQ[a[0]][a[1]]:
                swappable = True
            if grid[b[0]][b[1]]==gridQ[b[0]][b[1]]:
                swappable = True
                
            #but not if the two characters are the same
            if (gridQ[a[0]][a[1]]==gridQ[b[0]][b[1]]):
                swappable = False

            #and not if it creates a new green
            if grid[a[0]][a[1]]==gridQ[b[0]][b[1]]:
                swappable = False
            if grid[a[0]][a[1]]==gridQ[b[0]][b[1]]:
                swappable = False

            #and not if minsolved not increased (which can happen with repeats)
            if swappable:
                gridQTemp = [g.copy() for g in gridQ] 
                buffer = gridQTemp[a[0]][a[1]]
                gridQTemp[a[0]][a[1]]=gridQTemp[b[0]][b[1]]
                gridQTemp[b[0]][b[1]]=buffer
                
                
                newMinSolve = len(findSolutionMinSwap(grid,gridQTemp))
                print("counter", counter, "min solve from", minSolve, "to", newMinSolve)
                if newMinSolve == minSolve+1:
                    minSolve = newMinSolve
                elif newMinSolve > minSolve+1:
                    print("error in min solve function")
                    print("swapping", a[0],a[1],gridQ[a[0]][a[1]], "with", b[0],b[1],gridQ[b[0]][b[1]]) 
                    for g in gridQ:
                        print(g)
                    print()
                    for g in gridQTemp:
                        print(g)
                    print("grid, gridQ, gridQTemp")
                    print(grid)
                    print(gridQ)
                    print(gridQTemp)
                    print()
                    print(findSolutionMinSwap(grid,gridQ))                    
                    print(findSolutionMinSwap(grid,gridQTemp))                    
                    
                    sys.exit()
                    
                else:
                    print("min solve not increased - reject swap")
                    swappable = False

        if counter>=99:
            print("aborting - swap not found, num")
            return([],[])

        #print("swapping", a[0],a[1],gridQ[a[0]][a[1]], "with", b[0],b[1],gridQ[b[0]][b[1]]) 
        buffer = gridQ[a[0]][a[1]]
        gridQ[a[0]][a[1]]=gridQ[b[0]][b[1]]
        gridQ[b[0]][b[1]]=buffer
        #for g in gridQ:
        #    print(g)
        
        solveList += [[{'R':a[0],'C':a[1]},{'R':b[0],'C':b[1]}]]

    return gridQ, solveList


#swap symbols only - n times
def random_swap_sym(grid,n):
    gridQ = [g.copy() for g in grid] 
    solveList = []
    minSolve=0
    
    for i in range(n):
        swappable=False
        counter=0
        while (swappable==False) & (counter<100):
            counter+=1
            sym = False
            while sym==False:
                a = [random.randint(0,4),random.randint(0,4)]
                if grid[a[0]][a[1]]  in "+*-/":
                    sym = True
            sym = False
            while sym==False:
                b = [random.randint(0,4),random.randint(0,4)]
                if grid[b[0]][b[1]] in "+*-/":
                    sym = True

            #swappable if at least one of the two is currently green
            if grid[a[0]][a[1]]==gridQ[a[0]][a[1]]:
                swappable = True
            if grid[b[0]][b[1]]==gridQ[b[0]][b[1]]:
                swappable = True
                
            #but not if the two characters are the same
            if (gridQ[a[0]][a[1]]==gridQ[b[0]][b[1]]):
                swappable = False

            #and not if it creates a new green
            if grid[a[0]][a[1]]==gridQ[b[0]][b[1]]:
                swappable = False
            if grid[a[0]][a[1]]==gridQ[b[0]][b[1]]:
                swappable = False

            #and not if minsolved not increased (which can happen with repeats)
            if swappable:
                gridQTemp = [g.copy() for g in gridQ] 
                buffer = gridQTemp[a[0]][a[1]]
                gridQTemp[a[0]][a[1]]=gridQTemp[b[0]][b[1]]
                gridQTemp[b[0]][b[1]]=buffer
                
                
                newMinSolve = len(findSolutionMinSwap(grid,gridQTemp))
                print("counter", counter, "min solve from", minSolve, "to", newMinSolve)
                if newMinSolve == minSolve+1:
                    minSolve = newMinSolve
                elif newMinSolve > minSolve+1:
                    print("error in min solve function")
                    print("swapping", a[0],a[1],gridQ[a[0]][a[1]], "with", b[0],b[1],gridQ[b[0]][b[1]]) 
                    for g in gridQ:
                        print(g)
                    print()
                    for g in gridQTemp:
                        print(g)
                    print("grid, gridQ, gridQTemp")
                    print(grid)
                    print(gridQ)
                    print(gridQTemp)
                    print()
                    print(findSolutionMinSwap(grid,gridQ))                    
                    print(findSolutionMinSwap(grid,gridQTemp))                    
                    
                    sys.exit()
                    
                else:
                    print("min solve not increased - reject swap")
                    swappable = False

        if counter>=99:
            print("aborting - swap not found, sym")
            return([],[])

        #print("swapping", a[0],a[1],gridQ[a[0]][a[1]], "with", b[0],b[1],gridQ[b[0]][b[1]]) 
        buffer = gridQ[a[0]][a[1]]
        gridQ[a[0]][a[1]]=gridQ[b[0]][b[1]]
        gridQ[b[0]][b[1]]=buffer
        #for g in gridQ:
        #    print(g)
        
        solveList += [[{'R':a[0],'C':a[1]},{'R':b[0],'C':b[1]}]]

    return gridQ, solveList



def shuff(line,lineTrue, right=True, fixGreens=True):
    if line==lineTrue:
        return line
    
    if fixGreens:
        #shuffle but keep greens fixed
        lineDiff = [line[x] for x in range(len(line)) if line[x]!=lineTrue[x]]

        if right:
            lineDiffShuff = [lineDiff[-1]]+lineDiff[0:-1]
        else:
            lineDiffShuff = lineDiff[1:]+[lineDiff[0]]
            
        lineNew = []
        lineDiffCount = 0
        for x in range(len(line)):
            if line[x]==lineTrue[x]:
                lineNew.append(line[x])
            else:
                lineNew.append(lineDiffShuff[lineDiffCount])
                lineDiffCount+=1
    else:
        #shuffle ignoring greens (i.e shuffle all numbers)
        lineDiff = [line[x] for x in range(len(line)) if x%2==0]

        if right:
            lineDiffShuff = [lineDiff[-1]]+lineDiff[0:-1]
        else:
            lineDiffShuff = lineDiff[1:]+[lineDiff[0]]
            
        lineNew = []
        lineDiffCount = 0
        for x in range(len(line)):
            if x%2!=0:
                lineNew.append(line[x])
            else:
                lineNew.append(lineDiffShuff[lineDiffCount])
                print("b",lineDiffShuff[lineDiffCount])
                lineDiffCount+=1
        
    return lineNew

def unShuff(line,lineTrue, right=True):
    
    counter=0
    changed=False
    while changed==False:
        lineSame = [line[x]==lineTrue[x] for x in range(len(line))]
        #line fix = which greens to hold in place (always hold symbols): 1 for yes, 0 for no, -1 for not green
        lineFix = [random.randint(0,1) if (lineSame[x] and x%2==0) else (1 if x%2==1 else -1) for x in range(len(line))]
        #print(lineFix) 
        if lineFix.count(0) + lineFix.count(-1) <= 1:
            pass
        else:
            lineDiff = [line[x] for x in range(len(line)) if lineFix[x]!=1]
            if not right:
                lineDiffShuff = [lineDiff[-1]]+lineDiff[0:-1]
            else:
                lineDiffShuff = lineDiff[1:]+[lineDiff[0]]
                
            lineNew = []
            lineDiffCount = 0
            for x in range(len(line)):
                if lineFix[x]==1:
                    lineNew.append(line[x])
                else:
                    lineNew.append(lineDiffShuff[lineDiffCount])
                    lineDiffCount+=1
            changed = (line!=lineNew)
        counter+=1
        if counter>1000:
            print("give up")
            return line #give up and try new line
    return lineNew                                       

def unShuffle(grid,n):
    gridQ = [g.copy() for g in grid] 
    
    for i in range(n):
        #keep trying until a move actually changes the grid 
        attempts = 0
        gridTemp = [g.copy() for g in gridQ] 
        while gridTemp == gridQ:

            #choose row (0) or column (1)
            choice = random.randint(0,1)
            
            #row shuffle
            if choice == 0:
                #choose row
                choice2 = random.randint(0,int(len(grid)/2-1))*2
                choice3 = random.randint(0,1) #0 right, 1 left
                gridQ[choice2] = unShuff(gridQ[choice2],grid[choice2],right=(choice3==0))
    
            #col shuffle
            if choice == 1:
                #choose column
                choice2 = random.randint(0,int(len(grid)/2-1))*2
                choice3 = random.randint(0,1) #0 right (down), 1 left (up)
                column = [row.copy()[choice2] for row in grid]
                columnQ = [row.copy()[choice2] for row in gridQ]
                columnQNew = unShuff(columnQ,column,right=(choice3==0))
                for r in range(len(gridQ)):
                    gridQ[r][choice2]=columnQNew[r] 

            attempts+=1
            if attempts>1000:
                print("GIVE UP") 
                sys.exit()

        text1 = "row" if choice==0 else "column"
        text2 = "right" if choice3==0 else "left"
        print("Choice:", text1, "n=",  choice2, text2)

    return gridQ

def shuffle(gridQ,grid,instruction):
    gridNew = [g.copy() for g in gridQ] 
    rowcol = instruction[0]
    n = instruction[1]
    rightleft = instruction[2]

    fixGreens = len(instruction)==3
    choice2 = int(n)
    choice3 = (0 if (rightleft=='R' or rightleft=='D') else 1)
    
    if rowcol == 'R':
        #choose row
        gridNew[choice2]=shuff(gridQ[choice2],grid[choice2],right=(choice3==0),fixGreens=fixGreens)

    #col shuffle
    if rowcol == 'C':
        #choose column
        column = [row[choice2] for row in grid]
        columnQ = [row[choice2] for row in gridQ]
        columnQ = shuff(columnQ,column,right=(choice3==0),fixGreens=fixGreens)
        for r in range(len(gridQ)):
            gridNew[r][choice2]=columnQ[r] 
        
    return gridNew

def user_swap(gridQ,ab):
    (a,b) = ([int(ab[0])*2-2,int(ab[1])*2-2],[int(ab[2])*2-2,int(ab[3])*2-2])
    newGridQ = [g.copy() for g in gridQ] 
    
    buffer = newGridQ[a[0]][a[1]]
    newGridQ[a[0]][a[1]]=newGridQ[b[0]][b[1]]
    newGridQ[b[0]][b[1]]=buffer
    return newGridQ

def swap(gridQ,ab, debug=False, pause=False): #ab = RCRC eg 00,55 to swap R0C0 with R4C4
    (a,b) = ([int(ab[0]),int(ab[1])],[int(ab[2]),int(ab[3])])
    newGridQ = [g.copy() for g in gridQ] 
    
    buffer = newGridQ[a[0]][a[1]]
    newGridQ[a[0]][a[1]]=newGridQ[b[0]][b[1]]
    newGridQ[b[0]][b[1]]=buffer

    if debug:
        print("swapping", a,gridQ[a[0]][a[1]],b,gridQ[b[0]][b[1]])
        for g in gridQ:
            print(g)
        print()
        for g in newGridQ:
            print(g)

    if pause:
        input("enter to continue")
    return newGridQ

def findSolutionAnyUnder5(grid,gridQ):

    allGoes = []
    for part1 in ['R','C']:
        for part2 in ['0','2','4','6']:
            for part3 in ['R','L']:
                    allGoes.append(part1+part2+part3)

    allGoPerms = list(itertools.product(allGoes, repeat=4))

    minSolved=99
    minSolution=''
    for j, goList in enumerate(allGoPerms):
        if j%50000==0:
            print(j) 
        tempGrid = [g.copy() for g in gridQ] 
        for i in range(len(goList)):
            go = goList[i]
            tempGrid = shuffle(tempGrid,grid,go)
            if tempGrid==grid:
                if i+1<minSolved:
                    print('solved in ',i+1, "with goes:", goList[:i+1])
                    minSolved=i+1
                    minSolution=goList[:i+1]
                    return(minSolved, goList[:i+1])
                    
    print('finished')

    return(minSolved, minSolution)

def findSolutionMin(grid,gridQ):

    allGoes = []
    for part1 in ['R','C']:
        for part2 in ['0','2','4','6']:
            for part3 in ['R','L']:
                    allGoes.append(part1+part2+part3)

    allGoPerms = list(itertools.product(allGoes, repeat=5))

    minSolved=99
    minSolution=''
    for j, goList in enumerate(allGoPerms):
        if j%50000==0:
            print(j) 
        tempGrid = [g.copy() for g in gridQ] 
        for i in range(len(goList)):
            go = goList[i]
            tempGrid = shuffle(tempGrid,grid,go)
            if tempGrid==grid:
                if i+1<minSolved:
                    print('solved in ',i+1, "with goes:", goList[:i+1])
                    minSolved=i+1
                    minSolution=goList[:i+1]
                    if minSolved==1:
                        return(minSolved, goList[:i+1])
                    
    print('finished')

    return(minSolved, minSolution)

def findSolutionMinSwap(grid,gridQtemp,attempts=20):

    bestAttempt = []
    gridQmaster = [g.copy() for g in gridQtemp]
    
    for attempt in range(attempts):
        #print("attempt", attempt)
        gridQtemp = [g.copy() for g in gridQmaster]
   
        repeats = {}
        for g in grid:
            for d in g:
                if d not in repeats:
                    repeats[d]=1
                else:
                    repeats[d]+=1
    
        '''
        gridQtemp = [g.copy() for g in gridQ]
        '''
        solved=False
        solveList = []
        pause = False
        
        while not solved:
            singleGreenMove = []
            singleGreenMaxCount = 99
            doubleAchieved = False
                    
            for row1 in range(len(grid)):
                for col1 in range(len(grid)):
                    for row2 in range(len(grid)):
                        for col2 in range(len(grid)):
                            
                                if row1==row2 & col1==col2:
                                    pass
                                elif grid[row1][col1]==gridQtemp[row1][col1]: #already green
                                    pass
                                elif grid[row2][col2]==gridQtemp[row2][col2]: #already green
                                    pass
                                elif grid[row1][col1]==grid[row2][col2]: #the same
                                    pass
                                elif (grid[row1][col1]==gridQtemp[row2][col2]) & (gridQtemp[row1][col1]==grid[row2][col2]):
                                     #print("double green - do unswap", row1,col1,gridQtemp[row1][col1], "and", row2,col2,gridQtemp[row2][col2]) 
                                     doubleAchieved=True
                                     solveList+= [[{'R':row1,'C':col1,'D':grid[row1][col1]},{'R':row2,'C':col2,'D':grid[row2][col2]}]]
                                     gridQtemp = swap(gridQtemp,str(row1)+str(col1)+str(row2)+str(col2), debug=False, pause=pause)
                                elif (grid[row1][col1]==gridQtemp[row2][col2]) | (gridQtemp[row1][col1]==grid[row2][col2]): 
                                    #we prefer single gren moves that don't move a repeated digit
                                    repeatCount = max(repeats[gridQtemp[row1][col1]],repeats[gridQtemp[row2][col2]])
                                    if repeatCount<=singleGreenMaxCount:
                                        randomChoice = 1
                                        #if several 'best' single moves, need to randomise
                                        if repeatCount==singleGreenMaxCount:
                                            randomChoice = random.randint(0,1)
                                        if randomChoice == 1:
                                            #print("repeat count", repeatCount, gridQtemp[row1][col1], repeats[gridQtemp[row1][col1]],gridQtemp[row2][col2], repeats[gridQtemp[row2][col2]])
                                            singleGreenMove = [{'R':row1,'C':col1},{'R':row2,'C':col2}]
                                            singleGreenMaxCount = repeatCount
                                    
                                    
    
            if (singleGreenMove == []) or (doubleAchieved==True):
                pass
            else:
                row1 = singleGreenMove[0]['R']
                row2 = singleGreenMove[1]['R']
                col1 = singleGreenMove[0]['C']
                col2 = singleGreenMove[1]['C']
                #print("single green swap: rcd-count, rcd-count", row1,col1,gridQtemp[row1][col1],repeats[gridQtemp[row1][col1]], "and", row2,col2,gridQtemp[row2][col2],repeats[gridQtemp[row2][col2]])
                #print("single green repeat count", singleGreenMaxCount)
                solveList+= [[{'R':row1,'C':col1,'D':grid[row1][col1]},{'R':row2,'C':col2,'D':grid[row2][col2]}]]
                
                gridQtemp = swap(gridQtemp,str(row1)+str(col1)+str(row2)+str(col2), debug=False, pause=pause)
                
            if grid == gridQtemp:
                solved = True
                

        if bestAttempt == []:
            bestAttempt=solveList
            
        if len(solveList)<len(bestAttempt):
            bestAttempt=solveList

    #print('solved in', len(bestAttempt))
            
    return(bestAttempt)

#Create files:

    
#perms are allowed rows and columns other than final row/col.  permsLast are allowed last row/column
#this separation means that you could have higher numbers in the final row / column if desired
#calcType determins what format of calculations are allowed.  Default for production games is...

if mode == 'shuffle':
    calcType = "50x4"
else:
    calcType = "12strictx4"

perms = permutations(x=4, type=calcType,stripBoring=True)
permsLast = permutations(x=4, type=calcType, stripBoring=True)

grids = []
gridQs = []
gridSs = []

while len(grids)<questions:
    #create solved game
    print("FINDING SOLUTION", len(grids))
    grid = create_game(perms, permsLast, minTimesDivide=2)
    if grid==[]:
        print("no grid returned")
    else:
        print() 
        print("CREATING QUESTION", len(grids))
        #check if duplicates required has been met
        numbers = [x for x in sum(grid, []) if x not in ['+','-','*','/','=',' ']]
        duplicateNumbers = -len(set(numbers))+len(numbers)
        if duplicateNumbers>=duplicatesRequiredMin and duplicateNumbers<=duplicatesRequiredMax:
            
            #for shuffle puzzles, unshuffle grid 6 times to create question
            if mode == 'shuffle':
                gridQ = unShuffle(grid,6)
                grids.append(grid)
                gridQs.append(gridQ)

            #for 2d puzzles (called 'swap' mode here), swap puzzle n times to create question
            if mode[:4] == 'swap':
                if mode == 'swapBoth':
 
                    #Easy = 15 attempts, solvable in 10
                    #Medium = 18 attempts, solvable in 13  << This mode chosen for 2d launch
                    #Hard = 20 attempts, solvable in 15
                    #18 attempts, solvable in 12 (0-6 stars)
                    moves = 13
                    movesMinSymbols = 5
                    movesMinNumbers = 6

                    movesNum = random.randint(movesMinNumbers,moves-movesMinSymbols)
                    movesSym = moves - movesNum                        
                    print(movesNum, movesSym, movesNum+movesSym)
                elif mode == 'swapNum':
                    #15 attempts, solvable in 10 (1-6 stars)
                    movesNum = 9
                    movesSym = 0                      
                    moves = movesNum+movesSym

                elif mode == 'swapSym':
                    #15 attempts, solvable in 10 (1-6 stars)
                    gridQ=grid 
                    movesNum = 0
                    movesSym = 8
                    moves = movesNum+movesSym
                    
                    
                else:
                    print("invalid mode")
                    sys.exit()
                  
                solveList1=[]
                solveList2=[]
                
                #different swap functions depending on whether symbols being swapped
                if movesNum>0: 
                    gridQ, solveList1 = random_swap(grid,movesNum)
                if (movesSym>0) & (grid!=[]): 
                    gridQ, solveList2 = random_swap_sym(gridQ,movesSym)

                if gridQ==[]:
                    print("rejecting grid as question cannot be created")
                else:
                    solution = findSolutionMinSwap(grid,gridQ)
                    if len(solution)==moves:
                        print("minSolve success")
                    else:
                        print("minSolve fail")
                        print("target moves" ,moves, "actual solve", len(solution))
                        sys.exit()

                    solveList = solveList1+solveList2
                    grids.append(grid)
                    gridQs.append(gridQ)
                    gridSs.append(solveList)
                
        else:
            print("duplicates required not matched, try again")

    print()
    print("******************GRIDS FOUND SO FAR:",len(grids))
    print()
    print()
    print()
    
#save files

with open("output/"+fileStem+'_A.json', 'w') as f:
    json.dump(grids, f)
with open("output/"+fileStem+'_Q.json', 'w') as f:
    json.dump(gridQs, f)
with open("output/"+fileStem+'_S.json', 'w') as f:
    json.dump(gridSs, f)


