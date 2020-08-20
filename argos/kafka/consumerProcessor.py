import pydoc


class ConsumerProcessor(object):
    _consumer = None
    _process = None
    _processArgs = None

    @property
    def consumer(self):
        return self._consumer

    @property
    def process(self):
        return self._process

    @property
    def processArgs(self):
        return self._processArgs

    def __init__(self, consumer, process, **processArgs):
        self._consumer = consumer
        self._process = process
        self._processArgs = processArgs

    def start(self):
        pydoc.locate(self._process)(self.consumer, **self.processArgs)
