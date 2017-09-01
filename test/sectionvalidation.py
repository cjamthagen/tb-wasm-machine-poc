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
            modulevalidation = ModuleValidation(module)
            if "type" in directory:
                if not modulevalidation.TypeSection():
                    sys.exit(1)
            if "import" in directory:
                if not modulevalidation.ImportSection():
                    sys.exit(1)
            if "function" in directory:
                if not modulevalidation.FunctionSection():
                    sys.exit(1)
            if "table" in directory:
                if not modulevalidation.TableSection():
                    sys.exit(1)
            if "memory" in directory:
                if not modulevalidation.MemorySection():
                    sys.exit(1)
            if "global" in directory:
                if not modulevalidation.GlobalSection():
                    sys.exit(1)
            if "export" in directory:
                if not modulevalidation.ExportSection():
                    sys.exit(1)
            if "start" in directory:
                if not modulevalidation.StartSection():
                    sys.exit(1)
            if "element" in directory:
                if not modulevalidation.ElementSection():
                    sys.exit(1)
            if "code" in directory:
                if not modulevalidation.CodeSection():
                    sys.exit(1)
            if "data" in directory:
                if not modulevalidation.DataSection():
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
            if not interpreter.runValidations():
                sys.exit(1)
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
