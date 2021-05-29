#!/usr/bin/env python3
"""6.009 Lab 9: Snek Interpreter"""

import doctest
# NO ADDITIONAL IMPORTS!


###########################
# Snek-related Exceptions #
###########################

class SnekError(Exception):
    """
    A type of exception to be raised if there is an error with a Snek
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """
    pass


class SnekSyntaxError(SnekError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """
    pass


class SnekNameError(SnekError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """
    pass


class SnekEvaluationError(SnekError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SnekNameError.
    """
    pass

##############################
# Environments and Fucntions #
##############################

class Environment:
    def __init__(self, parent = None):
        self.parent = parent  # This way we can make an environment point to another.
        self.values = dict()  # Set it as a dictionary of variable names to variable value.
        
    def __setitem__(self, variable, value):
        self.values[variable] = value
                
    def __getitem__(self, variable):
        try:
            if variable in self.values:
                return self.values[variable]
            else:
                return self.parent[variable]
        except:
            raise SnekNameError  # If the variable isn't in the environment or parents, raise the error.
            
    def __contains__(self, variable):
        if variable in self.values:
            return True
        else:
            if self.parent is not None:
                return variable in self.parent  # Check if the variable exsts in the parents if it is not in the self environment.
            else:
                return False
            
class Functions:
    def __init__(self, parameters, body, environment = None):
        self.parameters = parameters
        self.body = body
        self.environment = environment
        
    def __call__(self, arguments):
        if len(arguments) != len(self.parameters):
            raise SnekEvaluationError
        environment = Environment(self.environment)
        
        for i in range(len(arguments)):
            environment[self.parameters[i]] = arguments[i]
        return evaluate(self.body, environment)  # Set the parameters to the arguments and then evaluate.

############################
# Tokenization and Parsing #
############################


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Snek
                      expression
    """
    new_source = source.replace(')', ' ) ')
    new_source = new_source.replace('(', ' ( ')
    new_source = new_source.replace('\n', ' \n ')  # We put spaces around the special characters so we can call .split() at the end.

    if '\n' in new_source:
        new_source = new_source.split('\n')  # Split at the new lines so we can analyse lines separately.
    else:
        new_source = [new_source]

    for i in range(len(new_source)):
        if ';' in new_source[i]:
            new_source[i] = new_source[i][:new_source[i].index(';')]  # If there is a comment, only add everything up to the comment.
            
    new_source = ''.join(new_source).split()  # Turn the list back into a string, and then split at the whitedspaces.
    return new_source


def helper(expression):
    """
    Function that checks if an input expression is valid.
    """
    if expression != []:
        if expression[0] == 'function':
            if len(expression) != 3:  # Function has 3 elements.
                raise SnekSyntaxError
            if not isinstance(expression[1], list):  # Second element must be a list.
                raise SnekSyntaxError
            for ele in expression[1]:
                if isinstance(ele, (int, float)):  # If any parameter can be turned into an int or float, we have a Syntax Error.
                    raise SnekSyntaxError
                
        elif expression[0] == ':=':
            if not (len(expression) == 3 and expression[1] and isinstance(expression[1], (str,list))):  # Assignment must have a string for second element.
                raise SnekSyntaxError
            if True in [isinstance(e, (int, float)) for e in expression[1]]:  # If variable name is not a string, we have an error.
                raise SnekSyntaxError
        
def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    if len(tokens) == 0:
        return None
    if tokens.count('(') != tokens.count(')'):  # If we don't have the same number of open and closed parantheses, we have an error.
        raise SnekSyntaxError
    if (len(tokens) > 1 and ('(' not in tokens and ')' not in tokens)):
        raise SnekSyntaxError
                
    tokens_copy = tokens[:]  # So we don't modify the input.
        
    def parse_expression(tokens):
        token = tokens[0]
        del tokens[0]  # We delete the first value, so we can analyse the first token and the rest separately.
        if token == '(':
            expression = []
            while tokens[0] != ')':  # We only stop once we get to a closed parentheses.
                expression.append(parse_expression(tokens))  # We recurse on the rest of the tokens.
            tokens.remove(tokens[0])  # We remove closed paretheses so we can get to the rest of the tokens.
            helper(expression)  # Make sure each expression is valid.
            return expression
        elif token == ')':  # If the first token is a right parantheses, we return a snytax error.
            raise SnekSyntaxError
        else:
            try:
                if '.' in token:
                    return float(token)  # Only a float would have a decimal point in it.
                else:
                    return int(token)
            except:
                return token  # If the token isn't a number, we can just add it to expression.
    
    parsed_expression =  parse_expression(tokens_copy)  
    return parsed_expression


######################
# Built-in Functions #
######################


def mul(expression):
    """
    Function that multiplies all elements in a list.
    """
    ans = 1
    for i in expression:
        ans = ans * i
    return ans

def div(expression):
    """
    Function that divides first element in list by the rest.
    """
    if len(expression) == 1:
        return expression[0]
    else:
        return expression[0] / mul(expression[1:])  # We can multiply all the divisors together.


snek_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    '*': mul,
    '/': div
}

snek_environment = Environment()
snek_environment.values = snek_builtins

##############
# Evaluation #
##############


def evaluate(tree, environment = None):
    """
    Evaluate the given syntax tree according to the rules of the Snek
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    
    if environment == None:
        environment = Environment()
        environment.parent = snek_environment  # Setting up the environment if not passed in as the lab describes.
    
    if not isinstance(tree, list):
        if isinstance(tree, str):  # If we have a variable, find it in the environment.
            return environment[tree]
        
        elif isinstance(tree, int) or isinstance(tree, float):
            return tree  # Individual number are to be returned.
                
        elif isinstance(tree, Functions):
            return environment[tree]  # If we have a function, find the function in the environment and return it.
        
    elif isinstance(tree, list):
        if tree[0] == ':=':  # If we have an assignment, we do this:
            if isinstance(tree[1], list):  # This is the case where we are doing an easy function assignment.
                environment[tree[1][0]] = Functions(tree[1][1:], tree[2], environment)  # The 1st element of the first index is the name, the rest are the parameters. Second index is the body.
                return environment[tree[1][0]]
            
            variable = tree[1]  # In this case, we are assigning a variable.
            environment[variable] = evaluate(tree[2], environment)  # We recurse on the value.
            return environment[variable]
            
        elif tree[0] == 'function':
            return Functions(tree[1], tree[2], environment)  # Simple function creation.
            
        else:
            operation = evaluate(tree[0], environment)  # If we don't have a function or assignment, then the first element is a function/operation in the environment.
        arguments = []
        for i in range(1, len(tree)):
            arguments.append(evaluate(tree[i], environment))  # Create the arguments for the function.
        try:
            return operation(arguments)  # Try to do the function with the arguments passed in.
        except TypeError:  #If the arguments are the wrong type, we have an evaluation error.
            raise SnekEvaluationError 

def REPL():
    """
    Function to allow user to write in LISP in a global environment.
    """
    user_input = input('in>')
    environment = Environment()
    environment.parent = snek_environment
    while user_input != 'QUIT':
        try:
            print('out> ' + str(evaluate(parse(tokenize(str(user_input))), environment)))
        except:
            print("ERROR")
        user_input = input('in>')
        
def result_and_env(expression, environment = None):
    """
    Function that allows us to evaluate expression and return environment too.
    """
    if environment == None:
        environment = Environment()
        environment.parent = snek_environment
    return (evaluate(expression, environment), environment)
        


if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    pass
