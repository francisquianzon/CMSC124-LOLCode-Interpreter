from sys import set_asyncgen_hooks
import lexer
import re

class CodeBlock:
    def __init__(self, tokens, bSyntax):
        self.tokens = tokens
        self.tokenIndex = len(tokens)
        self.statements = []                    #list of statements
        self.symbolTable = []                   #holds all the variables
        self.bSyntax = bSyntax

    #function for adding variables to the symbol table
    def addSymbolTable(self, variable):
        variable.variableFlag = 1;

        for i in self.symbolTable:
            #if variable already holds a value, updates; otherwise, appends
            if(variable.value == i.value): 
                i.variableData = variable.variableData
                i.variableFlag = 1
                return 0
                
        self.symbolTable.append(variable)

#a class that will hold the tokens of a statement
class Statement:
    def __init__(self, line):
        self.tokens = []                        #contains the tokens
        self.line = line                        #the line number of the statement
        self.type = None
        self.hasExpFlag = 0                     #a flag that checks whether a statement has an expression
        self.variables = []                     #list of variables in a statement
        self.expStack = []                      #a stack of the expression to be evaluated

#the BlockSyntax class will hold flags that will help in checking the syntax of the code
class BlockSyntax:
    def __init__(self):
        self.flags = 0
        self.impVarFlag = 0                     #a flag that checks whether an implicit variable is in use
        self.impVarValue = None                 #the value of an implicit variable
        self.line = 1                           #stores the line number of the current line
        self.startFlag = 0                      #checks whether the block of code can start (finds a start delimiter ('HAI))                        
        self.ifelseClause = 0                   #flag that checks if an if-else clause is found
        self.ifelseFlag = None                  #flag that determines whether YA RLY or NO WAI will be executed
        self.switchClause = 0                   #flag that checks if a switch clause is found
        self.executeDefaultSwitch = 1           #flag that checks whether the OMGWTF case should be executed

#function that removes the delimiter in the string
def removeDelimiter(string):
    return string[1:-1]

#function that prints a message if an error is found
def parseError(errortype, token):
    print("ParseError at line " + str(token.lineNumber))
    print(errortype)
    quit()

#function that print the tokens per statement; for checking
def printStatements(line):
    for i in line:
        print(str(i.value) + " ", end='')
    
    print(" ")

#function that finds the value of a variable in the symbolTable
def findInSymbolTable(block, token):
    for i in block.symbolTable:
        if(token.value == i.value and i.variableFlag == 1):
            stringVariable = re.search(r'"', str(i.variableData))
            if(stringVariable):
                return(removeDelimiter(i.variableData))
            else:
                return(i.variableData)
        elif(i.variableFlag == 0):
            return None
    return None

#function that assigns value to a variable in an assignment statemen
def assignValue(block, stateClass, token):

    #if the variable is an implicit variable
    if(stateClass.variables[0].classification == "Implicit Variable"):
        block.bSyntax.impVarFlag = 1
        if(isinstance(token, int) or isinstance(token, float) or isinstance(token, str)):
            block.bSyntax.impVarValue = token
            stateClass.variables[0].variableData = token
        else:
            if(token.classification == "Variable Identifier"):
                block.bSyntax.impVarValue = token
                stateClass.variables[0].variableData = token
            else:
                block.bSyntax.impVarValue = token.value
                stateClass.variables[0].variableData = token.value
        return 0

    if(isinstance(token, int) or isinstance(token, float) or isinstance(token, str)):
        stateClass.variables[0].variableData = token
    else:
        if(token.classification == "Variable Identifier"):
            stateClass.variables[0].variableData = findInSymbolTable(block, token)
        else:
            stateClass.variables[0].variableData = token.value

    stateClass.variables[0].variableFlag = 1

#mannually adds the tokens to the statement
def addTokens(tokens, statement):
    for i in tokens:
        statement.tokens.append(i)

def appendExpStack(block, statement, token):
    if(token.classification == "Variable Identifier" or token.classification == "Implicit Variable"):
        statement.expStack.append(str(findInSymbolTable(block,token)))
        return 0
    else:
        statement.expStack.append(str(token.value))


