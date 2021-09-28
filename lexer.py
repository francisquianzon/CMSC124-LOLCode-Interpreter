import re

class Token:
    def __init__(self, value, type_, lineNumber):
        self.value = value              #value of the token
        self.type = type_               #type of the token
        self.lineNumber = lineNumber    #stores the line number of the token
        self.classification =  ""       #description of the token
        self.variableFlag = 0           #flag for the variable to determine whether it has a value
        self.variableData = None        #data stored in a variable token

    def classify(self, classification):
        self.classification = classification

    def nextToken(self, next):
        self.next = next

# a syntax class contains flags that will help in checking the syntax of the code
class Syntax:
    def __init__(self):
        self.commentFlag = 0
        self.line = 0


keywords = [
        'HAI',
        'KTHXBYE',
        'I HAS A',
        'ITZ',
        'OBTW',
        'TLDR',
        'R',
        'SUM OF',
        'DIFF OF',
        'PRODUKT OF',
        'QUOSHUNT OF',
        'MOD OF',
        'BIGGR OF',
        'SMALLR OF',
        'BOTH OF',
        'EITHER OF',
        'WON OF',
        'NOT',
        'ANY OF',
        'ALL OF',
        'BOTH SAEM',
        'DIFFRINT',
        'SMOOSH',
        'MAEK',
        'A',
        'IS NOW A',
        'VISIBLE',
        'GIMMEH',
        'O RLY?',
        'YA RLY',
        'MEBBE',
        'NO WAI',
        'OIC',
        'WTF?',
        'OMG',
        'OMGWTF',
        'IM IN YR',
        'UPPIN',
        'NERFIN',
        'YR',
        'TIL',
        'WILE',
        'IM OUTTA YR',
        'AN',
        'WIN',
        'FAIL',
        'IT',
        'GTFO'
    ]

#switches the value from 0 to 1 or vice versa
def switchBool(val):
    if(val):
        return 0
    else:
        return 1

#turns a list of strings into a single string
def toString(line): 
    newString = ''
    for i in line:
        newString += i + ' '

    return newString[:-1]

#function that returns an error
def tokenError(errortype, line, token):
    print("TokenError at line " + str(line))
    print(errortype + " '" + str(token) + "'")
    quit()

#function that identifies a lexeme
def identifyLexeme(lexeme, lexSyntax): 

    #checks if the lexeme is found in the keywords
    for i in keywords:
        if(re.findall(lexeme,i)):
            return 1
            
            
    # checks if the lexeme is a valid variable, integer, float, string.
    YARN = re.search(r'".*"', lexeme)
    if(YARN):
        return 2
    variable = re.search(r'[a-zA-Z][a-zA-Z0-9_]*',lexeme)
    if(variable):
        return 3
    NUMBAR = re.search(r'[+-]?[0-9]+\.[0-9]+', lexeme)
    if(NUMBAR):
        return 4
    NUMBR = re.search(r'-?[1-9][0-9]*|0', lexeme)
    if(NUMBR):
        return 5

    return None #invalid lexeme

#function that checks if a lexeme is a NUMBR or NUMBAR or a variable identifier and returns it as is
def identifyInteger(lexeme, lexSyntax):
    lexeme = str(lexeme)

    if(lexSyntax.commentFlag == 0): #does not search for invalid characters in comments
        #a checker for an invalid variable (a variable that does not start with a letter)
        invalid = re.search(r'-?[0-9_][a-zA-Z][a-zA-Z0-9_]*', lexeme)
        if(invalid):
            tokenError("Invalid variable name", lexSyntax.line, lexeme)

        #a checker for invalid characters in a variable
        specialChar = re.search(r'[$&+,:;=?@#|\'\-^*()%!]', lexeme)
        if(specialChar):
            tokenError("Invalid character", lexSyntax.line, lexeme)

    variable = re.search(r'[a-zA-Z][a-zA-Z0-9_]*',lexeme)
    if(variable):
        return lexeme

    NUMBAR = re.search(r'[+-]?[0-9]+\.[0-9]+', lexeme)
    if(NUMBAR):
        return float(NUMBAR.group())

    NUMBR = re.search(r'-?[1-9][0-9]*|0', lexeme)
    if(NUMBR):
        return int(NUMBR.group())
    
