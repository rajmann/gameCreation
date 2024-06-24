# Nerdle

Rules:

- 8 “letters” 
- A “letter” is one of 0123456789+-*/=
- And a word must be a sum that is mathematically correct.
- So it must have one “=”
- Also, the number on the right of the “=” is just a number (not another sum)
 
- Standard order of operations applies, so calculate * and / before + and -.
 
So valid “words” are for example:

- 3+6*4=27
- 99+3=102
- 9*27=243
- 99/9+1=2

## Setup and build

- Install ts-node (npm install -g ts-node)

- Create the 'word' files/folders:

  - Easiest way is to unzip scripts/word_folders.zip and copy the contents into the public folder. This zip file has been created after the word folders were already generated. They do not need to change. 

  - Otherwise, if you want to start from scratch, run the word-per-file.ts and speed-words.ts scripts to generate the 'word' files:
    - cd scripts
    - ts-node word-per-file.ts
    - ts-node speed-words.ts

  - Move the generated 'words', 'miniwords', 'microwords', 'midiwords', 'instantwords' and 'speedwords' folders from scripts folder into public folder

  - Alternatively unzip the word_folders.zip file into the public folder!  Anything in the public folder is automatically deployed to the build folder by react.

- npm start

## To deploy

- AWS CLI is required with API credentials
- npm run build
- npm run deploy
- We need to tell CloudFront to invalidate index.html:
    - npm run invalidate

## Deploying the word files

As the word files are in the public folder, and react copies anything from here into the build folder, an initial build and deployment of the game will deploy the word folders too.  So:

- npm run build

The included npm run deploy script excludes the word folders from deployment. This is to prevent S3 from trying to sync thousands of files each time we deploy an updatre. The word folders do not change so do not need to be deployed each time there is an update. 

However, if you want to deploy application somewhere else, or to deploy for the first time, either just manually upload the generated build folder and all sub folders to your server, or if using S3 you could sync the entire build folder without the exclusions:

- aws s3 sync build/ s3://nerdle-serverless-app --acl public-read 

## How word files are constructed and decoded

Initially a list of solutions was created using the nerdle_gen.py script. The list was then converted to a JS array and randomised. You will find the arrays in wordlist.ts, miniwordlist.ts, microwordlist.ts, etc ... these should never change. Never change existing solutions for day indexes prior to current as this will impact replays.

The word-per-file.ts script (and speed-words.ts script) take an array of solutions (from the files mentioned above) and create a separate file for each solution in a new folder. The solution is first obfuscated using a simple ROT13 like alogorithm and the filename is the MD5 hash of the array index.

The generated word folders are then manually copied to the public folder. Therefore when the game is initially built and deployed these will be included as anything in the public folder is automatically copied to the build folder by react (npm run build)

When the games starts the array index is determined based on the date and a predefined epoch, that index is then MD5 hashed and the file is then fetched. The content of the file is then decoded.

See: 
- lib/words.ts 
- lib/deObfs.ts

The benefits of this approach are:
- The solution array is not visible in the client side source code, making it harder to determine the day's solution
- The solution array is large so it further reduces bandwidth as the entire array does not have to be downloaded with the code
- The basic deobfuscation means it's harder to determine the solution by looking at the content of the fetched file

Cheating is not considered a major issue as people will only be cheating themselves. Other games made it easy to determine the days solution by looking at the source code and there's a limit to what can be done with purely client side code. Determined 'hackers' or experienced developers will have no difficulty but making it a little less obvious for everyone else makes sense.

### pro nerdle

Pro nerdle allows people to create custom games. It's not a daily game. Instead puzzles are created (by create.html in nerdle-static repo). A special URL is created .. e.g. https://pro.nerdlegame.com/773284e85262f188bd631799f5bc68b4/6/EOCFd%C2%B2%C2%B3 where the first parameter is an encoded puzzle. This requires two back end Lambda functions - encodeSolution to create it and decryptSolution for the game to decode it. See serverFunctions folder.

## game modes and domains

nerdlegame.com, mini.nerdlegame.com, micro.nerdlegame.com, speed.nerdlegame.com, instant.nerdlegame.com, maxi.nerdlegame.com and pro.nerdlegame.com are all handled by this app. Each domain resolves to the same location. The app checks the subdomain to determine the 'gameMode'. See top of App.tsx.

One benefit of this is that localStorage is kept separate for each game, simplifying the structure of local storage (no need to differentiate between games - stats are separate etc). 

Keeping localStorage separate is also a disadvantage! E.g. keeping track of the Leaderboardle session token across all games to prevent the user having to log in for each game is made a little more complex - this is mitigated for Chrome by requesting a page in an iframe for each domain and passing the token to it. For the mobile APP it is simply achieved using message handling so that the app itself can store the token. An issue exists with Safari which is far more strict with cross site scripting to the extent it will block localStorage access in an iframe hosted at a different subdomain.

bi.nerdlegame.com and mini.bi.nerdlegame are hosted separately as these require different game code. See bi-nerdle repository.