#helper function for parsing print statements
def parseOutput(block, statement, token, count, statementClass):
    allowContinue = False
    tokenClass = token.classification

    #if token is an output keyword
    if(tokenClass == "Input/Output Keyword"):

        # the next could be a string, a literal, a NUMBR/NUMBAR, a TROOF Literal, an expression, or the implicit IT variable
        if(count == len(statement)-1):
            parseError("Invalid syntax: nothing to print", token)
        elif(statement[count+1].type == "Literal" or statement[count+1].classification == "TROOF Literal"):
            allowContinue = True
        elif(statement[count+1].classification == "Implicit Variable"):
            allowContinue = True
        elif(statement[count+1].classification == "Arithmetic Operator" or statement[count+1].classification == "Boolean Operator" or statement[count+1].classification == "Comparison Operator"):
            count += 1
            statementClass.hasExpFlag = 1 #flags the statement as containing an expression
            parseExpression(block, statement, statement[count], count, statementClass)
            return 0; #an expression is always at the end of the statement; after parsing the expression, the statement is parsed
        else:
            parseError("Invalid syntax: cannot print", token)
        
    #if token is a literal
    elif(token.type == "Literal"):
        
        # the next could be a string, a literal, a NUMBR/NUMBAR, a TROOF Literal or an end of statement
        if(count == len(statement)-1):
            allowContinue = True
        elif(statement[count+1].type == "Literal" or statement[count+1].classification == "TROOF Literal"):
            allowContinue = True
        elif(statement[count+1].classification == "Arithmetic Operator" or statement[count+1].classification == "Boolean Operator" or statement[count+1].classification == "Comparison Operator"):
            count += 1
            statementClass.hasExpFlag = 1 #flags the statement as containing an expression
            parseExpression(block, statement, statement[count], count, statementClass)
            return 0; #an expression is always at the end of the statement; after parsing the expression, the statement is parsed
        else:
            parseError("Invalid syntax: cannot print", token)
    
    #if token is an implicit variable
    if(tokenClass == "Implicit Variable"):

        #the next could be the end of the statement
        if(count == len(statement)-1):
            allowContinue = True
        

    if(allowContinue):
        if(count < len(statement)-1):
            count += 1
            parseOutput(block, statement, statement[count], count, statementClass)
    else:
        parseError("Invalid print statement", token)

#helper function for parsing in input statement (GIMMEH)
def parseInput(statement, token, count, statementClass):
    allowContinue = False
    tokenClass = token.classification
    
    #if token is an output keyword
    if(tokenClass == "Variable Identifier"):

        # the next could be a variable
        if(count == len(statement)-1):
            allowContinue = True
        elif(statement[count+1].classification == "Variable Assignment"):
            allowContinue = True
        else:
            parseError("Invalid syntax: not an input", token)
    
    if(allowContinue):
        if(count < len(statement)-1):
            count += 1
            parseInput(statement, statement[count], count, statementClass)
    else:
        parseError("print ", token)

#helper function for parsing an assignment statement
def parseAssignment(block, statement, token, count, statementClass):
    allowContinue = False
    tokenClass = token.classification

    #if token is a variable declaration keyword
    if(tokenClass == "Variable Declaration"):
    
        #the next could be a variable identifier
        if(count == len(statement)-1):
            parseError("Invalid syntax: no assignment", token)
        elif(statement[count+1].classification == "Variable Identifier"):
            allowContinue = True

    #if token is variable or an implicit variable
    elif((tokenClass == "Variable Identifier" or tokenClass == "Implicit Variable") and (count == 0 or count == 1) ):

        #the next could be a variable assignment token or end of statement; if not 
        if(count == len(statement)-1):
            allowContinue = True
        elif(statement[count+1].classification == "Variable Assignment"):
            allowContinue = True
        else:
            parseError("Invalid syntax: not assignment", token)

        #adds the variable token to the list of variables in the statement
        if(allowContinue):
            statementClass.variables.append(token)

    #if token is R or ITZ
    elif(tokenClass == "Variable Assignment"):
        
        #the next could be a NUMBR, NUMBAR Literal, string, TROOF Literal, or an expression
        if(count == len(statement)-1):
            parseError("Invalid syntax: no assignment", token)
        elif(statement[count+1].type == "Literal" or statement[count+1].classification == "TROOF Literal"):
            allowContinue = True
        elif(statement[count+1].classification == "Arithmetic Operator" or statement[count+1].classification == "Boolean Operator" or statement[count+1].classification == "Comparison Operator"):
            count += 1
            statementClass.hasExpFlag = 1 #flags the statement as containing an expression
            parseExpression(block, statement, statement[count], count, statementClass)
            return 0; #an expression is always at the end of the statement; after parsing the expression, the statement is parsed
        else:
            parseError("Invalid syntax: cannot assign to variable", token)

    #if token is a literal
    elif((token.type == "Literal" or tokenClass == "TROOF Literal")):
        #the next could be an end of statement
        if(count == len(statement)-1):
            allowContinue = True
        else:
            parseError("Invalid syntax: cannot assign values to variable", token)
    
        assignValue(block, statementClass, token)

    if(allowContinue):
        if(count < len(statement)-1):
            count += 1
            parseAssignment(block, statement, statement[count], count, statementClass)
    else:
        parseError("Invalid syntax: invalid assignment ", token)

