#!/usr/bin/python -s
#
# py-format
#
# Formats the imput to colourize keywords, vairables, etc.
#
# Output may be TEXT (default), ANSI, or HTML.
#
# This  program is free software: you can redistribute it and/or modify  it
# under  the  terms of the GNU General Public License as published  by  the
# Free  Software  Foundation, either version 3 of the License, or (at  your
# option) any later version.
#
# This  program  is  distributed in the hope that it will  be  useful,  but
# WITHOUT   ANY   WARRANTY;   without  even   the   implied   warranty   of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You  should have received a copy of the GNU General Public License  along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# 20 Mar 16   0.1   - Initial version - MEJT
# 10 Apr 16   0.2   - Reads input files character by character - MEJT
# 11 Jun 16         - Keyword parsing working (with a lot of fudge for
#                     newline characters to allow them to be part of a
#                     token) - MEJT
# 12 Jun 16         - Allow for multi line comments and strings - MEJT
#                   - Add key words for shell scripts (bash) - MEJT
# 16 Jun 16         - Add escape character handling - MEJT
# 25 Jun 16         - Added ability to produce HTML and subsitute character
#                     codes for special characters to preserve formatting
#                     when HTML is included in Wordpress posts - MEJT
#                   - Fixed bug in escape sequence code - MEJT
#                   - Fix bug when highlighting functions - MEJT
# 26 Jun 16         - Subsitute character codes in escape sequences - MEJT
#                   - Highlights numbers - MEJT
#                   - Line numbers now formatted properly when output is
#                     HTML - MEJT
# 15 Jul 16         - Fixed issues with hightlighting escape characters and
#                     added hightlighting of reserved words - MEJT
# 28 Nov 16         - Modified ANSI highlighting codes - MEJT
# 08 Mar 17         - Added a qualifier to allow the user to explicitly
#                     select plain text output - MEJT
#                   - HTML output now encodes 'x' and 'X' characters as they
#                     are modified by Wordpress - MEJT
# 12 Aug 18         - Added Microsoft BASIC keywords - MEJT
#                   - Start each file with a new line, which also ensures
#                     that the first character is formatted correctly - MEJT
#                   - Started to add PowerShell keywords - MEJT 
# 04 Mar 19         - Started to add DOS Batch file keywords - MEJT
# 19 Mar 19         - Updated  lists  of  Visual BASIC Script  keywords  and
#                     functions - MEJT
# 22 Mar 19         - Added Digital Comand Language definitions - MEJT
# 24 Jun 20         - Added some definitions for Rust - MEJT
# 26 Jul 20         - Added Quick PASCAL definitions - MEJT
# 14 Jan 21         - Added COMMENT and CO to ALGOL68 comemnt delimiters - MEJT
#
# To Do:            - Highlight operators.
#                   - Fix 'leading spaces' problem (extra spaces being inserted
#                     at the beginning of a line...)
#
 
import sys, os
 
def _about():
  _path = os.path.basename(sys.argv[0])
  sys.stdout.write(
    "Usage: " + sys.argv[0] + "[OPTION]... [FILE]...\n"
    "Concatenate FILE(s)to standard output.\n" + "\n" +
    "  -a, --ansi               use ansi escape sequences (default)\n" +
    "  -b, --number-nonblank    number nonempty output lines," +
    " overrides -n\n" +
    "  -h, --html               use html markup\n" +
    "  -n, --number             number all output lines \n" +
    "  -r, --restart            line numbers start at zero, implies -n\n" +
    "  -s, --squeeze-blank      suppress repeated empty output lines\n" +
    "  -t, --text               use plain text\n" +
    "      --help               display this help and exit\n" +
    "      --version            output version information and exit\n\n" +
    "Example:\n" +
    "  " + _path + " f g\t   output f's contents, then g's contents.\n")
  raise SystemExit
 
def _version():
  _path = os.path.basename(sys.argv[0])
  sys.stdout.write(_path + " 0.1\n" +
    "License GPLv3+: GNU GPL version 3 or later.\n"
    "This is free software: you are free to change and redistribute it.\n"
    "There is NO WARRANTY, to the extent permitted by law.\n")
  raise SystemExit
 
def _invalid(_option):
  _path = os.path.basename(sys.argv[0])
  sys.stderr.write(_path + ": invalid option -- '" + _option[1:] + "'\n")
  sys.stderr.write("Try '" + _path + " --help' for more information.\n")
  raise SystemExit
 
def _unrecognized(_option):
  _path = os.path.basename(sys.argv[0])
  sys.stderr.write(_path + ": unrecognized option '" + _option + "'\n")
  sys.stderr.write("Try '" + _path + " --help' for more information.\n")
  raise SystemExit
 
def _error(_error):
  sys.stderr.write(os.path.basename(sys.argv[0]) + ": " + _name +
    ": " + _error + "\n")
 
# Colours - 
#   Black: 0, Red: 1, Green: 2, Yellow: 3, Blue: 4, Magenta: 5, Cyan: 6, 
#   White: 7, Default: 9
# Attributes - 
#   Normal: 0, Bold: 1, Dark: 2, Itallic: 3, Underline: 4, Inverse: 7,
#   Strikethrough: 9
 
