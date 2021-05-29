import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:
    """
    The superclass for all of our symbolic algebra.
    """
    def __add__(self, other):
        return Add(self, other)
    
    def __radd__(self, n):
        return Add(n, self)  # If the operation does not work on a + b, try b + a, just try the reverse.

    def __sub__(self, other):
        return Sub(self, other)
    
    def __rsub__(self, n):
        return Sub(n, self)
        
    def __mul__(self, other):
        return Mul(self, other)
    
    def __rmul__(self, n):
        return Mul(n, self)
        
    def __truediv__(self, other):
        return Div(self, other)
    
    def __rtruediv__(self, n):
        return Div(n, self)
        

class Var(Symbol):
    """
    The class for any variables. Inherits from Symbol.
    """
    precedence = 3  # Logically, individual numbers and variables will have the highest precedence.
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n
        
    def deriv(self, variable):
        if self.name == variable:  # If we are taking the derivative of a variable with respect to itself, then it will just become Num(1).
            return Num(1)
        return Num(0)  # Taking the derivative of a variable with no respect to itself will result in Num(0).

    def simplify(self):
        return self

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Var(' + repr(self.name) + ')'
    
    def eval(self, mapping):
        if self.name not in mapping.keys():  # If we cannot find a key for a variable, return a KeyError.
            raise KeyError("Mapping is not correct")
        else:
            return mapping[self.name]

class Num(Symbol):
    """
    The class for numbers in ouy symbolic algebra.
    """
    precedence = 4  # Logically, individual numbers and variables will have the highest precedence.
    
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n
        
    def deriv(self, variable):
        return Num(0)  # The derivaticve of a number is just 0.
    
    def simplify(self):
        return self
        
        
    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return 'Num(' + repr(self.n) + ')'
    
    def eval(self, mapping):  # If we evaluate a number, we can just return the number.
        return self.n
    

class BinOp(Symbol):
    """
    Class to internally represent our algebra in binary form.
    """
    def __init__(self, left, right):
        if isinstance(left, Symbol):
            self.left = left
        else:
            if isinstance(left, str):  # If the input is something other than an instance of symbol, we turn it into the correct form.
                self.left = Var(left)
            else:
                self.left = Num(left)
                
        if isinstance(right, Symbol):
            self.right = right
        else:
            if isinstance(right, str):
                self.right = Var(right)
            else:
                self.right = Num(right)
                
def wrap(string):
    """
    Takes in a string and wraps it with parantheses.
    """
    return '(' + string + ')'


def string_join(left, right, precedence, operation, strict):
    """
    Takes in the left and right side of the equation, including the precedence
    of the overall equation, the operation, and a bool setting. If strict, we
    are doing mutliplication or addition, else subtract and division. Returns
    the correct wrapping of left + right based on their precedences.
    """
    left_string = str(left)
    right_string = str(right)
    if strict:
        if left.precedence < precedence:
            left_string = wrap(left_string)  # If the left side has a smaller precedence than the equation, then it needs to be wrapped in parantheses.
        if right.precedence < precedence:  # Same for the right side as the left.
            right_string = wrap(right_string)
            
    else:
        if left.precedence < precedence:
            left_string = wrap(left_string)
        if right.precedence <= precedence:  # For our special rules, when the right side has the same precedence as the overall equation, we wrap it.
            right_string = wrap(right_string)
            
        
    return left_string + ' ' + operation + ' ' + right_string
    
        
class Add(BinOp):
    """
    Class to represent how we add the left hand side to the right hand
    in a binary operation.
    """
    precedence = 1  # Assign the lower precedent operations with 1.
        
    def __str__(self):
        return string_join(self.left, self.right, 1, '+',  True)
        
    def __repr__(self):
        return 'Add(' + repr(self.left) + ',' + ' ' + repr(self.right) + ')'
    
    def deriv(self, variable):
        """
        Take derivative of both sides independetly for addition.
        """
        return self.left.deriv(variable) + self.right.deriv(variable)  # We go down to the individual numbers and variables to determine the derivatives of them.
    
    def simplify(self):
        left = self.left.simplify()  # Recurse to the bottom so we can analyse the numbers and variables.
        right = self.right.simplify()
        
        if left.precedence == 4 and right.precedence == 4:  # We determine if we are wokring with numbers or variables by checking their precedences, then do the required computation depending on the conditions.
            return Num(left.n + right.n)
        
        elif left.precedence == 4 and left.n == 0:
            return right
    
        elif right.precedence == 4 and right.n == 0:
            return left
        
        return left + right
    
    def eval(self, mapping): 
        return self.left.eval(mapping) + self.right.eval(mapping)  # Recurse to the bottom and evaluate the numbers and variables.
    
