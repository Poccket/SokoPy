# SokoPy - A Sokoban clone made in Python

**Features:**
- Text Graphics!
- Runs on anything with Python!
- No Settings!
- A "Tutorial"!
- A few levels from the 1982 original!
- An open level creation system!

---

While it only features base Sokoban blocks currently, the game allows for level creation as long as you are willing to learn it.
I have not yet added a proper level creator, however, it's fairly simple.

Each block in a level is a 4bit character. This allows for a hex editor to show the level easily by representing each block as a single hexadecimal character. All the blocks are below:

|Tables|need|headers|...|
|---|---|---|---|
| EOL | Out of bounds | Walkable | Player spawn |
| Wall | Crate spawn | Crate goal | Crate (on goal) |
| Player (on goal) | Null | Null | Null |
| Null | Null | Null | Null |

Simply write it, line by line, with an EOL at the end of every line to make a level.

Once you have some levels, you will need a metadata JSON file. There's one included with the 1982 level pack you can use as an example.

You will need a title, description and to list each level with it's name and relative location