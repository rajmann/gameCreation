# -*- coding: utf-8 -*-
"""
@author: richard mann, nerdle

A solved shuffle puzzle is a magic square of 5 letter words.
This file then generates a question by playing a shuffle sliding puzzle game in reverse.  

File inputs:
    - Valid word list file (note: this is currently augmented in the script)

Algorithm step 1 - generate solved puzzles exhaustively:
    - Generate a magic square by selecting random starting word and then attempting to fit other words
    - There are not that many possible magic words so it makes sense to generate an exhaustive list by iterating through the word list and generating a magic square by attempting to fit other words until valid solution found
    - File output = 'allMagicSqWords_dedupesNew.json' - currently 1006 solutions
    
Algorithm step 2 - generate question from solved puzzle:
    - Enter "n" at prompt to avoid regenerating exhaustive magic square list
    - Create file of desired length by repeating input list if required (starting puzzles will be different even if solutions are the same)
    - Play game backwards by 'unshuffling' (for Shuffle) n times to create question  
    
File output:
    - [fileStem]_[number_of_puzzles]_A.json - solved puzzles
    - [fileStem]_[number_of_puzzles]_Q.json - starting questions
    - [fileStem]_[number_of_puzzles]_Moves.json - move sequence to solve (not required for game)
    
"""

from collections import Counter
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

# setting params

#number of games to be created
questions = 10
filePrefix = 'shufflePuzzlesWords' 

fileStem = filePrefix + '_'+str(questions)


