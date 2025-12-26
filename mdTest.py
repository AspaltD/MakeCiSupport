
import os
from logging import getLogger, config
from typing import List
import json
import pprint
import re
from pathlib import Path

testPath = "C:/Users/asufa/OneDrive/デスクトップ/1006_1h/MVAuNiUV_autored.cif"
testPath2 = "D:/2_Saturn/0829_n/MVAuNi_autored.cif"
#testPath2 = "C:/Users/asufa/OneDrive/デスクトップ/test_autored.cif"
testOutPath = "D:/2_Saturn/1113_3/outpuuuut.txt"
testOutPath2 = "C:/Users/asufa/OneDrive/デスクトップ/1006_1h_def/outpuuuut.txt"
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
                    if "_space_group_IT_number" in test_line:
                        spaceNumStock = test_line.strip().split()
                        testList.append([spaceNumStock[0][1:],spaceNumStock[1]])
                    elif "_space_group_name_H-M_alt" in test_line:
                        spaceGStock = test_line.strip().split()
                        testList.append([spaceGStock[0][1:],test_line.strip().split("'")[1]])
                    elif "_cell_length_" in test_line:
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
                            if not atomsStock[7] == "1":
                                testList[-1].append(atomsStock[7].split('(')[0])
                            atomInnerNum = 2
                        elif atomName == testList[-1][0]:
                            atomNum = int(testList[-1][1])
                            atomInnerNum = int(testList[-1][2]) + 1
                            testList.append([atomName,str(atomNum),str(atomInnerNum),atomsStock[2].split('(')[0],atomsStock[3].split('(')[0],atomsStock[4].split('(')[0]])
                            if not atomsStock[7] == "1":
                                testList[-1].append(atomsStock[7].split('(')[0])
                        else:
                            atomNum = int(testList[-1][1]) + 1
                            atomInnerNum = 1
                            testList.append([atomName,str(atomNum),str(atomInnerNum),atomsStock[2].split('(')[0],atomsStock[3].split('(')[0],atomsStock[4].split('(')[0]])
                            if not atomsStock[7] == "1":
                                testList[-1].append(atomsStock[7].split('(')[0])

                        #print(test_line.strip())
            i+=1

    outputLines = ["MakeCi_output"]
    for outputLine in testList:
        #print(str(outputLines))
        print(outputLine)
        outputLines.append('  '.join(outputLine))

    with open(testOutPath, mode='w') as f:
        f.write('\n'.join(outputLines))

def LoggingTest():
    """
    with open('logging_config.json','r')as f:
        log_conf = json.load(f)
        config.dictConfig(log_conf)
    """
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'exampleFormatter': {
                'format': '%(asctime)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'consoleHandler': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'exampleFormatter',
                'stream': 'ext://sys.stdout'
            },
            'fileHandler': {
                'class': 'logging.FileHandler',
                'level': 'DEBUG',
                'formatter': 'exampleFormatter',
                'filename': 'app.log',
                'mode': 'w',
                'encoding': 'utf-8'
            }
        },
        'loggers': {
            '': {  # ルートロガーの設定
                'level': 'DEBUG',
                'handlers': ['consoleHandler', 'fileHandler']
            },
            'exampleLogger': {  # 特定のロガー設定
                'level': 'DEBUG',
                'handlers': ['consoleHandler', 'fileHandler'],
                'propagate': False
            }
        }
    }
    config.dictConfig(logging_config)

    logger = getLogger(__name__)

    logger.info("Info_Hello!!!!")
    logger.warning("warning_Hello!!!!")

def LoggingTest2():

    with open('logging_config.json',mode='r',encoding='utf_8') as f:
        log_conf = json.load(f)
        #pprint.pprint(log_conf)
        config.dictConfig(log_conf)

    #config.dictConfig(log_conf)

    logger = getLogger(__name__)

    logger.info("Info_Hello!!!!")
    logger.warning("warning_Hello!!!!")

def re_test():
    fileData:List[List[str]] = [["FileData_Output"]]
    #fileData.clear()
    with open(testOutPath2) as f:
        i:int = 0
        for line in f:
            lineParts = line.strip()
            print(line.rstrip())
            print(lineParts)
            match i:
                case 0:
                    if not lineParts == "MakeCi_output":
                        return
                case 3:
                    atomInfo = lineParts.split()
                    spaceGroup = '_'.join(atomInfo[1:])
                    fileData.append([atomInfo[0],spaceGroup])
                case _:
                    atomInfo = lineParts.split()
                    fileData.append([])
                    for info in atomInfo:
                        fileData[-1].append(info)
            i += 1
        print(f"end_line: {i}")
    
    for n in fileData:
        print(n)
    
    testData:List[List[str]]=[[]]
    i = 0
    for inList in fileData:
        if i == 0:
            if inList[0] == 'FileData_Output':
                print("continue")
            else:
                return
        elif i == 1 and inList[0] == 'fileName':
            #self.dataName.value = inList[1]
            print(f"head: {inList}")
        elif i == 400:
            return

        if i >= 2:
            match inList[0]:
                case 'space_group_IT_number':
                    #self.spaceGItNum = inList[1]
                    print(inList)
                case 'space_group_name_H-M_alt':
                    #self.spaceGName = inList[1]
                    print(inList)
                case 'cell_length_a':
                    #self.cellLenA.value = inList[1]
                    print(inList)
                case 'cell_length_b':
                    #self.cellLenB.value = inList[1]
                    print(inList)
                case 'cell_length_c':
                    #self.cellLenC.value = inList[1]
                    print(inList)
                case 'cell_angle_alpha':
                    #self.cellAngleA.value = inList[1]
                    print(inList)
                case 'cell_angle_beta':
                    #self.cellAngleB.value = inList[1]
                    print(inList)
                case 'cell_angle_gamma':
                    #self.cellAngleC.value = inList[1]
                    print(inList)
                case x if re.match('[A-Z][a-z]{0,1}',x):
                    read_row:List[str] = []
                    for inData in inList:
                        read_row.append(inData)
                    if len(inList) <= 6:
                        read_row.append("-")

                    testData.append(read_row)
                case _:
                    pass
        i += 1
    
    for n in testData:
        print(n)
    
def path_test():
        print(Path("a").name == "a")
        print(Path("None").resolve())


if __name__ == '__main__':
    #addressSort()
    #openTest()
    #makeListTest()
    #LoggingTest()
    #LoggingTest2()
    #re_test()
    path_test()
