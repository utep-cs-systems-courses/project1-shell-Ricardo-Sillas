#!/usr/bin/env python3

import os
import sys
import re

while True:
    
    if 'PS1' in os.environ:
        os.write(1,(os.environ['PS1']).encode())
    else:
        os.write(1,(os.getcwd().split("/")[-1] + "$ ").encode())
    inputs = input()
    
    if inputs == "exit":
        break

    if inputs.startswith("cd ") and len(inputs) > 3:
        directory = inputs.split("cd")[1].strip()
        try:
            os.chdir(directory)
        except FileNotFoundError:
            os.write(1, ("-bash: cd: %s: No such file or directory\n" % directory).encode())
        continue
    
    
    elif inputs.startswith("ls > ") and len(inputs) > 5 and inputs.endswith(".txt"):
        slashes = inputs.split("/")
        a = os.listdir(os.getcwd())
        for i in range(1, len(slashes) - 1):
            try:
                os.chdir(slashes[i])
            except FileNotFoundError:
                os.write(1, ("-bash: cd: %s: No such file or directory\n" % directory).encode())
            continue
        fdOut = os.open(slashes[-1], os.O_CREAT | os.O_WRONLY)
        for i in a:
            os.write(fdOut, (i+"\n").encode())
        for i in range(len(slashes)-2):
            os.chdir("..")

    elif inputs.startswith("cat < ") and len(inputs) > 6 and inputs.endswith(".txt"):
        fdIn = os.open(inputs[6:], os.O_RDONLY)
        lineNum = 1
        while 1:
            inputs = os.read(fdIn, 10000)  # read up to 10k bytes
            if len(inputs) == 0: break     # done if nothing read
            lines = re.split(b"\n", inputs)
            for line in lines:
                strToPrint = f"{line.decode()}\n"
                os.write(1    , strToPrint.encode()) # write to fd1 (standard output)
                lineNum += 1

    elif inputs.startswith("ls"):
        directory_list = os.listdir(os.getcwd())
        for i in directory_list:
            print(i, end = "   ")
        print("")

    elif (inputs.startswith("wc ") and len(inputs) > 3) or (inputs.startswith("python3 ") and len(inputs) > 8):
        rc = os.fork()
        
        if rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0:                   # child
            if(inputs.startswith("wc")):
                files = inputs.split("wc")[1].strip()
                args = ["wc", files]
            else:
                files = inputs.split("python3")[1].strip()
                args = ["python3", files]
            for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                    pass                              # ...fail quietly

            os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
            sys.exit(1)                 # terminate with error
        else:
            os.wait()
        
        
        
        
        
        
        
        
        
    
    elif inputs not in os.environ:
        os.write(1,(inputs + ": command not found\n").encode())