def permutations(lngth=5):  
    #start with original 2309 words
    di = pd.read_csv('input/5letterOriginals.txt') #2309 words
    di.words = di.words.apply(lambda x: x.upper())
    
    
    #add additional words to make more possibilities
    
    addWords = ['SALES', 'TERMS', 'WORKS', 'TIRED', 'LATIN', 'ARMED', 'SLAVE', 'YOURS', 'NAKED', 'JEANS', 'ROMAN', 'GREEK', 'MIXED', 'CUBAN', 'FIXED', 'ADDED']
    for word in addWords:
        if word not in list(di.words):
           di = di.append(pd.Series({'words':word}),ignore_index=True)

    addWords = ['WORDS', 'YEARS', 'ASKED', 'PARTS', 'TIMES', 'MEANS', 'MILES', 'LINES', 'TREES', 'HANDS', 'KINDS', 'MAKES', 'COMES', 'LIVED', 'SHOWS', 'BIRDS', 'GIRLS', 'HOURS', 'MOVED', 'NAMES', 'FORMS', 'IDEAS', 'NAMED', 'BOOKS', 
                'TAKES', 'SEEMS', 'SIDES', 'TELLS', 'GIVES', 'LOOKS', 'LIVES', 'STEPS', 'AREAS', 'CELLS', 'PAGES', 'SHIPS', 'NEEDS', 'ROCKS', 'STARS', 'SONGS', 'WAVES', 'WEEKS', 'LANDS', 'LIKED', 'WAXES', 'KNOWS', 'HOMES', 'FACTS', 
                'RULES', 'NOTES', 'UNITS', 'VERBS', 'SEEDS', 'HELPS', 'WOODS', 'WALLS', 'WINGS', 'CASES', 'FOODS', 'CROPS', 'WANTS', 'NOUNS', 'BONES', 'TURNS', 'MOVES', 'BASED', 'MARKS', 'FARMS', 'SHOES', 'GOODS', 'CENTS', 'PAIRS', 
                'ROOTS', 'HEADS', 'SIGNS', 'HILLS', 'TYPES', 'LOVED', 'FACES', 'BOATS', 'TOWNS', 'PLANS', 'YARDS', 'TOOLS', 'BOXES', 'ROADS', 'WINDS', 'GAMES', 'FALLS', 'PLAYS', 'ATOMS', 'GROWS', 'SAVED', 'KEEPS', 'EDGES', 'BELLS',
                'ENDED', 'HOLES', 'HOLDS', 'COSTS', 'CALLS', 'TONES', 'GASES', 'DOORS', 'POLES', 'TEARS', 'TESTS', 'ITEMS', 'HOPED', 'LAKES', 'ROOMS', 'LIKES', 'KNEES', 'DROPS', 'BANKS', 'FLIES', 'FEELS', 'FLOWS', 'OWNED', 'SIZES',
                'NOTED', 'LUNGS', 'BEARS', 'KINGS', 'CARDS', 'BEATS', 'WIRES', 'FINDS', 'POEMS', 'BEANS', 'RISES', 'STEMS', 'BOOTS', 'TUBES', 'ACRES', 'FACED', 'MINES', 'RACED', 'WAVED', 'MILLS', 'VIEWS', 'SPOTS', 'RINGS', 'NAILS',
                'HORNS', 'BALLS', 'RATES', 'SKINS', 'WAXED', 'SEATS', 'MINDS', 'COINS', 'TRIPS', 'LEADS', 'HOPES', 'BASES', 'FIRES', 'MEALS', 'SHOPS', 'TEAMS', 'FOLKS', 'FIRED', 'BANDS', 'RULED', 'WALKS', 'TALES', 'GERMS', 'READS',
                'DUCKS', 'GIFTS', 'LISTS', 'STOPS', 'CLAWS', 'BEADS', 'CAKES', 'LIONS', 'FROGS', 'TRIES', 'TAXES', 'PULLS', 'DRUMS', 'TALKS', 'DATES', 'BLOWS', 'WAGES', 'DRUGS', 'TANKS', 'SINGS', 'TAILS', 'HERDS', 'HATED', 'CLUES',
                'RACES', 'HEELS', 'COATS', 'DIMES', 'PIPES', 'WORMS', 'BILLS', 'SUITS', 'RAINS', 'PARKS', 'ROLLS', 'GATES', 'PATHS', 'FUNDS', 'TIDES', 'SAILS', 'URGED', 'NESTS', 'WEEDS', 'ACTED', 'GOATS', 'LOVES', 'BACKS', 'ROPES',
                'SHOTS', 'PEAKS', 'CRIES', 'ASHES', 'OPENS', 'WIVES', 'BURNS', 'POETS', 'BAKED', 'SORTS', 'STAYS', 'WIPED', 'PILED', 'CLUBS', 'HIDES', 'DEEDS', 'RIDES', 'SENDS', 'TENTS', 'ROSES', 'POSTS', 'HIRED', 'BOWED', 'TIRES',
                'BELTS', 'TENDS', 'LOADS', 'JOKES', 'VEINS', 'HEARS', 'LOSES', 'HOSTS', 'TOADS', 'TASKS', 'SEAMS', 'JUMPS', 'FEARS', 'PORTS', 'SOCKS', 'GOALS', 'FILMS', 'TUNES', 'FIRMS', 'SKIES', 'BONDS', 'DARED', 'FADED', 'PANTS',
                'VOTES', 'WELLS', 'HAIRS', 'WEARS', 'DOLLS', 'VOTED', 'CAVES', 'CARED', 'BENDS', 'LAMPS', 'RUINS', 'SCHWA', 'LAMBS', 'SELLS', 'COOLS', 'LIMBS', 'GAZED', 'CUBES', 'BEAMS', 'RANKS', 'VINES', 'PICKS', 'SOILS', 'PONDS',
                'TWINS', 'POOLS', 'REEDS', 'HOOFS', 'BUSES', 'MELTS', 'FLAGS', 'ROOFS', 'PILES', 'AIMED', 'TWIGS', 'RESTS', 'CORDS', 'TUNED', 'DIVED', 'MOLDS', 'YARNS', 'GULLS', 'RAILS', 'DRAWS', 'BOWLS', 'DEALS', 'KNOTS', 'MOONS',
                'HANGS', 'GAINS', 'BOMBS', 'PALMS', 'CONES', 'BORED', 'ACIDS', 'CAMPS', 'HOOKS', 'MALES', 'REINS', 'NOSES', 'LINKS', 'FILLS', 'SITES', 'MOTHS', 'MEATS', 'FOXES', 'MINED', 'TRAPS', 'GILLS', 'POLIO', 'SEALS', 'MULES',
                'FOLDS', 'JOINS', 'LORDS', 'DUNES', 'BURRO', 'HAWKS', 'FEEDS', 'HALLS', 'COALS', 'SOULS', 'PUMPS', 'LOANS', 'SPINS', 'FILES', 'PAINS', 'FLATS', 'SANDS', 'PINTS', 'CLAMS', 'CODES', 'FAILS', 'PAVED', 'ZONES', 'FOURS',
                'TILES', 'KILLS', 'ROLES', 'LOOPS', 'ZEROS', 'BITES', 'MODES', 'DEBTS', 'SWIMS', 'POKED', 'LIFTS', 'LUMPS', 'BARNS', 'DOCKS', 'MASTS', 'POURS', 'ROBES', 'SEEKS', 'CURLS', 'MYTHS', 'CAGES', 'LOCKS', 'BEETS', 'CROWS', 'ROWED', 'CHIPS', 'FISTS', 'WINES', 'CARES', 'NECKS', 'BLUES', 'CREWS', 'SAVES', 'IDOLS', 'COOKS', 'CARTS', 'BULBS', 'LAWNS', 'LASTS', 'FUELS', 'FILED', 'SLIPS', 'BOLTS', 'ATLAS', 'CRABS', 'DESKS', 'LEAPS', 'TUSKS', 'BULLS', 'MOODS', 'PINES', 'SACKS', 'FONTS', 'FERNS', 'TEENS', 'GENES', 'HAIKU', 'DIKES', 'EASED', 'TOMBS', 'DARTS', 'FORTS', 'HEATS', 'HERBS', 'USERS', 'AIDED', 'LACKS', 'MASKS', 'WADED', 'RISKS', 'SEWED', 'CURED', 'SINKS', 'COLTS', 'SLEDS', 'MAIDS', 'MEETS', 'HYMNS', 'HINTS', 'COILS', 'SNOWS', 'PLOWS', 'TAMED', 'WAITS', 'GLUED', 'WARMS', 'FOOLS', 'PEARS', 'GENUS', 'ACHED', 'FIVES', 'FLAPS', 'FUMES', 'CUFFS', 'CLIPS', 'DISKS', 'LANES', 'RAGED', 'TEXTS', 'TYPED', 'HATES', 'BEAKS', 
                'CASTS', 'BATHS', 'PLOTS', 'SLUMS', 'PUFFS', 'DECKS', 'EDGED', 'HEAPS', 'AUNTS', 'PACKS', 'CORPS', 'WIRED', 'HURTS', 'DATED', 'HUNTS', 'MISTS', 'DRIES', 'MATES', 'OASIS', 'BOILS', 'SPURS', 'DOVES', 'PACES', 'STRUM']

    ##Note: more words that could be added if desired: 'BALES', 'PIPED', 'TACKS', 'CITED', 'RENTS', 'YELLS', 'SNAPS', 'KICKS', 'SLITS', 'RATED', 'PLUMS', 'EARNS', 'SILKS', 'SLABS', 'BUMPS', 'EVILS', 'FANGS', 'GRINS', 'SCARS', 'CHOPS', 'RAIDS', 'SKIPS', 'SOLES', 'MISTY', 'KNOBS', 'PESTS', 'FORKS', 'TRAYS', 'PAILS', 'WARES', 'WAKES', 'POLLS', 'TAXIS', 'OASES', 'ASSES', 'SHEDS', 'PILLS', 'THINE', 'TIMED', 'GEARS', 'SIGHS', 'SLOWS', 'SIXES', 'PACED', 'SPIES', 'DISCS', 'POSED', 'SLOTS', 'TAXED', 'RAKED', 'CURDS', 'LOINS', 'TAPES', 'LEANS', 'BUNKS', 'TOWED', 'PANES', 'SAKES', 'HEIRS', 'PORES', 'WARNS', 'DRAGS', 'SQUID', 'PELTS', 'IRONS', 'BARKS', 'DIETS', 'WHIPS', 'DOZED', 'KITES', 'BIKES', 'TICKS', 'RIOTS', 'ROARS', 'LOOMS', 'PUPAE', 'DUCTS', 'LENDS', 'FEATS', 'ARGON', 'SEXES', 'SALTS', 'DINED', 'GUSTS', 'REEFS', 'OATHS', 'MIXES', 'RAFTS', 'DIVES', 'BROWS', 'STIRS', 'BARBS', 'VOLTS', 'BEIGE', 'LACED', 'LEAKS', 'FARES', 'SQUAW', 'DOSES', 'VASES', 'COLDS', 'MESSY', 'CORES', 'SOAKS', 'AMINO', 'MOWED', 'PEERS', 'VOWED', 'PIOUS', 'SWANS', 'EXITS', 'PLUGS', 'RITES', 'SERFS', 'GRUBS', 'WASPS', 'BARED', 'AUGER', 'CHAPS', 'FAIRS', 'MUMPS', 'EMERY', 'OVENS', 'ELVES', 'ROPED', 'GRABS', 'FLEAS', 'SAWED', 'COOKY', 'WAGED', 'VANES', 'COMBS', 'LACES', 'HUMPS', 'SWISS', 'MARES', 'SOAPS', 'HUSKS', 'SNIPS', 'LINED', 'CAFES', 'WRAPS', 'SIZED', 'PIERS', 'TONGS', 'TOURS', 'TUFTS', 'WILDS', 'LASER', 'HARES', 'TARRY', 'MUTED', 'FLIPS', 'CURES', 'BOXED', 'HOOPS', 'GASPS', 'HOODS', 'YUCCA', 'GLOWS', 'FUSES', 'GOWNS', 'BUCKS', 'PANGS', 'MAILS', 'URGES', 'SUNUP', 'MENUS', 'HOWLS', 'CAKED', 'BANGS', 'POSES', 'FINED', 'GRIPS', 'GAPED', 'HIKED', 'COCKS', 'DIALS', 'SLAPS', 'SOUPS', 'WILLS', 'FOAMS', 'SOLOS', 'EAVES', 'FUSED', 'LATEX', 'VEILS', 'MUSED', 'MAINS', 'RACKS', 'GALLS', 'GNATS', 'BOUTS', 'SISAL', 'SHUTS', 'HOSES', 'SEEPS', 'OBOES', 'SPANS', 'FOWLS', 'DARES', 'OBEYS', 'BAKES', 'GANGS', 'ACHES', 'CLAPS', 'FADES', 'PUSSY', 'TARTS', 'SHEAF', 'MOLES', 'VEXED', 'AUTOS', 'DOMES', 'SOWED', 'STUDS', 'SLUGS', 'ASPEN', 'HALTS', 'HOGAN', 'JEEPS', 'FINES', 'PROPS', 'PESOS', 'POKES', 'TILED', 'BINDS', 'CITES', 'FIXES', 'JERKS', 'WAKED', 'INKED', 'BOOMS', 'CHEWS', 'LICKS', 'TUCKS', 'MOLTS', 'SECTS', 'SPARS', 'DUMPS', 'WISPS', 'SORES', 'PANDA', 'AXLES', 'TINTS', 'TOLLS', 'FLAWS', 'SNAGS', 'MONKS', 'CRAGS', 'CAGED', 'TAPED', 'GRIDS', 'MORES', 'AIDES', 'BURRS', 'MUGGY', 'LITER', 'JOKED', 'EXAMS', 'LURED', 'OMENS', 'NEARS', 'ALDER', 'PRAYS', 'WRENS', 'HAULS', 'TILTS', 'PECKS', 'GALES', 'TEMPT', 'CAPES', 'MESAS', 'OMITS', 'LIMES', 'HIGHS', 'CANES', 'FARED', 'ASTIR', 'BUOYS', 'STUBS', 'AFORE', 'HULLS', 'CLOGS', 'SLATS', 'GAZES', 'CALMS', 'BITCH', 'GULPS', 'CODED', 'LOBES', 'ISLES', 'CLODS', 'DAZED', 'OOZED', 'CLAYS', 'WARTS', 'KETCH', 'MANES', 'FIORD', 'MINKS', 'THAWS', 'WATTS', 'PALED', 'TWAIN', 'PAWED', 'GABLE', 'WANED', 'WARDS', 'FAWNS', 'BABES', 'NINES', 'BUTTS', 'SILLS', 'JAILS', 'SABER', 'MITER', 'BEEPS', 'DOMED', 'GULFS', 'CURBS', 'MOORS', 'LARKS', 'CHEEP', 'RAGES', 'LURES', 'SLAMS', 'KNITS', 'SPITS', 'FIRTH', 'HIKES', 'TROTS', 'NOSED', 'BALSA', 'MIDDY', 'STILE', 'KEYED', 'WILES', 'AMIGO', 'COPRA', 'POPES', 'CHINS', 'TINES', 'GRITS', 'JUNKS', 'TOILS', 'MOCKS', 'SCANS', 'HOARY', 'REELS', 'SCUFF', 'FLOES', 'WIPES', 'KINKS', 'FRANC', 'LIARS', 'SOARS', 'SIDED', 'OVALS', 'HEALS', 'PLEAS', 'VENTS', 'WAKEN', 'CHIMP', 'FUMED', 'SODAS', 'WADES', 'MITES', 'BORES', 'MILKS', 'MIRED', 'CASKS', 'MOANS', 'ERRED', 'HEWED', 'STABS', 'PORED', 'RONDO', 'LOPED', 'HIRES', 'FOALS', 'FEUDS', 'JAMBS', 'THUDS', 'JEERS', 'GREYS', 'LYRES', 'GLUES', 'LOTUS', 'RUNGS', 'TOMMY', 'YOKES', 'EPICS', 'TRILL', 'PIKES', 'FREES', 'FAMED', 'ROBED', 'JACKS', 'RUMPS', 'PINKS', 'TOOTS', 'GLENS', 'COOED', 'RUSTS', 'STEWS', 'SHRED', 'CHUGS', 'WINKS', 'CLOTS', 'BOOED', 'DENTS', 'GRAYS', 'HOOKY', 'DOGIE', 'POLED', 'REAMS', 'FIFES', 'OPALS', 'COCKY', 'FAKED', 'HYDRA', 'BRAGS', 'YANKS', 'ALTOS', 'EASES', 'METED', 'LONGS', 'QUAYS', 'DAWNS', 'DUETS', 'DREGS', 'WAILS', 'SUEDE', 'COVES', 'BREWS', 'SOFAS', 'CHUMS', 'ZOOMS', 'HALOS', 'CRIBS', 'SAGAS', 'HARPS', 'FLOPS', 'WEEPS', 'MINTS', 'FELTS', 'MEWED', 'DIVAN', 'VICES', 'BLOBS', 'BLOTS', 'CUBED', 'CLANS', 'FLEES', 'SLURS', 'GNAWS', 'WELDS', 'FORDS', 'EMITS', 'PUMAS', 'MENDS', 'DARKS', 'DUKES', 'PLIES', 'HOOTS', 'OOZES', 'LAMED', 'FOULS', 'CLEFS', 'NICKS', 'MATED', 'SKIMS', 'TINGE', 'FATES', 'THINS', 'FRETS', 'EIDER', 'FASTS', 'DAMPS', 'MORNS', 'CROON', 'TACOS', 'SKITS', 'MIKES', 'QUITS', 'ASTER', 'ADDER', 'SCOWS', 'BALED', 'LAVAS', 'WELTS', 'BUSTS', 'RAZED', 'SHINS', 'TOTES', 'SCOOT', 'DEARS', 'MUTES', 'TRIMS', 'SKEIN', 'DOTED', 'SHUNS', 'VEERS', 'FAKES', 'YOKED', 'WOOED', 'HACKS', 'WANDS', 'LULLS', 'SEERS', 'SNOBS', 'NOOKS', 'PINED', 'MOOED', 'DINES', 'DRIPS', 'LEVEE', 'SIDLE', 'CORKS', 'YELPS', 'BUFFS', 'TIERS', 'BOGEY', 'DOLED', 'VALES', 'COPED', 'HAILS', 'BULKS', 'AIRED', 'STAGS', 'STREW', 'COCCI', 'PACTS', 'SCABS', 'SILOS', 'DUSTS', 'YODEL', 'JADED', 'BASER', 'JIBES', 'FOILS', 'SWAYS', 'SLAYS', 'PREYS', 'TREKS', 'PEEKS', 'LURKS', 'BOARS', 'WANES', 'LUTES', 'WHIMS', 'DOSED', 'CHEWY', 'TEEMS', 'DOZES', 'KELPS', 'UPPED', 'DOPED', 'RINDS', 'VOILE', 'JESTS', 'SLEWS', 'TOTED', 'RAVES', 'SULFA', 'GRIST', 'SKIED', 'CIVET', 'HOMEY', 'MOPED', 'RUNTS', 'SERGE', 'RILLS', 'CORNS', 'BRATS', 'PRIES', 'FRIES', 'LOONS', 'TSARS', 'PIGMY', 'RAVEL', 'OVULE', 'FRAYS', 'SILTS', 'SIFTS', 'PLODS', 'RAMPS', 'TRESS', 'EARLS', 'DUDES', 'KARAT', 'JOLTS', 'PEONS', 'BEERS', 'PALES', 'LAIRS', 'LYNCH', 'ROVES', 'KILTS', 'ADIOS', 'DULLS', 'MEMOS', 'DALES', 'PEELS', 'PEALS', 'BARES', 'SINUS', 'SABLE', 'HINDS', 'ENROL', 'WILTS', 'ROAMS', 'DUPED', 'CYSTS', 'MITTS', 'SAFES', 'SPATS', 'COOPS', 'KNELL', 'PUNKS', 'KILNS', 'FITLY', 'TALCS', 'HEEDS', 'DUELS', 'WANLY', 'RUFFS', 'GAUSS', 'GAUZY', 'EDITS', 'WORMY', 'MOATS', 'PRODS', 'VESTS', 'BAYED', 'RASPS', 'TAMES', 'CEDED', 'NOVAS', 'SPEWS', 'LARCH', 'HUFFS', 'DOLES', 'MAMAS', 'HULKS', 'BRIMS', 'IRKED', 'ASPIC', 'SWIPE', 'SLAKE', 'PENIS', 'BRAYS', 'PUPAS', 'PHLOX', 'PEONY', 'DOUSE', 'BLURS', 'DARNS', 'LEFTS', 'CHATS', 'VIALS', 'RINKS', 'WOOFS', 'WOWED', 'BONGS', 'SHYER', 'FLIED', 'SLOPS', 'DOLTS', 'DELLS', 'WHELK', 'FETED', 'COCOS', 'HIVES', 'JIBED', 'MAZES', 'TRIOS', 'SIRUP', 'SQUAB', 'LATHS', 'LEERS', 'RIFTS', 'LOPES', 'ALIAS', 'WHIRS', 'DICED', 'SLAGS', 'LODES', 'FOXED', 'IDLED', 'PROWS', 'MALTS', 'TOYED', 'CHEFS', 'KEELS', 'STIES', 'SUCKS', 'SULKS', 'MICAS', 'CZARS', 'AILED', 'ABLER', 'GOLDS', 'VISAS', 'PALLS', 'MOPES', 'BONED', 'RAVED', 'SWAPS', 'JUNKY', 'DOILY', 'PAWNS', 'POACH', 'BAITS', 'DAMNS', 'HUNKS', 'HERES', 'HONKS', 'STOWS', 'UNBAR', 'IDLES', 'ROUTS', 'SAGES', 'GOADS', 'COPES', 'CULLS', 'GIRDS', 'HAVES', 'LUCKS', 'DODOS', 'SHAMS', 'SNUBS', 'ICONS', 'DOOMS', 'HELLS', 'SOLED', 'COMAS', 'PAVES', 'MATHS', 'PERKS', 'LIMPS', 'WOMBS', 'DAUBS', 'COKES', 'SOURS', 'STUNS', 'CASED', 'MUSTS', 'COEDS', 'COWED', 'ZONED', 'RUMMY', 'FETES', 'QUAFF', 'DEANS', 'REAPS', 'GALAS', 'TILLS', 'ROVED', 'KUDOS', 'TONED', 'PARED', 'SCULL', 'VEXES', 'PUNTS', 'BAILS', 'DAMES', 'HAZES', 'LORES', 'MARTS', 'VOIDS', 'AMEBA', 'RAKES', 'ADZES', 'HARMS', 'REARS', 'HEXES', 'COLIC', 'LEEKS', 'HURLS', 'YOWLS', 'IVIES', 'PLOPS', 'MUSKS', 'PAPAW', 'JELLS', 'CRUET', 'BIDED', 'FILCH', 'ZESTS', 'ROOKS', 'LAXLY', 'RENDS', 'LOAMS', 'BASKS', 'SIRES', 'CARPS', 'POKEY', 'FLITS', 'MUSES', 'BAWLS', 'VILER', 'LISPS', 'PEEPS', 'SORER', 'LOLLS', 'DIKED', 'FLOGS', 'SCUMS', 'DOPES', 'BOGIE', 'LEAFS', 'TUBAS', 'SCADS', 'LOWED', 'YESES', 'BIKED', 'EVENS', 'CANED', 'GAWKS', 'WHITS', 'GLUTS', 'ROMPS', 'BESTS', 'TUNAS', 'BONER', 'MALLS', 'PARCH', 'AVERS', 'CRAMS', 'PARES', 'KALES', 'FLAYS', 'GUSHY', 'HUGER', 'SLYER', 'GOLFS', 'MIRES', 'FLUES', 'LOAFS', 'ARCED', 'ACNES', 'NEONS', 'FIEFS', 'DINTS', 'DAZES', 'POUTS', 'CORED', 'YULES', 'LILTS', 'BEEFS', 'MUTTS', 'FELLS', 'COWLS', 'SPUDS', 'LAMES', 'JAWED', 'DUPES', 'DEADS', 'NOONS', 'NIFTY', 'VIREO', 'GAPES', 'METES', 'CUTER', 'MAIMS', 'CUPID', 'MAULS', 'SEDGE', 'PAPAS', 'WHEYS', 'LOOTS', 'HILTS', 'MEOWS', 'BEAUS', 'DICES', 'PEPPY', 'FOGEY', 'GISTS', 'YOGAS', 'GILTS', 'SKEWS', 'CEDES', 'ZEALS', 'ALUMS', 'OKAYS', 'GRUMP', 'WAFTS', 'SOOTS', 'HEFTS', 'MULLS', 'HOSED', 'DOFFS', 'WAIFS', 'OUSTS', 'PUCKS', 'BIERS', 'SUETS', 'HOBOS', 'LINTS', 'BRANS', 'TEALS', 'GARBS', 'PEWEE', 'HELMS', 'TURFS', 'QUIPS', 'WENDS', 'BANES', 'NAPES', 'ICIER', 'SWATS', 'HEXED', 'OGRES', 'GILDS', 'PYRES', 'LARDS', 'BIDES', 'PAGED', 'VEALS', 'PUTTS', 'DIRKS', 'DOTES', 'TIPPY', 'PITHS', 'ACING', 'BARER', 'WHETS', 'GAITS', 'WOOLS', 'DUNKS', 'HEROS', 'SWABS', 'DIRTS', 'JUTES', 'HEMPS', 'SURFS', 'OKAPI', 'CHOWS', 'SHOOS', 'DUSKS', 'FURLS', 'CILIA', 'SEARS', 'NOVAE', 'MURKS', 'WARPS', 'SLUES', 'LAMER', 'SARIS', 'WEANS', 'PURRS', 'DILLS', 'TOGAS', 'NEWTS', 'MEANY', 'BUNTS', 'RAZES', 'GOONS', 'WICKS', 'RUSES', 'VENDS', 'GEODE', 'JUDOS', 'LOFTS', 'PULPS', 'LAUDS', 'MUCKS', 'VISES', 'OILED', 'ETHYL', 'GOTTA', 'BUMPY', 'RADIX', 'CUBIT', 'VERSA', 'ADIEU', 'ANNUM', 'NORMS', 'YOLKS', 'TERNS', 'MIXER', 'COMBO', 'KINDA', 'EPHOD', 'VELDT', 'BONNY', 'BREAM', 'ROSIN', 'BOLLS', 'DOERS', 'DOWNS', 'MOULD', 'KERNS', 'ALOHA', 'BLEST', 'BERYL', 'WANNA', 'BRIER', 'TUNER', 'CANST', 'LEMME', 'TENON', 'DEEPS', 'PADRE', 'PACER', 'TRANS', 'LOLLY', 'QUIPU', 'CODEX', 'MANNA', 'FERNY', 'DUPLE', 'BORON', 'ALACK', 'WHIST', 'CULTS', 'SPAKE', 'LOESS', 'DUNNO', 'AVANT', 'WAXER', 'CALYX', 'COONS', 'SEINE', 'LEMMA', 'TRAMS', 'WHIRR', 'SAITH', 'TUMMY', 'FARAD', 'SAVER', 'JINGO', 'BOWER', 'FACTO', 'INSET', 'BOGUS', 'CAVED', 'TOVES', 'YELLA', 'SCRIP', 'ALEPH', 'TINNY', 'WANTA', 'JOWLS', 'GONGS', 'GARDE', 'BORIC', 'TWILL', 'HENRY', 'SABRE', 'SONNY', 'QUIRT', 'MEBBE', 'XENON', 'HULLO', 'NEGRO', 'HADST', 'ALOES', 'LOUIS', 'QUINT', 'CLUNK', 'RAPED', 'HERTZ', 'XYLEM', 'APACE', 'CAWED', 'PETER', 'WENCH', 'COHOS', 'SORTA', 'GAMBA', 'BYTES', 'ALECK', 'CLOMP', 'GORED', 'SIREE', 'BANDY', 'GUNNY', 'RUNIC', 'WHIZZ', 'FATED', 'WIPER', 'BARDS', 'HOCKS', 'OCHRE', 'YUMMY', 'GENTS', 'SOUPY', 'ROPER', 'EDGER', 'SPATE', 'GIMME', 'EBBED', 'BREVE', 'DEEMS', 'DYKES', 'SERVO', 'TELLY', 'TARES', 'BLOCS', 'VITAE', 'DINKY', 'BRONC', 'TABOR', 'TEENY', 'COMER', 'BORER', 'SIRED', 'DEARY', 'GYROS', 'SPRIT', 'CONGA', 'QUIRE', 'THUGS', 'RUNES', 'CADRE', 'EGGED', 'ANION', 'NODES', 'JELLO', 'ECHOS', 'FAGOT', 'LETUP', 'EYRIE', 'FOUNT', 'CAPED', 'AXONS', 'AMUCK', 'RILED', 'PETIT', 'UMBER', 'MILER', 'FIBRE', 'AGAVE', 'BATED', 'VITRO', 'FEINT', 'MATER', 'UMPED', 'STREP', 'PYLON', 'CARET', 'TEMPS', 'NEWEL', 'YAWNS', 'TREED', 'COUPS', 'RANGY', 'BRADS', 'LONER', 'MOMMY', 'TITER', 'CARNE', 'KOOKY', 'MOTES', 'SAMBA', 'NEWSY', 'ANISE', 'IMAMS', 'AWAYS', 'LIVEN', 'HALLO', 'WALES', 'OPTED', 'CANTO', 'BODES', 'HIKER', 'CHIVE', 'YOKEL', 'DOTTY', 'CUSPS', 'SPECS', 'QUADS', 'LAITY', 'TONER', 'WRITS', 'AUGHT', 'LOGOS', 'NATTY', 'DUCAL', 'BIDET', 'BULGY', 'METRE', 'LUSTS', 'UNARY', 'GOETH', 'SITED', 'SHIES', 'HASPS', 'BRUNG', 'HOLED', 'SWANK', 'LOOKY', 'HUFFY', 'PIMPS', 'LIBRA', 'SEDER', 'HONED', 'ANNAS', 'COYPU', 'SHIMS', 'ZOWIE', 'JIHAD', 'BASSO', 'MONIC', 'MANED', 'MOUSY', 'LAVER', 'PRIMA', 'PICAS', 'REALS', 'TROTH', 'BALKY', 'CHINK', 'ABETS', 'ABACI', 'MORAY', 'LEVIS', 'MOTET', 'NUKES', 'GRADS', 'BLUED', 'WHOMP', 'SWARD', 'SKEET', 'CHINE', 'AERIE', 'BOWIE', 'TUBBY', 'EMIRS', 'COATI', 'SLOBS', 'TRIKE', 'DUCAT', 'DEWEY', 'SKOAL', 'WADIS', 'OOMPH', 'GETUP', 'RUNTY', 'FLYBY', 'BRAZE', 'LOUTS', 'PEATY', 'ORLON', 'HUMPY', 'RADON', 'BEAUT', 'NAPPY', 'VIZOR', 'YIPES', 'DIVOT', 'KIWIS', 'VETCH', 'SITAR', 'KIDDO', 'DYERS', 'COTTA', 'MATZO', 'ZEBUS', 'DACHA', 'DICTA', 'FAKIR', 'KNURL', 'RUNNY', 'UNPIN', 'JULEP', 'GLOBS', 'NUDES', 'KAPUT', 'HULAS', 'CROFT', 'ACHOO', 'GENII', 'NODAL', 'VIOLS', 'FUDGY', 'HANKY', 'LAPIS', 'COOTS', 'MELBA', 'FRIZZ', 'DREAR', 'KOOKS', 'HOAGY', 'ARIAS', 'PAEAN', 'LACEY', 'BANNS', 'SWAIN', 'FRYER', 'GIGAS', 'OGLED', 'RUMEN', 'BEGOT', 'CRUSE', 'ABUTS', 'RIVEN', 'BALKS', 'SINES', 'GORES', 'SATED', 'ODIUM', 'DINGS', 'MOIRE', 'HENNA', 'KRAUT', 'DICKS', 'LIFER', 'PRIGS', 'BEBOP', 'GAGES', 'GIBES', 'AURAL', 'TEMPI', 'HOOCH', 'RAPES', 'HARTS', 'TECHS', 'EMEND', 'SCARP', 'TUFTY', 'TOMES', 'CAROB', 'PRAMS', 'HUBBA', 'JOULE', 'BAIZE', 'BLIPS', 'SCRIM', 'CUBBY', 'CLAVE', 'WINOS', 'LIENS', 'FICHU', 'CHOMP', 'HOMOS', 'PURTY', 'MASER', 'WOOSH', 'SHILL', 'RUSKS', 'AVAST', 'BODED', 'AHHHH', 'LOBED', 'NATCH', 'SHISH', 'TANSY', 'SNOOT', 'ALTHO', 'LAXER', 'HUBBY', 'AEGIS', 'RILES', 'SEPTA', 'PEAKY', 'HEERD', 'SEAMY', 'APSES', 'CHARY', 'PHYLA', 'CLIME', 'BABEL', 'SUMPS', 'SKIDS', 'KHANS', 'INURE', 'NONCE', 'OUTEN', 'FAIRE', 'HOOEY', 'ANOLE', 'KAZOO', 'CALVE', 'ARGOT', 'DUCKY', 'FAKER', 'VIBES', 'NERVY', 'BITER', 'FICHE', 'BOORS', 'SAXES', 'SYNCH', 'FACIE', 'OUIJA', 'HEWER', 'LEGIT', 'GURUS', 'CARON', 'TYPOS', 'POLLY', 'SURDS', 'HAMZA', 'NULLS', 'PATES', 'BLABS', 'SPLAY', 'TALUS', 'PORNO', 'MOOLA', 'NIXED', 'KILOS', 'HORSY', 'GESSO', 'JAGGY', 'NIXES', 'CREEL', 'PATER', 'IOTAS', 'CADGE', 'SKYED', 'HOKUM', 'FURZE', 'ANKHS', 'CURIE', 'NUTSY', 'HILUM', 'REMIX', 'BURLS', 'JIMMY', 'VEINY', 'CODON', 'BEFOG', 'GAMED', 'AXMAN', 'DOOZY', 'LUBES', 'RHEAS', 'BOZOS', 'BUTYL', 'KELLY', 'MYNAH', 'JOCKS', 'WURST', 'QUALS', 'HAYED', 'BOMBE', 'CUSHY', 'SPACY', 'PUKED', 'THEWS', 'PRINK', 'AMENS', 'TESLA', 'FIVER', 'FRUMP', 'CAPOS', 'CODER', 'NAMER', 'JOWLY', 'PUKES', 'HALED', 'DUFFS', 'BRUIN', 'WHANG', 'TOONS', 'FRATS', 'SILTY', 'TELEX', 'CUTUP', 'NISEI', 'NEATO', 'DECAF', 'SOFTY', 'BIMBO', 'ADLIB', 'LOONY', 'SHOED', 'AGUES', 'PEEVE', 'NOWAY', 'GAMEY', 'SARGE', 'RERAN', 'EPACT', 'POTTY', 'CONED', 'UPEND', 'NARCO', 'IKATS', 'WHORL', 'JINKS', 'TIZZY', 'WEEPY', 'MARGE', 'CLOPS', 'NUMBS', 'REEKS', 'RUBES', 'BIPED', 'TIFFS', 'HOCUS', 'HAMMY', 'BUNCO', 'FIXIT', 'TYKES', 'CHAWS', 'YUCKY', 'HOKEY', 'RESEW', 'MAVEN', 'ADMAN', 'SCUZZ', 'SLOGS', 'SOUSE', 'NACHO', 'MIMED', 'MELDS', 'BOFFO', 'PINUP', 'VAGUS', 'GULAG', 'BOSUN', 'EDUCE', 'FAXES', 'AURAS', 'ANTSY', 'BETAS', 'DORKY', 'SNITS', 'MOXIE', 'THANE', 'MYLAR', 'NOBBY', 'GAMIN', 'GOUTY', 'ESSES', 'GOYIM', 'PANED', 'JADES', 'GOFER', 'TZARS', 'HOMED', 'SOCKO', 'DORKS', 'EARED', 'ANTED', 'FAZES', 'OXBOW', 'DOWSE', 'SITUS', 'DRILY', 'MOOCH', 'GATED', 'UNJAM', 'MITRE', 'VENAL', 'KNISH', 'RITZY', 'DIVAS', 'DIMER', 'MESON', 'WINED', 'FENDS', 'PHAGE', 'FIATS', 'PANTY', 'ROANS', 'BILKS', 'HONES', 'ESTOP', 'GELDS', 'AHOLD', 'RAPER', 'PAGER', 'INFIX', 'HICKS', 'TUXES', 'PLEBE', 'TWITS', 'ABASH', 'WACKO', 'PRIMP', 'NABLA', 'GIRTS', 'MIFFS', 'EMOTE', 'XEROX', 'REBID', 'SHAHS', 'RUTTY', 'GRIFT', 'DEIFY', 'KOPEK', 'SEMIS', 'BRIES', 'ACMES', 'PITON', 'TORTS', 'WHORE', 'GIBED', 'VAMPS', 'AMOUR', 'SOPPY', 'GONZO', 'DURST', 'WADER', 'TUTUS', 'PERMS', 'GLITZ', 'BRIGS', 'NERDS', 'BARMY', 'GIZMO', 'OWLET', 'SAYER', 'MOLLS', 'WHOPS', 'COMPS', 'COLAS', 'MATTE', 'DROID', 'PLOYS', 'DEISM', 'MIXUP', 'YIKES', 'PROSY', 'RAKER', 'FLUBS', 'WHISH', 'REIFY', 'CRAPS', 'SHAGS', 'HAZED', 'RECTO', 'REFIX', 'DRAMS', 'BIKER', 'AQUAS', 'PORKY', 'DOYEN', 'EXUDE', 'GOOFS', 'DIVVY', 'NOELS', 'JIVED', 'HULKY', 'CAGER', 'OLDIE', 'VIVAS', 'ADMIX', 'CODAS', 'ZILCH', 'DEIST', 'ORCAS', 'PILAF', 'RANTS', 'ZINGY', 'CHIFF', 'VEEPS', 'NEXUS', 'DEMOS', 'BIBBS', 'ANTES', 'LULUS', 'GNARL', 'ZIPPY', 'IVIED', 'EPEES', 'WIMPS', 'TROMP', 'YOYOS', 'POUFS', 'HALES', 'ROUST', 'RAWER', 'PAMPA', 'MOSEY', 'KEFIR', 'BURGS', 'CUSPY', 'BOOBS', 'BOONS', 'HYPES', 'DYNES', 'NARDS', 'LANAI', 'YOGIS', 'SEPAL', 'TOKED', 'PRATE', 'AYINS', 'HAWED', 'SWIGS', 'VITAS', 'TOKER', 'DOPER', 'BOSSA', 'LINTY', 'MONDO', 'KAYOS', 'TWERP', 'CAPON', 'REWED', 'FUNGO', 'FROSH', 'KABOB', 'PINKO', 'REDID', 'MIMEO', 'TARPS', 'LAMAS', 'SUTRA', 'DINAR', 'WHAMS', 'BUSTY', 'SPAYS', 'NABOB', 'PREPS', 'ODOUR', 'CONKS', 'SLUFF', 'DADOS', 'HOURI', 'SWART', 'BALMS', 'GUTSY', 'FAXED', 'EGADS', 'AGORA', 'DRUBS', 'DAFFY', 'CHITS', 'MUFTI', 'LOTTO', 'TOFFS', 'BURPS', 'ZINGS', 'CLADS', 'DOGGY', 'DUPER', 'SCAMS', 'OGLER', 'MIMES', 'THROE', 'ZETAS', 'WALED', 'PROMO', 'BLATS', 'MUFFS', 'OINKS', 'VIAND', 'COSET', 'FINKS', 'FADDY', 'MINIS', 'SNAFU', 'USURY', 'MUXES', 'CRAWS', 'STATS', 'COXES', 'DORMS', 'DIPPY', 'EXECS', 'ENVOI', 'UMPTY', 'GISMO', 'FAZED', 'STROP', 'JIVES', 'SLIMS', 'BATIK', 'PINGS', 'SONLY', 'LEGGO', 'PEKOE', 'LUAUS', 'CAMPY', 'OODLE', 'PREXY', 'PROMS', 'TOUTS', 'OGLES', 'TOADY', 'NAIAD', 'HIDER', 'NUKED', 'FATSO', 'SLUTS', 'OBITS', 'NARCS', 'TYROS', 'DELIS', 'HYPED', 'POSET', 'BYWAY', 'TEXAS', 'SCROD', 'AVOWS', 'FUTON', 'TORTE', 'TUPLE', 'CAROM', 'TAMPS', 'JILTS', 'DUALS', 'REPRO', 'TOPED', 'PSYCH', 'SICKO', 'KLUTZ', 'TARNS', 'COXED', 'DRAYS', 'CLOYS', 'ANDED', 'PIKER', 'AIMER', 'SURAS', 'LIMOS', 'HAPAX', 'KLIEG', 'STAPH', 'LAYUP', 'TOKES', 'AXING', 'TOPER', 'COWRY', 'PROFS', 'BLAHS', 'ADDLE', 'SUDSY', 'COIFS', 'SUETY', 'GABBY', 'HAFTA', 'PITAS', 'GOUDA', 'DEICE', 'TAUPE', 'TOPES', 'NITRO', 'CARNY', 'LIMEY', 'ORALS', 'HIRER', 'TAXER', 'ROILS', 'RUBLE', 'DOLOR', 'WRYER', 'SNOTS', 'QUAIS', 'COKED', 'GIMEL', 'GORSE', 'MINAS', 'GOEST', 'MANTA', 'JINGS', 'ADMEN', 'OFFEN', 'CILLS', 'LOTTA', 'BOLAS', 'THWAP', 'ALWAY', 'BOGGY', 'DONNA', 'LOCOS', 'BELAY', 'GLUEY', 'BITSY', 'MIMSY', 'HILAR', 'OUTTA', 'VROOM', 'RATHS', 'DYADS', 'CROCS', 'VIRES', 'CULPA', 'KIVAS', 'FEIST', 'TEATS', 'THATS', 'YAWLS', 'WHENS', 'ABACA', 'OHHHH', 'APHIS', 'FUSTY', 'PERDU', 'MAYST', 'EXEAT', 'MOLLY', 'SUPRA', 'WETLY', 'PLASM', 'BUFFA', 'PUKKA', 'TAGUA', 'PARAS', 'STOAT', 'SECCO', 'CARTE', 'MOLAL', 'SHADS', 'FORMA', 'PIONS', 'MODUS', 'BUENO', 'RHEUM', 'SCURF', 'EPHAH', 'DOEST', 'SPRUE', 'FLAMS', 'MOLTO', 'DIETH', 'CHOOS', 'MIKED', 'BRONX', 'GOOPY', 'BALLY', 'PLUMY', 'MOONY', 'MORTS', 'YOURN', 'BIPOD', 'SPUME', 'ALGAL', 'AMBIT', 'MUCHO', 'SPUED', 'DOZER', 'HARUM', 'GROAT', 'SKINT', 'LAUDE', 'PAPPY', 'ONCET', 'RIMED', 'GIGUE', 'LIMED', 'PLEIN', 'REDLY', 'HUMPF', 'LITES', 'SEEST', 'GREBE', 'ABSIT', 'THANX', 'PSHAW', 'YAWPS', 'PLATS', 'PAYED', 'AREAL', 'TILTH', 'YOUSE', 'GWINE', 'THEES', 'WATSA', 'LENTO', 'SPITZ', 'YAWED', 'SPRAT', 'CORNU', 'AMAHS', 'BLOWY', 'WAHOO', 'LUBRA', 'MECUM', 'WHOOO', 'COQUI', 'SABRA', 'EDEMA', 'MRADS', 'DICOT', 'ASTRO', 'KITED', 'OUZEL', 'DIDOS', 'GRATA', 'BONNE', 'AXMEN', 'KLUNK', 'SUMMA', 'LAVES', 'PURLS', 'YAWNY', 'LARGO', 'BAZAR', 'PSSST', 'SYLPH', 'LULAB', 'TOQUE', 'FUGIT', 'ORTHO', 'LUCRE', 'COOCH', 'WHIPT', 'FOLKY', 'TYRES', 'WHEEE', 'CORKY', 'INJUN', 'SOLON', 'DIDOT', 'KERFS', 'RAYED', 'WASSA', 'CHILE', 'NIPPY', 'LITRE', 'MAGNA', 'REBOX', 'MILCH', 'BRENT', 'GYVES', 'LAZED', 'FEUED', 'MAVIS', 'INAPT', 'BAULK', 'CASUS', 'WISED', 'FOSSA', 'DOWER', 'KYRIE', 'BHOYS', 'SCUSE', 'FEUAR', 'OHMIC', 'JUSTE', 'UKASE', 'BEAUX', 'TUSKY', 'ORATE', 'MUSTA', 'LARDY', 'INTRA', 'QUIFF', 'EPSOM', 'NEATH', 'OCHER', 'TARED', 'HOMME', 'MEZZO', 'CORMS', 'PSOAS', 'BEAKY', 'TERRY', 'INFRA', 'SPIVS', 'TUANS', 'BELLI', 'BERGS', 'ANIMA', 'WEIRS', 'MAHUA', 'SCOPS', 'MANSE', 'TITRE', 'CURIA', 'KEBOB', 'CYCAD', 'TALKY', 'FUCKS', 'TAPIS', 'AMIDE', 'DOLCE', 'SLOES', 'JAKES', 'RUSSE', 'BLASH', 'TUTTI', 'PRUTA', 'PANGA', 'BLEBS', 'TENCH', 'SWARF', 'HEREM', 'MERSE', 'PAWKY', 'LIMEN', 'VIVRE', 'CHERT', 'UNSEE', 'TIROS', 'BRACK', 'FOOTS', 'FOSSE', 'KNOPS', 'ILEUM', 'NOIRE', 'FIRMA', 'PODGY', 'LAIRD', 'THUNK', 'SHUTE', 'ROWAN', 'SHOJI', 'UNCAP', 'FAMES', 'GLEES', 'COSTA', 'TURPS', 'FORES', 'SOLUM', 'IMAGO', 'BYRES', 'FONDU', 'CONEY', 'POLIS', 'DICTU', 'KRAAL', 'SHERD', 'MUMBO', 'WROTH', 'CHARS', 'UNBOX', 'VACUO', 'SLUED', 'WEEST', 'HADES', 'WILED', 'SYNCS', 'MUSER', 'EXCON', 'HOARS', 'SIBYL', 'PASSE', 'JOEYS', 'LOTSA', 'LEPTA', 'SHAYS', 'BOCKS', 'ENDUE', 'DARER', 'NONES', 'ILEUS', 'PLASH', 'BUSBY', 'WHEAL', 'BUFFO', 'YOBBO', 'BILES', 'POXES', 'ROOTY', 'LICIT', 'TERCE', 'BROMO', 'HAYEY', 'DWEEB', 'IMBED', 'SARAN', 'BRUIT', 'PUNKY', 'SOFTS', 'BIFFS', 'LOPPY', 'AGARS', 'AQUAE', 'LIVRE', 'BUNDS', 'SHEWS', 'DIEMS', 'GINNY', 'DEGUM', 'POLOS', 'DESEX', 'UNMAN', 'DUNGY', 'VITAM', 'WEDGY', 'GLEBE', 'APERS', 'RIDGY', 'ROIDS', 'WIFEY', 'VAPES', 'WHOAS', 'BUNKO', 'YOLKY', 'ULNAS', 'REEKY', 'BODGE', 'BRANT', 'DAVIT', 'DEQUE', 'LIKER', 'JENNY', 'TACTS', 'FULLS', 'TREAP', 'LIGNE', 'ACKED', 'REFRY', 'VOWER', 'AARGH', 'CHURL', 'MOMMA', 'GAOLS', 'WHUMP', 'ARRAS', 'MARLS', 'TILER', 'GROGS', 'MEMES', 'MIDIS', 'TIDED', 'HALER', 'DUCES', 'TWINY', 'POSTE', 'UNRIG', 'PRISE', 'DRABS', 'QUIDS', 'FACER', 'SPIER', 'BARIC', 'GEOID', 'REMAP', 'TRIER', 'GUNKS', 'STENO', 'STOMA', 'AIRER', 'TORAH', 'APIAN', 'SMUTS', 'POCKS', 'YURTS', 'EXURB', 'DEFOG', 'NUDER', 'BOSKY', 'NIMBI', 'MOTHY', 'JOYED', 'LABIA', 'PARDS', 'JAMMY', 'BIGLY', 'FAXER', 'HOPPY', 'NURBS', 'COTES', 'DISHY', 'VISED', 'CELEB', 'PISMO', 'CASAS', 'WITHS', 'SCUDI', 'MUNGS', 'MUONS', 'UREAS', 'IOCTL', 'UNHIP', 'KRONE', 'SAGER', 'VERST', 'EXPAT', 'GRONK', 'UVULA', 'SHAWM', 'BILGY', 'BRAES', 'CENTO', 'WEBBY', 'LIPPY', 'GAMIC', 'LORDY', 'MAZED', 'TINGS', 'SHOAT', 'FAERY', 'WIRER', 'DIAZO', 'CARER', 'RATER', 'GREPS', 'RENTE', 'ZLOTY', 'VIERS', 'UNAPT', 'POOPS', 'KEPIS', 'TAXON', 'EYERS', 'WONTS', 'SPINA', 'STOAE', 'YENTA', 'POOEY', 'BURET', 'JAPAN', 'BEDEW', 'HAFTS', 'SELFS', 'OARED', 'HERBY', 'PRYER', 'OAKUM', 'DINKS', 'TITTY', 'SEPOY', 'PENES', 'FUSEE', 'WINEY', 'GIMPS', 'NIHIL', 'RILLE', 'GIBER', 'OUSEL', 'UMIAK', 'CUPPY', 'HAMES', 'SHITS', 'AZINE', 'GLADS', 'TACET', 'BUMPH', 'COYER', 'HONKY', 'GOOKY', 'WASPY', 'SEDGY', 'BENTS', 'VARIA', 'DJINN', 'JUNCO', 'WILCO', 'LAZES', 'IDYLS', 'RIVES', 'SNOOD', 'SCHMO', 'SPAZZ', 'FINIS', 'NOTER', 'PAVAN', 'ORBED', 'BATES', 'PIPET', 'BADDY', 'GOERS', 'SHAKO', 'STETS', 'SEBUM', 'SEETH', 'LOBAR', 'RAVER', 'AJUGA', 'RICED', 'VELDS', 'DRIBS', 'VILLE', 'DHOWS', 'UNSEW', 'HALMA', 'KRONA', 'LIMBY', 'JIFFS', 'TREYS', 'BAUDS', 'PFFFT', 'MIMER', 'PLEBS', 'CANER', 'JIBER', 'CUPPA', 'WASHY', 'CHUFF', 'UNARM', 'YUKKY', 'STYES', 'WAKER', 'FLAKS', 'MACES', 'RIMES', 'GIMPY', 'GUANO', 'LIRAS', 'KAPOK', 'SCUDS', 'BWANA', 'ORING', 'PRIER', 'KLUGY', 'MONTE', 'VELAR', 'FIRER', 'PIETA', 'UMBEL', 'CAMPO', 'UNPEG', 'FOVEA', 'ABEAM', 'BOSON', 'ASKER', 'GOTHS', 'VOCAB', 'VINED', 'TROWS', 'TIKIS', 'LOPER', 'INDIE', 'BOFFS', 'SPANG', 'GRAPY', 'TATER', 'ICHOR', 'KILTY', 'LOCHS', 'SUPES', 'DEGAS', 'FLICS', 'TORSI', 'BETHS', 'WEBER', 'RESAW', 'LAWNY', 'MUJIK', 'RELET', 'THERM', 'HEIGH', 'SHNOR', 'TRUED', 'ZAYIN', 'LIEST', 'BARFS', 'BASSI', 'QOPHS', 'ROILY', 'FLABS', 'PUNNY', 'OKRAS', 'HANKS', 'DIPSO', 'NERFS', 'FAUNS', 'CALLA', 'PSEUD', 'LURER', 'MAGUS', 'OBEAH', 'ATRIA', 'TWINK', 'PALMY', 'POCKY', 'PENDS', 'RECTA', 'PLONK', 'SLAWS', 'KEENS', 'NICAD', 'PONES', 'INKER', 'WHEWS', 'GROKS', 'MOSTS', 'TREWS', 'ULNAR', 'GYPPY', 'COCAS', 'EXPOS', 'ERUCT', 'OILER', 'VACUA', 'DRECK', 'DATER', 'ARUMS', 'VOXEL', 'DIXIT', 'BEERY', 'ASSAI', 'LADES', 'ACTIN', 'GHOTI', 'BUZZY', 'MEADS', 'GRODY', 'RIBBY', 'CLEWS', 'PYXIE', 'KULAK', 'BOCCI', 'RIVED', 'DUDDY', 'HOPER', 'LAPIN', 'WONKS', 'PETRI', 'PHIAL', 'FUGAL', 'HOLON', 'BOOMY', 'DUOMO', 'MUSOS', 'SHIER', 'HAYER', 'PORGY', 'HIVED', 'LITHO', 'FISTY', 'STAGY', 'LUVYA', 'MARIA', 'SMOGS', 'ASANA', 'YOGIC', 'SLOMO', 'FAWNY', 'AMINE', 'WEFTS', 'TWIRP', 'BRAVA', 'PLYER', 'FERMI', 'LOGES', 'NITER', 'REVET', 'UNATE', 'GYVED', 'TOTTY', 'ZAPPY', 'HONER', 'GIROS', 'DICER', 'CALKS', 'LUXES', 'MONAD', 'CRUFT', 'QUOIN', 'FUMER', 'AMPED', 'SHLEP', 'VINCA', 'YAHOO', 'VULVA', 'ZOOEY', 'DRYAD', 'NIXIE', 'MOPER', 'IAMBS', 'LUNES', 'NUDIE', 'LIMNS', 'WEALS', 'NOHOW', 'MIAOW', 'GOUTS', 'MYNAS', 'MAZER', 'KIKES', 'OXEYE', 'STOUP', 'JUJUS', 'PUBES', 'TAELS', 'DEFUN', 'RANDS', 'BLEAR', 'PAVER', 'GOOSY', 'SPROG', 'OLEOS', 'TOFFY', 'PAWER', 'MACED', 'CRITS', 'KLUGE', 'TUBED', 'SAHIB', 'GANEF', 'SCATS', 'SPUTA', 'VANED', 'ACNED', 'TAXOL', 'PLINK', 'OWETH', 'TRIBS', 'RESAY', 'THOUS', 'HAPLY', 'GLANS', 'MAXIS', 'ANTIS', 'PORKS', 'QUOIT', 'ALKYD', 'GLARY', 'BEAMY', 'HEXAD', 'BONKS', 'TECUM', 'KERBS', 'FILAR', 'FRIER', 'REDUX', 'ABUZZ', 'FADER', 'SHOER', 'COUTH', 'TRUES', 'GUYED', 'GOONY', 'BOOKY', 'FUZES', 'HURLY', 'GENET', 'HODAD', 'CALIX', 'PAWLS', 'IODIC', 'UTERO', 'HENGE', 'UNSAY', 'LIERS', 'PIING', 'WEALD', 'SEXED', 'FOLIC', 'POXED', 'CUNTS', 'ANILE', 'KITHS', 'BECKS', 'PLENA', 'TOYER', 'ATTAR', 'TEAKS', 'AIOLI', 'AWING', 'ANENT', 'FECES', 'REDIP', 'WISTS', 'PRATS', 'MESNE', 'MUTER', 'SMURF', 'OWEST', 'BAHTS', 'LOSSY', 'FTPED', 'HOERS', 'SLIER', 'SICKS', 'FATLY', 'DELFT', 'HIVER', 'HIMBO', 'PENGO', 'BUSKS', 'LOXES', 'ZONKS', 'ILIUM', 'APORT', 'IKONS', 'MULCT', 'REEVE', 'CIVVY', 'CANNA', 'BARFY', 'KAIAK', 'SCUDO', 'KNOUT', 'GAPER', 'BHANG', 'PEASE', 'UTERI', 'LASES', 'PATEN', 'RASAE', 'AXELS', 'STOAS', 'STYLI', 'GUNKY', 'HAZER', 'KENAF', 'AHOYS', 'AMMOS', 'WEENY', 'URGER', 'KUDZU', 'PAREN', 'BOLOS', 'FETOR', 'NITTY', 'TECHY', 'LIETH', 'SOMAS', 'DARKY', 'VILLI', 'GLUON', 'JANES', 'CANTS', 'FARTS', 'SOCLE', 'JINNS', 'RUING', 'SLILY', 'RICER', 'HADDA', 'WOWEE', 'RICES', 'NERTS', 'CAULS', 'SWIVE', 'LILTY', 'MICKS', 'ARITY', 'PASHA', 'FINIF', 'OINKY', 'GUTTY', 'TETRA', 'WISES', 'WOLDS', 'BALDS', 'PICOT', 'WHATS', 'SHIKI', 'BUNGS', 'SNARF', 'LEGOS', 'DUNGS', 'STOGY', 'BERMS', 'TANGS', 'VAILS', 'ROODS', 'MOREL', 'SWARE', 'ELANS', 'LATUS', 'GULES', 'RAZER', 'DOXIE', 'BUENA', 'OVERS', 'GUTTA', 'ZINCS', 'NATES', 'KIRKS', 'TIKES', 'DONEE', 'JERRY', 'MOHEL', 'CEDER', 'DOGES', 'UNMAP', 'FOLIA', 'RAWLY', 'SNARK', 'TOPOI', 'CEILS', 'IMMIX', 'YORES', 'DIEST', 'BUBBA', 'POMPS', 'FORKY', 'TURDY', 'LAWZY', 'POOHS', 'WORTS', 'GLOMS', 'BEANO', 'MULEY', 'BARKY', 'TUNNY', 'AURIC', 'FUNKS', 'GAFFS', 'CORDY', 'CURDY', 'LISLE', 'TORIC', 'SOYAS', 'REMAN', 'MUNGY', 'CARPY', 'APISH', 'OATEN', 'GAPPY', 'AURAE', 'BRACT', 'ROOKY', 'AXLED', 'BURRY', 'SIZER', 'PROEM', 'TURFY', 'IMPRO', 'MASHY', 'MIENS', 'NONNY', 'OLIOS', 'GROOK', 'SATES', 'AGLEY', 'CORGI', 'DASHY', 'DOSER', 'DILDO', 'APSOS', 'XORED', 'LAKER', 'PLAYA', 'SELAH', 'MALTY', 'DULSE', 'FRIGS', 'DEMIT', 'WHOSO', 'RIALS', 'SAWER', 'SPICS', 'BEDIM', 'SNUGS', 'FANIN', 'AZOIC', 'ICERS', 'SUERS', 'WIZEN', 'KOINE', 'TOPOS', 'SHIRR', 'RIFER', 'LADED', 'LASED', 'TURDS', 'SWEDE', 'EASTS', 'COZEN', 'UNHIT', 'PALLY', 'AITCH', 'SEDUM', 'COPER', 'RUCHE', 'GEEKS', 'SWAGS', 'ETEXT', 'ALGIN', 'OFFED', 'HOLER', 'DOTER', 'TOTER', 'BESOT', 'DICUT', 'MACER', 'PEENS', 'PEWIT', 'REDOX', 'POLER', 'YECCH', 'FLUKY', 'DOETH', 'TWATS', 'CRUDS', 'BEBUG', 'BIDER', 'STELE', 'HEXER', 'WESTS', 'GLUER', 'PILAU', 'ABAFT', 'WHELM', 'LACER', 'INODE', 'TABUS', 'GATOR', 'CUING', 'REFLY', 'LUTED', 'CUKES', 'BAIRN', 'BIGHT', 'ARSES', 'LOGGY', 'BLINI', 'SPOOR', 'TOYON', 'HARKS', 'WAZOO', 'FENNY', 'NAVES', 'KEYER', 'TUFAS', 'RAJAS', 'TYPAL', 'SPIFF', 'OXLIP', 'UNBAN', 'MUSSY', 'FINNY', 'RIMER', 'MOLAS', 'CIRRI', 'HUZZA', 'AGONE', 'UNSEX', 'UNWON', 'PEATS', 'TOILE', 'ZOMBI', 'DEWED', 'NOOKY', 'ALKYL', 'IXNAY', 'DOVEY', 'HOLEY', 'CUBER', 'AMYLS', 'PODIA', 'CHINO', 'PRIMS', 'LYCRA', 'JOHNS', 'FATWA', 'EGGER', 'HEMPY', 'SNOOK', 'HYING', 'FUZED', 'BARMS', 'CRINK', 'MOOTS', 'YERBA', 'RHUMB', 'UNARC', 'DIRER', 'MUNGE', 'ELAND', 'NARES', 'WRIER', 'NODDY', 'ATILT', 'JUKES', 'ENDER', 'THENS', 'UNFIX', 'DOGGO', 'ZOOKS', 'DIDDY', 'SHMOO', 'BRUSK', 'PREST', 'CURER', 'PASTS', 'KELPY', 'BOCCE', 'KICKY', 'TAROS', 'LINGS', 'DICKY', 'ABEND', 'STELA', 'BIGGY', 'LAVED', 'BALDY', 'PUBIS', 'GOOKS', 'WONKY', 'STIED', 'HYPOS', 'ASSED', 'SPUMY', 'OSIER', 'ROBLE', 'BIFFY', 'PUPAL']

    for word in addWords:
        if word not in list(di.words):
           di = di.append(pd.Series({'words':word}),ignore_index=True)
    
    #filter out words with different british/american english spelling
    with open('input/british-american-words.txt') as fin:
        brit_am=fin.readlines()
    
    brit_am_list = [x.replace("\n","").split(" ") for x in brit_am]
    brit_am_list = [item for sublist in brit_am_list for item in sublist]
    
    perms = di[~di.words.isin(brit_am_list)]    
    
    return(perms)