class Sub(BinOp):
    """
    Class to represent how we subtract the right hand side from the left hand side in
    in a binary operation.
    """
    precedence = 1
    
    def __str__(self):
        return string_join(self.left, self.right, 1, '-',  False)
    
    def __repr__(self):
        return 'Sub(' + repr(self.left) + ',' + ' ' + repr(self.right) + ')'
    
    def deriv(self, variable):
        """
        Take derivative of both sides independetly for subtraction.
        """
        return self.left.deriv(variable) - self.right.deriv(variable)
    
    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()
        
        if left.precedence == 4 and right.precedence == 4:  # If both LHS and RHS are numbers, just subtract them.
            return Num(left.n - right.n)
        
        elif right.precedence == 4 and right.n == 0:  # If the RHSis 0, just return the LHS.
            return left
        
        return left - right  # In the overaell case, just subtract the two using our method for subtraction.
    
    def eval(self, mapping): 
        return self.left.eval(mapping) - self.right.eval(mapping)

class Mul(BinOp):
    """
    Class to represent how we multiply the right hand side with the left hand side in
    in a binary operation.
    """
    precedence = 2  # Assign the hgher operations with 2.
        
    def __str__(self):
        return string_join(self.left, self.right, 2, '*',  True)            
    
    def __repr__(self):
        return 'Mul(' + repr(self.left) + ',' + ' ' + repr(self.right) + ')'
    
    def deriv(self, variable):
        """
        Use product rule for derivative of a product.
        """
        return self.left * self.right.deriv(variable) + self.right * self.left.deriv(variable)
        
    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()

        if left.precedence == 4 and right.precedence == 4:  # If both are numbers, multiply them.
            return Num(left.n * right.n)
        
        elif (left.precedence == 4 and left.n == 0) or (right.precedence == 4 and right.n == 0):  # If either side is 0, return 0.
            return Num(0)
        
        elif left.precedence == 4 and left.n == 1:  # If either side is 1, return the other side.
            return right
        
        elif right.precedence == 4 and right.n == 1:
            return left
        
        return left * right  # In the overall case, multiply both the LHS and RHS using our multiplication rules.
    
    def eval(self, mapping): 
        return self.left.eval(mapping) * self.right.eval(mapping)
        
class Div(BinOp):
    """
    Class to represent how we divide the left hand side with the right hand side in
    in a binary operation.
    """
    precedence = 2

    def __str__(self):
        return string_join(self.left, self.right, 2, '/',  False)
    
    def __repr__(self):
        return 'Div(' + repr(self.left) + ',' + ' ' + repr(self.right) + ')'
    
    def deriv(self, variable):
        """
        Use quotient rule to find derivative of a division.
        """
        return (self.right * self.left.deriv(variable) - self.left * self.right.deriv(variable))/ (self.right * self.right)
    
    def simplify(self):
        left = self.left.simplify()
        right = self.right.simplify()
        
        if left.precedence == 4 and left.n == 0:  # If the LHS is 0, return 0.
            return Num(0)
        
        if right.precedence == 4 and right.n == 1:  # if the RHS is 1, return the LHS.
            return left
        
        if left.precedence == 4 and right.precedence == 4:  # If both are numbers, we can just divide them.
            return Num(left.n / right.n)
        
        return left / right  # In the overall case, we just divide the two numbers using out division rules.

    def eval(self, mapping): 
        return self.left.eval(mapping) / self.right.eval(mapping)
    
def tokenize(string):
    """
    Takes in a string and tokenizes it in the form specified in the lab.
    """
    output = []
    for i in range(len(string)):
        if string[i] in '()+-/*':  # Individual symbols are their own element.
            output.append(string[i])
            continue
        elif string[i] == ' ':  # We ignore spaces.
                continue
        elif string[i] in '0123456789':
            if len(output) == 0:  # We just add the first number.
                output.append(string[i])
                continue
            elif string[i - 1] == '-':  # If we have a negative number, just add the number to the negative symbol.
                output[-1] += string[i]
                continue
            elif string[i - 1] in '0123456789':  # If we a number of multiple digits, concatenate the number beforehand with the new one.
                output[-1] += string[i]
                continue
        output.append(string[i])  # We just add variables onto output on their own.
    return output

def parse(tokens):
    """
    Takes in a tokenated string and returns the string in a symbolic
    expression.
    """
    
    def parse_expression(index):
        """
        Recursively finds the correct expression for a operation b in our tokens.
        """
        token = tokens[index]
        
        if token in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':  # If we have a variable on it's own, just return in symbolic form and add 1 to the index.
            return Var(token), index + 1
        
        elif token == '(':  # If we are at an expression, we go into the left and right hand side, while saving the operation that is used in the expression.
            left_value, left_index = parse_expression(index + 1)
            operation = tokens[left_index]
            right_value, right_index = parse_expression(left_index + 1)
            
            if operation == '+':  # Do the appropriate operation depending on the operation, and add 1 to the right index, because now we are done with everything before it.
                return Add(left_value, right_value), right_index + 1
            
            if operation == '-':
                return Sub(left_value, right_value), right_index + 1
            
            if operation == '*':
                return Mul(left_value, right_value), right_index + 1

            if operation == '/':
                return Div(left_value, right_value), right_index + 1
        else:
            return Num(int(token)), index + 1  # If we have a number, just return it in symbolic form and add 1 to the index. 
        
    parsed_expression, next_index = parse_expression(0)
    
    return parsed_expression

def sym(string):
    """
    Takes in a string of the appropriate form and returns it in symbolic algebra form.
    """
    return parse(tokenize(string))

if __name__ == '__main__':
    doctest.testmod()