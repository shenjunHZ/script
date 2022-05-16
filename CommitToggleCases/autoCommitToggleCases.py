#! python3
import getopt
import os
import re
import subprocess
import sys
import json

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

class DecoderJsonArchive(object):
    """decoder json file"""

    def __init__(self, extractDir):
        """
            @extractDir: output files
        """
        self.extractDir = extractDir

    def run(self):
        if inputFileName.endswith(".json"):
            jsonFile = os.path.join(inputFilePath, inputFileName)
            file = os.path.splitext(inputFileName)
            name,type = file
            jsonFolder = os.path.join(self.extractDir, name)
            #get toggle case from json file
            jsonDatas = self.readJson(jsonFile, jsonFolder)
            toggleDatas = self.filterJsonDataForToggle(jsonDatas)
            #add toggle tag to sct case
            absFileNames = self.searchAndChangeToggleCase(toggleDatas)
            if len(absFileNames):
                self.commitCodeChange(absFileNames)
        else:
            print("Not json file!!!")

    def commitCodeChange(self, absFileNames):
        print("commit code path: ", codePath)
        #for absFileName in absFileNames:
        #    subprocess.check_call('git add %s' %absFileName, cwd=codePath)
        #subprocess.check_call('git commit -m "[none] fix unstable cases"', cwd=codePath)
        #subprocess.check_call('git push origin HEAD:refs/for/master', cwd=codePath)
        #for linux
        #subprocess.check_call('git add .', cwd=codePath, shell=True)
        #subprocess.check_call('git commit -m "[none] fix unstable cases"', cwd=codePath, shell=True)
        #subprocess.check_call('git push origin HEAD:refs/for/master', cwd=codePath, shell=True)

    def searchAndChangeToggleCase(self, toggleDatas):
        absFileNames = []
        for toggleData in toggleDatas:
            data = toggleData.split('.', 1)
            toggleFile = data[0] + ".ttcn3"
            caseName = data[1] + "("
            absFileName = self.getSpecialFile(toggleFile)   
            if(len(absFileName) > 1):
                print("Toggle file path: %s, case name: %s" %(absFileName, caseName))
                caseLine = self.getSpecialCaseLine(absFileName, caseName)
                if caseLine > 2:
                    self.setUnstableTag(absFileName, caseLine)
                    absFileNames.append(absFileName)
        return absFileNames

    def setUnstableTag(self, absFileName, caseLine):
        lines = []
        file = open(absFileName, "r")
        for line in file:
            lines.append(line)
        tagLine = caseLine
        maxline = 5
        while not self.getInsertTagLine(lines[tagLine]) and maxline > 0:
            tagLine = tagLine - 1
            maxline = maxline - 1
        unstable = "@unstable"
        if not unstable in lines[tagLine -1]:
            lines.insert(tagLine, "    * @unstable heavily unstable case\n")
        file.close()
        
        with open(absFileName, "w") as f:
            for line in lines:
                f.write(line)
            f.close()

    def getInsertTagLine(self, line):
        caseLine = "*/"
        if caseLine in line:
                return True
        return False

    def getSpecialCaseLine(self, absFileName, caseName):
        caseLine = 0
        fileRead = open(absFileName, 'r')
        #for line in fileRead.readlines():
        for (num, line) in enumerate(fileRead):
            if caseName in line:
                fileRead.close()
                return num
        fileRead.close()
        return caseLine

    def getSpecialRequirementLine(self, absFileName, caseLine):
        requirementLine = caseLine - 1
        searchLine = 10
        file = open(absFileName)
        while searchLine > 0:
            result = re.findall("*/", requirementLine)
            if result.count() > 1:
                file.close()
                return requirementLine
            requirementLine = requirementLine -1
        file.close()
        return 0

    #based on code path find toggle ttcn3 file
    def getSpecialFile(self, toggleFile):
        if ':' in toggleFile:
            return toggleFile
        absPath = ''
        while len(toggleFile) > 1:
            #p = os.path.abspath(cp)
            yid = os.walk(codePath)
            for rootDir, pathList, fileList in yid:
                for file in fileList:
                    if os.path.sep in toggleFile:
                        fp = os.path.join(rootDir, toggleFile)
                        if toggleFile in fp or toggleFile in fp.lower():
                            absPath = os.path.join(rootDir, fp)
                            return absPath
                    else:
                        if toggleFile == file or toggleFile == file.lower():
                            absPath = os.path.join(rootDir, file)
                            return absPath

        print("not find special file: '%s'.", toggleFile)
        return absPath

    def readJson(self, jsonFile, folderPath):
        """
            @read json file
        """
        #global jsonDatas
        print("jsonfile: %s" %(jsonFile))
        #process json file
        with open(jsonFile, 'r') as loadfile:
            loadDict = json.load(loadfile)
            #print(loadDict)

        jsonDatas = loadDict['data']
        return jsonDatas

    def filterJsonDataForToggle(self, jsonDatas):
        toggleDatas = []
        #json items in data
        for jsonData in jsonDatas.items():
            #tuple object
            value = jsonData[1]
            toggles3 = value['toggles3']
            if(toggles3 > 5):
                toggleDatas.append(value['name'])
        print("Toggle case file: ", toggleDatas)
        return toggleDatas

###function###
def parseInputParams(opts):
    global inputFile
    global codePath
    global passWord
    for op, value in opts:
        if "-h" == op or "--help" == op:
            print("use --file fileName -c codePath")
            sys.exit()
        elif "-f" == op or "--file" == op:
            inputFile = value
            print("input path file: %s" % (inputFile))
        elif "-c" == op or "--code" == op:
            codePath = value
        elif "-p" == op or "--password" == op:
            passWord = value
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
    if ".json" != type:
        print("file not correct.")
        sys.exit()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hf:c:p:", ["help", "file=", "code=", "password"])
            parseInputParams(opts)
            checkFile(inputFile)

            archive = DecoderJsonArchive("")
            print("Decoder json file to commit Complate !!!")
            archive.run()
            print("===========================segmentation============================")
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