def next_letters(words):
   allCombos = []
   allCombos+=(list(set([x[0:2] for x in words])))
   allCombos+=(list(set([x[0:3] for x in words])))
   allCombos+=(list(set([x[0:4] for x in words])))
   return(allCombos)
    
def create_all_games(perms, target, start, end):    

    words = perms.words.values
    #random.shuffle(words)    
    
    #get all word stems
    allCombos=next_letters(words)
    allCombos2=[x for x in allCombos if len(x)==2]
    allCombos3=[x for x in allCombos if len(x)==3]
    allCombos4=[x for x in allCombos if len(x)==4]
    allCombos5=words
    
    (r0,r1,r2,r3,r4)=("","","","","")
    magicSquares = []
    counter=0
    print("start.end",start,end)
    for i, r0 in enumerate(words[start:end]):
        print('row0',i, r0)
        foundThisWords=0 
        found=False 
        possibleC0 = [x for x in words if (x[0]==r0[0]) & (x not in [r0])]  #exclude r0/c0 same
        #possibleC0 = [x for x in possibleC0 if x>r0] #only check where c0>r0 as can transpose later        
        for c0 in possibleC0:
            if found:
                break
            #all words starting with column 0
            possibleR1 = [x for x in words if (x[0]==c0[1])]
            #then filter out impossible columns
            possibleR1 = [x for x in possibleR1 if r0[1]+x[1] in allCombos2] 
            possibleR1 = [x for x in possibleR1 if r0[2]+x[2] in allCombos2] 
            possibleR1 = [x for x in possibleR1 if r0[3]+x[3] in allCombos2] 
            possibleR1 = [x for x in possibleR1 if r0[4]+x[4] in allCombos2] 

            for r1 in possibleR1:
                if found:
                    break
                #all words starting with column 0
                possibleR2 = [x for x in words if (x[0]==c0[2])] 
                #then filter out impossible columns
                possibleR2 = [x for x in possibleR2 if r0[1]+r1[1]+x[1] in allCombos3] 
                possibleR2 = [x for x in possibleR2 if r0[2]+r1[2]+x[2] in allCombos3] 
                possibleR2 = [x for x in possibleR2 if r0[3]+r1[3]+x[3] in allCombos3] 
                possibleR2 = [x for x in possibleR2 if r0[4]+r1[4]+x[4] in allCombos3] 
        
                for r2 in possibleR2:
                    if found:
                        break
                    #all words starting with column 0
                    possibleR3 = [x for x in words if (x[0]==c0[3])] 
                    #then filter out impossible columns
                    possibleR3 = [x for x in possibleR3 if r0[1]+r1[1]+r2[1]+x[1] in allCombos4] 
                    possibleR3 = [x for x in possibleR3 if r0[2]+r1[2]+r2[2]+x[2] in allCombos4] 
                    possibleR3 = [x for x in possibleR3 if r0[3]+r1[3]+r2[3]+x[3] in allCombos4] 
                    possibleR3 = [x for x in possibleR3 if r0[4]+r1[4]+r2[4]+x[4] in allCombos4] 
    
                    for r3 in possibleR3:
                        if found:
                            break
                        counter+=1
                        if counter%1000==0:
                            print(counter, r0,r1,r2,r3)
                        #all words starting with column 0
                        possibleR4 = [x for x in words if (x[0]==c0[4])] 
                        #then filter out impossible columns
                        possibleR4 = [x for x in possibleR4 if (r0[1]+r1[1]+r2[1]+r3[1]+x[1] in allCombos5)] 
                        possibleR4 = [x for x in possibleR4 if (r0[2]+r1[2]+r2[2]+r3[2]+x[2] in allCombos5)] 
                        possibleR4 = [x for x in possibleR4 if (r0[3]+r1[3]+r2[3]+r3[3]+x[3] in allCombos5)] 
                        possibleR4 = [x for x in possibleR4 if (r0[4]+r1[4]+r2[4]+r3[4]+x[4] in allCombos5)] 

                        if len(possibleR4)>0:
                            for r4 in possibleR4:
                                magicSquares.append([r0,r1,r2,r3,r4])
                            print(r0)
                            print(r1)
                            print(r2)
                            print(r3)
                            print(r4)
                            print(len(magicSquares))
                            r4=""
                            foundThisWords+=1
                            #max n magic squares per starting column
                            if foundThisWords>=1000: 
                                found=True
        if len(magicSquares)>=target:
            return(magicSquares)

    return(magicSquares)

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
        
