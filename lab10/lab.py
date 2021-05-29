"""6.009 Lab 10: Snek Interpreter Part 2"""

import sys
sys.setrecursionlimit(5000)

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

####################################
# Environments, Fucntions and Pair #
####################################

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

class Pair:
    def __innit__(self, cells):
        if len(cells) != 2:
            raise SnekEvaluationError
        self.car = cells[0]
        self.cdr = cells[1]
        
    def __str__(self):
        ans = ""
        while isinstance(self, Pair):
            ans += f"{self.car},"
            self = self.cdr
        ans = ans[:len(ans) - 1]
        return ans


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
    
def equal_to(expression):
    """
    Function that determines whether all elements in expression are equal.
    """
    for i in range(len(expression) - 1):
        if expression[i] == expression[i + 1]:
            continue
        else:
            return False
    return True

def greater_than(expression):
    """
    Function that determines whether elements in expression are in decreasing order.
    """
    for i in range(len(expression) - 1):
        if not expression[i] > expression[i + 1]:
            return False
    return True

def geq(expression):
    """
    Function that determines whether elements in expression are in nonincreasing order
    """
    for i in range(len(expression) - 1):
        if not expression[i] >= expression[i + 1]:
            return False
    return True

def less_than(expression):
    """
    Function that determines whether elements in expression and in decreasing order.
    """
    for i in range(len(expression) - 1):
        if not expression[i] < expression[i + 1]:
            return False
    return True
    
def leq(expression):
    """
    Function that determines whether elements in expression are in non increasing order.
    """
    for i in range(len(expression) - 1):
        if not expression[i] <= expression[i + 1]:
            return False
    return True

def cons(cells):
    """
    Constructs a Pair instance from the passed in cells.
    """
    car = cells[0]
    cdr = cells[1]
    cons_cells = Pair()
    cons_cells.car = car
    cons_cells.cdr = cdr
    return cons_cells

def car(cons_cell):
    """
    Retrieves the car from a given cons cell.
    """
    try:
        return cons_cell[0].car
    except:
        raise SnekEvaluationError
        
def cdr(cons_cell):
    """
    Retrieves the cdr from a given cons cell.
    """
    try:
        return cons_cell[0].cdr
    except:
        raise SnekEvaluationError


def make_linked_list(args):
    '''
    Given a Python list of arguments that are length 0 or greater, create
    a LISP linked list representation
    '''
    if len(args) == 0:
        return None
    else:
        return cons([args[0], make_linked_list(args[1:])])  # This way we ensure the very last element is None.


def length(list_, length_ = 1):
    """
    Function that recursively finds that length of a list.
    """
    linked_list = list_[0]
    if not linked_list:
        return 0
    
    if isinstance(linked_list, Pair):
        if linked_list.cdr is None:
            return length_  # Once we are at the last element in the list, we have counted the length and can return it.
        else:
            return length([linked_list.cdr], length_ + 1)
    else:
        raise SnekEvaluationError
    
def elt_at_index(list_and_index):
    """
    Finds the element at a given index of a list.
    """
    linked_list = list_and_index[0]
    index = list_and_index[1]
    
    if linked_list is None:
        raise SnekEvaluationError
    if not isinstance(linked_list, Pair):
        raise SnekEvaluationError
        
    if index == 0:
        return linked_list.car
    else:
        return elt_at_index([linked_list.cdr, index - 1])  # Move onto the next element in the list and decrease the index by 1.

def concat(linked_lists):
    """
    Function that concatenates linked linked_lists together.
    """
    if len(linked_lists) == 0:
        return None
    if len(linked_lists) == 1:
        return pair_copy(linked_lists[0])  # Always check if the linked list is one.
    
    result = pair_copy(linked_lists[0])
    
    if result == None:
        return concat(linked_lists[1:])  # When we come across empty linked_lists we ignore and continue concatenating.
    
    last_element_ = last_element(result)
    last_element_.cdr = concat(linked_lists[1:])  # Keep concatenating the rest of the lists together.
    
    return result

