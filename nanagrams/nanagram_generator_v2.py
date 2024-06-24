# -*- coding: utf-8 -*-
"""
@author: richard mann, nerdle

A nangram puzzle is a list of between 5 and 9 'characters' being either digits 0-9 or symbols +-*/.  
Each puzzle has a number of possible aswers that can be used by using some or all of the characters
The equals sign plus one additional character is compulsory i.e. must be used in each answer.  
Each character can either be used once or not at all.  No repeats allowed.

File inputs:
    - 'word' lists being all valid calculations of length 3-9 (although length 3 actually specified in the script)

Algorithm:
    - Choose random calculation of desired length from full list and choose one character to be compulsory
    - Calculate all possible calculations that can be made by using all or a subset of the characters (but including the compululsory character)
    - Reduce answers to a smaller list by treating commuative answers as the same answer
    - Identify which answers are simple rearrangements of each other so that these can be auto-solved by user clicking the 'rearrange' button
    
    
File output:
    - [fileStem]_[number_of_puzzles](Ln).json - where 'n' = targetLength
    - output columns are:
        'question, - full question (6-9 characters depending on settings)
        'answersLong' - all answers, including commutative variations
        'answersLongCommutative' - lists first index of answer this answer is commutative with (a+b=c is commutative with b+a=c)
        'answersShort' - all answers, excluding commutative repeat variations
        'answersShortCommutative' - short version of answersLongCommutative index list
        'answersShortCommutations'- lists number of commutations of each short answer
        'answersShortRearrangements' - lists index of answer that this answer could be rearranged with (a+b=c could be rearranged to a=c-b)
        'fixed' - identifies which characters are fixed i.e. compulsory in the answer
        'questionCoded' - question including encoding of which characters are fixed
        'questionFixed' - fixed encoding arranged as string like question
    
"""

import random
import pandas as pd
import cv2
import numpy as np
import itertools 
import json  
import sys
import pandas
import cv2

# setting params

#number of games to be created
targetPuzzles = 10 #number of puzzles to be produced
targetLength = 9 #length of puzzles (6,7,8 or 9 for different nanagram levels)
maxDoubles = 1 #max number of doubles allowed (only 0 and 1 supported)
minSolutions = 8 #minimum number of answers - we don't want too few answers to find
maxSolutions = 20 #maximum number of answers - don't want too many answers to find
maxAtTargetLength = 3 #max number of possible answers (exc commutatives) that include all characters i.e. length answer = length question
visualisePuzzles = False #if True, script will visualise puzzles in cv2 window (space to rearrange, escape to close)

if targetLength == 6:
    minSolutions = 1
    maxDoubles = 2
    maxAtTargetLength = 6 
if targetLength == 7:
    minSolutions = 6
    maxAtTargetLength = 6 

filePrefix = 'nanagramPuzzles' 


def components(a):
    [al, ar] = a.split("=")
    for x in '()+-*/':
        al=al.replace(x,"~"+x+"~")
    #double ~ can only appear with brackets eg +() 
    al.replace("~~","~") 
    al.replace("~~","~") 
    al = al.split("~")
    al = [x for x in al if x!=""] #blanks can occur at the start if a bracket
    return(al,ar)

def jitter(al):
    jitterA=[]
    for x in al:
        if x in '()+-*/':
            jitterA+=x
        else:
            jitterA+=[str(int(x)+int(x)*int(x)/(int(x)+1))]
    return(jitterA)

