
import os
#import re

testPath = "C:/Users/asufa/OneDrive/デスクトップ/1006_1h/MVAuNiUV_autored.cif"
testPath2 = "C:/Users/asufa/OneDrive/デスクトップ/test_autored.cif"
testOutPath = "C:/Users/asufa/OneDrive/デスクトップ/1006_1h_def/outpuuuut.txt"
fileName = os.path.splitext(os.path.basename(testPath))[0]
fileName2 = os.path.splitext(os.path.basename(testPath2))[0]

def addressSort():
    print("os.sep: "+os.sep)
    print("testPath: "+ testPath)
    print("baseName: "+ os.path.basename(testPath))
    print("fileName: "+ fileName)

def openTest():
    i: int = 0
    atoms: bool = False
    with open(testPath) as f:
        print("\n")
        for test_line in f:
            match i:
                case 0:
                    if fileName.lower() in test_line:
                        print("fileName: " + test_line.strip())
                    else:
                        print("file is not compleat by Olex2-1.5")
                        break
                case 400:
                    print("readline is over.(400 lines)")
                    break
                case _:
                    if "_cell_length_" in test_line:
                        print(test_line.strip())
                    elif "_cell_angle_" in test_line:
                        print(test_line.strip())
                    elif "_atom_site_disorder_group" in test_line:
                        atoms = True
                        continue
                    elif "loop_" in test_line:
                        if atoms:
                            print("read finished")
                            print("i: " + str(i))
                            break
                        else:
                            atoms = False
                            continue
                    else:
                        pass
                    if atoms:
                        print(test_line.strip())
            i+=1


def makeListTest():
    i: int = 0
    atoms: bool = False
    testList = [["fileName"]]
    atomNum: int = 0
    atomInnerNum: int = 0
    with open(testPath2) as f:
        print("\n")
        for test_line in f:
            match i:
                case 0:
                    if fileName2.lower() in test_line:
                        testList[0].append(test_line.strip())
                        #print("fileName: " + test_line.strip())
                    else:
                        print("file is not compleat by Olex2-1.5")
                        break
                case 400:
                    print("readline is over.(400 lines)")
                    break
                case _:
                    if "_cell_length_" in test_line:
                        lengthStock = test_line.strip().split()
                        testList.append([lengthStock[0][1:],lengthStock[1].split('(')[0]])
                        #print(test_line.strip().split())
                    elif "_cell_angle_" in test_line:
                        angleStock = test_line.strip().split()
                        testList.append([angleStock[0][1:],angleStock[1].split('(')[0]])
                        #print(test_line.strip())
                    elif "_atom_site_disorder_group" in test_line:
                        atoms = True
                        atomNum = 1
                        atomInnerNum = 1
                        continue
                    elif "loop_" in test_line:
                        if atoms:
                            print("read finished")
                            print("i: " + str(i))
                            break
                        else:
                            atoms = False
                            continue
                    else:
                        pass
                    if atoms:
                        atomsStock = test_line.strip().split()
                        #print(atomsStock)
                        if len(atomsStock) < 5:
                            continue
                        atomName = atomsStock[1]

                        if atomNum == 1 and atomInnerNum == 1:
                            testList.append([atomName,str(atomNum),str(atomInnerNum),atomsStock[2].split('(')[0],atomsStock[3].split('(')[0],atomsStock[4].split('(')[0]])
                            atomInnerNum = 2
                        elif atomName == testList[-1][0]:
                            atomNum = int(testList[-1][1])
                            atomInnerNum = int(testList[-1][2]) + 1
                            testList.append([atomName,str(atomNum),str(atomInnerNum),atomsStock[2].split('(')[0],atomsStock[3].split('(')[0],atomsStock[4].split('(')[0]])
                        else:
                            atomNum = int(testList[-1][1]) + 1
                            atomInnerNum = 1
                            testList.append([atomName,str(atomNum),str(atomInnerNum),atomsStock[2].split('(')[0],atomsStock[3].split('(')[0],atomsStock[4].split('(')[0]])

                        #print(test_line.strip())
            i+=1

    outputLines = ["MakeCi_output"]
    for outputLine in testList:
        #print(str(outputLines))
        print(outputLine)
        outputLines.append('  '.join(outputLine))

    with open(testOutPath, mode='w') as f:
        f.write('\n'.join(outputLines))





#addressSort()
#openTest()
makeListTest()
