#!/bin/python3.5

# call it the regression testing file
# @DEVI-if you wanna pipe the output, run with python -u. buffered output
# screws up the output

import sys
import os
from test_LEB128 import test_signed_LEB128
from test_LEB128 import test_unsigned_LEB128
from leb128s import leb128sencodedecodeexhaustive
from leb128s import leb128uencodedecodeexhaustive
from sectionvalidation import *
from abc import ABCMeta, abstractmethod
sys.path.append('../')
from utils import Colors
from argparser import *
from TBInit import *

total_test_cnt = int()
expected_pass_cnt = int()
expected_fail_cnt = int()

success = Colors.green + "SUCCESS: " + Colors.ENDC
fail = Colors.red + "FAIL: " + Colors.ENDC


# in order to keep the regression test script clean, the tests will need to
# inherit from this test class, implement the two virtual methods and then call
# it inside the main.
class Void_Spwner():
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    # this is the method that runs your tests
    @abstractmethod
    def Legacy(self):
        pass

    # this tells the class what name to use to display your test results
    @abstractmethod
    def GetName(self):
        return(str())

    def Spwn(self):
        pid = os.fork()

        # I don't have a bellybutton
        if pid == 0:
            self.Legacy()
            sys.exit()
        elif pid > 0:
            cpid, status = os.waitpid(pid, 0)
            if status == 0:
                print(success + ': ' + self.GetName())
            else:
                print(fail + ': ' + self.GetName())
        else:
            # basically we couldnt fork a child
            print(fail + 'return code:' + pid)
            raise Exception("could not fork child")

################################################################################
class LEB128EncodeTest(Void_Spwner):
    def Legacy(self):
        test_unsigned_LEB128()
        test_signed_LEB128()

    def GetName(self):
        return('leb128encodetest')

class LEB128Exhaustive(Void_Spwner):
    def Legacy(self):
        leb128sencodedecodeexhaustive()
        leb128uencodedecodeexhaustive()

    def GetName(self):
        return('leb128exhaustive')

class SectionValidationTest(Void_Spwner):
    def Legacy(self):
        fail_dir = "/testsuite_fail/"
        section_validation()
        section_validation_fail(fail_dir + "type")
        #section_validation_fail(fail_dir + "import")
        #section_validation_fail(fail_dir + "function")
        #section_validation_fail(fail_dir + "table")
        #section_validation_fail(fail_dir + "memory")
        #section_validation_fail(fail_dir + "global")
        #section_validation_fail(fail_dir + "export")
        #section_validation_fail(fail_dir + "start")
        #section_validation_fail(fail_dir + "element")
        #section_validation_fail(fail_dir + "code")
        #section_validation_fail(fail_dir + "data")

    def GetName(self):
        return('sectionvalidationtest')

################################################################################
def main():
    # LEB128 tests
    leb128encodetest = LEB128EncodeTest()
    leb128encodetest.Spwn()
    # leb128s exhaustive
    leb128sex = LEB128Exhaustive()
    leb128sex.Spwn()

    # parser test on the WASM testsuite
    sectionvalidation = SectionValidationTest()
    sectionvalidation.Spwn()

if __name__ == '__main__':
    main()