def random_swap(grid,n):
    gridQ = [g.copy() for g in grid] 
    
    for i in range(n):
        same=True
        while same==True:
            a = [random.randint(0,3)*2,random.randint(0,3)*2]
            b = [random.randint(0,3)*2,random.randint(0,3)*2]
            same = (a==b or grid[a[0]][a[1]]==grid[b[0]][b[1]])
    
        buffer = gridQ[a[0]][a[1]]
        gridQ[a[0]][a[1]]=gridQ[b[0]][b[1]]
        gridQ[b[0]][b[1]]=buffer

    return gridQ

def user_swap(gridQ,ab):
    (a,b) = ([int(ab[0])*2-2,int(ab[1])*2-2],[int(ab[2])*2-2,int(ab[3])*2-2])
    newGridQ = [g.copy() for g in gridQ] 
    
    buffer = newGridQ[a[0]][a[1]]
    newGridQ[a[0]][a[1]]=newGridQ[b[0]][b[1]]
    newGridQ[b[0]][b[1]]=buffer

    return newGridQ

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
        lineDiff = line

        if right:
            lineDiffShuff = [lineDiff[-1]]+lineDiff[0:-1]
        else:
            lineDiffShuff = lineDiff[1:]+[lineDiff[0]]
            
        lineNew = lineDiffShuff
        
    return lineNew

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

