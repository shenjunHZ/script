from datetime import datetime
import time
import re

def _convert_timestamp_to_datetime(format, value):
    value = time.localtime(value)
    dt = time.strftime(format, value)
    return dt

def from_json(json_data, key):
    
    """ Models for Gerrit JSON data. """

    if key in json_data:
        return json_data[key]
    return None

class Change(object):
    """ Gerrit change. """

    def __init__(self, json_data):
        self.project = from_json(json_data, "project")
        self.branch = from_json(json_data, "branch")
        self.topic = from_json(json_data, "topic")
        self.change_id = from_json(json_data, "id")
        self.number = from_json(json_data, "number")
        self.subject = from_json(json_data, "subject")
        self.url = from_json(json_data, "url")
        self.owner = Account.from_json(json_data, "owner")
        self.status = from_json(json_data, "status")
        self.open = from_json(json_data, "open")
        self.currentPatchset = CurrentPatchset.from_json(json_data)
        self.patchSets = Patchsets.from_json(json_data)
        self.createdOn = from_json(json_data, "createdOn")
        self.lastUpdated = from_json(json_data, "lastUpdated")
        self.upAndCpComponent = UpAndCpComponent()
        self.isHanging = 'n'
        self.hangingDays = 0
        self.commentNum = 0
        self.codeModifiedLines = 0
        self.utModifiedLines = 0
        self.sctModifiedLines = 0
        self.fakeCodeDeletions = 0
        self.fakeCodeInsertions = 0
        self.noTworeviewPlusOne = 'n'
        self.plane = 'n'
        self.selfApproval = 'n'
        self.noGuardReview = 'n'
        self.isRevert = 'n'
        self.reviewers = []
        self.parseReviwersInfo(json_data)
        self.calOpenDay()
        self.getChangeFeature()
    
    def getInsertions(self):
        if self.currentPatchset:
            if self.currentPatchset.insertions:
                return self.currentPatchset.insertions - self.fakeCodeInsertions
        return 0

    def getDeletions(self):
        if self.currentPatchset:
            if self.currentPatchset.deletions:
                return self.currentPatchset.deletions - self.fakeCodeDeletions
        return 0

    def calOpenDay(self):
        delta = datetime.now() - datetime.fromtimestamp(self.createdOn)
        if(self.open == True) and (delta.days > 7):
            self.isHanging = "y"
            self.hangingDays = delta.days
        
    def parseReviwersInfo(self, json_data):
        comments = []
        approvals = []
        if self.currentPatchset:
            approvals = self.currentPatchset.approvals
        for p in self.patchSets.patchSet:
            comments.extend(p.comments)
        self.commentNum = len(comments)
        if "allReviewers" in json_data:
            for a in json_data["allReviewers"]:
                if ("username", "c_lteulm") not in a.items():
                        self.reviewers.append(Reviwer(Account(a), comments, approvals))
    
    def getChangeFeature(self):
        featureId = re.search("^\[5GC.*\]", self.subject)
        if featureId is None:
            self.featureId = 'none'
        else:
            tmp = featureId.group()
            temp = tmp.split(']')[0].split('-')
            if len(temp) > 1:
                self.featureId = temp[0] + '-' + temp[1] + ']'
            else:
                self.featureId = temp[0] + ']'

class Account(object):

    """ Gerrit user account (name and email address). """

    def __init__(self, json_data):
        self.name = from_json(json_data, "name")
        self.email = from_json(json_data, "email")
        self.username = from_json(json_data, "username")

    @staticmethod
    def from_json(json_data, key):
        if key in json_data:
            return Account(json_data[key])
        return None

class Reviwer(object):
    def __init__(self, account, comments, approvals):
        self.account = account
        self.role = ""
        self.commentCD = {}
        if approvals:
            for a in approvals:
                if a.approver.name == self.account.name and a.category == 'Code-Review':
                    self.role = "Review+" + a.value
        if comments:
            for c in comments:
                if c.reviewer.name == self.account.name:
                    yearMonthDay = _convert_timestamp_to_datetime('%Y-%m-%d', c.createdOn)
                    if self.commentCD.has_key(yearMonthDay):
                        self.commentCD[yearMonthDay] += 1
                    else:
                        self.commentCD[yearMonthDay] = 1

class Patchset(object):

    """ Gerrit patch set. """

    def __init__(self, json_data):
        self.number = from_json(json_data, "number")
        self.revision = from_json(json_data, "revision")
        self.deletions = from_json(json_data, "sizeDeletions")
        self.insertions = from_json(json_data, "sizeInsertions")
        self.ref = from_json(json_data, "ref")
        self.uploader = Account.from_json(json_data, "uploader")
        self.author = Account.from_json(json_data, "author")
        self.createdOn = from_json(json_data, "createdOn")
        self.comments = []
        if "comments" in json_data:
            for comment in json_data["comments"]:
                reviewer = Account.from_json(comment, "reviewer")
                if reviewer.name != self.uploader.name:
                    self.comments.append(Comment(comment, self.createdOn, reviewer))

    @staticmethod
    def from_json(json_data):
        if "patchSet" in json_data:
            return Patchset(json_data["patchSet"])
        return None

class Patchsets():
    
    def __init__(self, json_data):
        self.patchSet = []
        for j in json_data:
            temp = Patchset(j)
            self.patchSet.append(temp)
        self.number = len(self.patchSet)

    @staticmethod
    def from_json(json_data):
        if "patchSets" in json_data:
            return Patchsets(json_data["patchSets"])
        return None


