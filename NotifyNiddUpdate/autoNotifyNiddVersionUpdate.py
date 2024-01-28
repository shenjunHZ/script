#! python3
import getopt
import os
import sys
import subprocess
import win32com.client as win32
import configparser
import time

###Object###
class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

class GitOperationArchive(object):
    """operation git repository"""

    def __init__(self, extractDir):
        self.extractDir = extractDir

    def run(self):
        if os.path.exists(self.extractDir):
            print("git repository path: %s." %self.extractDir)
        else:
            print("Git path invalide!!!")

    def searchCurrentFile(self, fileKey):
        for root, dirs, files in os.walk(self.extractDir):
            for file in files:
                if fileKey in file:
                    return file
                    print(file)
        return ""

    def pullCodeChange(self):
        print("pull code path: ", codePath)
        subprocess.check_call('git pull --rebase"', cwd=codePath)

class EmilArchive(object):
    """operation emil"""
    def __init__(self, title, message, receiver):
        self.title = title
        self.message = message
        self.receiver = receiver

    def sendEmil(self):
        outlook = win32.Dispatch("outlook.Application")
        #mail = outlook.CreateItem(win32.constants.olMailItem)
        mail = outlook.CreateItem(0)
        mail.To = self.receiver
        mail.Subject = self.title
        #mail.Body = self.message
        mail.HTMLBody = '''\
            <html>
            <head></head>
            <body>
            <p>Hello, Master branch nidd update.
            <font color ='blue'>
            <br><body> ''' + str(self.message) + ''' </br></body>
            </font>
            <br></br>
            <font color ='red'>
                Please note this is an automated mail do not reply.<t1>
            </font>
             </p>
            </body>
            </style>
            </html>
            '''
        mail.Send()

###function###
def parseInputParams(opts):
    global configFile
    global codePath
    result = False
    for op, value in opts:
        if "-h" == op or "--help" == op:
            print("use --path codePath")
            sys.exit()
        elif "-c" == op or "--config" == op:
            configFile = value
            print("config path file: %s" % (configFile))
        elif "-p" == op or "--path" == op:
            codePath = value
            result = True
        else:
            print("for help use --help")
            sys.exit()
    return result

def parseConfigFile():
    config = configparser.ConfigParser()
    filePath = os.path.join(os.getcwd() + "\\NotifyNiddUpdate", configFile)
    config.read(filePath)
    receiver = config.get('mail', 'receiver')
    return receiver

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hc:p:", ["help", "config=", "path="])
            result = parseInputParams(opts)
            if result:
                archive = GitOperationArchive(codePath)
                archive.run()
                fileKey = "CMProductRelease_XML_SBTS5GCP"
                localFile = archive.searchCurrentFile(fileKey)
                archive.pullCodeChange()
                updateFile = archive.searchCurrentFile(fileKey)            
                if updateFile != localFile:
                    reveiver = parseConfigFile()
                    emilArchive = EmilArchive("Auto send for nidd update!!!", updateFile, reveiver)
                    emilArchive.sendEmil()
            print("===========================segmentation============================")
            time.sleep(3)
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