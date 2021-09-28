from interpreter import interpretBlock
from sys import path
import lexer
import parser
import interpreter

# import tkMessageBox
import tkinter
from tkinter.constants import BOTH
from tkinter.filedialog import askopenfilename
import tkinter.font as tkFont


# GLOBAL vairables
filename = ""                               #variable for selecting a filename
mainCodeBlock = ""

top = tkinter.Tk()

#function that creates tokens from the selected file
def readTokens():
    listOfTokens = []
    lexSyntax = lexer.Syntax()
    input_file = open(filename)
    global mainCodeBlock
    
    font = tkFont.Font(family="Arial", size="12")
    read = input_file.readlines()

    #creates the textboxes for the frame
    lexemesTB = tkinter.Text(frameInterpreter, width="45", height="19", font=font)          #textbox for the lexemes

    for i in read: 
        line = i.split()
        lexer.createTokens(line,listOfTokens,lexSyntax)

    #analyzes the syntax of the tokens created from the lexemes
    blockSyntax = parser.BlockSyntax()

    mainCodeBlock = parser.CodeBlock(listOfTokens, blockSyntax)
    parser.parse(mainCodeBlock)


    #prints the tokens to the lexeme text box
    for i in mainCodeBlock.tokens:
        if(i.type == "NewLine"):
            continue

        lexemesTB.insert("end", "  {:<40s}{:>8s}".format(str(i.value),i.classification))
        lexemesTB.insert("end", '\n')

    lexemesTB.place(x=5,y=50)

    # #prints the symbol table to the symbol table text box
    # for i in mainCodeBlock.symbolTable:
    #     symbolTB.insert("end", '  {:<40s}{:>8s}'.format(str(i.value),str(i.variableData)))
    #     symbolTB.insert("end", '\n')

    # symbolTB.place(x=375, y=50)

    #insert labels
    labelFont = tkFont.Font(family="Arial", size="13")
    lexLabel = tkinter.Label(frameInterpreter, text="Lexemes", font=labelFont)
    lexLabel.place(x=10, y=30)

    classLabel = tkinter.Label(frameInterpreter, text="Classfication", font=labelFont)
    classLabel.place(x=200,y=30)

    symLabel = tkinter.Label(frameInterpreter, text="Identifier", font=labelFont)
    symLabel.place(x=380, y=30)

    valLabel = tkinter.Label(frameInterpreter, text="Value", font=labelFont)
    valLabel.place(x=560,y=30)
    

