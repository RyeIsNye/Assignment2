from pathlib import Path
import sys

labelCounter = 0
callCounter = 0
currentFunction = ""
fileName = "FileName"

# These are just conversions from the VM language so I can easily use them for the code
operations = {
    "add" : "+",
    "sub" : "-",
    "and" : "&",
    "or" : "|",
    "not" : "!",
    "neg" : "-"
}

# More conversions from VM language to hack assembly
segments ={
    "argument" : "ARG",
    "local" : "LCL",
    "static" : "16", # base address of static segment
    "this" : "THIS",
    "that" : "THAT",
    "pointer" : "3", # base address of pointer segment
    "temp" : "5" # base address of temp segment
}

eq = "D;JEQ\n" # jump if equal
lt = "D;JLT\n" # jump if less than
gt = "D;JGT\n" # jump if greater than


push = "@SP\nA=M\nM=D\n" + "@SP\nM=M+1\n" # push D onto stack
pop = "@SP\nM=M-1\nA=M\nD=M\n" 

# This function is for the eq, lt, and gt commands, and uses a global label counter to make sure that the labels are unique
def compares(instruction):
    #I could not figure this out for the life of me until you said aloud to someone else that it would be global.
    global labelCounter
    trueLabel = "CompTrue_" + str(labelCounter)
    endLabel = "CompEnd_" + str(labelCounter)
    
    if instruction[0] not in ("eq", "lt", "gt"):
        raise ValueError("Invalid command")

    if instruction[0] == "eq":
        jump = eq
    
    elif instruction[0] == "lt":
        jump = lt

    elif instruction[0] == "gt":
        jump = gt

    labelCounter += 1
    # To quickly explain this whole section it pops x and y off then subtracts them. Where it jumps next depends on what was inputed.
    return (
        # pop y
        "@SP\n"
        "M=M-1\n"
        "A=M\n"
        "D=M\n"

        # pop x and compute x - y
        "@SP\n"
        "M=M-1\n"
        "A=M\n"
        "D=M-D\n"

        # if true, jump
        # Side note: f"{}" or formatted string is so amazing
        f"@{trueLabel}\n"
        f"{jump}"

        #false
        "@SP\n"
        "A=M\n"
        "M=0\n"
        f"@{endLabel}\n"
        "0;JMP\n"

        #true
        f"({trueLabel})\n"
        "@SP\n"
        "A=M\n"
        "M=-1\n"

        # end
        f"({endLabel})\n"
        "@SP\n"
        "M=M+1\n"
    )

# This pushCommand takes in the segment and index and returns the assembly code to push the value at that segment and index onto the stack.
def pushCommand(segment, index):
    # If constant then just set D reg to A
    if segment == "constant":
        return f"@{index}\nD=A\n" + push

    if segment in ("local", "argument", "this", "that"):
        return (
            # This converts the segment into hack assembly then adds the index to it to get the correct address
            # Then it sets D to the value at that address and pushes it onto the stack
            f"@{segments[segment]}\nD=M\n"
            f"@{index}\nA=D+A\nD=M\n"
            + push
        )

    # Temp and pointer are just direct address
    if segment == "temp":
        return f"@{5 + int(index)}\nD=M\n" + push

    if segment == "pointer":
        return f"@{3 + int(index)}\nD=M\n" + push

    # Static is just fileName.index
    if segment == "static":
        return f"@{fileName}.{index}\nD=M\n" + push
    
# This popCommand takes in the segment and index and returns the assembly code to pop the value at the top of the stack and store it at that segment and index
def popCommand(segment, index):
    if segment in ("local", "argument", "this", "that"):
        return (
            f"@{segments[segment]}\nD=M\n"
            f"@{index}\nD=D+A\n"
            # Temporary R13 is used to store the address
            "@R13\nM=D\n"
            + pop +
            # Then it pops the value off the stack and stores it in the address stored in R13
            "@R13\nA=M\nM=D\n"
        )

    if segment == "temp":
        return pop + f"@{5 + int(index)}\nM=D\n"

    if segment == "pointer":
        return pop + f"@{3 + int(index)}\nM=D\n"

    if segment == "static":
        return pop + f"@{fileName}.{index}\nM=D\n"


