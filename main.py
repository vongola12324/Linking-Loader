import os
import sys

# Open File
filename = ""
filename = input("Enter Input Filename: ")
if filename == "":
    filename = "linkin.txt"

fin = open(filename, "r")

# Variable Prepare
PGBLOCKS = {}
MODIFY = []
OBJCODE = []

# Method Prepare
def splitLine(line):
    word = line.strip().split()
    return word


def getObjline(START=None):
    start = int(START, 16)
    for i in OBJCODE:
        objstart = int(i.get("START"), 16)
        objlen = int(i.get("LENGTH"), 16)
        if objstart <= start <= objstart + objlen:
            return i
        else:
            continue

def toSignedInt(hexstr):
    i = int(hexstr, 16)
    if i > 0x7FFFFF:
        i -= 0x1000000
    return i

def toSignedHex(num):
    return hex(((abs(num) ^ 0xffff) + 1) & 0xffff)

# Program Start
Offset = input("Enter Program Start Address: ")
Offset = int(Offset, 16)
Length = 0
while True:
    line = fin.readline()
    if not line:
        break
    else:
        if line[0] == "H":
            word = splitLine(line)
            PGBLOCKS.update({word[1]: hex(int(word[2], 16) + Offset)[2:].upper()})
            Length = int(word[3], 16)
        elif line[0] == "D":
            word = splitLine(line)
            for i in range(1, len(word), 2):
                PGBLOCKS.update({word[i]: word[i + 1]})
        elif line[0] == "R":
            continue
        elif line[0] == "E":
            Offset += Length
            continue
        elif line[0] == "T":
            word = splitLine(line)
            string = ""
            for i in range(3, len(word)):
                string += word[i]
            string = hex(toSignedInt(word[1]) + Offset)[2:].upper()
            while len(string) < 6:
                string = "0" + string
            OBJCODE.append({"START": string, "LENGTH": word[2], "OBJC": string})
        else:
            word = splitLine(line)
            if word != []:
                MODIFY.append({"ADDR": hex(toSignedInt(word[1]) + Offset), "LENGTH": word[2], "OPER": word[3], "PGB": word[4]})

for i in MODIFY:
    ObjLine = getObjline(i.get("ADDR"))
    Objc = ObjLine.get("OBJC")
    selectStart = (int(i.get("ADDR"), 16) - int(ObjLine.get("START"), 16)) * 2
    if int(i.get("LENGTH"), 16) % 2 == 1:
        selectStart += 1

    ModObjc = Objc[selectStart:selectStart + int(i.get("LENGTH"), 16)]
    PGB = PGBLOCKS.get(i.get("PGB"))
    print("PGB: " + PGB + ", MOD: " + ModObjc)
    if i.get("OPER") == "+":
        ModObjc = toSignedHex(toSignedInt(ModObjc) + toSignedInt(PGB))[2:].upper()
    else:
        ModObjc = toSignedHex(toSignedInt(ModObjc) - toSignedInt(PGB))[2:].upper()
    print(ModObjc)
    while len(ModObjc) < int(i.get("LENGTH"), 16):
        ModObjc = "0" + ModObjc
    ObjLine.update({"OBJC": Objc[:selectStart] + ModObjc + Objc[selectStart + int(i.get("LENGTH"), 16):]})

for i in OBJCODE:
    Objc = i.get("OBJC")
    while len(Objc) < 32:
        Objc += "."
    i.update({"OBJC": Objc})
    print(
        "{0:<06s}    {1:<8s}  {2:<8s}  {3:<8s}  {4:<8s}".format(i.get("START"), i.get("OBJC")[0:8], i.get("OBJC")[8:16],
                                                               i.get("OBJC")[16:24], i.get("OBJC")[24:32]))