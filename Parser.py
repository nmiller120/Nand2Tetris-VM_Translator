# Parser.py

class Parser:
    # handles the parsing of a single .vm file
    hasMoreCommands = True # are there more commands in the input?
    currentCommand = "" # string with the current command
    vmFile = None # vm file object

    # list of VM commands
    commandList = ["arithmetic", "push", "pop", "label", "goto", "if-goto",
                   "function", "return", "call"]

    def __init__(self, file):
        # opens the input file stream and gets ready to parse it
        self.vmFile = open(file, "r")

    def advance(self):
        # Reads the next command from the input and makes it the current
        # command, should be called only if hasMoreCommands is true. Initially
        # there is no current command
        nextCommand = self.parseLine()

        # if there are more commands ruturn the next command, otherwise return
        # false
        if nextCommand != -1:
            self.currentCommand = nextCommand

        else:
            self.hasMoreCommands = False


    def parseLine(self):
        # filters non command content from the input stream, filters comments,
        # whitespace, newline characters, etc.

        # read the next line in the file
        line = self.vmFile.readline()

        # strip whitespace and return characters, chop off comments from the end
        # of the line.
        line = line.strip()
        i = line.find("/")
        if i != -1:
            line = line[0:i]

        # if there is no commands in the line, return -1
        if line == "":
            return -1

        # if there is content still, return the command string
        if type(line) == str:
            line = line.strip()
        return line


    def commandType(self):
        # Returns a constant representing the type of the current command.

        # 0. Arithmetic
        # 1. push
        # 2. pop
        # 3. label
        # 4. goto
        # 5. if goto
        # 6. function
        # 7. return
        # 8. call

        # list of arithmetic commands
        arithmetic_list = ["add", "sub", "neg", "eq", "gt", "lt", "and",
                           "or", "not"]


        # if the current command is valid
        if self.currentCommand == -1:
            self.typeCode = -1

        # if the current command contains any of the strings in the arithmetic
        # list, the current command is an arithmetic command, return 0
        for x in range(len(arithmetic_list)):
            if self.currentCommand.find(arithmetic_list[x]) == 0:
                return 0


        # if the current command contains the given string in the commandList
        # return the corresponding typecode
        for x in range(len(self.commandList)):
            if self.currentCommand.find(self.commandList[x]):
                return x




    def arg1(self):
        # returns the first argument of the current command, returns as string

        cmdType = self.commandType()

        # if the command is not a command, return -1
        if cmdType == -1:
            return -1

        # if the command is arithmetic, return the whole command as a string
        if cmdType == 0:
            return self.currentCommand

        # if the command type is a return, return -1, there is no argument
        if cmdType == 7:
            return -1

        # otherwise
        if cmdType > 0:

            # get the command string from the command list
            cmdtypeStr = self.commandList[cmdType]

            # find the command in the given string (eg. "push local 0" returns
            # i=0, push is at index 0)
            i = self.currentCommand.find(cmdtypeStr)

            # truncate the command from the given string, (eg. arg1 = "local 0")
            arg1 = self.currentCommand[i + len(cmdtypeStr)+1:]

            # truncate the rest of the arguments from the given string and return
            # (eg. arg1 becomes "local"). Translator assumes single spaces between
            # commands. Otherwise it won't be able to parse VM files.
            i = arg1.find(" ")
            if i != -1:
                arg1 = arg1[:i]

            return arg1



    def arg2(self):
        # returns the second argument of the current command , called only
        # for push, pop, function, call

        # get the command type
        cmdType = self.commandType()

        # if called on the appropriate commands types...
        if cmdType == 1 or cmdType == 2 or cmdType == 6 or cmdType == 8:

            # get the first argument of the command
            arg1 = self.arg1()

            # truncate the text so value is just equal to arg2 as a string
            i = self.currentCommand.find(arg1)
            value = self.currentCommand[i+len(arg1)+1:len(self.currentCommand)]

            # return arg2 as an integer
            return int(value)

        # otherwise return -1
        else:
            return -1

    def close(self):
        # closes the input file
        self.vmFile.close()

