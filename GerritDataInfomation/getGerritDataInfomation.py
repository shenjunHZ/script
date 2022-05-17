#! Python3
import getopt
import sys
from GerritOperation import GerritOperation

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def getData(host, port, cmd):
    gerritOperation = GerritOperation(host, port)
    data = gerritOperation.getChanges(cmd)
    return data

def parseInputParams(opts):
    global commitFile
    result = False
    for op, value in opts:
        if "-h" == op or "--help" == op:
            print("use --file code file name")
            sys.exit()
        elif "-f" == op or "--file" == op:
            commitFile = value
            print("fetch commit file: %s" % (commitFile))
            result = True
        else:
            print("for help use --help")
            sys.exit()
    return result

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hf:", ["help", "file="])
            result = parseInputParams(opts)
            if result:
                cplaneChanges = getData('gerrit.ext.net.nokia.com', 29418, 'project:MN/5G/NB/gnb' + ' file:' + str(commitFile))
        except getopt.error:
            msg = getopt.error
            raise Usage(msg)       
        print("===========================segmentation============================")
    except Usage:
        err = Usage
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2    


if __name__ == '__main__':
    sys.exit(main())