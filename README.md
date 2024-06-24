# Nerdle secondary game - creator scripts

Nerdle secondary games covered in this repository are:

- 2d (see code in shuffleNumbers folder)
- Cross nerdle
- Nanagrams
- ShuffleNumbers
- ShuffleWords
- Targets

# Python creator script

Each folder contains a python script that generates .json output containing all the game info (eg starting puzzle and solution) required by the front end game application to run the game

Each folder also contains an 'output' folder where output files are saved to.  

Some games require input files.  Eg a word / calculation list or puzzle template.  In these cases, the files are saved in an 'input' folder

# Game creation logic

Each python script is set out in a consistent manner and includes the following:

- Comments to explain the high level steps in the game creation process
- Imports
- Game parameters (eg the number of output games to be created)
- Game functions
- Main code to loop through the required number of games to be created

