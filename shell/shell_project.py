#!/usr/bin/env python3

import os
import sys
import re

def pipes(pipe_input):
        writeCommands = inputs[0:inputs.index("|")]
        readCommands = inputs[inputs.index("|") + 1:]
        pr, pw = os.pipe()
        rc = os.fork()
        if rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0:
            os.close(1)  # close fd 1 (output)
            os.dup2(pw, 1)  # duplicate pw in fd1
            for fd in (pr, pw):
                os.close(fd)  # close pw & pr
            executing(writeCommands)  # Run the process as normal
            os.write(2, ("Could not exec %s\n" % writeCommands[0]).encode())
            sys.exit(1)
        else:
            os.close(0)  # close fd 0 (input)
            os.dup2(pr, 0)  # dup pr in fd0
            for fd in (pw, pr):
                os.close(fd)
            if "|" in readCommands:
                pipe(readCommands)
            executing(readCommands)  # Run the process as normal
            os.write(2, ("Could not exec %s\n" % writeCommands[0]).encode())

def executing(args):
    for dir in re.split(":", os.environ['PATH']): # try each directory in the path
        program = "%s/%s" % (dir, args[0])
        try:
            os.execve(program, args, os.environ) # try to exec program
        except FileNotFoundError:             # ...expected
            pass                              # ...fail quietly

    os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
    sys.exit(1)                 # terminate with error

while True:    
    
    end_string = os.getcwd() + "$ "
    if 'PS1' in os.environ:
        end_string=os.environ['PS1']
    try:
        inputs = [str(n) for n in input(end_string).split()]
    except EOFError:    #catch error
        sys.exit(1)
    
    if len(inputs) < 1:
        continue
    
    if inputs[0] == "exit":
        sys.exit(0)

    if inputs[0] == 'cd':
        try:
            os.chdir(inputs[1])
        except FileNotFoundError:
            pass
            
    elif '|' in inputs:
        pipes(inputs)

    else:
        rc = os.fork()
        if rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0:   
            if '>' in inputs:
                os.close(0)
                os.open(inputs[inputs.index('>')+1], os.O_RDONLY);
                os.set_inheritable(0, True)
                executing(inputs[0:inputs.index('>')])
            else:
                os.close(0)
                os.open(inputs[inputs.index('<')+1], os.O_RDONLY);
                os.set_inheritable(0, True)
                executing(inputs[0:inputs.index('<')])
        else:
            os.wait()
