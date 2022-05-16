#! python3

"""
@copyright jun shen
"""
import zipfile
import tarfile
import lzma
import os
import sys
import getopt
import shutil
import string
import time
import glob

###global params###
#input absolute zip file for decompression
inputFile=""    
#input file absolute path
inputFilePath=""
#input file name contain file type
inputFileName=""
#passWord if needed
passWord=""
#decompression path
outputPath="."
#when paht to deep will move to this path then decompression
movePath="."
#search path for Control Plane logs collect
searchPath="."
#collect Control Plane logs path
collectPath="."
#when value > 1 need to move source zip file
needDelete=0
###class###
class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

class DecompressionArchive(object):
    """decompression zip file"""

    def __init__(self, extractDir):
        """
            @extractDir: output files after decompression
        """
        self.extractDir = extractDir

    def run(self):
        if inputFileName.endswith(".zip"):
            # create dir
            global movePath
            global collectPath
            os.mkdir(os.path.join(self.extractDir, inputFileName[:-4]))
            movePath = os.path.join(self.extractDir, inputFileName[:-4]) + "\\moves"
            collectPath = os.path.join(self.extractDir, inputFileName[:-4]) + "\\Control-Plane-logs"
            #os.mkdir(movePath)
            #os.mkdir(collectPath)
            zipFile = os.path.join(inputFilePath, inputFileName)
            file = os.path.splitext(inputFileName)
            name,type = file
            unZipFolder = os.path.join(self.extractDir, name)
            #self.decompressionScrambling(zipFile, unZipFolder)
            self.extractZip(zipFile, unZipFolder)
            self.collectControlPlaneLogs()
        else:
            print("not zip file.")

    def collectControlPlaneLogs(self):
        global collectPath
        global searchPath
        for cpRoot,cpDirs,cpFiles in os.walk(searchPath):
            for cpDir in cpDirs:
                if (0 < cpDir.find("-cpcl-") or 0 < cpDir.find("-cpif-")
                    or 0 < cpDir.find("-cpnb-") or 0 < cpDir.find("-cpue-") 
                    or 0 < cpDir.find("-cpnrt-")):
                    absPath = os.path.abspath(os.path.join(cpRoot, cpDir))
                    for root,dirs,files in os.walk(absPath):
                        for dir in dirs:
                            if(0 == dir.find("syslog_info")):
                                print("collect: %s" %(absPath))
                                dstPath = os.path.join(collectPath, cpDir)
                                shutil.copytree(absPath, dstPath)
                if (0 < cpDir.find("E05F_pm") or 0 < cpDir.find("E051_pm")
                    or 0 < cpDir.find("E050_pm") or 0 < cpDir.find("E060_pm")
                    or 0 < cpDir.find("E070_pm")):
                    absPath = os.path.abspath(os.path.join(cpRoot, cpDir))
                    print("collect: %s" %(absPath))
                    dstPath = os.path.join(collectPath, cpDir)
                    shutil.copytree(absPath, dstPath)
                if (cpDir.endswith("E05F_startup") or cpDir.endswith("E05F_runtime")):
                    absPath = os.path.abspath(os.path.join(cpRoot, cpDir))
                    print("collect: %s" %(absPath))
                    dstPath = os.path.join(collectPath, cpDir)
                    shutil.copytree(absPath, dstPath)
                if (cpDir.endswith("1011_runtime") or cpDir.endswith("1021_runtime")
                    or cpDir.endswith("1011_startup") or cpDir.endswith("1021_startup")):
                    absPath = os.path.abspath(os.path.join(cpRoot, cpDir))
                    print("collect: %s" %(absPath))
                    dstPath = os.path.join(collectPath, cpDir)
                    shutil.copytree(absPath, dstPath)
                if (0 < cpDir.find("1011_pm_") or 0 < cpDir.find("1021_pm_")):
                    absPath = os.path.abspath(os.path.join(cpRoot, cpDir))
                    print("collect: %s" %(absPath))
                    dstPath = os.path.join(collectPath, cpDir)
                    shutil.copytree(absPath, dstPath)
                if (cpDir.endswith("E002_startup") or cpDir.endswith("E003_startup")
                    or cpDir.endswith("E004_startup") or cpDir.endswith("E005_startup")
                    or cpDir.endswith("E007_startup") or cpDir.endswith("E008_startup")
                    or cpDir.endswith("E002_runtime") or cpDir.endswith("E003_runtime")
                    or cpDir.endswith("E004_runtime") or cpDir.endswith("E005_runtime")
                    or cpDir.endswith("E007_runtime") or cpDir.endswith("E008_runtime")):
                    absPath = os.path.abspath(os.path.join(cpRoot, cpDir))
                    print("collect: %s" %(absPath))
                    dstPath = os.path.join(collectPath, cpDir)
                    shutil.copytree(absPath, dstPath)
                if (0 < cpDir.find("E002_pm_") or 0 < cpDir.find("E003_pm_")
                    or 0 < cpDir.find("E004_pm_") or 0 < cpDir.find("E005_pm_")
                    or 0 < cpDir.find("E007_pm_") or 0 < cpDir.find("E008_pm_")):
                    absPath = os.path.abspath(os.path.join(cpRoot, cpDir))
                    print("collect: %s" %(absPath))
                    dstPath = os.path.join(collectPath, cpDir)
                    shutil.copytree(absPath, dstPath)

    def progressBar(self, processIndex, totalIndex):
        getProgress = int((processIndex + 1) * (50 / totalIndex))
        getValue = int(50 - getProgress)
        percent = (processIndex + 1) * (100 / totalIndex)
        print("\r"+"["+">"*getProgress+"-"*getValue+']'+"%.2f" % percent + "%",end=""+"\r")

    def copyFile(self, srcFile, dstFile):
        if not os.path.isfile(srcFile):
            print("source %s not exist!!!" % (srcFile))
        elif os.path.exists(dstFile):
            print("target %s have exist!!!" % (dstFile))
        else:
            shutil.copyfile(srcFile, dstFile)

    def printCoding(self, f):
        print ("%s.%s(): %s" % (f.__module__, f.__name__, f()))

    def decompressionScrambling(self, scramblingFile, desPath):
        executeCmd = '\"D:\\Program Files\\7-Zip\\7z.exe\" x -tzip \"{0}\" -pf0162cb946205b024bb38ec04ec892ea -o' + desPath + ' -r'
        cmd = executeCmd.format(scramblingFile)
        os.popen(cmd)
        print("==============%s" %(cmd))
        time.sleep(1)
        paths = glob.glob(desPath + '\**',recursive=True)
        fileList = []
        fileList.append(paths)

    def extractZip(self, zipFile, folderPath):
        """
            @recursion extract zip file
        """
        #print("========zipfile: %s" %(zipFile))
        #print("========folderPath: %s" %(folderPath))
        # decompression
        #shutil.unpack_archive(zipFile, folderPath)
        global passWord
        global needDelete
        try:
            if zipFile.endswith(".zip"):
                zipT = zipfile.ZipFile(zipFile, 'r', allowZip64=True)
                if(0 == needDelete and "" != passWord):
                    try:
                        print("password: %s" % (passWord.encode("utf8")))
                        self.printCoding(sys.getdefaultencoding)
                        self.printCoding(sys.getfilesystemencoding)
                        zipT.extractall(folderPath, pwd=passWord.encode("utf8"))
                        zipT.close()
                    except Exception as ex:
                        print(ex)
                else:
                    zipT.extractall(folderPath)
                    zipT.close()
            elif zipFile.endswith(".xz"):
                fileName = os.path.basename(zipFile)
                file = os.path.splitext(fileName)
                name,type = file
                outputFile = os.path.join(folderPath, name)
                with lzma.open(zipFile, "rb") as input:
                    with open(outputFile, "wb") as output:
                        shutil.copyfileobj(input, output)
            # delete zip file
            #print("============= %d" % (needDelete))
            if (0 == needDelete % 10):
                #print(".................................")
                self.progressBar(needDelete, 800)
            if needDelete >= 1:
                os.remove(zipFile)
            needDelete = needDelete + 1
        # recursion
        except (FileExistsError, FileNotFoundError) as e:
            print("\r\n" + "move to moves directory as: %s" % (e))
            global movePath
            os.mkdir(movePath)
            fileName = os.path.basename(zipFile)
            dstFile = os.path.join(movePath, fileName)
            if (not os.path.exists(dstFile)):
                self.copyFile(zipFile, dstFile)

                for root,dirs,files in os.walk(movePath):
                    for filename in files:
                        if filename.endswith(".zip") or filename.endswith(".xz"):
                            file = os.path.splitext(filename)
                            name,type = file
                            path = os.path.abspath(os.path.join(root, name))
                            if(not os.path.exists(os.path.join(root, name) )):
                                os.mkdir(os.path.join(root, name))

                            moveFolderPath = os.path.join(root, name)
                            moveZipFile = os.path.join(root, filename)
                            self.extractZip(moveZipFile, moveFolderPath)
        else:
            for root,dirs,files in os.walk(folderPath):
                for filename in files:
                    if filename.endswith(".zip") or filename.endswith(".xz"):
                        file = os.path.splitext(filename)
                        name,type = file
                        #print("============== %s " %(filename))
                        path = os.path.abspath(os.path.join(root, name))
                        countPath = path.count('\\')
                        #print("==============absolute path: %s" % (path))
                        #print("==============path number: %d" % (countPath))
                        os.mkdir(os.path.join(root, name))
                        folderPath = os.path.join(root, name)
                        zipFile = os.path.join(root, filename)
                        self.extractZip(zipFile, folderPath)

###function###
def parseInputParams(opts):
    global inputFile
    global outputPath
    global movePath
    global passWord
    for op, value in opts:
        if "-h" == op or "--help" == op:
            print("use --file fileName -o outputPath")
            sys.exit()
        elif "-f" == op or "--file" == op:
            inputFile = value
            print("input path file: %s" % (inputFile))
        elif "-o" == op or "--output" == op:
            outputPath = value
        elif "-p" == op or "--password" == op:
            passWord = value
        else:
            print("for help use --help")
            sys.exit()

def checkFile(fileName):
    global inputFilePath
    global inputFileName
    global searchPath
    inputFileName = os.path.basename(fileName)
    inputFilePath = os.path.dirname(fileName)

    file = os.path.splitext(inputFileName)
    name,type = file
    print("file type: %s" % (type))
    print("file name: %s" % (name))
    searchPath = outputPath + "\\" + name
    if ".zip" != type:
        print("file not correct.")
        sys.exit()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hf:o:p:", ["help", "file=", "output=", "password"])
            parseInputParams(opts)
            checkFile(inputFile)
            archive = DecompressionArchive(outputPath)
            archive.run()
            print("==========================")
            print("Decompression Complate !!!")
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