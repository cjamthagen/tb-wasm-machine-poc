import sys
import os
sys.path.append('../')
from utils import Colors
from argparser import *
from TBInit import *

success = Colors.green + "SUCCESS: " + Colors.ENDC
fail = Colors.red + "FAIL: " + Colors.ENDC

def ObjectList(directory):
    obj_list = []
    cwd = os.getcwd()

    for file in os.listdir(cwd + directory):
        if file.endswith(".wasm"):
            obj_list.append(cwd + directory + "/" + file)

    return(obj_list)

def section_validation_fail(directory):
    return_list = []
    obj_list = ObjectList(directory)
    for testfile in obj_list:
        pid = os.fork()
        # I dont have a bellybutton
        if pid == 0:
            # @DEVI-FIXME-pipe stdout and stderr to a file instead of the
            # bitbucket
            sys.stdout = open('/dev/null', 'w')
            sys.stderr = open('/dev/null', 'w')

            interpreter = PythonInterpreter()
            module = interpreter.parse(testfile)
            interpreter.appendmodule(module)
            interpreter.dump_sections(module)
            if "type" in directory:
                if not interpreter.TypeSection():
                    sys.exit(1)
            if "global" in directory:
                if not interpreter.GlobalSection():
                    sys.exit(1)
            sys.exit()
        # the parent process
        elif pid > 0:
            # @DEVI-FIXME-we are intentionally blocking. later i will fix this
            # so we can use multicores to run our reg tests faster.
            cpid, status = os.waitpid(pid, 0)
            return_list.append(status)
            if status != 0:
                print(success + testfile)
            else:
                print(fail + testfile)
        else:
            # basically we couldnt fork a child
            print(fail + 'return code:' + pid)
            raise Exception("could not fork child")


def section_validation():
    return_list = []
    obj_list = ObjectList("/testsuite")
    for testfile in obj_list:
        pid = os.fork()
        # I dont have a bellybutton
        if pid == 0:
            # @DEVI-FIXME-pipe stdout and stderr to a file instead of the
            # bitbucket
            sys.stdout = open('/dev/null', 'w')
            sys.stderr = open('/dev/null', 'w')

            interpreter = PythonInterpreter()
            module = interpreter.parse(testfile)
            interpreter.appendmodule(module)
            interpreter.dump_sections(module)
            interpreter.runValidations()
            vm = VM(interpreter.getmodules())
            ms = vm.getState()
            # interpreter.dump_sections(module)
            DumpIndexSpaces(ms)
            DumpLinearMems(ms.Linear_Memory, 1000)
            sys.exit()
        # the parent process
        elif pid > 0:
            # @DEVI-FIXME-we are intentionally blocking. later i will fix this
            # so we can use multicores to run our reg tests faster.
            cpid, status = os.waitpid(pid, 0)
            return_list.append(status)
            if status == 0:
                print(success + testfile)
            else:
                print(fail + testfile)
        else:
            # basically we couldnt fork a child
            print(fail + 'return code:' + pid)
            raise Exception("could not fork child")

def main():
    sectionvalidation(False)
    sectionvalidation(True)

if __name__ == '__main__':
    main()