def commutativeCheckSpecial(a,b):
    
    if not commutativeCheck(a,b):
        return False
    #The code is currently only designed to work with max 1 double
    
    #does question have a double?
    #No - proceed with normal check    
    #Yes - does double cancel out (4/4) (check by replacing both 4s with the same new number)
        #No - proceed with normal check
        #Yes - replace one of the doubles with something else and check if either alternative is commutative

    #does question not have a double?
    if (len(set([x for x in a if x not in '+-*/']))==len([x for x in a if x not in '+-*/'])):
        return (True)

    #Does double cancel out (4/4) (check by replacing both 4s with the same new number)

    dupes = [x for n, x in enumerate(a) if (x in a[:n]) & (x not in '+-*/')]
    
    double = dupes[0]
    
    morphAtemplate = a.replace(double,'X',1).replace(double,'Y',1)
    morphBtemplate = b.replace(double,'X',1).replace(double,'Y',1)
    morphA = a.replace(double,str(int(double)+1))
    #morphB = b.replace(double,str(int(double)+1))
    
    if not (eval(morphA.replace('=','=='))):
        return (True)
    
    #Is till commutative if replace one of doubles with something else (check both combos)?
    morph1A = morphAtemplate.replace('X',str(int(double)+1)).replace('Y',double).split('=')[0]
    morph1B = morphBtemplate.replace('X',str(int(double)+1)).replace('Y',double).split('=')[0]
    morph1A = morph1A+'='+str(eval(morph1A))
    morph1B = morph1B+'='+str(eval(morph1B))

    #morph2A = morphAtemplate.replace('Y',str(int(double)+1)).replace('X',double).split('=')[0]
    morph2B = morphBtemplate.replace('Y',str(int(double)+1)).replace('X',double).split('=')[0]
    #morph2A = morph2A+'='+str(eval(morph2A))
    morph2B = morph2B+'='+str(eval(morph2B))
    
    #Check only if 1A commutes with either 1B or 2B
    if (commutativeCheck(morph1A,morph1B)) | (commutativeCheck(morph1A,morph2B)) & commutativeCheck(a,b):
        return(True)
    
    return(False)

def commutativeCheck(a,b):
    if len(a)!=len(b):
        #different lenghts, cant be commutative
        return(False)
    
    al,ar = components(a)
    bl,br = components(b)
    
    altemp = al.copy()
    altemp.sort()
    bltemp = bl.copy()
    bltemp.sort()
    
    if altemp!=bltemp:
        #different constituen parts, cant be commutative
        return(False)

    jitterA = jitter(al)
    jitterB = jitter(bl)

    #print(jitterA, jitterB)

    #check valid inputs
    if eval("".join(al))==eval(ar):
        #print("a valid")
        pass
    else:
        print("a not valid") 
        sys.exit()
    if eval("".join(bl))==eval(br):
        #print("b valid")
        pass
    else:
        print("b not valid") 
        sys.exit()

    #check commutative
    if (abs(eval("".join(jitterA))-eval("".join(jitterB)))<0.00000001):
        commutative=True
    else:
        commutative=False

    return(commutative)

def shiftLeft(x):
    l,r = x.split("=")
    xNew = l+"-"+r+"=0"
    return(xNew)

def shiftLeft2(x):
    l,r = x.split("=")
    xNew = "("+l+")/"+r+"=1"
    return(xNew)

def checkRearrangement(a,b):
    aLeft = shiftLeft(a)
    bLeft = shiftLeft(b)
    
    aLeftPlus = "+"+aLeft
    bLeftPlus = "+"+bLeft
    bLeftMinus = bLeftPlus.replace("+","@").replace("-","+").replace("@","-")
    if commutativeCheckSpecial(aLeft,bLeft):
        return(True)
    if commutativeCheckSpecial(aLeftPlus,bLeftMinus):
        return(True)
    
    aLeft2 = shiftLeft2(a)
    bLeft2 = shiftLeft2(b)
    if commutativeCheckSpecial(aLeft2,bLeft2):
        return(True)

    return(False)
            
