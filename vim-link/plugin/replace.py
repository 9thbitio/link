
import re
import ast

dict_search = re.compile('{(.*)}')
def replace_old(string):
    ret = ""  

    if not string:
        return ""

    iter = dict_search.finditer(string)  
    
    for next in iter:
        print next.group()
        print next.span()
        for group in next.groups():
            print group
            ret += replace(group)
    
    return ret + "blah"

def format_code(code, annotate_fields=True, include_attributes=False, indent='  '):
    """
    Take the string code and c
    Return a formatted dump of the tree in *node*.  This is mainly useful for
    debugging purposes.  The returned string will show the names and the values
    for fields.  This makes the code impossible to evaluate, so if evaluation is
    wanted *annotate_fields* must be set to False.  Attributes such as line
    numbers and column offsets are not dumped by default.  If this is wanted,
    *include_attributes* can be set to True.
    """
    def _format(node, level=0):
        if isinstance(node, ast.AST):
            fields = [(a, _format(b, level)) for a, b in ast.iter_fields(node)]
            if include_attributes and node._attributes:
                fields.extend([(a, _format(getattr(node, a), level))
                               for a in node._attributes])
            return ''.join([
                node.__class__.__name__,
                '(',
                ', '.join(('%s=%s' % field for field in fields)
                           if annotate_fields else
                           (b for a, b in fields)),
                ')'])
        elif isinstance(node, list):
            lines = ['[']
            lines.append(
                indent * (level + 2) + ','.join([_format(x, level +2 ) for x in node])
            )
            lines.append(indent * level +  ']')
            return '\n'.join(lines)

        elif isinstance(node, tuple):
            lines = ['(']
            lines.append(
                indent * (level + 2) + ','.join([_format(x, level +2 ) for x in node])
            )
            lines.append(indent * level +  ')')
            return '\n'.join(lines)

        elif isinstance(node, dict):
            lines = ['{']
            lines.append(
                indent * (level + 2) + ','.join([_format(x, level +2 ) for x in node])
            )
            lines.append(indent * level +  '}')
            return '\n'.join(lines)


        return repr(node)
    
    # use ast.parse to parse the code into a tree
    node = ast.parse(code)   
    
    if not isinstance(node, ast.AST):
        raise TypeError('expected AST, got %r' % node.__class__.__name__)
    return _format(node)


class CodeFormater(object):

    def __init__(self, code):
        self.parsed = ast.parse(code)   
        self.formatted = None
        self.default_indent = '  '
        self.indent = ''
        self.level = 0

    def format_string(self, node):
        return "'%s'" % node.s

    def format_number(self, node):
        return "%s" % node.n

    def format_function(self, node):
        return "%s" % node.s

    
    def format_comma(self, iterable):
            comma = ( ', '.join(
                                [self.format_node(x,2) for x in
                                 iterable]
                                )
                    )
            indented = self.indent + comma
            return indented
    
    def indent_offset(self, offset):
        self.level += offset
        self.indent = self.default_indent * self.level

    def format_dict(self, node):
        lines = ['\n' + self.indent  + '{']
        self.indent_offset(2)
        lines.append(self.format_comma(node.keys))
        lines.append(self.indent + '}')
        self.indent_offset(-2)
        return '\n'.join(lines)

    def format_list(self, node):
        lines = ['\n' + '[']
        self.indent_offset(2)
        lines.append(self.format_comma(node.elts))
        lines.append(self.indent +  ']')
        self.indent_offset(-2)
        return '\n'.join(lines)

    def format_tuple(self, node):
        lines = ['\n' + self.indent +'(']
        self.indent_offset(2)
        lines.append(
            self.indent + ', '.join([self.format_node(x) for
                                             x in node.elts])
        )
        self.indent_offset(-2)
        lines.append(self.indent + ')')
        return '\n'.join(lines)

    def format_name(self, node):
        return node.id

    def format_node(self, node, annotate_fields=True,
                    include_attributes=False, indent = '    '):
        """
        Format an idividual node
        """
        formatted = []

        if isinstance(node, ast.Module):
            formatted.append(self.format_node(node.body))
            return formatted

        if isinstance(node, ast.Num):
            return self.format_number(node)

        if isinstance(node, ast.List):
            return self.format_list(node)

        if isinstance(node, ast.Dict):
            return self.format_dict(node)

        if isinstance(node, ast.Str):
            return self.format_string(node)

        if isinstance(node, ast.Tuple):
            return self.format_tuple(node)

        if isinstance(node, ast.Name):
            return self.format_name(node)

        if isinstance(node, list):
            return self.indent + ', '.join([self.format_node(x) for x in node])

        if isinstance(node, ast.Expr):
            return self.format_node(node.value)

        return repr(node)
 
    def format(self, annotate_fields=True, include_attributes=False, indent='  '):
        """
        Tak the string code and c
        Return a formatted dump of the tree in *node*.  This is mainly useful for
        debugging purposes.  The returned string will show the names and the values
        for fields.  This makes the code impossible to evaluate, so if evaluation is
        wanted *annotate_fields* must be set to False.  Attributes such as line
        numbers and column offsets are not dumped by default.  If this is wanted,
        *include_attributes* can be set to True.
        """
       
        # use ast.parse to parse the code into a tree
        
        if not isinstance(self.parsed, ast.AST):
            raise TypeError('expected AST, got %r' % self.parsed.__class__.__name__)
        return '.'.join(self.format_node(self.parsed))


