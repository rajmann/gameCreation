# -*- coding: utf-8 -*-
"""
@author: richard mann, nerdle

File inputs:
    - Word lists: exhaustive lists of valid calculations of length 3 to 9
    - Blank crossword patterns [filestem].txt (with maximum calc length being 9)
    - Blank crossword pattern specification:
        X = black square (cannot be used)
        _ = white square (to be filled)
        Template can be blank but can also be pre-populated with digits or symbols (including =).  This can speed up puzzle creation as it reduces search space.

Algorithm:
    - Semi-random population of grid until valid puzzle solved
    - Algorithm efficiency improved by working out any characters that cannot be placed in each square ("impossibles") at each stage to reduce search space
    - Algo randomly takes steps back from partially complete puzzle and periodically starts from scratch until solution found 
    - Note that, when creating new puzzle formats, try to make sure the puzzle format has a feasible solution.  Algorithm is likely to identify impossible solutions but some thought in designing puzzle is worthwhile.
    
File output:
    - Completed crossnerdle puzzles with no missing squares
    - n puzzles per pattern generated - see setting params
    - saved to [filestem]_answers.json - see setting params
    
"""

import random
import pandas as pd
import cv2
import numpy as np
import os
import datetime
import itertools 
import ast
import json  
import sys
import pandas

# setting params

#fileStem specifes .txt file to read in for puzzles and is retained as prefix for output file
fileStem = 'patterns7x7_to_10x10-x4'
#taretPerPatter is the number of output puzzles for each pattern.  For production games, this should be a relatively high number (50+?).  For testing, it might as well be 1
targetPerPattern=1



# read in exhaustive word lists
#note: these files do not include words with leading zeros even though we check that puzzles cannot be solved with leading zeros in question generator to avoid confusion
words9 = pandas.read_csv('input/nerdlewords9.txt', header=None, names=['word'])
words9 = words9[words9.word.apply(lambda x: x[4]!="=")] #remove words such as 1234=1234
words8 = pandas.read_csv('input/nerdlewords8.txt', header=None, names=['word'])
words7 = pandas.read_csv('input/nerdlewords7.txt', header=None, names=['word'])
words6 = pandas.read_csv('input/nerdlewords6.txt', header=None, names=['word'])
words5 = pandas.read_csv('input/nerdlewords5.txt', header=None, names=['word'])
words3 = pd.DataFrame(['1=1','2=2','3=3','4=4','5=5','6=6','7=7','8=8','9=9'], columns=['word'])  #intentionally omits 0=0 as this breaks the leading zero rule

def patternMatch(toMatch,returnAll=False, impossibles=[]):
    if len(toMatch)>9 or len(toMatch) in [2,4]:
        if "_" in toMatch:
            print("no word list exists for length", len(toMatch), toMatch)
            sys.exit()
        else:
            return([toMatch])
        
    if len(toMatch)==9:
        words=words9.copy()
    if len(toMatch)==8:
        words=words8.copy()
    if len(toMatch)==7:
        words=words7.copy()
    if len(toMatch)==6:
        words=words6.copy()
    if len(toMatch)==5:
        words=words5.copy()
    if len(toMatch)==3:
        words=words3.copy()
    for j in range(len(toMatch)):
        if len(words)>0: 
            if toMatch[j]=="n": 
                words=words[words.word.apply(lambda x: x[j] in '0123456789')]
            elif toMatch[j]=="s": 
                words=words[words.word.apply(lambda x: x[j] in '+-/*')]
            elif toMatch[j]!="_": 
                words=words[words.word.apply(lambda x: x[j]==toMatch[j])]
    
    if impossibles!=[]:                
        #remove impossibles
        if len(toMatch)!=len(impossibles):
            print("mismatch in field lenghts") 
            return("fail")
        else:
            for j in range(len(toMatch)):
                if len(words)>0:
                    words=words[words.word.apply(lambda x: x[j] not in impossibles[j])]

    if len(words)==0:
        return("fail")
    if returnAll:
        return(words['word'].tolist())
    else:    
        return(words.sample().iloc[0]['word'])

