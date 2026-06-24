import json
while True:
    strIn = ""
    nextLine = "TEMP"
    while nextLine != "":
        nextLine = input()
        strIn = strIn + nextLine
    
    cmdClass, *cmdSubClasses = strIn.split("\t")
    output = {}
    subOutput = {}
    
    print("    '" + cmdClass + "': {")
    for i in range(0, len(cmdSubClasses), 2):
        name = cmdSubClasses[i]
        cmd = cmdSubClasses[i + 1]
        out = ""
        for i in cmd.split(" "):
            out = out + r"\x" + i
        print(" "*8 + "'" + name + "': " + "rb'" + out + "',")
    print("    },")

