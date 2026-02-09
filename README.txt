Creator: Ryan Mason

This is the basic VM translator for project 7 of Nand2Tetris, which converts .vm files with stack into .asm files with hack assembly.

The VM translator allows for: 

Memory commands: "push" and "pop"
Comparison commands: "eq", "lt", "gt"
Arithmetic commands: "add", "sub", "neg", "and", "not", "or"  
Segments: "constant", "arguemnt", "local", "this", "that", "temp", "static", "pointer"

*comments using "//" are also supported*

Example:
push constant 5
push constant 5
eq   // should be true (-1) if code is correct and Ryan is not big dumb dumb. 

*Please note that everything MUST be in all lowercase, otherwise it will not work*  

"FileName.vm.txt" should contain some example code to translate unless I just forgot.

*Also this style of a README file was just me looking at images of README files + what I remeber from Java READMEs and mashing them together until I got something I liked.*
*Please let me know if this is good enough or if there's a more specific way I should be writing this.*
*Have fun!*