def last_element(pair):
    """
    Helper function that finds the last element in a list.
    """
    if isinstance(pair, Pair):
        if pair.cdr != None:
            return last_element(pair.cdr)  # Recursively find the last element.
        else:
            return pair
    raise SnekEvaluationError

def pair_copy(pair):
    """
    Function that creates copies of a linked lists.
    """
    if pair == None or isinstance(pair, (int, float)):
        return pair
    car = pair.car
    cdr = pair.cdr
    if isinstance(car, Pair):
        car = pair_copy(car)
    if isinstance(cdr, Pair):
        cdr = pair_copy(cdr)
        
    new_pair = Pair()
    
    new_pair.car = car
    new_pair.cdr = cdr

    return new_pair
        
def map_(function_and_list):
    """
    Function that maps a list depending on the input function.
    """
    if function_and_list[1] is None:  # If we have no function, return None.
        return None
    if not isinstance(function_and_list[1], Pair):
        raise SnekEvaluationError           
    return map_helper(function_and_list[0], function_and_list[1])


def map_helper(function, current_list_):
    """
    Function that evaluates an element in a list and moves to the next, or returns the finished list.
    """
    new_val = function([current_list_.car])
    if current_list_.cdr is None:
        return cons([new_val, None])  # If we have a one element current_list_t, we can just return that mapping.
    else:
        return cons([new_val, map_helper(function, current_list_.cdr)])  # Else we can continue mapping the rest of the elements.

def filter_(function_and_list):
    """
    Function that filters a list depending on the input function.
    """
    if function_and_list[1] is None:
        return None  # If we have no function, we can return None.
    if not isinstance(function_and_list[1], Pair):
        raise SnekEvaluationError       
    return filter_helper(function_and_list[0], function_and_list[1])

def filter_helper(function, list_):
    """
    Function that filters an element in a list, then moves onto the next recursively, or returns the finished list.
    """
    if list_.cdr is None:
        if function([list_.car]):
            return cons([list_.car, None])
        else:
            return None           
    if function([list_.car]):
        return cons([list_.car, filter_helper(function, list_.cdr)])
    else:
        return filter_helper(function, list_.cdr)

def reduce(function_list_initial):
    """
    Function that reduces a list depending on the initial value and function passed in.
    The inital value and first element in list are both put in the function, then the result
    and every next value in the list are also passed into the function to get a final result.
    """
    function = function_list_initial[0]
    list_ = function_list_initial[1]
    initial = function_list_initial[2]
    if list_ is None:
        return initial  # If we have no function, we can return the initial.
    if not isinstance(list_, Pair):
        raise SnekEvaluationError
    return reduce_helper(function, list_, initial) 

def reduce_helper(function, list_, result):
    """
    Function that applies given function on list element and current result.
    """
    if list_.cdr is None:
        return function([result, list_.car])  # If there is nothing after this element, we can return the result.
    else:
        return reduce_helper(function, list_.cdr, function([result, list_.car]))

def begin(expression):
    """
    Returns the expressions' last argument, with the rest evaluated.
    """
    return expression[-1]  # Everything has already been evaluated, so we can just return the last argument.
    

