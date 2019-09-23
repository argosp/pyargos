from collections.abc import Iterable
from itertools import zip_longest
import os
from ..experimentManagement import Experiment


def andClause(excludelist =[],**filters):
    L  =[]
    for key,value in filters.items():
        if key in excludelist:
            continue
        if isinstance(value,str):
            L.append("%s == '%s' " % (key,value))
        else:
            predicate = "in" if isinstance(value,Iterable) else " == "
            L.append("%s %s %s" % (key,predicate,value))

    return " and ".join(L)

class abstractReport(object):

    _jinjaEnv = None
    _templateName = None

    _outpath = None
    _outName = None

    @property
    def outPath(self):
        return self._outPath

    @property
    def outName(self):
        return self._outName

    @property
    def templateName(self):
        return self._templateName

    @property
    def trialsProperties(self):
        return self._trialsProperties

    @property
    def trialsEntities(self):
        return self._trialsEntities

    @property
    def jinjaEnv(self):
        return self._jinjaEnv

    def __init__(self, templateName, outName, expConf, jinjaEnv, outPath):
        self._jinjaEnv =  jinjaEnv
        self._templateName = templateName
        self._outPath = outPath
        self._outName = outName
        self._exp = Experiment(expConf)
        self._trialsProperties = self._exp.getTrials()
        self._trialsEntities = self._exp.getTrialsEntities()

    def _create(self):
        raise NotImplementedError("Must implement in child")

    def makeReport(self):
        metaData = self._create()
        print(metaData)
        ###
        template = self.jinjaEnv.get_template('%s.tex' % self.templateName)
        rendered_tex = template.render(metaData=metaData,enumerate=enumerate,len=len,zip_longest=zip_longest)

        with open(os.path.join(self.outPath,"%s.tex" % self.outName), 'w') as outFile:
            outFile.write(rendered_tex)