_formats = { # Formatting escape sequences or HTML
  'ansi':  {'body'      : (''),             # Do nothing!!!
            'end'       : (''),
            'comment'   : ('\033[0;36m'),   # Cyan.
            'string'    : ('\033[1;33m'),   # Yellow
            'number'    : ('\033[0;36m'),   # Cyan
            'keyword'   : ('\033[0;32m'),   # Green
            'function'  : ('\033[1;2;35m'), # Purple
            'reserved'  : ('\033[1;34m'),   # Blue
            'definition': ('\033[0;35m'),   # Magenta
            'operator'  : ('\033[0;35m'),   # Magenta
            'escape'    : ('\033[1;31m'),   # Dark red
            ''          : ('\033[0m')},
 
  'html':  {'body'      : ('<div style="border-color:#d2d0ce; ' +
                           'border-style:solid; border-width:1px; ' +
                           'border-radius:5px; background:#f7f7f7; ' +
                           'padding:10px; line-height:133%; ' +
                           'font-family:monospace; white-space:nowrap; '
                           'white-space:pre; overflow:auto; ' +
                           'font-size:10pt; color:#696969;">'),
            'end'       : ('</div><br><p>\n'),
            'comment'   : ('<span style="color:slategray;">'),
#           'comment'   : ('<span style="color:sienna;">'),
            'string'    : ('<span style="color:forestgreen;">'),
            'number'    : ('<span style="color:darkturquoise;">'),
            'keyword'   : ('<span style="color:dodgerblue;">'),
            'function'  : ('<span style="color:purple;">'),
            'reserved'  : ('<span style="color:green;">'),
            'definition': ('<span style="color:indianred;">'),
            'operator'  : ('<span style="color:darkcyan;">'),
            'escape'    : ('<span style="color:brown;">'),
            ''          : ('</span>')},
 
#  'html':  {'body'      : ('<div style="border-color:#d2d0ce; ' +
#                           'border-style:solid; border-width:1px; ' +
#                           'border-radius:5px; background:#f7f7f7; ' +
#                           'padding:10px; line-height:133%; ' +
#                           'font-family:monospace; white-space:nowrap; '
#                           'white-space:pre; overflow:auto; ' +
#                           'font-size:10pt; color:#696969;">'),
#            'end'       : ('</div><br><p>\n'),
#            'comment'   : ('<span style="color:slategray;">'),
#            'string'    : ('<span style="color:dodgerblue;">'),
#            'number'    : ('<span>'),
#            'keyword'   : ('<span style="color:forestgreen;">'),
#            'function'  : ('<span style="color:brown;">'),
#            'reserved'  : ('<span style="color:brown;">'),
#            'definition': ('<span style="color:brown;">'),
#            'operator'  : ('<span>'),
#            'escape'    : ('<span style="color:forestgreen;">'),
#            ''          : ('</span>')},
 
  ''    :  {'body'      : (''),
            'end'       : (''),
            'comment'   : (''),
            'string'    : (''),
            'number'    : (''),
            'keyword'   : (''),
            'function'  : (''),
            'reserved'  : (''),
            'definition': (''),
            'operator'  : (''),
            'escape'    : (''),
            ''          : ('')}
}     # Reset attributes
 
_spaces = [' ', '\t', '\r']
 
_eoln = ['\n', '\v', '\f']
 
_hexadecimal = '0123456789abcdefABCDEF'
 
_types = ['.a68', '.bas', '.c', '.cmd', '.dcl', '.f77', '.for', '.ftn', '.h',
 '.pas', '.py', '.ps1', '.rs', '.sh', '.vbs', '']
 
_escape = { # Tokens that signal an escape character
  '.a68': ['' ],
  '.bas': ['' ],
  '.c'  : ['\\'],
  '.cmd'  : [''],
  '.dcl': [''],
  '.f77': [''],
  '.for': [''],
  '.ftn': [''],
  '.h'  : ['\\'],
  '.pas': ['' ],
  '.py' : ['\\'],
  '.ps1': ['\`'],
  '.rs' : ['\`'],
  '.sh' : ['\\'],
  '.vbs': [''],
  ''    : [''],
  }
 
_quotes = { # Tokens that start or end a string
  '.a68': ['"'],
  '.bas': ['"'],
  '.c'  : ['"', '\''],
  '.cmd': ['"'],
  '.dcl': ['"'],
  '.f77': ['"', '\''],
  '.for': ['"', '\''],
  '.ftn': ['"', '\''],
  '.h'  : ['"', '\''],
  '.pas': ['\''],
  '.py' : ['"', '\''],
  '.ps1': ['"', '\''],
  '.rs' : ['"', '\''],
  '.sh' : ['"', '\''],
  '.vbs': ['"'],
  ''    : ['']
  }
 
