
import pytest
import addLatLong
import filecmp
from shutil import copyfile

# init contents
test_initlocFileName = "testData/testInitLoc.json"
# the test loc DB
test_locFileName = "testData/testLoc.json"

# output file names for several tests
test_locCountsFileName = "testData/testLocCounts.json"
test_locInstFileName   = "testData/testLocInst.json"


def init_test_loc_file():
    '''the loc file should not change in many tests below'''
    copyfile(test_initlocFileName, test_locFileName)


def test_open_json():
    init_test_loc_file()

    # read the locations json and initialize data structures:
    #               clear the count to 0
    # but do not scan the spreadsheet
    a1 = addLatLong.AcqInfo(test_locFileName,
                            test_locCountsFileName,
                            test_locInstFileName)
    assert a1.all_data["Gloucester Ontario Canada"]["count"] == 0
    a1.write_location_DB()

    # output locations DB should be unchanged,
    #     and should equal the test check file
    assert filecmp.cmp(test_locFileName,
                       test_initlocFileName, shallow=False)
    return True

# each unique addr with one or two rows
# a                                 Country
# b                     city,       Country
# c                     city, prov, Country
#
# one  unique addr with inst permutations: one two three or four rows
#  one with no inst
#  one with instname only
#  one with instdept only
#  one with instname and instdept
#
# d           instname, city, prov, Country
# e  instdpt, instname, city, prov, Country
# f  instdpt,           city, prov, Country
# g    each permutation?


def test_b_one_row():
    init_test_loc_file()
    a1 = addLatLong.AcqInfo(test_locFileName,
                            test_locCountsFileName,
                            test_locInstFileName)

    # test with one row in the input, having InstName, Prov, Country
    a1.scan_spreadsheet("testData/test_B_one.xlsx")
    assert a1.all_data["Ontario Canada"]["count"] == 1
    a1.write_location_DB()

    # output locations DB should be unchanged,
    #     and should equal the test check file
    assert filecmp.cmp(test_locFileName,
                       test_initlocFileName, shallow=False)

    # output locations counts and inst files
    #      should equal the test reference files
    assert filecmp.cmp(test_locCountsFileName,
                       "testData/test_B_oneLocCountsRef.json", shallow=False)

    assert filecmp.cmp(test_locInstFileName,
                       "testData/test_B_oneLocInstRef.json", shallow=False)
    return True


def test_b_two_rows_same_addr():
    init_test_loc_file()
    a1 = addLatLong.AcqInfo(test_locFileName,
                            test_locCountsFileName,
                            test_locInstFileName)

    # test with two rows in the input, both having InstName, Prov, Country
    a1.scan_spreadsheet("testData/test_B_two.xlsx")
    assert a1.all_data["Ontario Canada"]["count"] == 2
    a1.write_location_DB()
    # output locations DB should be unchanged,
    #     and should equal the test check file
    assert filecmp.cmp(test_locFileName,
                       test_initlocFileName, shallow=False)

    # output locations counts and inst files
    #      should equal the test reference files
    assert filecmp.cmp(test_locCountsFileName,
                       "testData/test_B_twoLocCountsRef.json", shallow=False)

    # output loc Inst files should equal the test check files
    assert filecmp.cmp(test_locInstFileName,
                       "testData/test_B_twoInstRef.json", shallow=False)
    return True


def test_c_one_row():
    init_test_loc_file()
    a1 = addLatLong.AcqInfo(test_locFileName,
                            test_locCountsFileName,
                            test_locInstFileName)

    # test with one row in the input, having InstName, City, Prov, Country
    test_xlsxFileName = "testData/test_C_one.xlsx"
    a1.scan_spreadsheet(test_xlsxFileName)
    assert a1.all_data["Cornwall Ontario Canada"]["count"] == 1
    a1.write_location_DB()
    # output locations DB should be unchanged,
    #     and should equal the test check file
    assert filecmp.cmp(test_locFileName,
                       test_initlocFileName, shallow=False)

    # output locations counts and inst files
    #      should equal the test reference files
    assert filecmp.cmp(test_locCountsFileName,
                       "testData/test_C_oneLocCountsRef.json", shallow=False)

    assert filecmp.cmp(test_locInstFileName,
                       "testData/test_C_oneLocInstRef.json", shallow=False)
    return True


def test_c_two_rows_same_addr():
    init_test_loc_file()
    a1 = addLatLong.AcqInfo(test_locFileName,
                            test_locCountsFileName,
                            test_locInstFileName)

    # test with two rows in the input,
    #      both having InstName, City, Prov, Country
    test_xlsxFileName = "testData/test_C_two.xlsx"
    a1.scan_spreadsheet(test_xlsxFileName)
    assert a1.all_data["Cornwall Ontario Canada"]["count"] == 2
    a1.write_location_DB()
    # output locations DB should be unchanged,
    #     and should equal the test check file
    assert filecmp.cmp(test_locFileName,
                       test_initlocFileName, shallow=False)

    # output locations counts and inst files
    #      should equal the test reference files
    assert filecmp.cmp(test_locCountsFileName,
                       "testData/test_C_twoLocCountsRef.json", shallow=False)

    # output loc Inst files should equal the test check files
    assert filecmp.cmp(test_locInstFileName,
                       "testData/test_C_twoLocInstRef.json", shallow=False)
    return True


def test_a_one_row():
    init_test_loc_file()
    a1 = addLatLong.AcqInfo(test_locFileName,
                            test_locCountsFileName,
                            test_locInstFileName)

    # test with one row in the input, having InstName, Prov, Country
    a1.scan_spreadsheet("testData/test_A_one.xlsx")
    assert a1.all_data["Russia"]["count"] == 1
    a1.write_location_DB()

    # output locations DB should be unchanged,
    #     and should equal the test check file
    assert filecmp.cmp(test_locFileName,
                       "testData/test_B_oneLocRef.json", shallow=False)

    # output locations counts and inst files
    #      should equal the test reference files
    assert filecmp.cmp(test_locCountsFileName,
                       "testData/test_A_oneLocCountsRef.json", shallow=False)

    assert filecmp.cmp(test_locInstFileName,
                       "testData/test_A_oneInstRef.json", shallow=False)
    return True
