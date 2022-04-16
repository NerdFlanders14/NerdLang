from sly import Lexer
from sly import Parser

class BasicLexer(Lexer):
    tokens = { NAME, NUMBER, STRING }
    ignore = "\t "
    literals = { '=', '+', '-', '/', 
                '*', '(', ')', ',', ';', '&', '£'}

    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    STRING = r'\".*?\"'

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    @_(r'//.*')
    def COMMENT(self, t):
        pass

    @_(r'\n+')
    def newline(self, t):
        self.lineno = t.value.count('\n')


class BasicParser(Parser):
    tokens = BasicLexer.tokens
    precedence = (
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('right', 'UMINUS'),
    )
    def __init__(self):
        self.env = { }
  
    @_('')
    def statement(self, p):
        pass
  
    @_('var_assign')
    def statement(self, p):
        return p.var_assign
    
    #assign a mathmatical expression to a variable
    @_('NAME "=" expr')
    def var_assign(self, p):
        return ('var_assign', p.NAME, p.expr)
  
    #assign a string to a variable
    @_('NAME "=" STRING')
    def var_assign(self, p):
        return ('var_assign', p.NAME, p.STRING)
    
    #solve a problem i guess
    @_('expr')
    def statement(self, p):
        return (p.expr)
    
    #add
    @_('expr "+" expr')
    def expr(self, p):
        return ('add', p.expr0, p.expr1)
    
    #subtract
    @_('expr "-" expr')
    def expr(self, p):
        return ('sub', p.expr0, p.expr1)
    
    #times
    @_('expr "*" expr')
    def expr(self, p):
        return ('mul', p.expr0, p.expr1)

    #divide
    @_('expr "/" expr')
    def expr(self, p):
        return ('div', p.expr0, p.expr1)

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return p.expr
    
    #output a variable
    @_('NAME')
    def expr(self, p):
        return ('var', p.NAME)
    
    #output a number
    @_('NUMBER')
    def expr(self, p):
        return ('num', p.NUMBER)

    #ieteration
    @_('expr "&" NAME')
    def expr(self, p):
        return ('iet', p.expr, p.NAME)

    #boolean if statement
    @_('NAME "£" NAME')
    def expr(self, p):
        return('cond', p.NAME0, p.NAME1)
class BasicExecute:
    
    def __init__(self, tree, env):
        self.env = env
        result = self.walkTree(tree)
        if result is not None and isinstance(result, int):
            print(result)
        if isinstance(result, str) and result[0] == '"':
            print(result)
  
    def walkTree(self, node):
  
        if isinstance(node, int):
            return node
        if isinstance(node, str):
            return node
  
        if node is None:
            return None
  
        if node[0] == 'program':
            if node[1] == None:
                self.walkTree(node[2])
            else:
                self.walkTree(node[1])
                self.walkTree(node[2])
  
        if node[0] == 'num':
            return node[1]
  
        if node[0] == 'str':
            return node[1]

        if node[0] == 'iet':
            for i in range(int(node[1][1])):
                print(self.env[node[2]])

        if node[0] == 'cond':
            if self.env[node[1]] == self.env[node[2]]:
                return(True)
            else:
                return(False)
  
        if node[0] == 'add':
            return self.walkTree(node[1]) + self.walkTree(node[2])
        elif node[0] == 'sub':
            return self.walkTree(node[1]) - self.walkTree(node[2])
        elif node[0] == 'mul':
            return self.walkTree(node[1]) * self.walkTree(node[2])
        elif node[0] == 'div':
            return self.walkTree(node[1]) / self.walkTree(node[2])
  
        if node[0] == 'var_assign':
            self.env[node[1]] = self.walkTree(node[2])
            return node[1]
  
        if node[0] == 'var':
            try:
                return self.env[node[1]]
            except LookupError:
                print("Undefined variable '"+node[1]+"' found!")
                return 0

if __name__ == '__main__':
    lexer = BasicLexer()
    parser = BasicParser()
    env = {}
    
    fname = input("File To Run: ")
    f = open(fname, "r")
    x = f.readlines()
    for i in range(len(x)):
        try:    
            text = x[i].replace("\n", "")
        except EOFError:
            break
          
        if text:
            tree = parser.parse(lexer.tokenize(text))
            BasicExecute(tree, env)