def patternMatchWordList(toMatch, wordList, returnAll=False):
    for j in range(len(toMatch)):
        if len(wordList)>0: 
            if toMatch[j]=="n": 
                wordList=[x for x in wordList if x[j] in '0123456789' ]
            elif toMatch[j]=="s": 
                wordList=[x for x in wordList if x[j] in '+-/*']
            elif toMatch[j]!="_": 
                wordList=[x for x in wordList if x[j] == toMatch[j]]
    
    if len(wordList)==0:
        return("fail")
    if returnAll:
        return(wordList)
    else:    
        return(random.choice(wordList))


def findWords(pattern):
    #get all across and down words from given pattern
    
    patternShape = [len(pattern[0]),len(pattern)]

    acrossList = []
    found=False
    for y in range(patternShape[1]):
        for x in range(patternShape[0]):
            if (found==False) & (pattern[y][x] not in " X@"):
                found=True
                start=[x,y]
                patternIn=''
                length=0
            if (found==True) & (pattern[y][x] not in " X@"):
                length+=1
                patternIn+=pattern[y][x]
            if (found==True) & (pattern[y][x] in " X@" or x == patternShape[0]-1):
                found=False
                if length>1:
                    acrossList+=[{'start':start, 'length':length, 'patternIn':patternIn}]
     
    across = [(x['start'][1], (x['start'][0],x['start'][0]+x['length']-1)) for x in acrossList]
    downList = []
    found=False
    for x in range(patternShape[0]):
        for y in range(patternShape[1]):
            print
            if (found==False) & (pattern[y][x] not in " X@"):
                found=True
                start=[x,y]
                patternIn=''
                length=0
            if (found==True) & (pattern[y][x] not in " X@"):
                length+=1
                patternIn+=pattern[y][x]
            if (found==True) & (pattern[y][x] in " X@" or y == patternShape[1]-1):
                found=False
                if length>1:
                    downList+=[{'start':start, 'length':length, 'patternIn':patternIn}]
            #print(x,y,found,patternIn,length)
            #print(downList)            

    down = [(x['start'][0], (x['start'][1],x['start'][1]+x['length']-1)) for x in downList]
                    
    return(across, down, acrossList, downList)

def findImpossibles(toMatch):
    words = patternMatch(toMatch,returnAll=True,impossibles=[])
    possibles = []
    impossibles = []
    
    for l in range(len(toMatch)):
        possible = list(set([word[l] for word in words]))
        possibles+=[possible]
    
        allLetters = '0123456789=+-/*'
        impossible = [x for x in allLetters if x not in possible]
        impossibles+=[impossible]
    return(impossibles)

#input grid pattern
with open('input/'+fileStem+'.txt') as f:
    patterns = json.load(f)

puzzleList=[]