def visualise(nanagram,fixed):
    letters = nanagram.copy()

    letters+=" "*(9-len(letters))
    for item in fixed:
        instance=0
        for i in range(len(letters)):
            if (letters[i]==item) & (instance==0):
                letters[i]="~"+letters[i]
                instance+=1                
        
    cellWidth=50
    patternShape = [3,3]
    
    puzzle = np.zeros((patternShape[1]*cellWidth,patternShape[0]*cellWidth,3)).astype(np.uint8)
    puzzle[:,:]=[88,4,130] #slightly grey
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 1
    color = (255,255,255)
    thickness = 2
    for row in range(patternShape[0]):
        for col in range(patternShape[1]):
            letter = letters[row*patternShape[1]+col]
            #print(letter)
            #puzzle[row*cellWidth:(row+1)*cellWidth,col*cellWidth:(col+1)*cellWidth,:]=255
            (width, height),_ = cv2.getTextSize(letter[-1], font, fontScale, thickness)
            #print(width,height)
            cv2.rectangle(puzzle, (col*cellWidth,row*cellWidth), ((col+1)*cellWidth,(row+1)*cellWidth), (0,0,0))
            if letter[0]=="~":
                cv2.rectangle(puzzle, (col*cellWidth,row*cellWidth), ((col+1)*cellWidth,(row+1)*cellWidth), (178,36,248), -1)
                letter=letter[1]
                #print(letter)
            cv2.putText(puzzle, letter, (col*cellWidth+int(cellWidth/2-width/2),row*cellWidth+cellWidth-int(cellWidth/2-height/2)),font, fontScale, color, thickness, cv2.LINE_AA)

    cv2.imshow("viz",puzzle)
    k=cv2.waitKey(0)
    cv2.destroyAllWindows()
    return(puzzle,k==27)


words={}
words['9nz'] = pandas.read_csv('input/nerdlewords9.txt', header=None, names=['word'])
words[9] = pandas.read_csv('input/nerdlewords9z.txt', header=None, names=['word'])
words[9] = words[9][words[9].word.apply(lambda x: x[4]!="=")] #remove words such as 1234=1234
words[8] = pandas.read_csv('input/nerdlewords8z.txt', header=None, names=['word'])
words[7] = pandas.read_csv('input/nerdlewords7z.txt', header=None, names=['word'])
words[6] = pandas.read_csv('input/nerdlewords6z.txt', header=None, names=['word'])
words[5] = pandas.read_csv('input/nerdlewords5z.txt', header=None, names=['word'])
words[3] = pd.DataFrame(['0=0','1=1','2=2','3=3','4=4','5=5','6=6','7=7','8=8','9=9'], columns=['word'])
#words[3] = pd.DataFrame(['1=1','2=2','3=3','4=4','5=5','6=6','7=7','8=8','9=9'], columns=['word'])

#clean files for correct length)
print("CLEANING FILES") 
for length in [3,5,6,7,8,9]:
    #print("LENGTH", length) 
    words[length] = words[length][words[length]['word'].apply(lambda x: len(x)==length)]
    words[length] = words[length].drop_duplicates()


#add sorted word for matching
print("ADDING SORTED KEY") 
for length in [3,5,6,7,8,9]:
    #print("LENGTH", length) 
    words[length]['sorted'] = words[length]['word'].apply(lambda x: "".join(sorted(x.replace("=",""))))

puzzles=[]
p=-1