#function that checks if a lexeme is a keyword
def checkInKeywords(lexeme):   
    for i in keywords:
        if(lexeme == i):
            return 1
    
    return 0

#function that puts a descripton to a keyword
def classifyKeyword(token):
    keyword = token.value

    HAI = re.search(r'HAI', keyword)
    KTHXBYE = re.search(r'KTHXBYE', keyword)

    I_HAS_A = re.search(r'I\sHAS\sA', keyword)
    ITZ = re.search(r'ITZ', keyword)
    R = re.search(r'R', keyword)

    SUM_OF = re.search(r'SUM\sOF', keyword)
    DIFF_OF = re.search(r'DIFF\sOF', keyword)
    PRODUKT_OF = re.search(r'PRODUKT\sOF', keyword)
    QUOSHUNT_OF = re.search(r'QUOSHUNT\sOF', keyword)
    MOD_OF = re.search(r'MOD\sOF', keyword)
    BIGGR_OF = re.search(r'BIGGR\sOF', keyword)
    SMALLR_OF = re.search(r'SMALLR\sOF', keyword)

    BOTH_OF = re.search(r'BOTH\sOF', keyword)
    EITHER_OF = re.search(r'EITHER\sOF', keyword)
    WON_OF = re.search(r'WON\sOF', keyword)
    NOT = re.search(r'NOT', keyword)
    ANY_OF = re.search(r'ANY\sOF', keyword)
    ALL_OF = re.search(r'ALL\sOF', keyword)

    BOTH_SAEM = re.search(r'BOTH\sSAEM', keyword)
    DIFFRINT = re.search(r'DIFFRINT', keyword)

    SMOOSH = re.search(r'SMOOSH', keyword)

    MAEK = re.search(r'MAEK', keyword)
    IS_NOW_A = re.search(r'IS\sNOW\sA', keyword)

    VISIBLE = re.search(r'VISIBLE', keyword)
    GIMMEH = re.search(r'GIMMEH', keyword)

    O_RLY = re.search(r'O\sRLY?', keyword)
    YA_RLY = re.search(r'YA\sRLY?', keyword)
    MEBBE = re.search(r'MEBBE', keyword)
    NO_WAI = re.search(r'NO\sWAI', keyword)
    OIC = re.search(r'OIC', keyword)

    WTF = re.search(r'WTF?', keyword)
    OMG = re.search(r'OMG', keyword)
    OMGWTF = re.search(r'OMGWTF', keyword)

    A = re.search(r'^A$', keyword)
    AN = re.search(r'^AN$', keyword)

    WIN = re.search(r'WIN', keyword)
    FAIL = re.search(r'FAIL', keyword)

    BTW = re.search(r'^BTW$', keyword)
    OBTW = re.search(r'OBTW', keyword)
    TLDR = re.search(r'TLDR', keyword)

    IT = re.search(r'^IT$', keyword)
    GTFO = re.search(r'^GTFO$', keyword)

    if(HAI or KTHXBYE):
        token.classify("Code Delimiter")
    if(I_HAS_A):
        token.classify("Variable Declaration")
    if(ITZ or R):
        token.classify("Variable Assignment")
    if(SUM_OF or DIFF_OF or PRODUKT_OF or QUOSHUNT_OF or MOD_OF or BIGGR_OF or BIGGR_OF or SMALLR_OF):
        token.classify("Arithmetic Operator")
    if(BOTH_OF or EITHER_OF or WON_OF or NOT or ANY_OF or ALL_OF):
        token.classify("Boolean Operator")
    if(BOTH_SAEM or DIFFRINT):
        token.classify("Comparison Operator")
    if(SMOOSH):
        token.classify("String Concatenation")
    if(MAEK or IS_NOW_A):
        token.classify("Typecasting")
    if(VISIBLE or GIMMEH):
        token.classify("Input/Output Keyword")
    if(O_RLY or YA_RLY or MEBBE or NO_WAI):
        token.classify("If/Then Keyword")
    if(OIC or GTFO):
        token.classify("Block Delimiter")
    if(WTF or OMG or OMGWTF):
        token.classify("Switch-case Keyword")
    if(A or AN):
        token.classify("Separator")
    if(WIN or FAIL):
        token.classify("TROOF Literal")
        token.type = "Literal"
    if(OBTW or TLDR or BTW):
        token.classify("Comment Separator")
    if(IT):
        token.classify("Implicit Variable")
    