#select pattern
for patternNo, pattern in enumerate(patterns[0:]):
    print()
    print()
    print("*******PATTERN NUMBER", patternNo)
    counter=0
    success=0
    
    #convert list of strings to list of lists
    patternList = [] 
    for p in pattern:
        newp = [" " if x=="X" else x for x in list(p)]
        patternList+=[newp]
    
    print("**Finding words**")
    _,_,acrossList, downList = findWords(pattern)

    #check if puzzle is possible
    print("**Finding impossibles**")
    patternImpossible = [([[]]*len(pattern[0])).copy() for y in range(len(pattern))]
    allLetters = '0123456789=+-/*'

    for across in acrossList:
        impossibles = findImpossibles(across['patternIn'])
        y = across['start'][1]
        for n,x in enumerate(range(across['start'][0],across['start'][0]+across['length'],1)):
            patternImpossible[y][x]=impossibles[n]
            if len(patternImpossible[y][x])==len(allLetters):
                print("puzzle not possible across @ x,y",x,y)
                print(across)
                sys.exit()
    
    for down in downList:
        if "_" in down:
            impossibles = findImpossibles(down['patternIn'])
            x = down['start'][0]
            for n,y in enumerate(range(down['start'][1],down['start'][1]+down['length'],1)):
                patternImpossible[y][x]=list(set(patternImpossible[y][x]+impossibles[n]))
                if len(patternImpossible[y][x])==len(allLetters):
                    print("puzzle not possible down @ x,y",x,y)
                    print(down)
                    sys.exit()
                
    print("**Calculating possible word lists")
    
    for m,across in enumerate(acrossList):
        print("across", m, end="; ")
        y = across['start'][1]
        impossibles=[]
        for n,x in enumerate(range(across['start'][0],across['start'][0]+across['length'],1)):
            impossibles+=[patternImpossible[y][x]]
        acrossList[m]['impossibles']=impossibles
        acrossList[m]['possibleWords']=patternMatch(across['patternIn'],returnAll=True,impossibles=impossibles)
        if acrossList[m]['possibleWords']=="fail":
            print("no possible words, across", across)
            sys.exit()

    for m,down in enumerate(downList):
        print("down", m, end="; ")
        x = down['start'][0]
        impossibles=[]
        for n,y in enumerate(range(down['start'][1],down['start'][1]+down['length'],1)):
            impossibles+=[patternImpossible[y][x]]
        downList[m]['impossibles']=impossibles
        downList[m]['possibleWords']=patternMatch(down['patternIn'],returnAll=True,impossibles=impossibles)
        if downList[m]['possibleWords']=="fail":
            print("no possible words, down", down)
            sys.exit()

    #sort by criteria
    def lenFunc(e):
      #return (e['length'])
      return (len(e['possibleWords']))
    
    downList.sort(key=lenFunc)
    acrossList.sort(key=lenFunc)
    failMatchA=[]
    failMatchPreviousA=['x']
    failMatchD=[]
    failMatchPreviousD=['x']
    failMatchCount=0
    
    while success<targetPerPattern:    
        counter+=1
        print("*** Pattern", patternNo, "of", len(patterns), "attempt", counter,"; success", success, "of", targetPerPattern, "cumulative:", len(puzzleList))
        

        
        #start solving
        attemptList=[x.copy() for x in patternList.copy()] 
        maxAttempts=25000
        attempts=0
        fail=True
        maxReached=0
        best=[]
        i=0
        while (attempts<maxAttempts) & (fail==True):
            if best!=[]:
                attemptList = [b.copy() for b in best]

            #for p in attemptList:
            #    print(" ".join(p))
            #input("Press Enter to continue...")

            #if too many fails or every 500 attempts, start from scratch
            if (failMatchCount>10) | (attempts%500==499):
                print("resetting", failMatchCount, end=" ")
                attemptList=[x.copy() for x in patternList.copy()] 
                best=[]
                failMatchCount=0
            
            attempts+=1
            if attempts%100==0:
                print(attempts, i, end=" ")   

            #choose number of words to replace and reset to input pattern - across
            replacements = random.randint(1,len(acrossList))
            replacementList = random.sample(range(0,len(acrossList)),replacements)
            #replace all replacementList            
            for j in replacementList:
                across = acrossList[j]
                y = across['start'][1]
                for n,x in enumerate(range(across['start'][0],across['start'][0]+across['length'],1)):
                    if across['patternIn'][n] in "ns=_": 
                        attemptList[y][x]=across['patternIn'][n]

            #choose number of words to replace and reset to input pattern - down
            replacements = random.randint(1,len(downList))
            replacementList = random.sample(range(0,len(downList)),replacements)
            #replace all replacementList            
            for j in replacementList:
                down = downList[j]
                x = down['start'][0]
                for n,y in enumerate(range(down['start'][1],down['start'][1]+down['length'],1)):
                    if down['patternIn'][n] in "ns=_":
                        attemptList[y][x]=down['patternIn'][n]
            '''
            print("checkpoint after replacement")
            for a in attemptList:
                print(a)
            '''
            
            #start with the shortest words to solve
            i=0
            fail=False
            failDirection=''
            failLocation=[]
            while (i<max(len(acrossList),len(downList))) & (fail==False):
                
                #solve across
                if len(acrossList)>i:
                    
                    direction="across" 
                    across = acrossList[i]
                    y = across['start'][1]
                    toMatch = []
                    impossibles = []
                    for x in range(across['start'][0],across['start'][0]+across['length'],1):
                        toMatch += attemptList[y][x]
                        impossibles += [patternImpossible[y][x]]
                    
                    #find calc to match pattern from word list.  
                    attempt = patternMatchWordList(toMatch, across['possibleWords'], returnAll=False)
                    if attempt=='fail':
                        fail=True
                        failDirection=direction
                        failLocation=acrossList[i]['start']
                        failMatchA=toMatch
                        if failMatchA==failMatchPreviousA:
                            failMatchCount+=1
                        else:
                            failMatchCount=0
                        failMatchPreviousA=failMatchA.copy()
                        #print("failMatchA , yx, Count", failMatchA, y,x, failMatchA==failMatchPreviousA, failMatchCount)

                        #clear failed word
                        y = across['start'][1]
                        for n,x in enumerate(range(across['start'][0],across['start'][0]+across['length'],1)):
                            if across['patternIn'][n] == "_": 
                                attemptList[y][x]="_"



                    else: 
                        for pos,x in enumerate(range(across['start'][0],across['start'][0]+across['length'],1)):
                            attemptList[y][x]=attempt[pos]
                    
                    '''
                    print("checkpoint after solving one iteration", i, 'across')
                    for a in attemptList:
                        print(a)        
                    '''
                    
                #solve down
                if len(downList)>i:
                    direction="down" 
                    down = downList[i]
                    x = down['start'][0]
                    toMatch = []
                    impossibles = []
                    for y in range(down['start'][1],down['start'][1]+down['length'],1):
                        #print(x,y) 
                        toMatch += attemptList[y][x]
                        impossibles += [patternImpossible[y][x]]
        
                    #find calc to match pattern from word list.  
                    attempt = patternMatchWordList(toMatch, down['possibleWords'], returnAll=False)
                    if attempt=='fail':
                        fail=True
                        failDirection=direction
                        failLocation=downList[i]['start']
                        failMatchD=toMatch
                        if failMatchD==failMatchPreviousD:
                            failMatchCount+=1
                        else:
                            failMatchCount=0
                        failMatchPreviousD=failMatchD.copy()
                        #print("failMatchD , yx, Count", failMatchD, y,x, failMatchD==failMatchPreviousD, failMatchCount)

                        
                        #clear failed word
                        x = down['start'][0]
                        for n,y in enumerate(range(down['start'][1],down['start'][1]+down['length'],1)):
                            if down['patternIn'][n] == "_":
                                attemptList[y][x]="_"

                        
                    else: 
                        for pos,y in enumerate(range(down['start'][1],down['start'][1]+down['length'],1)):
                            attemptList[y][x]=attempt[pos]
        
                    '''
                    print("checkpoint after solving one iteration", i, 'down')
                    for a in attemptList:
                        print(a)        
                    '''
                    
                i+=1
            if i>=maxReached: 
                maxReached = i 
                best = attemptList.copy() 
                #print("reached",i, "faildirection", failDirection, "faillocation", failLocation, "matchA", failMatchA,"matchD", failMatchD)
                '''
                for p in attemptList:
                    print(" ".join(p))
                '''
                
        print()

        '''
        print("checkpoint after solving all iterations")
        for a in attemptList:
            print(a)        
        '''
        
        #double-check that all words are valid
        #note - puzzle shouldn't reach this stage with invalid words but this simply serves as a double-check
        _, _, acrossListT, downListT = findWords(attemptList) 
        wordsT = [x['patternIn'] for x in acrossListT]+[x['patternIn'] for x in downListT]
        for w in wordsT:
            try:
                [a,b]=w.split('=')
                if (eval(a)!=eval(b)):
                    print()
                    print(a,b,"ERROR, RETRYING *********************************************")
                    
                    fail=True
                    attemptList=[x.copy() for x in patternList.copy()] 

            except:
                print("ERROR EVALUATING WORD", w, "*************************************")
                fail=True
                attemptList=[x.copy() for x in patternList.copy()] 
                            
        
        if fail==False:
            #check duplicates
            puzzleJoined = ",".join(["".join(x.copy()) for x in attemptList.copy()]) 
            if "_" in puzzleJoined: 
                print("__ error")
                sys.exit()
            puzzleListJoined=[",".join(["".join(x.copy()) for x in y]) for y in puzzleList.copy()]
            if puzzleJoined in puzzleListJoined:
                print("DUPLICATE PUZZLE")
            else:
                print("SUCCESS")
                for p in attemptList:
                    print(" ".join(p))

                success+=1
                puzzleList+=[attemptList]

                if len(puzzleList)%10==0:
                    with open('output/'+fileStem+'_answers.json', 'w') as f:
                        json.dump(puzzleList, f)
            
        else: 
            print("FAILED")

#save puzzles to file
with open(fileStem+'_puzzleList.json', 'w') as f:
    json.dump(puzzleList, f)

'''
#print puzzles
for x in puzzleList:
    for y in x:
        print(y)
    print()

   
'''    