snek_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    '*': mul,
    '/': div,
    '=?': equal_to,
    '>': greater_than,
    '>=': geq,
    '<': less_than,
    '<=': leq,
    'not': lambda args: not args[0],  # Will just return the opposite of whatever the function gives.
    '#t': True,
    '#f': False,
    'cons': cons,
    'car': car,
    'cdr': cdr,
    'nil': None,
    'list': make_linked_list,
    'length': length,
    'elt-at-index': elt_at_index,
    'concat': concat,
    'map': map_,
    'filter': filter_,
    'reduce': reduce,
    'begin': begin
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
   
    elif isinstance(tree, list):
        if len(tree) == 0:
            raise SnekEvaluationError
            
        elif tree[0] == ':=':  # If we have an assignment, we do this:
            if isinstance(tree[1], list):  # This is the case where we are doing an easy function assignment.
                environment[tree[1][0]] = Functions(tree[1][1:], tree[2], environment)  # The 1st element of the first index is the name, the rest are the parameters. Second index is the body.
                return environment[tree[1][0]]
            
            variable = tree[1]  # In this case, we are assigning a variable.
            environment[variable] = evaluate(tree[2], environment)  # We recurse on the value.
            return environment[variable]
            
        elif tree[0] == 'function':
            return Functions(tree[1], tree[2], environment)  # Simple function creation.
        
        elif tree[0] == 'if':
            condition = tree[1]
            true_exp = tree[2]
            false_exp = tree[3]
            if evaluate(condition, environment):  # If the condition is true in the environment, we can evaluate the true expression.
                return evaluate(true_exp, environment)
            else:
                return evaluate(false_exp, environment)
            
        elif tree[0] == 'and':
            conditions = tree[1:]
            for condition in conditions:
                if not evaluate(condition, environment):  # We must check every condition, if any are false, then the whole thing is false.
                    return False
            return True
        
        elif tree[0] == 'or':
            conditions = tree[1:]
            for condition in conditions:
                if evaluate(condition, environment):  # If any of the conditions are true, then the whole thing is true and we can return True.
                    return True
            return False
        
        elif tree[0] == 'del':
            variable = tree[1]
            if variable not in environment.values:  # If the variable isn't in the current environmnet, we raise an Error.
                raise SnekNameError   
            else:
                value = environment.values[variable]
                del environment.values[variable]  # Delete the variable from the environment once we have the value.
                return value
                
        elif tree[0] == 'let':
            variables = tree[1]
            body = tree[2]
            new_environment = Environment()
            new_environment.parent = environment  # Create the new environment and set it's parent to the original environment.
            
            for variable in variables:
                new_environment[variable[0]] = evaluate(variable[1], new_environment)  # Evaluate all the variables to their given values in the new environment.
                
            return evaluate(body, new_environment)  # Evaluate the body of the function with the variables we have just defined.
        
        elif tree[0] == 'set!':
            variable = tree[1]
            expression = tree[2]
            expression = evaluate(expression, environment)
            current_environment = environment
            
            while variable not in current_environment.values:
                current_environment = current_environment.parent  # Look for the closest environment above that has the variable.
                if current_environment is None:
                    raise SnekNameError
                    
            current_environment[variable] = expression  # Once we find that environment, set the variable equal to the expression we evaluated earlier.
            return expression
            
        else:
            operation = evaluate(tree[0], environment)  # If we don't have a function or assignment, then the first element is a function/operation in the environment.
        arguments = []
        for i in range(1, len(tree)):
            arguments.append(evaluate(tree[i], environment))  # Create the arguments for the function.
        try:
            return operation(arguments)  # Try to do the function with the arguments passed in.
        except TypeError:  #If the arguments are the wrong type, we have an evaluation error.
            raise SnekEvaluationError 

def result_and_env(expression, environment = None):
    """
    Function that allows us to evaluate expression and return environment too.
    """
    if environment == None:
        environment = Environment()
        environment.parent = snek_environment
    return (evaluate(expression, environment), environment)

def evaluate_file(filename, environment = None):
    """
    Function that can run content in file before dropping into REPL.
    """
    with open(filename, 'r') as f:
        file_text = f.read()
    return evaluate(parse(tokenize(file_text)), environment)

def REPL(environment = None):
    """
    Function to allow user to write in LISP in a global environment.
    """
    user_input = input('in>')
    
    if environment == None:
        environment = Environment()
        environment.parent = snek_environment
    while user_input != 'QUIT':
        try:
            print('out> ' + str(evaluate(parse(tokenize(str(user_input))), environment)))
        except:
            print("ERROR")
        user_input = input('in>')


if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    environment = snek_environment
    if len(sys.argv) != 1:
        for i in range(1, len(sys.argv)):
            evaluate_file(sys.argv[i], environment)
            
    REPL(environment)
        