#helper function for parsing expression statements (arithmetic, boolean, comparison)
def parseExpression(block, statement, token, count, statementClass):
    allowContinue = False
    tokenClass = token.classification

    #if token is an operator
    if(tokenClass == "Arithmetic Operator" or tokenClass == "Boolean Operator" or tokenClass == "Comparison Operator"):
        
        #the next token could be a NUMBR, NUMBAR, variable, or TROOF Literal, or an expression, or the Implicit variable
        if(count == len(statement)-1):
            parseError("Invalid syntax: no expression", token)
        elif(statement[count+1].classification == "NUMBR Literal" or statement[count+1].classification == "NUMBAR Literal"):
            allowContinue = True
        elif(statement[count+1].classification == "Variable Identifier" or statement[count+1].classification == "TROOF Literal"):
            allowContinue = True
        elif(statement[count+1].classification == "Arithmetic Operator" or statement[count+1].classification == "Boolean Operator" or statement[count+1].classification == "Comparison Operator"):
            allowContinue = True
        elif(statement[count+1].classification == "Implicit Variable"):
            allowContinue = True
        else:

            parseError("Invalid syntax: invalid expression", token)

        appendExpStack(block,statementClass,token)
        
    #if token is a literal or an implicit variable
    elif(token.type == "Literal" or tokenClass == "Implicit Variable" and token.classification != "String Literal"):

        #the next token could be a separator or end of statement
        if(count == len(statement)-1):
            allowContinue = True
        elif(statement[count+1].classification == "Separator"):
            allowContinue = True
        else:
            parseError("Invalid syntax: invalid value", token)
        
        appendExpStack(block,statementClass,token)
    
    #if token is a separator
    elif(tokenClass == "Separator"):

        #the next token could be a literal, or an expression
        if(count == len(statement)-1):
            parseError("Invalid syntax: invalid end of statement", token)
        elif(statement[count+1].classification == "NUMBR Literal" or statement[count+1].classification == "NUMBAR Literal"):
            allowContinue = True
        elif(statement[count+1].classification == "Variable Identifier" or statement[count+1].classification == "TROOF Literal"):
            allowContinue = True
        elif(statement[count+1].classification == "Arithmetic Operator" or statement[count+1].classification == "Boolean Operator" or statement[count+1].classification == "Comparison Operator"):
            allowContinue = True
        elif(statement[count+1].classification == "Implicit Variable"):
            allowContinue = True
        else:
            parseError("Invalid syntax: invalid separator in expression", token)
    
    if(allowContinue):
        if(count < len(statement)-1):
            count += 1
            parseExpression(block, statement, statement[count], count, statementClass)
    else:
        parseError("Invalid expression statement", token)


