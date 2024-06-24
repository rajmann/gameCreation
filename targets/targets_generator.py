"""
@author: richard mann, nerdle

A Targets puzzle consists of 4 target numbers that have to be calculated from a reduced keyboard of possible input numbers
The 4 targets are of increasing difficulty, defined by the minimum number of inputs required to match the target
In game play, 1-4 of these targets are displayed, starting with the easiest.

File inputs:
    - no input files required

Algorithm:
    - Randomly generate numbers to appear on keyboard based on specified rules (n small and n large numbers)
    - Generate suitable targets that meet specified conditions (and check that they can't be achieved by another simpler method)
    
File output:
    - targets_questions.json - keyboard numbers used for each game
    - targets_calculations.json - solutions that achieve target from keyboard numbers
    - targets_solutions.json - targets for each game, in order of increasing complexity
    
"""

import numpy as np
import random
import json
import sys
from itertools import combinations, permutations, product

# setting params
targetQs = 10 #number of games to produce

numberListBottom = [1,2,3,4,5,6,7,8,9,10,11,12] #possible small numbers to use
numberListTop = [25,30,40,50,60,75,80,100] #possible large numbers to use
symbols = [x for x in '+-/*'] #possible symbols to use

#generate calcs including up to 6 numbers

nTotal = 6  #number of options to appear on keyboard
nFromTop = 1 #number of 'bigs' to use in puzzle keyboard
nFromBottom = nTotal-nFromTop #number of 'smalls' to use in puzzle keyboard

#number of groupings required for 1st, 2nd, 3rd, 4th answer.  [2,2,2] is the most complex as it requires all 6 inputs to be paired and then combined
nGroupsInAnswer = [[2,1],[2,2],[2,2,1],[2,2,1],[2,2,2]] #e.g [2,1] = (a*b)+c

#numerical range required for each of the targets
nDigitsRangeAnswer = [[1,50],[50,100],[100,200],[200,999],[200,999]]



def combine(dig, sym):
    m=len(sym) 
    calc=[]
    for i in range(m):
        calc+=[dig[i]]+[sym[i]]
    calc+=[dig[-1]]
    return(calc)

def calcLeftToRight(calc):
    miniCalc = calc[0] 
    for i in range(1,len(calc),2):
        miniCalc+=calc[i]+calc[i+1]
        miniCalc=str(eval(miniCalc))
    return(eval(miniCalc))

def createDisallowed(question,n):
    
   
    digitsList = list(permutations([str(q) for q in question],n))
    symbolsList  = list(product(symbols,repeat=n-1))

    calcList = []
    for sym in symbolsList:
        for dig in digitsList:
            calcList += [combine(dig,sym)]
    
    disallowedList = [calcLeftToRight(calc) for calc in calcList]
    disallowedList = [int(d) for d in disallowedList if ((d==np.round(d,0)) & (d>=0) & (d<=1000))]            
    disallowedList = list(set(disallowedList))
    disallowedList.sort()
    
    return(disallowedList)

def replace_nth(base_str, find_str, replace_str, n):
    return base_str.replace(find_str, "xxxxx", n-1).replace(find_str, replace_str, 1).replace("xxxxx", find_str)
    
def stripBrackets(calculation):
    nBrackets = len(calculation)-len(calculation.replace("(",""))
    newCalc = calculation
    for n in range(nBrackets,0,-1):
        print(n)
        tempCalc = replace_nth(replace_nth(newCalc, "(", "", n),")","",n)
        print(tempCalc)
        if (eval(tempCalc)==eval(calculation)):
            newCalc=tempCalc
    return(newCalc)

