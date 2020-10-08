##create a copy of an object 
import copy
##regular expression library (search pattern)
import re

#lets build a LISP to C compiler!
# from LISP
# i.e (add 2 (subtract 4 2))  
# to C
## add(2, (subtract(4, 2))


#There are 3 parts to a compiler
# 1 PARSING
## a. Lexical Analysis/Tokenization (vocabulary)
## b. Syntactic Analysis/Parsing (grammar)

# 2 TRANSFORMATION
## a. Traversal 
## b. Transform via Traversal 

# 3 CODE GENERATION
## a. Stringify!


#Tokenizer function receives starting input
# i.e (add 2 (subtract 4 2))
def tokenizer(input_expression):
    #counter variable for iterating through input array 
    current = 0
    #array to store computed tokens
    tokens = []
    ##use regex library to create search patterns for
    #letters a,z
    alphabet = re.compile(r"[a-z]", re.I);
    #numbers 1-9
    numbers = re.compile(r"[0-9]");
    #white space
    whiteSpace = re.compile(r"\s");
    #iterate through input
    while current < len(input_expression):
        #track position
        char = input_expression[current]
        #If white space is detected, no token created
        if re.match(whiteSpace, char):
            current = current+1
            continue
        #create + add token to array for open parens
        if char == '(':
            tokens.append({
                'type': 'left_paren',
                'value': '('
            })
            #continue iterating
            current = current+1
            continue
        #create + add token to array for closed parens
        if char == ')':
            tokens.append({
                'type': 'right_paren',
                'value': ')'
            })
            #continue iterating
            current = current+1
            continue
        #create + add token to array for numbers
        if re.match(numbers, char):
            value = ''
            #nested iteration if a number is multi-num 
            while re.match(numbers, char):
                value += char
                current = current+1
                char = input_expression[current];
            tokens.append({
                'type': 'number',
                'value': value
            })
            continue
        #create + add token to array for letters
        if re.match(alphabet, char):
            value = ''
            #nested iteration if a word is multi-char (all are in this case)
            while re.match(alphabet, char):
                value += char
                current = current+1
                char = input_expression[current]
            tokens.append({
                'type': 'name',
                'value': value
            })
            continue
        #error condition if we find an unknown value in the input
        raise ValueError('what are THOSE?: ' + char);
    return tokens

#The parse function creates an Abstract Syntax Tree given the computed
#tokens from the previous function   
def parser(tokens):
    #keep track of position while iterating
    global current
    current = 0
    #nested walk function for building an abstract syntax tree
    def walk():
        #keep track of position while iterating? 
        global current
        token = tokens[current]
        #if a number is encountered, return a "NumberLiteral" node
        if token.get('type') == 'number':
            current = current + 1
            return {
                'type': 'NumberLiteral',
                'value': token.get('value')
            }
          
        #if open parentheses encountered, return a "CallExpression" node
        if token.get('type') == 'left_paren':
           #skip past the parenthesis, we're not storing that
            current = current + 1
            token = tokens[current]
            #store the name of operation
            node = {
                'type': 'CallExpression',
                'name': token.get('value'),
                'params': []
            }
            #and this node will have child nodes as parameters
            #and input expression can have many nested expressions
            #so we'll use recursion to build a tree of relations!
            current = current + 1
            token = tokens[current]
            #until the expression ends with a closed parens
            while token.get('type') != 'right_paren':
                #recursively add nodes to the params array via the walk function
                node['params'].append(walk());
                token = tokens[current]
            current = current + 1
            return node
        #error if unknown type encountered
        raise TypeError(token.get('type'))
    
    
    #Let's initialize an empty Abstract Syntax Tree
    ast = {
        'type': 'Program',
        'body': []
    }
    #then populate it by calling the walk function
    #until the global current variable reaches the end of the token array
    while current < len(tokens):
        ast['body'].append(walk())
    #return the completed AST
    return ast