def shuffleMulti(gridQ,grid,instructionList):
    gridNew = [g.copy() for g in gridQ] 
    for instruction in instructionList:
        gridNew = shuffle([g.copy() for g in gridNew],grid,instruction)
    return gridNew

def unShuff(line,lineTrue, right=True):
    
    counter=0
    changed=False
    while changed==False:
        lineSame = [line[x]==lineTrue[x] for x in range(len(line))]
        #line fix = which greens to hold in place (always hold symbols): 1 for yes, 0 for no, -1 for not green
        lineFix = [random.randint(0,1) if lineSame[x] else -1 for x in range(len(line))]
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
    moves=[]
    for i in range(n):
        attempts = 0
        #a valid shuffle mustn't leave grid unchanged and mustn't change a purple tile to green
        
        criteria=False
        while criteria==False:
            gridTemp = [g.copy() for g in gridQ]

            #choose row (0) or column (1)
            choice = random.randint(0,1)
            #row shuffle
            if choice == 0:
                #choose row
                choice2 = random.randint(0,int(len(grid))-1)
                choice3 = random.randint(0,1) #0 right, 1 left
                gridTemp[choice2] = unShuff(gridQ[choice2],grid[choice2],right=(choice3==0))
    
            #col shuffle
            if choice == 1:
                #choose column
                choice2 = random.randint(0,int(len(grid))-1)
                choice3 = random.randint(0,1) #0 right (down), 1 left (up)
                column = [row.copy()[choice2] for row in grid]
                columnQ = [row.copy()[choice2] for row in gridTemp]
                columnQNew = unShuff(columnQ,column,right=(choice3==0))
                for r in range(len(gridQ)):
                    gridTemp[r][choice2]=columnQNew[r] 

            attempts+=1
            if attempts>1000:
                print("GIVE UP") 
                sys.exit()

            if gridTemp != gridQ:
                criteria=True
                #check no purples turned green
                for x in range(len(grid)):
                    for y in range(len(grid[0])):
                        if (grid[x][y]==gridTemp[x][y]) & (grid[x][y]!=gridQ[x][y]):
                            criteria=False
                            print('rejecting green creator', x, y)
                
        gridQ=gridTemp.copy()
        text1 = "R" if choice==0 else "C"
        text2 = "R" if choice3==0 else "L"
        print("Choice:", text1+str(choice2)+text2)
        #print(gridQ)
        moves.append(text1+str(choice2)+text2)
    return(gridQ, moves)