_delimiters = { # Token seperators
  '.a68': ['(', ')', '[', ']', ';', ':', '.', ','],
  '.bas': ['(', ')', '[', ']', ':', '.', ','],
  '.c'  : ['(', ')', '{', '}', '[', ']', ';', ':', '.', ',', '!'],
  '.cmd': ['(', ')', '[', ']', ';', ':', '.', ',', '@'],
  '.dcl': ['(', ')', '{', '}', '[', ']', ';', ':', '.', ',', '\'','+', '-', '/', '*'],
  '.f77': ['(', ')', '[', ']', ':', '.', ','],
  '.for': ['(', ')', '[', ']', ':', '.', ','],
  '.ftn': ['(', ')', '[', ']', ':', '.', ','],
  '.h'  : ['(', ')', '{', '}', '[', ']', ';', ':', '.', ',', '!'],
  '.pas': ['(', ')', '[', ']', ';', ':', '.', ',', '$', ' '],
  '.py' : ['(', ')', '{', '}', '[', ']', ';', ':', '.', ',', '!'],
  '.ps1': ['(', ')', '{', '}', '[', ']', ';', ':', '.', ',', '!', '|'],
  '.rs' : ['(', ')', '{', '}', '[', ']', ';', ':', '.', ',', '!'],
  '.sh' : ['(', ')', '{', '}', '[', ']', ';', ':', '.', ',', '!'],
  '.vbs': ['(', ')', '{', '}', '[', ']', ';', ':', '.', ',', '!'],
  ''    : []
  }
 
_comments = { # Tokens that start a comment section
  '.a68': ['CO','COMMENT','{'],
  '.bas': ['REM'],
  '.c'  : ['/*', '//'],
  '.cmd': ['rem'],
  '.dcl': ['\n$!'],
  '.f77': [],
  '.for': ['\nC'],
  '.ftn': ['\nC'],
  '.h'  : ['/*', '//'],
  '.pas': ['{', '(*'],
  '.py' : ['#'],
  '.ps1': ['#'],
  '.rs' : ['//'],
  '.sh' : ['#'],
  '.vbs': ['\''],
  '': []
  }
 
_code = { # Tokens that end a comment section - paired with comments.
  '.a68': ['CO','COMMENT','}'],
  '.bas': ['\n'],
  '.c'  : ['*/', '\n'],
  '.cmd': ['\n'],
  '.dcl': ['\n'],
  '.f77': [],
  '.for': ['\n'],
  '.ftn': ['\n'],
  '.h'  : ['*/', '\n'],
  '.pas': ['}', '*)'],
  '.py' : ['\n'],
  '.ps1': ['\n'],
  '.rs' : ['\n'],
  '.sh' : ['\n'],
  '.vbs': ['\n'],
  ''    : []
  }
 
_operators = { # Operator Tokens
  '.a68': ['+', '-', '/', '*', '&', '^', '~', '|', '%', '='],
  '.bas': ['+', '-', '/', '*', '^', '='],
  '.c'  : ['+', '-', '/', '*', '&', '^', '~', '|', '%', '='],
  '.cmd': ['+', '-', '/', '*', '==', '='],
  '.h'  : ['+', '-', '/', '*', '&', '^', '~', '|', '%', '='],
  '.dcl': ['+', '-', '/', '*', '==', ':=', '='],
  '.f77': ['+', '-', '/', '*', '^', '%', '='],
  '.for': ['+', '-', '/', '*', '^', '%', '='],
  '.ftn': ['+', '-', '/', '*', '^', '%', '='],
  '.pas': ['+', '-', '/', '*', '=', '<>', '>', '>=',  '<', '<=', '@'],
  '.py' : ['+', '-', '/', '*', '&', '^', '~', '|', '%', '='],
  '.ps1': ['+', '-', '/', '*', '&', '^', '~', '|', '%', '='],
  '.rs' : ['+', '-', '/', '*', '&', '\'&', '^', '~', '|', '%', '='],
  '.sh' : ['+', '-', '/', '*', '&', '^', '~', '|', '%', '=', '[', ']'],
  '.vbs': ['+', '-', '/', '*', '^', '%', '=', '==', '<>'],
  ''    : []
  }
 