while len(puzzles)<targetPuzzles:
    p+=1
    print()
    print("***CREATING PUZZLE", p)
    found=False
    while found==False:
        if targetLength==9: 
            calcQuestion= [x for x in words['9nz'].sample(1).word.tolist()[0]] #choose from non zero list otherwise too likely to contain a zero

        else:
            calcQuestion= [x for x in words[targetLength].sample(1).word.tolist()[0]]

        

        #force first puzzle to check commutativity issue
        calcQuestionNoEquals = calcQuestion.copy() 
        calcQuestionNoEquals.remove("=")
    
        #check that puzzle meets certain critera
        if (("*" in calcQuestion) or ("/" in calcQuestion)) & ("1" in calcQuestion):
            #remove possibility of *1 or /1
            pass 
            print("REJECT: *1 or /1; ", end="")

        elif len(calcQuestion)-len(set(calcQuestion))>maxDoubles:
            pass 
            print("REJECT: fail doubles; ", end="")
        elif len(calcQuestion)-len([x for x in calcQuestion if x!='0'])>0:
            pass
            print("REJECT: no double zero;", end="")
        
        
        else:
            #print("pass doubles", calcQuestion)
            
            #start game creation
            randomQuestion = calcQuestion.copy()
            random.shuffle(randomQuestion)
            
            #get all answers of length 3-9
            answers=[]
            for length in [x for x in [3,5,6,7,8,9] if x<=targetLength]:
                newAnswers=[]
                combos = set(itertools.combinations(sorted(calcQuestionNoEquals), length-1))
                #filter out only combos that exist as an entry in the sorted word list
                for c in combos:
                    co = "".join(c) 
                    matches = words[length][words[length]['sorted']==co]
                    if len(matches)>0:
                        newAnswers+=matches.word.tolist()
                answers+=newAnswers

            answersDf = pd.DataFrame(answers, columns=['word'])
            answersDf['length']=answersDf['word'].apply(lambda x: len(x))
            answersDf['commutativeWith'] = 9999
            for index1, row1 in answersDf.iterrows():
                for index2, row2 in answersDf.iterrows():
                    #print(index1,index2)
                    if index1!=index2:
                        a = answersDf.at[index1,'word']
                        b = answersDf.at[index2,'word']
                        if commutativeCheckSpecial(a,b):
                            answersDf.at[index1,'commutativeWith']=min(index1,index2,answersDf.at[index1,'commutativeWith'],answersDf.at[index2,'commutativeWith'])
                            answersDf.at[index2,'commutativeWith']=min(index1,index2,answersDf.at[index1,'commutativeWith'],answersDf.at[index2,'commutativeWith'])

            #sort answers by length and then alphabetically
            answersDf = answersDf.sort_values(by=['length','word'])

            
            #now create shorter list combining commutatives together
            uniqueList = set(answersDf.commutativeWith)
            reducedAnswers = []
            for u in [u for u in uniqueList if u!=9999]:
                subset = answersDf[answersDf.commutativeWith==u]
                reducedAnswers+=[[subset.word.iloc[0],subset.length.iloc[0],subset.commutativeWith.iloc[0],len(subset)]]
            
            subset999 = answersDf[answersDf.commutativeWith==9999]
            for i,row in subset999.iterrows():
                reducedAnswers+=[[row.word,row.length,9999,1]]
                
            reducedAnswersDf = pd.DataFrame(reducedAnswers, columns=['word','length','commutativeWith','commutations'])
            #reducedAnswersDf = reducedAnswersDf.sort_values(by=['length','commutations'])
            reducedAnswersDf = reducedAnswersDf.sort_values(by=['length','word'])
        
            #Version 2: random fixed
            centre = random.sample([x for x in randomQuestion if x!="="],1)[0] 
            answersDfSelect = answersDf[answersDf['word'].apply(lambda x: centre in x)]
            reducedAnswersDfSelect = reducedAnswersDf[reducedAnswersDf['word'].apply(lambda x: centre in x)].copy()
    
            if len(reducedAnswersDfSelect[reducedAnswersDfSelect.length==targetLength])<=maxAtTargetLength:
                if (len(reducedAnswersDfSelect)<=maxSolutions) & (len(reducedAnswersDfSelect)>=minSolutions):
                    found=True
                else:
                    print("REJECT: wrong number of solutions:", len(reducedAnswersDfSelect))
            else:
                print("REJECT: too many solutions at max length:", len(reducedAnswersDfSelect[reducedAnswersDfSelect.length==targetLength]))
                #print(reducedAnswersDfSelect[reducedAnswersDfSelect.length==targetLength])
            

            #Add calculation of rearrangements
            reducedAnswersDfSelect.loc[:,'rearrangesWith'] = 9999
            for index1, row1 in reducedAnswersDfSelect.iterrows():
                for index2, row2 in reducedAnswersDfSelect.iterrows():
                    #print(index1,index2)
                    if index1!=index2:
                        a = reducedAnswersDfSelect.at[index1,'word']
                        b = reducedAnswersDfSelect.at[index2,'word']
                        if checkRearrangement(a,b):
                            reducedAnswersDfSelect.at[index1,'rearrangesWith']=min(index1,index2,reducedAnswersDfSelect.at[index1,'rearrangesWith'],reducedAnswersDfSelect.at[index2,'rearrangesWith'])
                            reducedAnswersDfSelect.at[index2,'rearrangesWith']=min(index1,index2,reducedAnswersDfSelect.at[index1,'rearrangesWith'],reducedAnswersDfSelect.at[index2,'rearrangesWith'])
            
    #Pad question with spaces to length 9
    randomQuestion+=" "*(9-len(randomQuestion))

    puzzleItem = {}
    puzzleItem['question']=randomQuestion
   
    puzzleItem['answersLong']=answersDfSelect.word.to_json(orient="records") 
    puzzleItem['answersLongCommutative']=answersDfSelect.commutativeWith.to_json(orient="records") 
    puzzleItem['answersShort']=reducedAnswersDfSelect.word.to_json(orient="records") 
    puzzleItem['answersShortCommutative']=reducedAnswersDfSelect.commutativeWith.to_json(orient="records") 
    puzzleItem['answersShortCommutations']=reducedAnswersDfSelect.commutations.to_json(orient="records") 
    puzzleItem['answersShortRearrangements']=reducedAnswersDfSelect.rearrangesWith.to_json(orient="records") 
    puzzleItem['fixed']=[centre,"="]


    letters = randomQuestion.copy()

    letters2 = ["" for x in randomQuestion]
    centre+="=" 
    for item in centre:
        instance=0
        for i in range(len(randomQuestion)):
            if (letters[i]==item) & (instance==0):
                letters[i]="~"+letters[i]
                letters2[i]="~"
                instance+=1
                

    puzzleItem['questionCoded']=letters
    puzzleItem['questionFixed']=letters2
    
    
    puzzles+=[puzzleItem]
        

    print()
    print("SUCCESS: question =", calcQuestion)

