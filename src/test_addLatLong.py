
import pytest
import addLatLong
import filecmp
from shutil import copyfile

test_initlocFileName = "testData/testinitloc.json"
test_locFileName = "testData/testloc.json"
test_locInstFileName = "testData/testlocInst.json"


def init_test_loc_file():
    copyfile(test_initlocFileName, test_locFileName)


def test_open_json():
    init_test_loc_file()

    # read the locations json and initialize data structures: clear the count to 0
    # but do not scan the spreadsheet
    a1 = addLatLong.AcqInfo(test_locFileName, test_locInstFileName)
    assert a1.all_data["Gloucester Ontario Canada"]["count"] == 0
    return True


def test_one_row():
    init_test_loc_file()
    a1 = addLatLong.AcqInfo(test_locFileName, test_locInstFileName)

    # test with one row in the input, having InstName, City, Prov, Country
    test_xlsxFileName = "testData/testOpen.xlsx"
    a1.scan_spreadsheet(test_xlsxFileName)
    assert a1.all_data["Cornwall Ontario Canada"]["count"] == 1

    # output locations files should equal the test check files
    test_dupFileName = "testData/duplicateloc.json"
    assert filecmp.cmp(test_locFileName, test_dupFileName, shallow=False)

    test_dupInstFileName = "testData/duplicatelocInst.json"
    assert filecmp.cmp(test_locInstFileName, test_dupInstFileName, shallow=False)
    return True


def test_two_rows_same_addr():
    init_test_loc_file()
    a1 = addLatLong.AcqInfo(test_locFileName, test_locInstFileName)

    # test with two rows in the input, both having InstName, City, Prov, Country
    test_xlsxFileName = "testData/testTwoSame.xlsx"
    a1.scan_spreadsheet(test_xlsxFileName)
    assert a1.all_data["Cornwall Ontario Canada"]["count"] == 2

    # output locations files should equal the test check files
    test_dupFileName = "testData/duplicateloc2.json"
    assert filecmp.cmp(test_locFileName, test_dupFileName, shallow=False)

    test_dupInstFileName = "testData/duplicatelocInst2.json"
    assert filecmp.cmp(test_locInstFileName, test_dupInstFileName, shallow=False)
    return True