_keywords =  { # Keyword Tokens
  '.a68': ['AT', 'BEGIN', 'bits', 'BOOL', 'BY', 'bytes', 'CASE', 'CHANNEL',
    'CHAR', 'CO', 'COMMENT', 'COMPL', 'DO', 'EITHER', 'ELIF', 'ELSE',
    'EMPTY', 'END', 'ESAC', 'EXIT', 'false', 'FI', 'FILE', 'FINISH', 'FLEX',
    'FOR', 'FORALL', 'FORMAT', 'FROM', 'GO TO', 'GOTO', 'HEAP', 'IF', 'IN',
    'INT', 'IS', 'IS NOT', 'ISNT', 'LOC', 'LONG', 'MODE', 'NIL', 'OD', 'OF',
    'OP', 'OUT', 'OVER', 'PAR', 'PR', 'PRAGMAT', 'PRIO', 'PROC', 'PROGRAM',
    'REAL', 'REF', 'SEMA', 'SHORT', 'SKIP', 'STRING', 'STRUCT', 'THEN',
    'TO', 'true', 'UNION,', 'VOID', 'WHILE'],
    
  '.bas':['NOT', 'AND', 'OR', 'XOR', 'IMP', 'EQV', 
    'AUTO', 'BASE', 'CALL', 'CHAIN', 'CLEAR', 'CLOAD', 'CLOSE', 'COMMON'
    'CONT', 'CSAVE', 'DATA', 'DEF', 'FN', 'DEFINT', 'DEFSNG', 'DEFDBL',
    'DEFSTR', 'DELETE', 'DIM', 'EDIT', 'ELSE', 'END', 'ERASE', 'ERR', 'ERL',
    'ERROR', 'FIELD', 'FILES', 'FN', 'FOR', 'GET', 'GOSUB', 'GOTO', 'IF',
    'INPUT', 'INPUT#', 'KILL', 'LET', 'LINE', 'LIST', 'LLIST', 'LOAD',
    'LOF', 'LPRINT', 'LSET', 'MERGE', 'NAME', 'NEW', 'NEXT', 'NULL', 'ON',
    'OPEN', 'OPTION', 'OUT', 'PEEK', 'POKE', 'PRINT', 'PRINT#', 'PUT',
    'RANDOMIZE', 'READ', 'REM', 'RENUM', 'RESET', 'RESTORE', 'RESUME',
    'RETURN', 'RSET', 'RUN', 'SAVE', 'STOP', 'SWAP', 'THEN', 'TRON',
    'TROFF', 'USING', 'WAIT', 'WEND', 'WHILE','WIDTH', 'WRITE', 'WRITE#'],
    
  '.c': ['auto', 'break', 'case', 'char', 'const', 'continue', 'default',
    'do', 'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if',
    'int', 'long', 'NULL', 'register', 'return', 'short', 'signed',
    'sizeof', 'static', 'struct', 'switch', 'typedef', 'union', 'unsigned',
    'void', 'volatile', 'while'],
    
  '.cmd':['not','NOT', 'if', 'IF', 'set', 'SET', 'goto', 'GOTO',
      'echo', 'ECHO', '@', 'rem', 'REM'],
    
  '.dcl':['CALL', 'CLOSE', 'CONTINUE', 'ENDSUBROUTINE', 'ELSE', 'EOD',
      'EOJ', 'ENDIF', 'EXIT', 'GOSUB', 'GOTO', 'IF', 'ON', 'OPEN', 'READ',
      'RETURN', 'RUN', 'SET', 'SHOW', 'SUBROUTINE', 'THEN', 'WRITE',
      'call', 'close', 'continue', 'endsubroutine', 'else', 'eod', 'eoj',
      'endif', 'exit', 'gosub', 'goto', 'if', 'on', 'open', 'read',
      'return', 'run', 'set', 'show', 'subroutine', 'then', 'write'
      ],
    
  '.h': ['auto', 'break', 'case', 'char', 'const', 'continue', 'default',
    'do', 'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if',
    'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof',
    'static', 'struct', 'switch', 'typedef', 'union', 'unsigned', 'void',
    'volatile', 'while'],
    
  '.f77': [
    'assign', 'backspace', 'block data', 'call', 'close', 'common',
    'continue', 'data', 'dimension', 'do', 'else', 'else if', 'end',
    'endfile', 'endif', 'entry', 'equivalence', 'external', 'format',
    'function', 'goto', 'if', 'implicit', 'inquire', 'intrinsic', 'open',
    'parameter', 'pause', 'print', 'program', 'read', 'return', 'rewind',
    'rewrite', 'save', 'stop', 'subroutine', 'then', 'write'],
    
  '.for': [
    'GO TO', 'ASSIGN', 'TO', 'IF', 'STOP', 'PAUSE', 'END', 'DO', 'CONTINUE',
    'CALL', 'SUBROUTINE', 'FUNCTION', 'RETURN', 'READ', 'WRITE', 'PRINT',
    'PROGRAM', 'PUNCH', 'FORMAT', 'REWIND', 'BACKSPACE', 'ENDFILE',
    'DIMENSION', 'COMMON', 'EQUIVALENCE', 'EXTERNAL', 'INTEGER', 'REAL',
    'DOUBLE PRECISION', 'COMPLEX', 'LOGICAL', 'DATA', 'NAMELIST', 'NOT',
    'ENTRY'],
    
  '.ftn': [
    'GO TO', 'ASSIGN', 'TO', 'IF', 'STOP', 'PAUSE', 'END', 'DO', 'CONTINUE',
    'CALL', 'SUBROUTINE', 'FUNCTION', 'RETURN', 'READ', 'WRITE', 'PRINT',
    'PROGRAM', 'PUNCH', 'FORMAT', 'REWIND', 'BACKSPACE', 'ENDFILE',
    'DIMENSION', 'COMMON', 'EQUIVALENCE', 'EXTERNAL', 'INTEGER', 'REAL',
    'DOUBLE PRECISION', 'COMPLEX', 'LOGICAL', 'DATA', 'NAMELIST','NOT',
    'ENTRY'],
  
  '.pas': [
    'ABSOLUTE', 'ARRAY', 'BEGIN', 'CASE', 'CONST', 'CSTRING', 'DO', 
    'DOWNTO', 'ELSE', 'END', 'EXTERNAL', 'FILE', 'FOR', 'FORWARD', 
    'FUNCTION', 'GOTO', 'IF', 'IMPLEMENTATION', 'INHERITED', 'INLINE',
    'INTERFACE', 'INTERRUPT', 'LABEL', 'NIL', 'OBJECT', 'OF', 'OVERRIDE', 
    'PACKED', 'PROCEDURE', 'PROGRAM', 'RECORD', 'REPEAT', 'SET', 'STRING', 
    'THEN', 'TO', 'TYPE', 'UNIT', 'UNTIL', 'USES', 'VAR', 'WHILE' , 'WITH', 
    'SHR', 'SHL', 'AND', 'OR', 'XOR', 'DIV', 'MOD', 'NOT'],
    
  '.py': ['and', 'as', 'assert', 'break', 'class', 'continue','def', 'del',
    'elif', 'else', 'except', 'exec', 'finally', 'for', 'from', 'global',
    'if', 'import', 'in', 'is', 'lambda', 'not', 'or', 'pass', 'print',
    'raise', 'return', 'try', 'while', 'with', 'yield'],
    
  '.ps1': ['Assembly', 'Base', 'Begin', 'Break', 'Catch', 'Class', 'Command', 
    'Configuration', 'Continue', 'Data', 'Define', 'Do', 'DynamicParam',
    'Else', 'ElseIf', 'End', 'Enum', 'Exit', 'Filter','Finally', 'For',
    'ForEach', 'From', 'Function', 'Hidden', 'If', 'In', 'InlineScript',
    'Interface', 'Module', 'NameSpace', 'Parallel', 'Param', 'Private',
    'Process', 'Public', 'Return', 'Sequence', 'Static', 'Switch', 'Throw',
    'Trap', 'Try', 'Type', 'Until', 'Using', 'Var', 'While', 'WorkFlow'],
    
  '.rs': ['and', 'as', 'assert', 'break', 'fn', 'for', 'if', 'in', 'let', 
    'loop', 'move', 'mut', 'static', 'use'],
  
  '.sh': ['case', 'do', 'done', 'elif', 'else', 'esac', 'fi', 'for',
    'function', 'if', 'in', 'select', 'then', 'time', 'until', 'while'],
    
  '.vbs':['And', 'As', 'Boolean', 'ByRef', 'Byte','ByVal', 'Call', 'Case',
    'Const', 'Currency', 'Debug', 'Dim', 'Do', 'Double', 'Each', 'Else',
    'ElseIf', 'Empty', 'End', 'EndIf', 'Enum', 'Eqv', 'Error', 'Event',
    'Exit', 'False', 'For', 'Function', 'Get', 'GoTo', 'If', 'Imp',
    'Implements', 'In', 'Integer', 'Is', 'Let', 'Like', 'Long', 'Loop',
    'LSet', 'Me', 'Mod', 'New', 'Next', 'Not', 'Nothing', 'Null', 'On',
    'Option', 'Optional', 'Or', 'ParamArray', 'Preserve', 'Private',
    'Public', 'RaiseEvent', 'ReDim', 'Rem', 'Resume', 'RSet', 'Select',
    'Set', 'Shared', 'Single', 'Static', 'Stop', 'Sub', 'Then', 'To', 
    'True', 'Type', 'TypeOf', 'Until', 'Variant', 'Wend', 'While', 'With',
    'Xor'],
  '': []
  }

 
