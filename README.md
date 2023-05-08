# SokoPy - A Sokoban clone made in Python

**Features:**
- Real Graphics!
- Runs on anything with Python and PyGame!
- Some Settings!
- A "Tutorial"!
- The levels from the 1982 original!
- David W. Skinner's level packs!
- An open level creation format!
- A Semi-Functional Level Editor!

---

The game only supports base Sokoban blocks right now, but colored blocks/targets and holes are planned to be added.  
There is a level editor included, though it is very primitive. If you are interested in the file format and how the editor works, read below.

The convert.py script allows you to convert a text representation of a level into a custom file format, and out of it, when provided with a valid level
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

A command like below can be used to compile your file.
```
python3 convert.py example.txt "Example Title (1970 - Example Co.)" "This is an example description! Both of these variables are required."
```

Each block in a level is a 4bit nibble, with the exception that any series of blocks larger than three will be compressed down

|[]()||||
|---|---|---|---|
| ! > EOL | Out of bounds | Space > Walkable | @ > Player spawn |
| # > Wall | $ > Crate spawn | . > Crate goal | * > Crate (on goal) |
| + > Player (on goal) | Null | Null | Null |
| Null | Repeat | Null | EOF |

The Repeat nibble is used to indicate that there's a series of four or more blocks in a row.  
It takes up three nibbles (1.5 bytes) so we don't use it for three or fewer blocks, as this would be less effecient.  
The first nibble is always `1101`, this is followed by a 4bit number indicating how many times the block is repeated.  
Since we're not using the numbers three through zero, `0001` is seen as 4, and `1111` is seen as 19.  
The third nibble is the block we're going to repeat.

The first four bytes of the file are always the identifier 'SKBN', or the file is seen as invalid.  
Following those bytes is the header, which consists of three parts.  

The first part of the header is two strings of indeterminate length, both end in a newline. These are the title and description of the levelpack.  
The second is a 1 byte integer, indicating how many levels are included. Hopefully no one ever makes a levelpack with more than 255 levels.  
The third and final part of the header is the file record, which is a series of 2-byte integers. Each of these is an offset of how far into the file a level is.

After the header, the rest of the file is just level data. Each level ends with a nibble of '1111', which will be padded with 0s if necessary, so that every level is a whole number of bytes.
