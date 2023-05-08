# SokoPy - A Sokoban clone made in Python

**Features:**
- Real Graphics!
- Runs on anything with Python!
- Some Settings!
- A "Tutorial"!
- The levels from the 1982 original!
- David W. Skinner's level packs!
- An open level creation format!

---

While it only features base Sokoban blocks currently, the game allows for level creation as long as you are willing to learn it.
I have not yet added a proper level creator yet, however, the convert.py script allows you to convert a text representation of a level into the format.
```
; An example of a valid level:
 #######
 # @...#
 #   ####
###$    #
#   #$# #
# $ #   #
#   #####
#####
```
Some caveats are that the software cannot handle broken boundaries. A level like below is therefor invalid.
```
; An example of a broken boundary:
##  ##
# @$ #
#.  ##
#####
```

Each block in a level is a 4bit nibble, with the exception that any series of blocks larger than three will be compressed down

|[]()||||
|---|---|---|---|
| EOL | Out of bounds | Walkable | Player spawn |
| Wall | Crate spawn | Crate goal | Crate (on goal) |
| Player (on goal) | Null | Null | Null |
| Null | Repeat | Null | EOF |

The Repeat nibble will always be followed by two nibbles, one with a value of how many times to repeat, and then the nibble to repeat.

A JSON file is no longer required, simply write out a text file with every level separated by semicolons and run a command like below:
```
python3 convert.py example.txt "Example Title (1970 - Example Co.)" "This is an example description! Both of these variables are required."
```