def unShuffleMoves(grid,move):
    gridQ = [g.copy() for g in grid] 
    choice = 0 if move[0][0]=="R" else 1
    choice2 = int(move[0][1])
    choice3 = 0 if move[0][2]=="R" else 1
    #row shuffle
    if choice == 0:
        gridQ[choice2] = unShuff(gridQ[choice2],grid[choice2],right=(choice3==0))
        print("row shuffle", choice2, gridQ[choice2])
    #col shuffle
    if choice == 1:
        #choose column
        column = [row.copy()[choice2] for row in grid]
        columnQ = [row.copy()[choice2] for row in gridQ]
        columnQNew = unShuff(columnQ,column,right=(choice3==0))
        for r in range(len(gridQ)):
            gridQ[r][choice2]=columnQNew[r] 
        print("col shuffle", choice2, columnQNew)

    print(gridQ)

    return(gridQ)

def findSolutionAnyUnder5(grid,gridQ):

    allGoes = []
    for part1 in ['R','C']:
        for part2 in ['0','1','2','3','4']:
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
        for part2 in ['0','1','2','3','4']:
            for part3 in ['R','L']:
                    allGoes.append(part1+part2+part3)

    allGoPerms = list(itertools.product(allGoes, repeat=6))

    minSolved=99
    minSolution=''
    for j, goList in enumerate(allGoPerms):
        if j%50000==0:
            print(j, "trying:",goList) 
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
                        print(minSolved, goList[:i+1])
                        sys.exit()
                        #return(minSolved, goList[:i+1])
    print('finished')

    return(minSolved, minSolution)