#function that identifies the type of the statement
def identifyStatement(block, statement):
    sType = statement[0].classification
    newStatement = Statement(statement[0].lineNumber)

    #if the start of a statement is a variable
    if(sType == "Variable Identifier" or sType == "Implicit Variable"):
        parseAssignment(block, statement, statement[0], 0, newStatement)
        newStatement.type = "Assignment Statement"
        addTokens(statement, newStatement)

        #updates the block class and the symbol table
        block.statements.append(newStatement)
        block.addSymbolTable(newStatement.variables[0])

    #if the start of a statement is a variable declaration keyword
    elif(sType == "Variable Declaration"):
        if(block.bSyntax.ifelseClause == 1 or block.bSyntax.switchClause):
            parseError("Invalid syntax: cannot instantiate variable inside a clause", statement[0])
        else:
            parseAssignment(block, statement, statement[0], 0, newStatement)
            newStatement.type = "Assignment Statement"
            addTokens(statement, newStatement)

            #updates the block class and the symbol table
            block.statements.append(newStatement)
            block.addSymbolTable(newStatement.variables[0])

    #if the start of the statement is an output/input keyword
    elif(sType == "Input/Output Keyword"):
        if(statement[0].value == "VISIBLE"):
            parseOutput(block, statement, statement[0], 0, newStatement)
            newStatement.type = "Print Statement"
            addTokens(statement, newStatement)

            #updates the block class and the symbol table
            block.statements.append(newStatement)

    #if the start of the statement is an expression
    elif(sType == "Arithmetic Operator" or sType == "Boolean Operator" or sType == "Comparison Operator"):
        parseExpression(block, statement, statement[0], 0, newStatement)
        newStatement.type = "Expression Statement"
        addTokens(statement, newStatement)
        newStatement.hasExpFlag = 1

        #updates the block class and the symbol table
        block.statements.append(newStatement)
    
    #if the start of the statement is a keyword of the if-else clause
    elif(sType == "If/Then Keyword"):
        block.bSyntax.ifelseClause = 1
        
        #checks if there are preceeding tokens after the statement; if so, returns a parse error
        if(len(statement) > 1):
            parseError("Invalid syntax: if-else keyword should not be preceeded", statement[0])

        newStatement.type = "If/Else Statement"
        addTokens(statement, newStatement)

        block.statements.append(newStatement)

    #if the start of the statement is the opening to the swtich clause
    elif(sType == "Switch-case Keyword" and (statement[0].value == "WTF?" or statement[0].value == "OMGWTF")):
        block.bSyntax.switchClause = 1

        #checks if there are preceeding tokens after the statement; if so, returns a parse error
        if(len(statement) > 1):
            parseError("Invalid syntax: if-else keyword should not be preceeded", statement[0])

        newStatement.type = "Switch Statement Opening"
        addTokens(statement, newStatement)

        block.statements.append(newStatement)

    #if the start of the statement is a keyword of the switch clause
    elif(sType == "Switch-case Keyword" and statement[0].value != "OMGWTF"):
        #the next could be any literal
        if(len(statement) < 1):
            parseError("Invalid syntax: switch has no arguement", statement[0])
        elif(statement[1].type != "Literal"):
            parseError("Invalid syntax: invalid argument", statement[0])

        newStatement.type = "Switch Statement"
        addTokens(statement, newStatement)

        block.statements.append(newStatement)

    elif(sType == "Block Delimiter"):
        if(block.bSyntax.ifelseClause == 1):
            block.bSyntax.ifelseClause = 0
        elif(block.bSyntax.switchClause == 1):
            block.bSyntax.switchClause = 0

        newStatement.type = "Block Delimiter Statement"
        addTokens(statement, newStatement)

        block.statements.append(newStatement)
        

#function that parses through a block of code 
def parse(block):
    startOfProgram = False #flag that checks for code delimiters; ensures that parsing starts and end tiwth the code delimiters
    statements = []
    tokenCount = 0

    for i in block.tokens:
        startProgram = re.search(r'HAI', str(i.value))
        endProgram = re.search(r'KTHXBYE', str(i.value))

        #checks the code block within the code delimiters, if there are tokens before the start delimiter, returns an error
        if(startProgram and tokenCount != 0):
            parseError("Invalid block", i)
        elif(startProgram):
                startOfProgram = True
                block.bSyntax.startFlag = 1
    
        #parses the tokens within the valid code block
        if(startOfProgram):
            tokenCount += 1

            #if a new line is found
            if(str(i.type) == "NewLine"):
                identifyStatement(block,statements)
                statements.clear()
                continue
            else:
                statements.append(i)

        #checks the code block within the code delimiters, if there are tokens after the end delimiter, returns an error
        if(endProgram and tokenCount != block.tokenIndex-1):
            parseError("Invalid block", i)
        elif(endProgram):
            startOfProgram = False