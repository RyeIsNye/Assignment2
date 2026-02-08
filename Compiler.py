import math
from pathlib import Path
import sys
# 13 - 15 are temperaruy registers
# 0 - 2 are for this, that, pointer
#
labelCounter = 0
fileName = "FileName"

operations = {
    "add" : "+",
    "sub" : "-",
    "and" : "&",
    "or" : "|",
    "not" : "!",
    "neg" : "-"
}

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
true = "D=M-D\nM=-1\n" # set to true
false = "@SP\nA=M-1\nM=0\n" # set to false


pop = "@SP\nAM=M-1\nD=M\n" #  Still gotta ask if AM = M-1 is allowed
getMem = "@SP\nA=M-1\n"

def compares(instruction):
    global labelCounter
    title = "CompTrue_" + str(labelCounter)
    label = "(" + title + ")\n"

    if instruction[0] not in compares:
        raise ValueError("Invalid command")

    if instruction[0] == "eq":
        jumpCode = "@" + title + eq
    
    elif instruction[0] == "lt":
        jumpCode = "@" + title + lt

    elif instruction[0] == "gt":
        jumpCode = "@" + title + gt
    labelCounter += 1
    return pop + getMem + jumpCode + false + label + true

def pushCommand(segment, index):
    if segment == "constant":
        return f"@{index}\nD=A\n" + push

    if segment in ("local", "argument", "this", "that"):
        return (
            f"@{segments[segment]}\nD=M\n"
            f"@{index}\nA=D+A\nD=M\n"
            + push
        )

    if segment == "temp":
        return f"@{5 + int(index)}\nD=M\n" + push

    if segment == "pointer":
        return f"@{3 + int(index)}\nD=M\n" + push

    if segment == "static":
        return f"@{fileName}.{index}\nD=M\n" + push

def popCommand(segment, index):
    if segment in ("local", "argument", "this", "that"):
        return (
            f"@{segments[segment]}\nD=M\n"
            f"@{index}\nD=D+A\n"
            "@R13\nM=D\n"
            + pop +
            "@R13\nA=M\nM=D\n"
        )

    if segment == "temp":
        return pop + f"@{5 + int(index)}\nM=D\n"

    if segment == "pointer":
        return pop + f"@{3 + int(index)}\nM=D\n"

    if segment == "static":
        return pop + f"@{fileName}.{index}\nM=D\n"

def arithmetic(command):
    if command in ("add", "sub", "and", "or"):
        return (
            "@SP\nM=M-1\nA=M\nD=M\n"
            "@SP\nM=M-1\nA=M\n"
            f"M=M{operations[command]}D\n"
            "@SP\nM=M+1\n"
        )

    if command in ("neg", "not"):
        return (
            "@SP\nA=M-1\n"
            f"M={operations[command]}M\n"
        )

    return compares([command])

def main():
    input = Path("FileName.vm.txt")

    if not input.exists():
        sys.exit(1)

    with input.open("r") as file:
        for line in file:
            line = line.strip()

            # skip blank lines and comments
            if not line or line.startswith("//"):
                continue
            command = line.split()

            if command[0] in operations or command[0] in ("eq", "lt", "gt"):
                asm = arithmetic(command[0])

            elif command[0] == "push":
                asm = pushCommand(command[1], command[2])

            elif command[0] == "pop":
                asm = popCommand(command[1], command[2])

            else:
                continue

            print(asm)


if __name__=="__main__":
    main()