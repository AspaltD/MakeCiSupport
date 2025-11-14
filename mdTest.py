
import os
from logging import getLogger, config
import json
import pprint
#import re

testPath = "C:/Users/asufa/OneDrive/デスクトップ/1006_1h/MVAuNiUV_autored.cif"
testPath2 = "D:/2_Saturn/1113_3/MVAuNi_autored.cif"
#testPath2 = "C:/Users/asufa/OneDrive/デスクトップ/test_autored.cif"
testOutPath = "D:/2_Saturn/1113_3/outpuuuut.txt"
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


if __name__ == '__main__':
    #addressSort()
    #openTest()
    makeListTest()
    #LoggingTest()
    #LoggingTest2()