class NodePrinter(ast.NodeVisitor):

    def __init__(self, string='', node=None):
        self._string = string
        #if you put in a node then use that 
        self.node = node or ast.parse(self._string)
        self.formatted = ''
        self._statements = None
    
    @property 
    def statements(self):
        if not self._statements:
            self.visit(ast.parse(self._string))
        return self._statements

    def __str__(self):
        return ''.join(map(str,self.statements))
    
    def visit_Module(self, node):
        print node
        self._statements = [] 
        self.parent = None
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        print(node.name)
        self.generic_visit(node)

    def visit_Num(self, node):
        self.formatted += str(node.n)

    def visit_List(self, node):
        print "in list"
        #return a comma seperated list of everything
        self.string = '[\n%s]\n' % ','.join(NodePrinter(node=node).statements)
        self._statements.append(self)
        print self.string

    def visit_Tuple(self, node):
        print "in tuple"
        #return a comma seperated list of everything
        self.string = '[\n%s]\n' % ','.join(NodePrinter(node=node).statements)
        self._statements.append(self)
        print self.string

    def visit_Dict(self, node):
        indent = 2
        str_indent = ' '
        ret = ''
        ret = str_indent + '{\n'
	ret += str_indent + ', '.join(
                                    ['%s:%s' % (format(key, indent ),
                                                format(value, indent))
                                    for key, value in zip(node.keys, node.values)]
                                    )
        ret += '\n' + str_indent + '}\n'
        print self.generic_visit(node)
        self.formatted += ret
	return ret
    
    def node_format(self):
        """
        Formats the string
        """
        n = cls()
        n.visit(ast.parse(string))
	return n 


def format(obj, indent = 0):

    if isinstance(obj, ast.Num):
	return str(obj.n)

    if isinstance(obj, ast.Str):
	return "'%s'" % obj.s
    
    #this means it's a variable or function Name
    if isinstance(obj, ast.Name):
	return "%s" % obj.id

    ret = ''
    str_indent = indent * ' '
    indent = indent +2

    if isinstance(obj, ast.Dict):
        ret = str_indent + '{\n'
	ret += str_indent + ', '.join(
                                    ['%s:%s' % (format(key, indent ),
                                                format(value, indent))
                                    for key, value in zip(obj.keys, obj.values)]
                                    )
        ret += '\n' + str_indent + '}\n'
	return ret

    if isinstance(obj, ast.List) or isinstance(obj, ast.Tuple):
        ret = str_indent + '[\n'
        ret += str_indent + ', '.join([format(item, indent) for item in obj.elts])
        ret += '\n' + str_indent + ']\n'
	return ret

    #this is what will kick it off the first time
    if isinstance(obj, str):
	return format(ast.parse(obj).body[0].value)

    return ret