_functions = { # Function Tokens
  '.a68': ['close', 'fixed', 'newline', 'open', 'print', 'read', 'reset',
    'sqrt', 'write'],
    
  '.bas':['ABS', 'ASC', 'ATN', 'CDBL', 'CHR$', 'CINT', 'COS', 'CSNG', 'CVD',
    'CVI', 'CVS', 'EOF', 'EXP', 'FIX', 'FRE', 'HEX$', 'INKEY$', 'INP',
    'INPUT$', 'INSTR', 'INT', 'LEFT$', 'LEN', 'LOC', 'LOG', 'LPOS', 'MID$',
    'MKD$', 'MKI$', 'MKD$', 'OCT$', 'POS', 'RIGHT$', 'RND', 'SGN', 'SIN',
    'SPACES$', 'SPC', 'SQR', 'STR$', 'STRING$', 'TAB', 'TAN', 'USR', 'VAL',
    'VARPTR$'],
    
  '.c': ['close', 'fprintf', 'open', 'printf', 'read', 'reset', 'write',
    'exit'],
    
  '.cmd': [],
    
  '.dcl': ['F$CONTEXT', 'F$CSID', 'F$CUNITS', 'F$CVSI', 'F$CVTIME',
    'F$CVUI', 'F$DELTA_TIME', 'F$DEVICE', 'F$DIRECTORY', 'F$EDIT',
    'F$ELEMENT', 'F$ENVIRONMENT', 'F$EXTRACT', 'F$FAO', 'F$FID_TO_NAME',
    'F$FILE_ATTRIBUTES', 'F$GETDVI', 'F$GETENV', 'F$GETJPI', 'F$GETQUI',
    'F$GETSYI', 'F$IDENTIFIER', 'F$INTEGER', 'F$LENGTH', 'F$LICENSE',
    'F$LOCATE', 'F$LOGICAL', 'F$MATCH_WILD', 'F$MESSAGE', 'F$MODE', 'F$MULTIPATH',
    'F$PARSE', 'F$PID', 'F$PRIVILEGE', 'F$PROCESS', 'F$SEARCH',
    'F$SETPRV', 'F$STRING', 'F$TIME', 'F$TRNLNM', 'F$TYPE', 'F$UNIQUE',
    'F$USER', 'F$VERIFY',
    'f$context', 'f$csid', 'f$cunits', 'f$cvsi', 'f$cvtime',
    'f$cvui', 'f$delta_time', 'f$device', 'f$directory', 'f$edit',
    'f$element', 'f$environment', 'f$extract', 'f$fao', 'f$fid_to_name',
    'f$file_attributes', 'f$getdvi', 'f$getenv', 'f$getjpi', 'f$getqui',
    'f$getsyi', 'f$identifier', 'f$integer', 'f$length', 'f$license',
    'f$locate', 'f$logical', 'f$match_wild', 'f$message', 'f$mode', 'f$multipath',
    'f$parse', 'f$pid', 'f$privilege', 'f$process', 'f$search',
    'f$setprv', 'f$string', 'f$time', 'f$trnlnm', 'f$type', 'f$unique',
    'f$user', 'f$verify',
    'f$elem', 'f$ext', 'f$len', 'f$loc', 'F$ELEM', 'F$EXT', 'F$LEN', 'F$LOC'],
    
  '.h': ['close', 'fprintf', 'open', 'printf', 'read', 'reset', 'write',
    'exit'],
    
  '.f77': [],
  
  '.for': [],
  
  '.ftn': [],
  
  '.pas': ['addr', 'append', 'arctan', 'assign', 'blockread', 'blockwrite', 
    'chdir', 'close', 'concat', 'copy', 'cos', 'cseg', 'dec', 'delete',
    'dispose', 'diskfree', 'disksize', 'dseg', 'eof', 'eoln', 'erase', 
    'exit', 'exp', 'filepos', 'filesize', 'fillchar', 'flush', 'frac', 
    'freemem', 'getdir', 'getmem', 'halt', 'hi', 'inc', 'insert', 'int', 
    'IOresult', 'length', 'ln', 'lo', 'mark', 'maxavail', 'memavail', 
    'member', 'mkdir', 'move', 'new', 'odd', 'ofs', 'ord', 'paramcount', 
    'paramstr', 'pi', 'pointer', 'pos', 'pred', 'ptr', 'random', 
    'randomize', 'read', 'readln', 'release', 'rename', 'reset', 'rewrite', 
    'rmdir', 'round', 'runerror', 'seek', 'seekeof', 'seekeoln', 'seg', 
    'self', 'sin', 'sizeof', 'sqr', 'sqrt', 'sseg', 'str', 'succ', 'swap', 
    'trunc', 'truncate', 'upcase', 'val', 'write', 'writeln'],
  
  '.py':  ['__import__', 'abs', 'all', 'apply', 'basestring', 'bin', 'bool',
    'buffer', 'bytearray', 'call', 'callable', 'chr', 'classmethod', 'cmp',
    'coerce', 'compile', 'complex', 'delattr', 'dict', 'dir', 'divmod',
    'enumerate', 'eval', 'execfile', 'file', 'filter', 'float', 'format',
    'getattr', 'globals', 'hasattr', 'hash', 'help', 'hex', 'id', 'input',
    'int', 'isinstance', 'issubclass', 'iter', 'len', 'list', 'locals',
    'long', 'map', 'max', 'memoryview', 'min', 'object', 'oct', 'open',
    'ord', 'pow', 'print', 'range', 'raw_input', 'reduce', 'reload',
    'repr', 'reversed', 'round', 'set', 'setattr', 'slice', 'sorted',
    'staticmethod', 'str', 'sum', 'super', 'tuple', 'type', 'unichr',
    'unicode', 'vars', 'xrange', 'zip'],
    
  '.ps1': ['Add-Member', 'CmdletBinding', 'Format-Table', 'Get-Acl', 
    'Get-ChildItem', 'Get-Content',
    'Group-Object', 'Measure-Object', 'New-Object', 'Select-Object',
    'Sort-Object', 'Test-Path', 'Where-Object', 'Write-Debug', 
    'Write-Error','Write-Host', 'Write-Output', 'Write-Verbose', 
    'Write-Warning'],
    
  '.rs': ['print!', 'println!'],
        
  '.sh':  ['alias', 'bg', 'bind', 'break', 'builtin', 'caller', 'cd',
    'command', 'continue', 'declare', 'dirs', 'echo', 'enable', 'eval',
    'exec', 'exit', 'export', 'fc', 'fg', 'getopts', 'hash', 'help',
    'history', 'jobs', 'kill', 'let', 'local', 'logout', 'mapfile', 'popd',
    'printf', 'pushd', 'pwd', 'read', 'readarray', 'readonly', 'return',
    'set', 'shift', 'shopt', 'source', 'suspend', 'test', 'times', 'trap',
    'tyeset', 'ulimit', 'umask', 'unalias', 'unset', 'wait'],
    
  '.vbs': [
    # Date/Time Functions
    'CDate', 'Date', 'DateAdd', 'DateDiff', 'DatePart', 'DateSerial',
    'DateValue', 'Day', 'FormatDateTime', 'Hour', 'IsDate', 'Minute',
    'Month', 'MonthName', 'Now', 'Second', 'Time', 'Timer', 'TimeSerial',
    'TimeValue', 'Weekday', 'WeekdayName', 'Year',
    # Conversion
    'Asc', 'CBool', 'CByte', 'CCur', 'CDate', 'CDbl', 'Chr', 'CInt', 'CLng',
    'CSng', 'CStr', 'Hex', 'Oct',
    # Formating
    'FormatCurrency', 'FormatDateTime', 'FormatNumber', 'FormatPercent',
    # Math
    'Abs', 'Atn', 'Cos', 'Exp', 'Hex', 'Int', 'Fix', 'Log', 'Oct', 'Rnd',
    'Sgn', 'Sin', 'Sqr', 'Tan',
    # Array
    'Array', 'Filter', 'IsArray', 'Join', 'LBound', 'Split', 'UBound',
    # String
    'InStr', 'InStrRev', 'LCase', 'Left', 'Len', 'LTrim', 'RTrim', 'Trim',
    'Mid', 'Replace', 'Right', 'Space', 'StrComp', 'String', 'StrReverse',
    'UCase',
    # Other
    'CreateObject', 'Eval', 'IsEmpty', 'IsNull', 'IsNumeric', 'IsObject',
    'RGB', 'Round', 'ScriptEngine', 'ScriptEngineBuildVersion',
    'ScriptEngineMajorVersion', 'ScriptEngineMinorVersion',
    'TypeName', 'VarType'
    ],
  '': []
  }
 
