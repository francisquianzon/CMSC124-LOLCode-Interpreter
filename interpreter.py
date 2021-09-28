from lexer import tokenError
import re
import parser
import lexer

#function that prints a message if an error is found
def InterpreterError(errortype, token):
    print("InterpreterError at line " + str(token.lineNumber))
    print(errortype)
    quit()


#function that identifies whether an integer is a float or lexeme
def identifyInteger(lexeme):
    NUMBAR = re.search(r'[+-]?[0-9]+\.[0-9]+', lexeme)
    if(NUMBAR):
        return float(NUMBAR.group())

    NUMBR = re.search(r'-?[1-9][0-9]*|0', lexeme)
    if(NUMBR):
        return int(NUMBR.group())
    
    return None

#function that returns the comparison between two integers
def returnCompare(operand1, operand2, type):
    #for BIGGER OF
    if(type == 1):
        if(operand1 > operand2):
            return operand1
        else:
            return operand2
    #for SMALLR OF
    elif(type == 2):
        if(operand1 < operand2):
            return operand1
        else:
            return operand2


#function that evaluates an expression in prefix form
def evalExpression(expression):
    stack = []

    for i in reversed(expression):
        #for arithmetic operators
        if(i == "SUM OF"):
            operand1 = stack.pop()
            operand2 = stack.pop()
            stack.append(operand1 + operand2)
        elif(i == "PRODUKT OF"):
            operand1 = stack.pop()
            operand2 = stack.pop()
            stack.append(operand1 * operand2)
        elif(i == "DIFF OF"):
            operand1 = stack.pop()
            operand2 = stack.pop()
            stack.append(operand1 - operand2)
        elif(i == "QUOSHUNT OF"):
            operand1 = stack.pop()
            operand2 = stack.pop()
            if(isinstance(operand1, float) or isinstance(operand1, float)):
                stack.append(operand1 / operand2)
            else:
                stack.append(operand1 // operand2)
        elif(i == "MOD OF"):
            operand1 = stack.pop()
            operand2 = stack.pop()
            stack.append(operand1 % operand2)
        elif(i == "BIGGR OF"):
            operand1 = stack.pop()
            operand2 = stack.pop()
            stack.append(returnCompare(operand1,operand2,1))
        elif(i == "SMALLR OF"):
            operand1 = stack.pop()
            operand2 = stack.pop()
            stack.append(returnCompare(operand1,operand2,2))
        
        #for comparison
        elif(i == "BOTH SAEM"):
            operand1 = stack.pop()
            operand2 = stack.pop()
            if(operand1 == operand2):
                stack.append('WIN')
            else:
                stack.append('FAIL')
        
        elif(i == "DIFFRINT"):
            operand1 = stack.pop()
            operand2 = stack.pop()
            if(operand1 != operand2):
                stack.append('WIN')
            else:
                stack.append('FAIL')
            
        #for boolean
        elif(i == "BOTH OF"):
            operand1 = stack.pop()
            operand2 = stack.pop()
            if(operand1 == operand2 and operand1 == 'WIN'):
                stack.append('WIN')
            else:
                stack.append('FAIL')

        elif(i == "EITHER OF"):
            operand1 = stack.pop()
            operand2 = stack.pop()
            if(operand1 == "WIN" or operand2 == "WIN"):
                stack.append('WIN')
            else:
                stack.append('FAIL')

        elif(i == "WON OF"):
            operand1 = stack.pop()
            operand2 = stack.pop()
            if(operand1 != operand2):
                stack.append('WIN')
            else:
                stack.append('FAIL')
        
        elif(i == "NOT"):
            operand1 = stack.pop()
            if(operand1 == 'FAIL'):
                stack.append('WIN')
            else:
                stack.append('FAIL')
        
        elif(i == "ALL OF"):
            while(len(stack) > 1):
                operand1 = stack.pop()
                if(operand1 == 'FAIL'):
                    stack.append('FAIL')
                    break
        
        elif(i == "ANY OF"):
            while(len(stack) > 1):
                operand1 = stack.pop()
                if(operand1 == 'WIN'):
                    stack.append('WIN')
                    break

        else:
            if(identifyInteger(i)):
                stack.append(identifyInteger(i)) #push to stack
            else:
                stack.append(i)
    
    return stack.pop()

#function for printing a statement
def printStatement(block, line, count):
    tokenBuffer = line.tokens[count]
    returnStr = ""

    if(tokenBuffer.classification == "Arithmetic Operator" or tokenBuffer.classification == "Boolean Operator" or tokenBuffer.classification == "Comparison Operator"):
        returnStr = str(evalExpression(line.expStack))
        return returnStr

    #if the token is a literal
    if(tokenBuffer.type == "Literal" and tokenBuffer.classification != "Variable Identifier"):
        stringVariable = re.search(r'"', str(tokenBuffer.value))
        if(stringVariable):
            returnStr = str(parser.removeDelimiter(tokenBuffer.value))
        else:
            returnStr = str(tokenBuffer.value) 
        
        return returnStr
    
    #if the token is variable, checks whether it holds a data and prints the data
    if(tokenBuffer.classification == "Variable Identifier"):
        #finds the variable in the symbol table
        value = parser.findInSymbolTable(block,tokenBuffer)
        if(value != None):
            returnStr = str(value)
        else:
            InterpreterError("Invalid syntax: variable has no value", tokenBuffer)
        
        return returnStr

    #if token is an implicit IT variable
    if(tokenBuffer.classification == "Implicit Variable"):
        if(block.bSyntax.impVarFlag):
            if(isinstance(block.bSyntax.impVarValue,str) and (block.bSyntax.impVarValue != 'WIN' and block.bSyntax.impVarValue != 'FAIL')):
                returnStr = str(parser.removeDelimiter(block.bSyntax.impVarValue))
            else:
                returnStr = str(block.bSyntax.impVarValue)
        else:
            InterpreterError("Invalid syntax: implicit variable empty", tokenBuffer)

        return returnStr

    return returnStr

#function for evaluating an expression in an assignment statement
def assignExpression(block, line, count):

    parser.assignValue(block, line, evalExpression(line.expStack))
    block.addSymbolTable(line.variables[0])

#function that assigns a value to the implicit variable
def assignImplicit(block, line):
    block.bSyntax.impVarFlag = 1
    block.bSyntax.impVarValue = evalExpression(line.expStack)

    itToken = lexer.Token("IT","Keyword", line.line)
    itToken.variableData = evalExpression(line.expStack)
    itToken.variableFlag = 1
    block.addSymbolTable(itToken)

#helper function that checks the IT variable in ifelse statement
def parseIfElseClause(block):
    block.bSyntax.ifelseClause = 1
    if(block.bSyntax.impVarValue == 'WIN'):
        block.bSyntax.ifelseFlag = 1
    if(block.bSyntax.impVarValue == 'FAIL'):
        block.bSyntax.ifelseFlag = 0

#helper function that compares against each argument in the swtich clause
def parseSwitchClause(block):
    block.bSyntax.switchClause = 1

#function that interprets each line in the code block and gives it a semantic meaning
def interpretBlock(block):
    allowContinue = True
    
    #iterates each statement in the codeBlock
    for i in block.statements:
        
        #if a block delimiter is found, resets clauses
        if(i.tokens[0].value == "OIC"):
            if(block.bSyntax.ifelseClause):
                block.bSyntax.ifelseClause = 0
                block.bSyntax.ifelseFlag = None
                block.bSyntax.switchClause = 0
            allowContinue = True
    
        #checks whether preceeding statements are inside an if-else clause
        if(block.bSyntax.ifelseClause):
            # print(str(block.bSyntax.ifelseFlag) + " " + i.tokens[0].value)
            if(block.bSyntax.ifelseFlag == 0):
                if(i.tokens[0].value == "YA RLY"):
                    allowContinue = False
                if(i.tokens[0].value == "NO WAI"):
                    allowContinue = True
            if(block.bSyntax.ifelseFlag == 1):
                if(i.tokens[0].value == "NO WAI"):
                    allowContinue = False
                if(i.tokens[0].value == "YA RLY"):
                    allowContinue = True
        
        #checks whether preceeding statements are inside a switch case clause
        if(block.bSyntax.switchClause):
            if(i.tokens[0].value == "OMG"):
                # print(str(i.tokens[1].value) + "|||" + str(block.bSyntax.impVarValue))
                if(i.tokens[1].value != block.bSyntax.impVarValue):
                    allowContinue = False
                elif(i.tokens[1].value == block.bSyntax.impVarValue):
                    allowContinue = True
                    block.bSyntax.executeDefaultSwitch = 0

            if(i.tokens[0].value == "OMGWTF" and block.bSyntax.executeDefaultSwitch == 0):
                allowContinue = False
            elif(i.tokens[0].value == "OMGWTF" and block.bSyntax.executeDefaultSwitch == 1):
                allowContinue = True
        
        #if a GTFO is found, exits a clause until a OIC is found
        if(i.tokens[0].value == "GTFO"):
            allowContinue = False
    
        if(allowContinue):
            #if the line is print statement, prints the tokens preceeding the output keyword
            if(i.type == "Assignment Statement" and i.hasExpFlag):
                assignExpression(block, i, 0)

            if(i.type == "Expression Statement"):
                assignImplicit(block, i)

            if(i.type == "Print Statement"):
                for j in range(len(i.tokens)):
                    # printStr = printStatement(block,i,j)
                    # if(printStr != ""):
                    #     print(printStr, end='')
                    printStatement(block,i,j)
                    if(i.hasExpFlag):
                        print(str(evalExpression(i.expStack)), end='')
                        break

                print('')

            if(i.type == "If/Else Statement"):
                parseIfElseClause(block)

            if(i.type == "Switch Statement Opening"):
                parseSwitchClause(block)