def minCalc(calculation):
    ans = eval(calculation)
    calcn = calculation
    for s in '+-*/()':
        calcn = calcn.replace(s,"|")
    question = [x for x in calcn.split('|') if x!='']
    n = len(question)

    digitsList = list(permutations([str(q) for q in question],n))
    symbolsList  = list(product(symbols,repeat=n-1))

    calcList = []
    for sym in symbolsList:
        for dig in digitsList:
            calcList += [combine(dig,sym)]

    if n>2:
        #try with 1 fewer number
        digitsList = list(permutations([str(q) for q in question],n-1))
        symbolsList  = list(product(symbols,repeat=n-1-1))
    
        calcList2 = []
        for sym in symbolsList:
            for dig in digitsList:
                calcList2 += [combine(dig,sym)]
        
        calcList+=calcList2

    if n>3:
        #try with 2 fewer number
        digitsList = list(permutations([str(q) for q in question],n-2))
        symbolsList  = list(product(symbols,repeat=n-1-2))
    
        calcList2 = []
        for sym in symbolsList:
            for dig in digitsList:
                calcList2 += [combine(dig,sym)]
        
        calcList+=calcList2

    #add one set of brackets
    calcList0 = [x.copy() for x in calcList]
    calcList2 = [x.copy() for x in calcList0]
    for i,c in enumerate(calcList2):
        if len(c)>=5:
            calcList2[i][2]="("+calcList2[i][2]
            calcList2[i][4]=calcList2[i][4]+")"
    calcList+=calcList2

    calcList2 = [x.copy() for x in calcList0]
    for i,c in enumerate(calcList2):
        if len(c)>=7:
            calcList2[i][4]="("+calcList2[i][4]
            calcList2[i][6]=calcList2[i][6]+")"
    calcList+=calcList2
    
    calcList2 = [x.copy() for x in calcList0]
    for i,c in enumerate(calcList2):
        if len(c)>=9:
            calcList2[i][6]="("+calcList2[i][6]
            calcList2[i][8]=calcList2[i][8]+")"
    calcList+=calcList2

    matchCalcList=[]
    minLength=99
    for i,c in enumerate(calcList):
        try:
          ev = eval("".join(c))  
          clc="".join(c)
          if (ev==ans) & (len(clc)<minLength): 
              #print(clc,ev, len(clc))
              minLength=len(clc) 
              matchCalcList+=[{'calc':clc,'nDigits':(len(c)+1)/2}]
        except:
          pass  

    if len(calcList)>0:
        minCalc = matchCalcList[-1]

    return(minCalc)    


def minCalcOrdered(calculation):
    symbolsLong =  ["+","-","/","*"]
    symbolsLong +=  ["+(","-(","/(","*("]
    symbolsLong +=  [")+",")-",")/",")*"]
    symbolsLong +=  [")+(",")-(",")/(",")*("]

    ans = eval(calculation)
    calcn = calculation
    for s in '+-*/()':
        calcn = calcn.replace(s,"|")
    question = [x for x in calcn.split('|') if x!='']
    n = len(question)

    digitsList = [question]

    
    symbolsList  = list(product(symbolsLong,repeat=n-1))

    calcList = []
    for sym in symbolsList:
        for dig in digitsList:
            combo=combine(dig,sym)
            diffBrackets = len("".join(combo).replace("(",""))-len("".join(combo).replace(")",""))
            if diffBrackets==0:
                calcList += [combo]
                calcList += [['('+combo[0]]+combo[1:-1]+[combo[-1]+')']]
            elif diffBrackets==1:
                calcList += [['('+combo[0]]+combo[1:-1]+[combo[-1]+'']]
            elif diffBrackets==-1:
                calcList += [[''+combo[0]]+combo[1:-1]+[combo[-1]+')']]

    matchCalcList=[]
    minLength=99
    for i,c in enumerate(calcList):
        try:
          ev = eval("".join(c))  
          clc="".join(c)
          if (ev==ans) & (len(clc)<minLength): 
              #print(clc,ev, len(clc))
              minLength=len(clc) 
              matchCalcList+=[{'calc':clc,'nDigits':(len(c)+1)/2}]
        except:
          pass  

    if len(calcList)>0:
        minCalc = matchCalcList[-1]

    return(minCalc)        
    
