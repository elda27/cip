import re

def getKeywordArgument(arg):
    sep = arg.find('=')
    if sep == -1:
        return (arg, None)
    else:
        return arg[:sep], arg[sep + 1:] 


class ArgumentsParser:
    def __init__(self):
        self.Tokens = list()
        pass

    def parse(self, args):
        self.Tokens = list()
        current_token = None
        for i, arg in enumerate(args):
            sep = arg.find(':')
            if sep == -1: # This argument is not command.
                if current_token is None:
                    raise ArgparseException(args, i, "Wrong format arguments.")
                else:
                    key, value = getKeywordArgument(arg)
                    if value is None: # This argument is usualy argument.
                        current_token['args'].append(key)
                    else:             # This argument is keyword argument.
                        current_token['kwargs'][key] = value
                    continue

            command = arg[:sep]

            if not current_token is None and sep != -1: # Found next command and need to create token.
                token = Token(current_token['namespace'], current_token['operation'], *current_token['args'], **current_token['kwargs'])
                self.Tokens.append(token)
                current_token = None

            current_token = dict()
            current_token['args'] = list()
            current_token['kwargs'] = dict()
            option = arg[sep:]
            if not option: # This argument has argument option
                key, value = getKeywordArgument(option)
                if value is None: # This argument is usualy argument.
                    current_token['args'].append(key)
                else:             # This argument is keyword argument.
                    current_token['kwargs'][key] = value

            if command.find('.') != -1:  # This command has namespace
                current_token['namespace'], current_token['operation'] = command.split('.')
            else:
                current_token['operation'] = command
                current_token['namespace'] = ''

        token = Token(current_token['namespace'], current_token['operation'], *current_token['args'], **current_token['kwargs'])
        self.Tokens.append(token)

    def tokens(self):
        return self.Tokens

class Token:
    def __init__(self, namespace, operation, *args, **kwargs):
        self.Operation = operation
        self.Namespace = namespace
        self.Arguments = args
        self.KeywordArguments = kwargs

    def namespace(self):
        return self.Namespace

    def args(self):
        return self.Arguments

    def kwargs(self):
        return self.KeywordArguments

    def operation(self):
        return self.Operation

    def command(self):
        return self.Namespace + "." + self.Operation if self.Namespace else self.Operation

    def __repr__(self):
        return '<{}:{}, {}>'.format(self.command(), self.Arguments, self.KeywordArguments)

class ArgparseException(Exception):
    def __init__(self, args, position, message):
        super().__init__(message)
        self.Args = args
        self.Position = position
        self.Message = message

class TokenError(Exception):
    def __init__(self, token, message):
        self.Token = token
        super().__init__(message + '\n  Token:' + str(token))
        