#remove duplicates
newPuzzles = [puzzles[0]]

print()
print("REMOVING DUPLICATES")
for i,puzzle in enumerate(puzzles[1:]):
    if puzzle['answersLong'] == newPuzzles[-1]['answersLong']:
        print("same 2 days in a row, skipping", i)
    else:
        if puzzle['answersLong'] in list(pd.DataFrame(newPuzzles).answersLong):
            print("already in file, skipping", i)
        else:
           print("adding new game")
           newPuzzles+=[puzzle]

print("file length, de-duped file length", len(puzzles), len(newPuzzles))    

#save file
puzzleFileName = filePrefix+'_'+str(targetPuzzles)+"(LN).json".replace('LN','L'+str(targetLength))
with open('output/'+puzzleFileName, 'w') as f:
        json.dump(newPuzzles, f)

#visualise final puzzle in CV2 window
if visualisePuzzles:    
    escape=False
    while escape==False:
        random.shuffle(randomQuestion)
        puzzle,escape=visualise(randomQuestion.copy(),centre)
    
#Check unique solutions
print("unique questions", len(pd.DataFrame(newPuzzles).question.apply(lambda x: "".join(x)).unique()))
print("unique answers", len(pd.DataFrame(newPuzzles).answersLong.apply(lambda x: "".join(x)).unique()))

newpuzzlesDf = pd.DataFrame(newPuzzles)

print(newpuzzlesDf[['question','answersShort']])