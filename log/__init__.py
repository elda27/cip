import logging
import logging.config
import env
import os
import os.path
import json

def initialize():
    appdir = env.getApplicationLocalDir()
    logdir = env.getLogDir()
    if not os.path.exists(logdir):
        os.makedirs(logdir)

    log_config = dict()
    log_config_filename = os.path.join(appdir, 'log.json')
    if not os.path.exists(log_config_filename):
        log_config = getDefaultLoggingConfig(logdir)
        with open(log_config_filename, 'w+') as fp:
            fp.writelines(json.dumps(log_config))
    else:
        with open(log_config_filename, 'r') as fp:
            try:
                log_config = json.load(fp)
            except json.JSONDecodeError as e:
                print('Wrong format log configuration file ({})\n{}'.format(log_config_filename, e))
                raise e

    logging.config.dictConfig(log_config)

def getLogger(name):
    return logging.getLogger('cip.' + name)

def setLevel(level):
    getLogger("cip").setLevel(level)

def getDefaultLoggingConfig(logdir):
    return {
    "version":1,
    "disable_existing_loggers": False,
    "formatters": {
        'verbose': {
            'format': '%(levelname)s %(name)s %(asctime)s %(module)s %(process)d %(thread)d %(pathname)s(%(lineno)s): %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(name)s %(filename)s(%(lineno)s): %(message)s'
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "WARNING", 
            "filters": []
        },
        "file" :{
            "class":"logging.FileHandler",
            "formatter": "verbose",
            "filename": os.path.join(logdir, 'runtime_log.txt'),
            "level": "INFO",
            "filters": []
        }
    },
    "root" :{
        "handlers": ["console"],
    },
    "gip" :{
        "handlers": ["console"],
    },
    "gip.env" :{
        "handlers": ["console"],
    },
    "gip.image" :{
        "handlers": ["console"],
    },
    "gip.builtin":{
        "handlers": ["console"],
    },
}

initialize()