#Helper function for the transformer that enables
#traversing our newly created AST
def traverser(ast, visitor):

    #we take the child node (current AST) and parent node (new AST) as
    #inputs
    def traverseArray(array, parent):
       #iterate through every parameter element in our current AST
        for child in array:
            #and traverse each
            traverseNode(child, parent)
    
    ##we again take the child node (current AST) and parent node (new AST) as
    #inputs. 
    def traverseNode(node, parent):
       #this is our highest level traversal function
       #store a reference to the new AST
        method = visitor.get(node['type'])
        if method:
            method(node, parent)
        #if only python had built-in switch statements like JS, lol its all good
        #we can use a series of if statements
        #if its the top level
        if node['type'] == 'Program':
            #traverse the body
            traverseArray(node['body'], node)
        #if its a call expression
        elif node['type'] == 'CallExpression':
            #traverse the nested paramemeters
            traverseArray(node['params'], node)
        #if its a number literal
        elif node['type'] == 'NumberLiteral':
          #break
            0
        else:
          #error for unknown type 
            raise TypeError(node['type'])
    traverseNode(ast, None)

# using our newly created traversal functions,
#we'll transform our exsiting AST
def transformer(ast):
   #letsd define an empty new AST
    newAst = {
        'type': 'Program',
        'body': []
    }
    #we'll copy the old one and fill the new one with it
    oldAst = ast
    ast = copy.deepcopy(oldAst)
    #let's store a reference to the newAST's body in this context property
    ast['_context'] = newAst.get('body')

    #helper function when a call expression is encountered 
    def CallExpressionTraverse(node, parent):
      #create a call expression node
        expression = {
            'type': 'CallExpression',
            'callee': {
                'type': 'Identifier',
                'name': node['name']
            },
            'arguments': []
        }
        #set the current context to its child args
        node['_context'] = expression['arguments']

        #store nested call expression references
        if parent['type'] != 'CallExpression':
            expression = {
                'type': 'ExpressionStatement',
                'expression': expression
            }
        #store the expression in the context property
        parent['_context'].append(expression)

    #helper function used when a number literal is encountered
    #during traversal. We'll just store the relevant node as we encounter it
    #in the context property
    def NumberLiteralTraverse(node, parent):
        parent['_context'].append({
            'type': 'NumberLiteral',
            'value': node['value']
        })
    #traverse through the AST using our helper functions
    #until we've fully populated the new AST
    traverser( ast , {
        'NumberLiteral': NumberLiteralTraverse,
        'CallExpression': CallExpressionTraverse 
    })
    #return the new AST
    return newAst


##last part! Code generation
#a recursive stringify function that iterates
#through the newly created AST, node by node, continually
#building a string output given the values in each node.
def codeGenerator(node):
    if node['type'] == 'Program':
        return '\n'.join([code for code in map(codeGenerator, node['body'])])
    elif node['type'] == 'Identifier':
        return node['name']
    elif node['type'] == 'NumberLiteral':
        return node['value']
    elif node['type'] == 'ExpressionStatement':
        expression = codeGenerator(node['expression']) 
        return '%s;' % expression
    elif node['type'] == 'CallExpression':
        callee = codeGenerator(node['callee']) 
        params = ', '.join([code for code in map(codeGenerator, node['arguments'])])
        return "%s(%s)" % (callee, params)
    else:
        raise TypeError(node['type'])

#finally, let's put it all together
def compiler(input_expression):
    #given an input expression, create a set of tokens
    tokens = tokenizer(input_expression)
    #create an abstract syntax tree given those tokens
    ast    = parser(tokens)
    #create a transformed AST given the existing one
    newAst = transformer(ast)
    #stringify the transformed AST into an output expression
    output = codeGenerator(newAst)
    #return!
    return output

def main():
    #test 
    input = "(add 2 (subtract 4 2))"
    output = compiler(input)
    print(output)


if __name__ == "__main__":
    main()