#function that tokenizes a lexeme
def tokenize(lexemes, tokens, lexSyntax):
    
    #iterates over the list of lexemes and creates a token
    for i in lexemes:
        i = str(i)

        #creates a new token object for keywords
        if(checkInKeywords(i)):
            newToken = Token(i, "Keyword", lexSyntax.line)
            classifyKeyword(newToken)

        #creates a new token object for variables
        if(identifyLexeme(i,lexSyntax) == 3):
            newToken = Token(i, "Literal", lexSyntax.line)
            newToken.classify("Variable Identifier")

        #creates a new token object for NUMBAR
        elif(identifyLexeme(i,lexSyntax) == 4):
            newToken = Token(identifyInteger(i,lexSyntax), "Literal", lexSyntax.line)
            newToken.classify("NUMBAR Literal")

        #creates a new token object for NUMBR
        elif(identifyLexeme(i,lexSyntax) == 5):
            newToken = Token(identifyInteger(i,lexSyntax), "Literal", lexSyntax.line)
            newToken.classify("NUMBR Literal")

        #creates a new token object for YARN
        elif(identifyLexeme(i,lexSyntax) == 2):
            newToken = Token(i, "Literal", lexSyntax.line)
            newToken.classify("String Literal")

        #when an 'OBTW' keyword is found, sets a flag and ignores the preceeding statements until 'TLDR' is found
        if(newToken.classification == "Comment Separator"):
            lexSyntax.commentFlag = switchBool(lexSyntax.commentFlag)

        if(lexSyntax.commentFlag == 1 or newToken.value == "TLDR"):
            break

        tokens.append(newToken)
    
    #creates a newline token; ensures that no new line is created succeedingly
    if(len(tokens)):
        if(tokens[len(tokens)-1].type != "NewLine"):
    
            newlineToken = Token("NL", "NewLine", lexSyntax.line)
            newlineToken.classify("New Line")
            tokens.append(newlineToken)

#creates tokens from a line of code
def createTokens(line, listOfTokens, lexSyntax): 
    tokens = []
    lexemes = []
    string = []
    stringLoop = 0

    lexSyntax.line += 1 #stores the line number of the statements

    #adds each character to the tokens list
    for i in line:
        
        #checks if lexeme is a comment (starts with BTW); doesn't read the line if BTW is found
        comment = re.search(r'^BTW$', i)
        if(comment):
            break

        #checks if lexeme is a single word string
        singleStringDelimiter = re.search(r'".*"', i)
        if(singleStringDelimiter):
            tokens.append(i)
            continue
    
        #checks if lexeme is a string; finds the start and end delimiter
        stringDelimiter = re.search(r'"', i)
        if(stringDelimiter or stringLoop == 1):
            if(stringDelimiter):
                stringLoop = switchBool(stringLoop)

            #compiles the string until end delimiter is found
            if(stringLoop): 
                string.append(i)
                continue
            
            #if end delimiter is found, adds to the list of tokens
            elif(stringDelimiter):
                string.append(i)
                tokens.append(toString(string))
                string.clear()
                continue
            
            #if no delimiter is found
            else:
                tokenError("Invalid token: incomplete string ", lexSyntax.line, i)

        if(stringLoop == 0):
            #searches the word in the list of keywords
            if(checkInKeywords(i) and len(lexemes) == 0):
                tokens.append(i)

            #if lexeme is not a keyword
            else:
                if(identifyLexeme(i,lexSyntax) == 1): #checks if the lexeme is found as part of a keyword; if so, adds to the list of lexemes
                    lexemes.append(i)

                    #checks if the combination of lexemes forms a keyword
                    if(checkInKeywords(toString(lexemes))):
                        tokens.append(toString(lexemes))
                        lexemes.clear()

                #if lexeme is not part of a keyword
                else:
                    if(identifyLexeme(i,lexSyntax)):
                        tokens.append(identifyInteger(i,lexSyntax))
                    else:
                        tokenError("Invalid lexeme", lexSyntax.line, i)

    tokenize(tokens, listOfTokens, lexSyntax)