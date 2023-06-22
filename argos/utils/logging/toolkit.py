import logging
import pathlib
from hera.datalayer import datatypes
from hera.toolkit import abstractToolkit
import logging.config
import json
import os

DEPRECATION_WARNING_TEXT = """
        ############################################################
        # WARNING:                                                 #
        #                                                          #
        # The Logging toolkit is deprecated                        #
        # Please change your code                                  #
        # to use hera.utils.logging.helpers.initialize_logging()   #
        # instead.                                                 #
        ############################################################
"""

EXECUTION = 15
logging.addLevelName(EXECUTION, 'EXECUTION')

def execution(self, message, *args, **kws):
    self.log(EXECUTION, message, *args, **kws)

logging.Logger.execution = execution


class loggingToolkit(abstractToolkit):
    """
        A toolkit to handle log files.


        Currently, it handles only the definition of logged objects and manages the configuration.
        However, in the future, it might also include tools to analyze logs and their performances.
        It could be any logs, include other programs like openFOAM.

        Since logging is global, there is no need to supply projectName to that
        toolkit.

        The logging configuration of each project is handled as a datasource.

        Remember that logger names are hierarchinal with '.' to separate them. That is,

        A
        + - A.B
        | + - A.B.G
        |
        + - A.C



    """

    _config = None

    @property
    def configuration(self):
        """ The current logger configuration """
        return self._config


    def __init__(self,projectName,filesDirectory=None,loggingConfig=None):
        """
            Initializes the logging toolkit to the required projectName.

            In default, the files directory are saved to the [filesDirectory]/log directory.


        Parameters
        ----------
        projectName: str
                The project name - not used.

        fileDirectory: str
                The log files are written to [filesDirectory]/log. Uses the default filesDirectory for default.


        loggingConfig: dict
                Dictionary to update the default configuration with.
        """
        print(DEPRECATION_WARNING_TEXT)
        super().__init__(toolkitName="loggingToolkit",projectName="loggingData",filesDirectory=filesDirectory)
        self.initializeLogger(resetToDefault=True, loggingConfig=loggingConfig)

    @property
    def defaultHeraLogDir(self):
        return os.path.join(pathlib.Path.home(), ".pyhera", "log")

    def getDefaultLoggingConfig(self):
        """
            Loads the default config and change the directories of the outputs.

        Returns
        -------
            dict

        """
        with open(os.path.join(os.path.dirname(__file__), 'argosLogging.config'), 'r') as logconfile:
            log_conf_str = logconfile.read().replace("\n", "")
            log_conf_str = log_conf_str.replace("{hera_log}", self.defaultHeraLogDir)
            log_conf = json.loads(log_conf_str)

        return log_conf


    def initializeLogger(self, resetToDefault=False, loggingConfig=None):
        """
            Adds a logging document to the project.

            If it doesn't exist, load the argosLogging.config, change the directories and update the document.

        Parameters
        ----------

        setToDefault : bool
                If true, reset the logging configuration to the default (i.e read the heralogging.config).


        loggingConfig: dict [optional]
                A logging configuration file. if not None, replace the existing configuration.

        Returns
        -------
                None
        """
        if resetToDefault:
            os.makedirs(self.defaultHeraLogDir, exist_ok=True)  # if this fails, let the exception be raised
            log_conf = self.getDefaultLoggingConfig()
        else:
            # It will always exist, because we call the initialize project with resetToDefault when we initialize the toolkit.
            log_conf = self.getDatasourceData("logging")

        if loggingConfig is not None:

            if not isinstance(loggingConfig, dict):
                raise ValueError(
                    "logging config must be a dict (with the logging format, see argosLogging.config for an example")

            log_conf.update(loggingConfig)


        # Add to the DB of the user.
        logDocument = self.getDatasourceDocument("logging")
        if logDocument is None:
            self.addDataSource(dataSourceName="logging",dataFormat=datatypes.DICT,resource=log_conf)

        # setup the config.
        try:
            logging.config.dictConfig(log_conf)
        except ValueError as e:
            raise RuntimeError(
                f"Unable to initialize logger.\n"
                f"Make sure that the logging subdirectory "
                f"(by default, {self.defaultHeraLogDir}) exists and is writable."
            ) from e

        self._config = log_conf

    def saveConfiguration(self):
        """
            Save the current configuration to the database.

        Returns
        -------
            None
        """
        logDoument = self.getDatasourceDocument("logging")
        logDoument.resource = self.configuration
        logDoument.save()


    def getHandlers(self):
        """
            Return a dict with the existing handlers.

        Returns
        -------
            dict
        """
        log_conf = self.getDatasourceData("logging")
        return log_conf["handlers"]


    def getFormatters(self):
        """
            Return a dict with the existing formatters.

        Returns
        -------
            dict
        """
        log_conf = self.getDatasourceData("logging")
        return log_conf["formatters"]

    def getLoggers(self):
        """
            Returns the existing loggers.

        Returns
        -------
            dict
        """
        log_conf = self.getDatasourceData("logging")
        return log_conf["loggers"]


    def addLogger(self,loggerName,handlers,level,propagate=False):
        """
                Adds a logger to the configuration file.

                Currently, we do not save these logger in the user database.

        Parameters
        ----------
        loggerName: str
            The name of the logger

        handlers: list,
            The list of handlers.

            level: str
                The level to print "DEBUG","EXECUTION","INFO","WARNING","ERROR","CRITICAL"
            propagate": bool , default False
                Propagate the log message to the father of the logger
                (i.e, another logger whose name is the prefix of the current logger)

        Returns
        -------
            None

        """

        self.configuration["loggers"][loggerName] = dict(handlers=handlers,level=level,propagate=propagate)

        # setup the config.
        logging.config.dictConfig(self.configuration)


    def addHandler(self, handlerName, handlerClass,formatter,**kwargs):
        """
                Adds a handler to the configuration file.

                Currently, we do not save these logger in the user database.

        Parameters
        ----------
        handlerName: str
            The name of the logger

            handlerClass: str
                The type of handler. See https://docs.python.org/3/library/logging.handlers.html for details.

                formatter: str
                    The name of the formatter to use.

                kwargs:
                    other class dependent fields.



        Returns
        -------
            None

        """

        handlerDefinition = {"class":handlerClass , "formatter":formatter}
        handlerDefinition.update(kwargs)

        self.configuration["handlers"][handlerName] = handlerDefinition

        # setup the config.
        logging.config.dictConfig(self.configuration)



    def addFormatter(self, formatterName, format,datefmt="%Y-%m-%d %H:%M:%S"):
        """
                Adds a handler to the configuration file.

                Currently, we do not save these logger in the user database.

        Parameters
        ----------
        formatterName: str
            The name of the logger

        formatterDefinition: dict
                Definition of the logger.

                A dict with the following keys:

                    "format": str
                        The format of each message. For example
                        "%(asctime)s %(filename)s/%(funcName)s(%(lineno)d) %(levelname)-8s %(name)-15s %(message)s",

                        for the options see https://docs.python.org/3/library/logging.html#logging.Formatter

                    "datefmt": str
                        The format of the date. for example: "%Y-%m-%d %H:%M:%S"



        Returns
        -------
            None

        """

        formatterDefinition = dict(format=format,datefmt=datefmt)
        self.configuration["formatters"][formatterName] = formatterDefinition

        # setup the config.
        logging.config.dictConfig(self.configuration)