class CurrentPatchset(Patchset):

    """ Gerrit current patch set. """

    def __init__(self, json_data):
        super(CurrentPatchset, self).__init__(json_data)
        self.author = Account.from_json(json_data, "author")
        self.approvals = []
        self.modifiedFiles = []
        if "files" in json_data:
            for modifiedFile in json_data["files"]:
                self.modifiedFiles.append(ModifiedFiles(modifiedFile))
        if "approvals" in json_data:
            for approval in json_data["approvals"]:
                self.approvals.append(Approval(approval))

    @staticmethod
    def from_json(json_data):
        if "currentPatchSet" in json_data:
            return CurrentPatchset(json_data["currentPatchSet"])
        return None


class Comment(object):

    """ Gerrit patch set. """

    def __init__(self, json_data, createdOn, reviewer):
        self.file = from_json(json_data, "file")
        self.message = from_json(json_data, "message")
        self.reviewer = reviewer
        self.createdOn = createdOn

class Approval(object):

    """ Gerrit approval (verified, code review, etc). """

    def __init__(self, json_data):
        self.category = from_json(json_data, "type")
        self.value = from_json(json_data, "value")
        self.description = from_json(json_data, "description")
        self.grantedOn = from_json(json_data, "grantedOn")
        self.approver = Account.from_json(json_data, "by")

class ModifiedFiles(object):

    """ Gerrit modifiedFiles. """

    def __init__(self, json_data):
        self.fileName = from_json(json_data, "file")
        self.type = from_json(json_data, "type")
        self.insertions = from_json(json_data, "insertions")
        self.deletions = from_json(json_data, "deletions")
        self.codeType = 'none'
        self.component = 'none'
        self.selectCodeType()
        self.selectComponent()
    
    def selectCodeType(self):
        if self.fileName != '/COMMIT_MSG':
            r1 = re.compile(".*\/ut\/.*", re.I)
            r2 = re.compile(".*\/sct\/.*", re.I)
            r3 = re.compile("^l2_l3_test.*\.asn", re.I)
            r4 = re.compile("^l2_l3_test.*\.erl", re.I)
            r5 = re.compile("^l2_l3_test.*\.hrl", re.I)
            if r3.match(self.fileName) or r4.match(self.fileName) or r5.match(self.fileName):
                self.codeType = 'fake'
            elif r2.match(self.fileName):
                self.codeType = 'sct'
            elif r1.match(self.fileName):
                self.codeType = 'ut'
            else:
                self.codeType = 'code'
    
    def selectComponent(self):
        if self.fileName != '/COMMIT_MSG':
            c1 = re.compile(".*uplane\/L2-PS\/.*")
            c2 = re.compile(".*uplane\/L2-HI\/.*")
            c3 = re.compile(".*uplane\/L2-LO\/.*")
            c4 = re.compile(".*cplane\/CP-NRT\/.*")
            c5 = re.compile(".*cplane\/CP-RT\/.*")
            c6 = re.compile(".*cplane\/cu\/cp_if\/.*")
            c7 = re.compile(".*cplane\/cu\/cp_nb\/.*")
            c8 = re.compile(".*cplane\/cu\/tests\/cp_if\/.*")
            c9 = re.compile(".*cplane\/cu\/tests\/cp_nb\/.*")
            c10 = re.compile(".*uplane\/sct\/tickler\/cpp_testsuites\/l2hi.*")
            c11 = re.compile(".*uplane\/sct\/tickler\/cpp_testsuites\/l2lo.*")
            c12 = re.compile(".*uplane\/sct\/tickler\/cpp_testsuites\/l2ps.*")
            if c1.match(self.fileName) or c12.match(self.fileName):
                self.component = 'l2ps'
            elif c2.match(self.fileName) or c10.match(self.fileName):
                self.component = 'l2hi'
            elif c3.match(self.fileName) or c11.match(self.fileName):
                self.component = 'l2lo'
            elif c4.match(self.fileName):
                self.component = 'cpnrt'
            elif c5.match(self.fileName):
                self.component = 'cprt'
            elif c6.match(self.fileName) or c8.match(self.fileName):
                self.component = 'cpif'
            elif c7.match(self.fileName) or c9.match(self.fileName):
                self.component = 'cpnb'

class UpAndCpComponent(object):
    
    """up and cp component modified Lines"""

    def __init__(self):
        self.l2ps = ComponentCodeModifiedLines()
        self.l2lo = ComponentCodeModifiedLines()
        self.l2hi = ComponentCodeModifiedLines()
        self.cprt = ComponentCodeModifiedLines()
        self.cpnrt = ComponentCodeModifiedLines()
        self.cpnb = ComponentCodeModifiedLines()
        self.cpif = ComponentCodeModifiedLines()
    
    def setData(self, component, codeType, number):
        if component == 'l2ps':
            self.l2ps.setData(codeType, number)
        elif component == 'l2lo':
            self.l2lo.setData(codeType, number)
        elif component == 'l2hi':
            self.l2hi.setData(codeType, number)
        elif component == 'cprt':
            self.cprt.setData(codeType, number)
        elif component == 'cpnrt':
            self.cpnrt.setData(codeType, number)
        elif component == 'cpnb':
            self.cpnb.setData(codeType, number)
        elif component == 'cpif':
            self.cpif.setData(codeType, number)
    
class ComponentCodeModifiedLines(object):

    """modified lines per component"""

    def __init__(self):
        self.code = 0
        self.ut = 0
        self.sct = 0
        self.all = 0

    def setData(self, codeType, number):
        if codeType == 'sct':
            self.sct += number
            self.all += number
        elif codeType == 'ut':
            self.ut += number
            self.all += number
        elif codeType == 'code':
            self.code += number
            self.all += number