#####CORE FILE CREATOR SCRIPTS START HERE

#find all magic squares (answers only, not questions).  Note: 150 found.
x = input("regenerate list of all possible magic squares? (Y or y for yes, anything else for no)") 
if x.lower()=="y":
    perms = permutations(lngth=5)
    print('word list length:', len(perms))
    all_grids = [] 
    for n in range(0,len(perms),10):
        m = min(n+10,len(perms))
        print("magic squares for words:",n,m)
        all_grids_chunk = create_all_games(perms, 9999, n, m)
        all_grids = all_grids+all_grids_chunk
    all_gridsX=[[[*y] for y in x] for x in all_grids] #separate words into lists of letters

    with open('allMagicSqWords.json', 'w') as f:
        json.dump(all_gridsX, f)    
    
    #filter out grids which have repeats or undesired words
    new_all_grids = []
    undesirables = ['REMOV'] #allows removal of words after time consuming preparation of grids
    for i in range(len(all_grids)):
        grid = all_grids[i]
        double=False
        undesirable=False
        mirror=False
        if any(grid) in undesirables:
            undesirable=True
            print("UNDESIRABLE", grid)

        reflection=[]
        for col in range(len(grid[0])):
            column = "".join([r[col] for r in grid])
            reflection.append(column)
            if column in grid:
                double=True
            if column in undesirables:
                undesirable=True
                print("UNDESIRABLE", grid)
        if (not double) & (not undesirable) & (not mirror):
            new_all_grids.append(grid)
                
    print("Was:", len(all_grids), "Now:", len(new_all_grids))
    
    new_all_grids=[[[*y] for y in x] for x in new_all_grids] #separate words into lists of letters
    
    with open('input/allMagicSqWords_dedupesNew.json', 'w') as f:
        json.dump(new_all_grids, f)    

