# Parser.py

class Parser:
    # handles the parsing of a single .vm file
    hasMoreCommands = True # are there more commands in the input?
    currentCommand = "" # string with the current command
    vmFile = None # vm file object
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

        if nextCommand != -1:
            self.currentCommand = nextCommand

        else:
            self.hasMoreCommands = False


    def parseLine(self):
        line = self.vmFile.readline()
        if line == "":
            return -1

        line = line.strip()
        i = line.find("/")
        if i != -1:
            line = line[0:i]

        if line == "":
            line = self.parseLine()
        if type(line) == str:
            line = line.strip()
        return line


    def commandType(self):
        # Returns a constant representing the type of the current command.
        #
        # 0. Arithmetic
        arithmetic_list = ["add", "sub", "neg", "eq", "gt", "lt", "and",
                           "or", "not"]
        # 1. push
        # 2. pop
        # 3. label
        # 4. goto
        # 5. if goto
        # 6. function
        # 7. return
        # 8. call

        if self.currentCommand == -1:
            self.typeCode = -1

        for x in range(len(arithmetic_list)):
            if self.currentCommand.find(arithmetic_list[x]) == 0:
                self.typeCode = 0

        if self.currentCommand.find("push") == 0:
            self.typeCode = 1

        if self.currentCommand.find("pop") == 0:
            self.typeCode = 2

        if self.currentCommand.find("label") == 0:
            self.typeCode = 3

        if self.currentCommand.find("goto") == 0:
            self.typeCode = 4

        if self.currentCommand.find("if-goto") == 0:
            self.typeCode = 5

        if self.currentCommand.find("function") == 0:
            self.typeCode = 6

        if self.currentCommand.find("return") == 0:
            self.typeCode = 7

        if self.currentCommand.find("call") == 0:
            self.typeCode = 8

        return self.typeCode


    def arg1(self):
        # returns the first argument of the current command, returns string
        cmdType = self.commandType()
        if cmdType == -1:
            return -1

        if cmdType == 0:
            return self.currentCommand

        if cmdType == 7:
            return -1

        if cmdType > 0:
            cmdtypeStr = self.commandList[cmdType]
            i = self.currentCommand.find(cmdtypeStr)
            arg1 = self.currentCommand[i + len(cmdtypeStr)+1:]
            i = arg1.find(" ")
            if i != -1:
                arg1 = arg1[:i]

            return arg1



    def arg2(self):
        # returns the second argument of the current command , called only
        # for push, pop, function, call

        cmdType = self.commandType()

        if cmdType == 1 or cmdType == 2 or cmdType == 6 or cmdType == 8:
            arg1 = self.arg1()
            i = self.currentCommand.find(arg1)
            value = self.currentCommand[i+len(arg1)+1:len(self.currentCommand)]
            return int(value)

        else:
            return -1

    def close(self):
        # closes the input file
        self.vmFile.close()

