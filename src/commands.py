
# Command templates
def baseCommand(commandName, arguments=None):
    if arguments == None:
        arguments = dict()
    return dict([('command', commandName), ('arguments', arguments)])


def loginCommand(userId, password, appName=''):
    return baseCommand('login', dict(userId=userId, password=password, appName=appName))


# example function for processing ticks from Streaming socket
def procTickExample(msg):
    print("TICK: ", msg)


# example function for processing trades from Streaming socket
def procTradeExample(msg):
    print("TRADE: ", msg)


# example function for processing trades from Streaming socket
def procBalanceExample(msg):
    print("BALANCE: ", msg)


# example function for processing trades from Streaming socket
def procTradeStatusExample(msg):
    print("TRADE STATUS: ", msg)


# example function for processing trades from Streaming socket
def procProfitExample(msg):
    print("PROFIT: ", msg)


# example function for processing news from Streaming socket
def procNewsExample(msg):
    print("NEWS: ", msg)
