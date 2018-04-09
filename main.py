import sys
import os.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import arguments
import log
import core
import builtin

def main(args, debug = False):
    log.initialize()
    logger = log.getLogger('cip')
    if debug:
        root_logger = log.logging.getLogger()
        root_logger.setLevel('DEBUG')
        for h in root_logger.handlers:
            h.setLevel('DEBUG')
        logger.warning('To display the verbose messages so the application performance maybe too bad.')

    app = core.Application()
    if len(args) < 2:
        args.append('help:')

    logger.debug('Loaded modules are following: {}'.format([m.getNamespace() for m in core.module.getModules()]))
    logger.debug(args)
    
    parser = arguments.ArgumentsParser()
    parser.parse(args[1:])
    tokens = parser.tokens()

    procedures = list()
    for token in tokens:
        logger.debug(token)
        proc = app.getProcedure(token.namespace(), token.operation())
        if proc is None:
            raise arguments.TokenError(token, 'A parsed token is not valid.')

        if '_Prior' in proc.__dict__ and proc._Prior:
            with proc() as p:
                logger.debug('Prior:{}'.format(proc))
                app.exec(p, token)
        else:
            procedures.append(proc)
    
    for proc, token in zip(procedures, tokens):
        with proc() as p:
            logger.debug(p)
            app.exec(p, token)

if __name__ == '__main__':
    debug = False
    try:
        if len(sys.argv) > 1 and sys.argv[1] == 'debug':
            debug = True
            main([sys.argv[0]] + sys.argv[2:], debug = True)
        else:
            debug = False
            main(sys.argv)
    except arguments.ArgparseException as e:
        print(e.Message)
        print('Position: {}({})'.format(e.Position, sys.argv[e.Position + 1]))
    except Exception as e:
        if debug:
            import traceback
            print('Unhandled exception occured!')
            print('-------------------------------------------------------')
            print(traceback.format_exc())
        else:
            print(e)