_reserved = { # Reserved Tokens 
  '.a68': [],
  '.bas': ['%INCLUDE'],
  '.c':   ['#include', '#define', '#ifdef'],
  '.cmd':   [],
  '.dcl': ['error', 'warning', 'control_Y', 'ERROR', 'WARNING', 'CONTROL_Y'],
  '.h':   [],
  '.f77': [],
  '.for': [],
  '.ftn': [],
  '.pas': [],
  '.py':  ['KeyboardInterrupt', 'SystemExit', 'IOError'],
  '.ps1': ['Continue', 'Ignore', 'Inquire', 'SilentlyContinue', 'Stop',
    'Suspend'],
  '.rs':  [],
  '.sh':  [],
  '.vbs': ['Nothing', 'vbTab', 'vbCRLF', 'vbOKOnly', 'vbError'],
  '':     []
  }
 
def _print(_line):
  global _number, _nonblank, _strip, _lines, _blanks, _comment, _string
  global _format
  if len(_line) > 1: _blanks = 0
  if not(_blanks > 1 and _strip):
    if _number and not(len(_line) == 1 and _nonblank):
      _lines += 1
      sys.stdout.write(_expand("%6d  " % _lines))
    sys.stdout.write(_line)
  _blanks += 1
 
def _flush(_buffer):
  global _line
  #_buffer = _buffer + '<>'   # Delimit output for debugging
  for _char in _buffer:
    _line += _char
    _buffer = _buffer[1:]
    if _char in _eoln:
      #sys.stdout.write(_line)
      _print(_line)
      _line = ""
 
