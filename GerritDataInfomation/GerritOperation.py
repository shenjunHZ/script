
#! python3
from datetime import datetime, date, timedelta
from json import JSONDecoder
from ModelChanges import Change
import os

class GerritOperation(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.max_records = 10000000
        self.loop_size = 100
        self.openChanges = []
        self.mergedChanges = []
        self.changes = []

    def fetchSingleRawData(self, cmd):
        results = []
        try:
            print ("[INFO] Executing: " + cmd)
            r = os.popen(cmd).read()
            for l in r.splitlines():
                results.append(JSONDecoder().decode(l))
        except:
            print("[ERR] the command failed")
        return results

    def fetch(self, cmd_ext):
        results = []
        #--format=TEXT default , --format=JSON
        #--current-patch-set
        #--patch-sets, all patch set information
        #--comments
        #--commit-message, the change's commit message
        #[--all-reviewers] --all reviewer's name and email
        #[--start <n> | -S <n>]  --Number of changes to skip
        #[limit:<n>] --limit the number of the result

        #age:'AGE' 可查询给定时间之前的change信息，如 age：1d 即为查询1天前的所有change信息，以change的最后更新时间为基准
        #projects:'xx' 查询项目名以xx开头的所有项目的chage信息
        #branch:'BRANCH' 查询指定分支的change信息
        #status：xxx 查询指定状态的change
        #file: xxx 指定文件
        #after:'TIME'/since:'TIME' 
        #Changes modified after the given 'TIME', inclusive. Must be in the format 2006-01-02[ 15:04:05[.890][ -0700]]; 
        #omitting the time defaults to 00:00:00 and omitting the timezone defaults to UTC.
        basicCmd = 'ssh -p %d %s gerrit query --format JSON --current-patch-set --files' \
                    % (self.port, self.host)
        since = date.today() - timedelta(days = 3)

        for start in range(0, self.max_records, self.loop_size):
            r = self.fetchSingleRawData(basicCmd + ' --start ' + str(start) + ' limit:' + str(self.loop_size) + ' since: ' + str(since) + cmd_ext)
            s = len(r)
            if s:
                results += r[:-1]
                if ("moreChanges", False) in r[s - 1].items():
                    break
            else:
                break
        return results

    def fetchAll(self, cmd_ext):
        #r1 = self.fetch(' status:open ' + cmd_ext)
        #print "[INFO] Fetch open records with size of " + str(len(r1))
        #self.openChanges = modelChanges(r1)
        #self.changes.extend(self.openChanges)

        result = self.fetch(' status:merged ' + cmd_ext)
        print ("[INFO] Fetch merged records with size of " + str(len(result)))
        self.mergedChanges = self.modelChanges(result)
        self.changes.extend(self.mergedChanges)

    def modelChanges(self, json_data):
        results = []
        for data in json_data:
            results.append(Change(data))
        return results

    def getChanges(self, cmd):
        self.fetchAll(cmd)
        return self.changes
