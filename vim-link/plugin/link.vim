if !has('python')
    echo "Error: Required vim compiled with +python"
    finish
endif


function! This()

python << EOF

import vim
import pprint
import re
import ast

#list_search = re.compile('\[(.*)\]')
#dict_search = re.compile('\[(.*)\]')
def replace(obj):

    if isinstance(obj, ast.Num):
	return ast.n

    if isinstance(obj, ast.Str):
	return ast.s

    ret = ''

    if isinstance(obj, ast.Dict):
	for b in obj.keys:
	    ret += replace(b)
	return ret

    if isinstance(obj, ast.List) or isinstance(obj, ast.Tuple):
	for b in obj.elts:
	    ret += replace(b)
	return ret

    return ret


#try parsing this using the pre-compilation parser of python
try:
    expr = ast.parse(string).body[0].value
    parsed = replace(exprs)
except Exception as e:
    print e

s = vim.current.line

for line in parsed.split('\n'):
    vim.current.buffer.append(line)

EOF

endfunction