#function that executes a code
def executeCode():
    allowContinue = True

    #create textbox that will print the executed code
    font = tkFont.Font(family="Arial", size="12")
    executeTB = tkinter.Text(frameExecute, width="250", height="16", font=font)

    symbolTB = tkinter.Text(frameInterpreter, width="45", height="19", font=font)

    #iterates each statement in the codeBlock
    for i in mainCodeBlock.statements:
        
        #if a mainCodeBlock delimiter is found, resets clauses
        if(i.tokens[0].value == "OIC"):
            if(mainCodeBlock.bSyntax.ifelseClause):
                mainCodeBlock.bSyntax.ifelseClause = 0
                mainCodeBlock.bSyntax.ifelseFlag = None
                mainCodeBlock.bSyntax.switchClause = 0
            allowContinue = True
    
        #checks whether preceeding statements are inside an if-else clause
        if(mainCodeBlock.bSyntax.ifelseClause):
            # print(str(mainCodeBlock.bSyntax.ifelseFlag) + " " + i.tokens[0].value)
            if(mainCodeBlock.bSyntax.ifelseFlag == 0):
                if(i.tokens[0].value == "YA RLY"):
                    allowContinue = False
                if(i.tokens[0].value == "NO WAI"):
                    allowContinue = True
            if(mainCodeBlock.bSyntax.ifelseFlag == 1):
                if(i.tokens[0].value == "NO WAI"):
                    allowContinue = False
                if(i.tokens[0].value == "YA RLY"):
                    allowContinue = True
        
        #checks whether preceeding statements are inside a switch case clause
        if(mainCodeBlock.bSyntax.switchClause):
            if(i.tokens[0].value == "OMG"):
                # print(str(i.tokens[1].value) + "|||" + str(mainCodeBlock.bSyntax.impVarValue))
                if(i.tokens[1].value != mainCodeBlock.bSyntax.impVarValue):
                    allowContinue = False
                elif(i.tokens[1].value == mainCodeBlock.bSyntax.impVarValue):
                    allowContinue = True
                    mainCodeBlock.bSyntax.executeDefaultSwitch = 0

            if(i.tokens[0].value == "OMGWTF" and mainCodeBlock.bSyntax.executeDefaultSwitch == 0):
                allowContinue = False
            elif(i.tokens[0].value == "OMGWTF" and mainCodeBlock.bSyntax.executeDefaultSwitch == 1):
                allowContinue = True
        
        #if a GTFO is found, exits a clause until a OIC is found
        if(i.tokens[0].value == "GTFO"):
            allowContinue = False
    
        if(allowContinue):
            #if the line is print statement, prints the tokens preceeding the output keyword
            if(i.type == "Assignment Statement" and i.hasExpFlag):
                interpreter.assignExpression(mainCodeBlock, i, 0)

            if(i.type == "Expression Statement"):
                interpreter.assignImplicit(mainCodeBlock, i)

            if(i.type == "Print Statement"):
                for j in range(len(i.tokens)):
                    printStr = interpreter.printStatement(mainCodeBlock,i,j)
                    if(printStr != ""):
                        executeTB.insert("end", printStr)
                    if(i.hasExpFlag):
                        executeTB.insert("end", str(interpreter.evalExpression(i.expStack)))
                        break
                executeTB.insert("end",'\n')

            if(i.type == "If/Else Statement"):
                interpreter.parseIfElseClause(mainCodeBlock)

            if(i.type == "Switch Statement Opening"):
                interpreter.parseSwitchClause(mainCodeBlock)
    
    executeTB.place(x=0,y=40)

    #prints the symbol table to the symbol table text box
    for i in mainCodeBlock.symbolTable:
        symbolTB.insert("end", '  {:<40s}{:>8s}'.format(str(i.value),str(i.variableData)))
        symbolTB.insert("end", '\n')

    symbolTB.place(x=375, y=50)


#function that selects a file
def selectFile():
    global filename, fileSelected
    filename = askopenfilename()
    
    input_file = open(filename)
    font = tkFont.Font(family="Arial", size="12")
    readFile = tkinter.Text(frameFileReader, width="42", height="20", font=font)

    read = input_file
    for i in read:
        readFile.insert("end", i)
    
    readFile.place(x=0,y=30)

    readTokens()
    

listBox1 = tkinter.Listbox(top)
listBox1.insert(1,"Hello There")

#creates the frames
frameExecute = tkinter.Frame(top, background="#DCDCDC", width="1100", height="300")
frameExecute.place(x=0,y=350)

frameInterpreter = tkinter.Frame(top, background="#DCDCDC", width="750", height="350")
frameInterpreter.place(x=350,y=0)

frameFileReader = tkinter.Frame(top, background="#DCDCDC", width="350", height="350")
frameFileReader.place(x=0,y=0)

#place elements for the filereader frame
selectFileBtn = tkinter.Button(frameFileReader,  width="46", command= selectFile, text="Select a file")
selectFileBtn.place(x=0, y=0)

#place elements for the Interpreter frame
font = tkFont.Font(family="Arial", size="15")
topLabel1 = tkinter.Label(frameInterpreter, text="Lexemes", font=font)
topLabel1.place(x=160,y=6)

topLabel2 = tkinter.Label(frameInterpreter, text="Symbol Table", font=font)
topLabel2.place(x=500,y=6)

#place elements for the Execute frame
executeCode = tkinter.Button(frameExecute, width="108", text="Execute", font=font, command= executeCode)
executeCode.place(x=0, y=0)

#set sizes for the window
top.geometry("1100x650") 

#adds the elements to the windows 
top.mainloop()