#from list of answers, randomise and repeat to desired length
with open('input/allMagicSqWords_dedupesNew.json', 'r') as f:
    grids=json.load(f)         
   
#loop 3 times to get 3000 puzzles
gridsCum = [] 

repeats = int(np.ceil(questions/len(grids)))
for j in range(repeats):
    #random sort   
    random.shuffle(grids)
    gridsCum += grids
#cut to desired length
gridsCum = gridsCum[0:questions]
    
with open(fileStem+'_A.json', 'w') as f:
    json.dump(gridsCum, f)    
        
#from list of answers of desired length, create a batch of questions  
grids=gridsCum         
    
#shuffle until conditions met
gridQs=[]
gridMoves=[]
nonGreensList=[]
num=6
start=0
for i,grid in enumerate(grids[start:]):
    print(i, "of", len(grids))
    criteria = False
    while criteria == False:
        for loop in range(100):
            gridQ,moves = unShuffle(grid,num)
            
            #check solution works with moves
            gridCheck = shuffleMulti(gridQ,grid,moves[::-1])
            if gridCheck != grid:
                print("mismatch error")
                sys.exit()
        #filter out grids with less than 10 nonGreens
        minimumNonGreens = 12
        maximumNonGreens = 20
        
        nonGreens = []
        for x in range(len(grid)):
            for y in range(len(grid[0])):
                if grid[x][y]!=gridQ[x][y]:
                    nonGreens.append(grid[x][y])
        encode_grid(gridQ,grid) 
        print(len(nonGreens))
        if (len(nonGreens)>=minimumNonGreens) & (len(nonGreens)<=maximumNonGreens):
            print("non greens ok:", len(nonGreens))
            #filter out grids which are solvable in less than 5 moves
            solutionAny = findSolutionAnyUnder5(grid, gridQ)
            print(i,solutionAny)
            if solutionAny[0]==99:
                print("question can only be solved in >5")
                criteria=True
                gridQs.append(gridQ)
                gridMoves.append(moves)
                nonGreensList.append(len(nonGreens))
            else:
                print("rejecting as can be solved in 5")

        if criteria==False:
            print("re-retry shuffle, grid #",i)

    '''
    #save every 50 grids if required    
    if (i%50 == 0) or (i==len(grids)-start-1):
        with open(fileStem+'_Q.json'.replace("_Q","_Q"+str(start)+'_'+str(i)), 'w') as f:
            json.dump(gridQs, f)        
        with open(fileStem+'_Moves.json'.replace("_Moves","_Moves"+str(start)+'_'+str(i)), 'w') as f:
            json.dump(gridMoves, f)        
    '''
            
with open('output/'+fileStem+'_Q.json', 'w') as f:
    json.dump(gridQs, f)        

with open('output/'+fileStem+'_Moves.json', 'w') as f:
    json.dump(gridMoves, f)        