def _expand(_buffer):
  global _format
  _return = ""
  for _char in _buffer:
    if _format == 'html':
      if _char == '&':
        _return += "&amp;"
      elif _char == "#":
        _return += "&#035;"
      elif _char == " ":
        _return += "&nbsp;"
      elif _char == ">":
        _return += "&#062;"
      elif _char == "<":
        _return += "&#060;"
      elif _char == "-":
        _return += "&#045;"
      elif _char == ".":
        _return += "&#046;"
      elif _char == "'":
        _return += "&#039;"
      elif _char == "\"":
        _return += "&#034;"
      elif _char == ":":
        _return += "&#058;"
      elif _char == "x":
        _return += "&#120;"
      elif _char == "X":
        _return += "&#088;"
      else:
        _return += _char
    else:
      _return += _char
  return _return
 
def _isnumeric(_value):
  try:
    _number = float(_value)
  except ValueError:
    return False
  else:
    return True
 
_names = []
_restart = False
_number = False
_nonblank = False
_strip = False
_format = "" # Default
 
for _arg in sys.argv[1:]:
  if _arg[:2] == "--":
    if _arg in "--text":
      _format = ""
    elif _arg in "--squeeze-blank":
      _strip = True
    elif _arg in "--restart":
      _number = True
      _restart = True
 
    elif _arg in "--number":
      _number = True
    elif _arg == "--html":
      _format = "html"
    elif _arg in "--number-nonblank":
      _number = True
      _nonblank = True
    elif _arg == "--ansi":
      _format = "ansi"
    elif _arg in "--help":
      _about()
    elif _arg in "--version":
      _version()
    else:
      _unrecognized(_arg)
  else:
    if _arg[:1] == "-" and len(_arg) > 1: # '-' by itself is valid (stdin).
      if _arg == "-t":
        _format = ""
      elif _arg == "-s":
        _strip = True
      elif _arg == "-r":
        _number = True
        _restart = True
      elif _arg == "-n":
        _number = True
      elif _arg == "-h":
        _format = "html"
      elif _arg == "-b":
        _number = True
        _nonblank = True
      elif _arg == "-a":
        _format = "ansi"
      else:
        _invalid(_arg)
    else:
      _names.append(_arg) # If it isn't a qualified
 
if not len(_names) : _names.append("") # Default to stdin.
 
_lines = 0
_blanks = 0
_string = False
_comment = False
 
