import sys
packagesPath = "C:/RootPath/Packages"
if packagesPath not in sys.path:
  sys.path.append(packagesPath)
import csv
import getopt
import os
import pandas
import numpy


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

class CounterArchive(object):
    """achive counter file"""

    def __init__(self, inputfile, extractDir):
        """
            @extractDir: output files after achive
        """
        self.inputfile = inputfile
        self.extractDir = extractDir
        self.filterKey=[]
        self.filterData=[]
        self.filterDic = {}

    def splitStringInfo(self, stringInfo):
        subStringInfo = stringInfo.split(';')
        for subString in subStringInfo:
            if "rt_" in subString:
                return subString

    def run(self, keyword):
        #read csv
        csv_read = pandas.read_csv(self.inputfile)
        #将csv文件读入的内容转为列表，一行为一个列表，目前实际只有一列
        csv_read_array=numpy.array(csv_read)
        
        for item in csv_read_array:
            stringInfo = item[0] 
            if len(keyword) != 0:
                if keyword in stringInfo:
                    #self.filterData.append(item)
                    self.filterDic.setdefault(keyword,[]).append(item)

            elif len(keyword) == 0:
                caseName = self.splitStringInfo(stringInfo)
                if self.filterKey.count(caseName) >= 1 :
                    self.filterDic.setdefault(caseName,[]).append(item)
                else:
                    self.filterKey.append(caseName)
                    self.filterDic.setdefault(caseName,[]).append(item)


    def createCSVFile(self):
        '''
        fetch csv file
        '''

        for key in self.filterDic.keys():
            #数据转为可按列写入csv文件的列表
            counter=[i[0] for i in self.filterDic[key]]
            #将筛选出来的数据重新写入新的csv文件
            rows = zip(counter)
            with open(os.path.join(inputFilePath, key+'.csv'), "w", newline='') as f:
                writer = csv.writer(f)
                csvrow1 = []
                csvrow1.extend('counter')
                writer.writerows(rows)

##############################Function###########################
def parseInputParams(opts):
    global inputFile
    global keyWord
    keyWord = ""
    for op, value in opts:
        if "-h" == op or "--help" == op:
            print("use --file fileName -k used key word")
            sys.exit()
        elif "-f" == op or "--file" == op:
            inputFile = value
            print("csv file: %s" % (inputFile))
        elif "-k" == op or "--key" == op:
            keyWord = value
            print("filter key: %s" % (keyWord))
        else:
            print("for help use --help")
            sys.exit()

def checkFile(fileName):
    global inputFilePath
    global inputFileName
    inputFileName = os.path.basename(fileName)
    inputFilePath = os.path.dirname(fileName)

    file = os.path.splitext(inputFileName)
    name,type = file
    print("file type: %s" % (type))
    print("file name: %s" % (name))
    if ".csv" != type:
        print("file not correct.")
        sys.exit()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts,args = getopt.getopt(argv[1:], "-h-f:-k:", ["help", "key", "file"])
            parseInputParams(opts)
            checkFile(inputFile)
            archive = CounterArchive(inputFile, inputFilePath)
            archive.run(keyWord)
            archive.createCSVFile()
            print("===========================================================")
            print("Generate Complate !!!")
        except getopt.error:
            msg = getopt.error
            raise Usage(msg)
    except Usage:
        err = Usage
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == '__main__':
    sys.exit(main())
