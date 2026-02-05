import math
from pathlib import Path
import sys
# 13 - 15 are temperaruy registers
# 0 - 2 are for this, that, pointer

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

push = "@SP\nA=M\nM=D\n" + "@SP\nM=M+1\n" # push D onto stack
true = "D=M-D\nM=-1\n" # set to true
false = "@SP\nA=M-1\nM=0\n" # set to false
eq = "D;JEQ\n" # jump if equal
lt = "D;JLT\n" # jump if less than
gt = "D;JGT\n" # jump if greater than

#This one is wrong fix it
# popDReg = "@SP\nAM=M-1\nD=M\n" # pop stack to D

getMem = "@SP\nA=M-1\n"

def conditionalJump(jumpType):
    jumpCode = ""
    if jumpType == "eq":
        jumpCode = eq
    elif jumpType == "lt":
        jumpCode = lt
    elif jumpType == "gt":
        jumpCode = gt
    return jumpCode

def main():
    print(push)

if __name__=="__main__":
    main()