for _name in _names:
  _type = os.path.splitext(_name)[1]
  if _type not in _types: _type = ''
 
  _seperators = _spaces + _delimiters[_type] + _quotes[_type]
  #_seperators += _operators[_type]
  _buffer = ""
  _line = ""
 
  try:
    with open(_name, 'r') as _file:
      if _restart : _lines = 0
      sys.stdout.write((_formats[_format]["body"]))
      #_char = _file.read(1)
      _char = "\n" # Start with a newline!!
      while _char:
        if _char in _seperators + _eoln:
 
          # - Check for strings.
          if _char in _quotes[_type]:
            _offset = _quotes[_type].index(_char)
            _flush(_expand(_buffer) + _formats[_format]["string"])
            _flush(_expand(_char))
            _flag = False
            _numeric = False
            _buffer = ""
            _char = _file.read(1)
            # Scan input until we find the closing quote.
            # Note - There will allways be at least one escaped character,
            # even if it is a quote!
            while _char <> _quotes[_type][_offset] or (_flag and _count == 1):
              if _char in _eoln:
                _flush(_buffer + _formats[_format][""] + _expand(_char))
                _flush(_formats[_format]["string"])
                _buffer = ""
                _char = ""
              if _flag:
                if _count == 1 and _char.isdigit(): _numeric = True
                if (((_char in _hexadecimal and _count < 4 or
                   (_char == "x" or _char =="X") and _count == 2) and
                   _numeric) or _count == 1):
                  # Both hexadecimal and octal constants contain up to three
                  # digits, if you don't count the 'X'.
                  if not (_char == "x" or _char =="X"): _count += 1
                else:
                  _buffer += _formats[_format][""]
                  _buffer += _formats[_format]["string"]
                  _flag = False
              else:
                if _char in _escape[_type]:
                  _buffer += _formats[_format][""]
                  _buffer += _formats[_format]["escape"]
                  _flag = True
                  _count = 1
              _buffer += _expand(_char)
              _char = _file.read(1)
            # Print string
            if _flag:
              _buffer += _formats[_format][""] + _formats[_format]["string"]
            _buffer += _expand(_char) + _formats[_format][""]
            _flush(_buffer)
            _char = ""
            _buffer = ""
 
          # - Check for comments (which _may_ be preceded by a newline).
          elif (_buffer in _comments[_type] or
                _buffer[1:] in _comments[_type]):
            if _buffer[:1] in _eoln or  _buffer[:1] in _spaces:
              _flush(_expand(_buffer[:1]))
              _buffer = _buffer[1:]
            _offset = 0
            for _count, _value in enumerate(_comments[_type]):
              if _buffer in _value:
                _offset = _count
            _flush(_formats[_format]["comment"] + _expand(_buffer))
            _buffer = ""
            # - Process comment until we find a terminator.
            while _char and not _code[_type][_offset] in (_buffer + _char):
              if _char in _eoln:
                _flush(_expand(_buffer) + _formats[_format][""])
                _flush(_expand(_char) + _formats[_format]["comment"])
                _buffer = ""
                _char = ""
              _buffer += _char
              _char = _file.read(1)
            if _char in _eoln:
              _flush(_expand(_buffer) + _formats[_format][""])
            else:
              _flush(_expand(_buffer + _char) + _formats[_format][""])
              _char = ""
            _buffer = ""
 
          # - Check for keywords.
          elif (_buffer in _keywords[_type] or
                _buffer[1:] in _keywords[_type]):
            if _buffer[:1] in _eoln or _seperators:
              _flush(_expand(_buffer[:1]))
              _buffer = _buffer[1:]
            _flush(_formats[_format]["keyword"] + _expand(_buffer))
            _flush(_formats[_format][""])
            _buffer = ""
 
          # - Check for functions.
          elif (_buffer in _functions[_type] or
                _buffer[1:] in _functions[_type]):
            if _buffer[:1] in _eoln or _seperators:
              _flush(_expand(_buffer[:1]))
              _buffer = _buffer[1:]
            _flush(_formats[_format]["function"] + _expand(_buffer))
            _flush(_formats[_format][""])
            _buffer = ""
 
          # - Check for reserved words.
          elif (_buffer in _reserved[_type] or
                _buffer[1:] in _reserved[_type]):
            if _buffer[:1] in _eoln or _seperators:
              _flush(_expand(_buffer[:1]))
              _buffer = _buffer[1:]
            _flush(_formats[_format]["reserved"] + _expand(_buffer))
            _flush(_formats[_format][""])
            _buffer = ""
 
          # - Check for numbers.
          elif _type <> '' and (_isnumeric(_buffer) or _isnumeric(_buffer[1:])):
            if _buffer[:1] in _eoln or _seperators:
              _flush(_expand(_buffer[:1]))
              _buffer = _buffer[1:]
              while (_isnumeric(_buffer + _char) and not
                     _char in _seperators + _eoln):
                _buffer += _char
                _char = _file.read(1)
            _flush(_formats[_format]["number"] + _expand(_buffer))
            _flush(_formats[_format][""])
            _buffer = ""
 
          _flush(_expand(_buffer))
          _buffer = _char
        else:
          _buffer += _char
 
        _char = _file.read(1)
 
      _char = "\n" # End with a newline!!
      _buffer += _char
      _flush(_expand(_buffer) + _formats[_format][""])
      sys.stdout.write((_formats[_format]["end"]))
 
  except KeyboardInterrupt :
    sys.stdout.write("\n")
    sys.stdout.flush()
    raise SystemExit 
  except IOError as _err :
    _error(_err.strerror) 