def arithmetic(command):
    # Add, Sub, And, Or need the top two values of the stack so the pop them off, do the math, the push back on
    if command in ("add", "sub", "and", "or"):
        return (
            "@SP\nM=M-1\nA=M\nD=M\n"
            "@SP\nM=M-1\nA=M\n"
            f"M=M{operations[command]}D\n"
            "@SP\nM=M+1\n"
        )

    # Neg and Not only need the top value of the stack
    if command in ("neg", "not"):
        return (
            "@SP\nA=M-1\n"
            f"M={operations[command]}M\n"
        )

    return compares([command])

#sets up a new stack frame and jumps into the function.
def writeCall(functionName, nArgs):
    global callCounter
    returnLabel = f"{functionName}$ret.{callCounter}"
    callCounter += 1

    code = ""

    code += f"@{returnLabel}\nD=A\n" + push

    for seg in ["LCL", "ARG", "THIS", "THAT"]:
        code += f"@{seg}\nD=M\n" + push

    code += (
        "@SP\nD=M\n"
        f"@{int(nArgs) + 5}\n"
        "D=D-A\n"
        "@ARG\nM=D\n"
    )

    code += "@SP\nD=M\n@LCL\nM=D\n"
    code += f"@{functionName}\n0;JMP\n"
    code += f"({returnLabel})\n"

    return code

# Defines a jump target inside a function
def writeLabel(label):
    return f"({currentFunction}${label})\n"

# A function that always jumps to the label that is inputed
def writeGoto(label):
    return f"@{currentFunction}${label}\n0;JMP\n"

# Same as WriteGoto but jumps to label only if the top of stack is true (non-zero number)
def writeIf(label):
    return (
        "@SP\nM=M-1\nA=M\nD=M\n"
        f"@{currentFunction}${label}\n"
        "D;JNE\n"
    )

# Starts the program at the address 256
def writeBootstrap():
    return (
        "@256\nD=A\n@SP\nM=D\n"
        + writeCall("Sys.init", 0)
    )

# Absolutley destroys the function frame and jumps back to the caller
def writeReturn():
    return (
        "@LCL\nD=M\n@R13\nM=D\n"
        "@5\nA=D-A\nD=M\n@R14\nM=D\n"
        + pop +
        "@ARG\nA=M\nM=D\n"
        "@ARG\nD=M+1\n@SP\nM=D\n"

        "@R13\nAM=M-1\nD=M\n@THAT\nM=D\n"
        "@R13\nAM=M-1\nD=M\n@THIS\nM=D\n"
        "@R13\nAM=M-1\nD=M\n@ARG\nM=D\n"
        "@R13\nAM=M-1\nD=M\n@LCL\nM=D\n"

        "@R14\nA=M\n0;JMP\n"
    )

# It creates the function and sets up its local variables
def writeFunction(functionName, nVars):
    global currentFunction
    currentFunction = functionName

    code = f"({functionName})\n"
    for _ in range(int(nVars)):
        code += "@0\nD=A\n" + push
    return code


# This portion does the file handling and calls the functions to convert the VM commands into assembly
def main():

    inputPath = Path(sys.argv[1])

    if not inputPath.exists():
        sys.exit(1)

    # Does a bunch of file handling and is basically magic to me
    if inputPath.is_dir():
        vmFiles = list(inputPath.glob("*.vm"))
        outputPath = inputPath / (inputPath.name + ".asm")
    else:
        vmFiles = [inputPath]
        outputPath = inputPath.with_suffix(".asm")

    with outputPath.open("w") as outfile:
        outfile.write(writeBootstrap())
        for vmFile in vmFiles:

            global fileName
            fileName = vmFile.stem 

            with vmFile.open("r") as infile:
                for line in infile:
                    line = line.strip()

                    if not line or line.startswith("//"):
                        continue

                    command = line.split()

                    # process all of the commands and calls all the functions when needed
                    if command[0] in operations or command[0] in ("eq", "lt", "gt"):
                        asm = arithmetic(command[0])

                    elif command[0] == "push":
                        asm = pushCommand(command[1], command[2])

                    elif command[0] == "pop":
                        asm = popCommand(command[1], command[2])
                    
                    elif command[0] == "label":
                        asm = writeLabel(command[1])

                    elif command[0] == "goto":
                        asm = writeGoto(command[1])

                    elif command[0] == "if-goto":
                        asm = writeIf(command[1])

                    elif command[0] == "function":
                        asm = writeFunction(command[1], command[2])

                    elif command[0] == "call":
                        asm = writeCall(command[1], command[2])

                    elif command[0] == "return":
                        asm = writeReturn()

                    else:
                        continue
                    
                    outfile.write(asm)


if __name__=="__main__":
    main()
