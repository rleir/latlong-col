
import pytest
import addLatLong
import filecmp

test_locFileName = "testData/testloc.json"
test_dupFileName = "testData/duplicateloc.json"
test_locInstFileName = "testData/testlocInst.json"

test_dupInstFileName = "testData/duplicatelocInst.json"

test_xlsxFileName = "testData/testOpen.xlsx"


# read the locations json and clear the count to 0
def test_open_json():
    a1 = addLatLong.AcqInfo(test_locFileName, test_locInstFileName)
    assert a1.all_data["Gloucester Ontario Canada"]["count"] == 0
    return True


def test_open_xlsx():
    a1 = addLatLong.AcqInfo(test_locFileName, test_locInstFileName)

    a1.scan_spreadsheet(test_xlsxFileName)
    assert a1.all_data["Cornwall Ontario Canada"]["count"] == 1

    # locations file should still equal the duplicate
    assert filecmp.cmp(test_locFileName, test_dupFileName, shallow=True)

    assert filecmp.cmp(test_locInstFileName, test_dupInstFileName, shallow=True)

    return True

    # zzz print(a1.all_data)
    # print(a1.all_data[  "Gloucester Ontario Canada"])