questionList = []
solutionList = []
calculationList = []

while len(solutionList)<targetQs:
    #determine number list first
    q=len(solutionList) 
    #generate question
    question = random.sample(numberListBottom, k=nFromBottom)  #without replacement
    question += random.choices(numberListTop, k=nFromTop)  #with replacement
    question.sort()
    
    questionRandom = question.copy() 

    #disallowed list = numbers that can be generated with fewer questions    
    disallowed = {}
    disallowed[1] = question.copy() 
    disallowed[2] = list(set(createDisallowed(question,2)+disallowed[1]))
    disallowed[3] = list(set(createDisallowed(question,3)+disallowed[2]))
    disallowed[4] = list(set(createDisallowed(question,4)+disallowed[3]))
    disallowed[5] = list(set(createDisallowed(question,5)+disallowed[4]))
    
    
    #generate possible answers defined by nGroupsInAnswer
    calculations = []
    calcGroups = []
    evaluations = []
    print()    
    print()    
    print("GENERATING QUESTION NUMBER:", q, ":", question)
    groupSuccess=True
    for i,nGroups in enumerate(nGroupsInAnswer):
        attempts=0
        if groupSuccess==True:
            success=False
            attempts=0
            while ((success==False) & (attempts<10000)):
                attempts+=1
    
                random.shuffle(questionRandom)
                counter = 0
                groups = {}
                digits = sum(nGroups)
                disallowedNum = digits-1
                disallowedList = disallowed[disallowedNum]
                #create a calculation max 2 at a time using random symbol then join calcs together using another random symbol
                calculation = ''
                for j, n in enumerate(nGroups):
                    selected = questionRandom[counter:counter+n]    
                    if len(selected) == 1: 
                        groups[j]=str(selected[0])
                    else: 
                        sym = random.choice(symbols) 
                        groups[j]="("+str(selected[0])+sym+str(selected[1])+")"
            
                    sym = ''
                    if j<len(nGroups)-1: 
                        sym = random.choice(symbols) 
                    calculation+=groups[j]+sym
                    counter+=n
                
                try: 
                    evaluation = eval(calculation)
                except:
                   evaluation = -9999 
                   
                if (evaluation>0) & (int(evaluation)==evaluation) & (int(evaluation)>=nDigitsRangeAnswer[i][0]) & (int(evaluation)<=nDigitsRangeAnswer[i][1]) & (int(evaluation) not in disallowedList) & (evaluation not in evaluations):
                    success=True 
                    print("EVAL", evaluation)
                    print("checking min calculation")
                    minClc = minCalcOrdered(calculation)
                    print("calc", calculation, "min calc", minClc['calc'], "shorter by", len(calculation)-len(minClc['calc']))
                    
                    if (minClc['nDigits']!= digits):
                        print("******************")
                        print("******************")
                        print("*****mis-matched min calc")
                        print("target digits", digits)
                        print("minCalc digits", minClc['nDigits'])
                        print("calculation", calculation)
                        print("minCalc", minClc['calc'])
                        sys.exit()
                    calculations+=[minClc['calc']]
                    evaluations+=[[str(int(evaluation))]]
                else:
                    pass
        
        if success==False:
            groupSuccess=False
            print("fail at group", i)
    
    if groupSuccess:
        print("Q", q, question, calculations, evaluations)     
        questionList+=[[str(qu) for qu in question]]
        calculationList+=[calculations]
        solutionList+=[evaluations]

       
fileName = "targets_questions.json"    
with open('output/'+fileName, 'w') as f:
        json.dump(questionList, f)

with open('output/'+fileName.replace('_questions.json','_solutions.json'), 'w') as f:
        json.dump(solutionList, f)

with open('output/'+fileName.replace('_questions.json','_calculations.json'), 'w') as f:
        json.dump(calculationList, f)

