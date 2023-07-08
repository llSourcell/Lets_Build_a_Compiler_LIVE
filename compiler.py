import copy
import re

# Tokenizes the input expression by breaking it into individual tokens
def tokenize(input_expression):
    current = 0
    tokens = []
    alphabet_pattern = re.compile(r"[a-z]", re.I)
    numbers_pattern = re.compile(r"[0-9]")
    whitespace_pattern = re.compile(r"\s")

    while current < len(input_expression):
        char = input_expression[current]

        if re.match(whitespace_pattern, char):
            current += 1
            continue

        if char == '(':
            tokens.append({
                'type': 'left_paren',
                'value': '('
            })
            current += 1
            continue

        if char == ')':
            tokens.append({
                'type': 'right_paren',
                'value': ')'
            })
            current += 1
            continue

        if re.match(numbers_pattern, char):
            value = ''
            while re.match(numbers_pattern, char):
                value += char
                current += 1
                char = input_expression[current]
            tokens.append({
                'type': 'number',
                'value': value
            })
            continue

        if re.match(alphabet_pattern, char):
            value = ''
            while re.match(alphabet_pattern, char):
                value += char
                current += 1
                char = input_expression[current]
            tokens.append({
                'type': 'name',
                'value': value
            })
            continue

        raise ValueError('Invalid character: ' + char)

    return tokens


# Parses the tokens into an abstract syntax tree (AST)
def parse(tokens):
    current = 0

    def walk():
        nonlocal current
        token = tokens[current]

        if token.get('type') == 'number':
            current += 1
            return {
                'type': 'NumberLiteral',
                'value': token.get('value')
            }

        if token.get('type') == 'left_paren':
            current += 1
            token = tokens[current]
            node = {
                'type': 'CallExpression',
                'name': token.get('value'),
                'params': []
            }
            current += 1
            token = tokens[current]
            while token.get('type') != 'right_paren':
                node['params'].append(walk())
                token = tokens[current]
            current += 1
            return node

        raise TypeError(token.get('type'))

    ast = {
        'type': 'Program',
        'body': []
    }

    while current < len(tokens):
        ast['body'].append(walk())

    return ast


# Traverses the AST and applies handlers to different node types
def traverse(ast, node_handlers):
    def traverse_array(array, parent):
        for child in array:
            traverse_node(child, parent)

    def traverse_node(node, parent):
        handler = node_handlers.get(node['type'])
        if handler:
            handler(node, parent)

        if node['type'] == 'Program':
            traverse_array(node['body'], node)
        elif node['type'] == 'CallExpression':
            traverse_array(node['params'], node)
        elif node['type'] == 'NumberLiteral':
            pass
        else:
            raise TypeError(node['type'])

    traverse_node(ast, None)


# Transforms the AST by replacing CallExpression nodes with a different structure
def transform(ast):
    new_ast = {
        'type': 'Program',
        'body': []
    }
    old_ast = ast
    ast = copy.deepcopy(old_ast)
    ast['_context'] = new_ast.get('body')

    def traverse_call_expression(node, parent):
        expression = {
            'type': 'CallExpression',
            'callee': {
                'type': 'Identifier',
                'name': node['name']
            },
            'arguments': []
        }
        node['_context'] = expression['arguments']

        if parent['type'] != 'CallExpression':
            expression = {
                'type': 'ExpressionStatement',
                'expression': expression
            }

        parent['_context'].append(expression)

    def traverse_number_literal(node, parent):
        parent['_context'].append({
            'type': 'NumberLiteral',
            'value': node['value']
        })

    traverse(ast, {
        'NumberLiteral': traverse_number_literal,
        'CallExpression': traverse_call_expression
    })

    return new_ast


# Generates code from the transformed AST
def generate_code(node):
    if node['type'] == 'Program':
        return '\n'.join([code for code in map(generate_code, node['body'])])
    elif node['type'] == 'Identifier':
        return node['name']
    elif node['type'] == 'NumberLiteral':
        return node['value']
    elif node['type'] == 'ExpressionStatement':
        expression = generate_code(node['expression'])
        return '%s;' % expression
    elif node['type'] == 'CallExpression':
        callee = generate_code(node['callee'])
        params = ', '.join([code for code in map(generate_code, node['arguments'])])
        return "%s(%s)" % (callee, params)
    else:
        raise TypeError(node['type'])


# Compiles the input expression into code
def compile_program(input_expression):
    tokens = tokenize(input_expression)
    ast = parse(tokens)

    def handle_program(node, parent):
        # Custom handling for Program nodes
        print("Handling Program node:", node)

    def handle_call_expression(node, parent):
        # Custom handling for CallExpression nodes
        print("Handling CallExpression node:", node)

    def handle_number_literal(node, parent):
        # Custom handling for NumberLiteral nodes
        print("Handling NumberLiteral node:", node)

    node_handlers = {
        'Program': handle_program,
        'CallExpression': handle_call_expression,
        'NumberLiteral': handle_number_literal
    }

    traverse(ast, node_handlers)
    new_ast = transform(ast)
    output = generate_code(new_ast)

    return output


def main():
    input_expression = "(add 2 (subtract 4 2))"
    output = compile_program(input_expression)
    print(output)


if __name__ == "__main__":
    main()

