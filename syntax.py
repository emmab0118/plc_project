import tokenize
import io
import keyword
import builtins
import re
import tkinter as tk
from tkinter import font as tkfont
from collections import defaultdict

class SyntaxHighlighter:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self._setup_colors()
        self._configure_tags()
        self._setup_font()
        
        #avoid repeated dir() calls
        self.builtins = set(dir(builtins)) | {'self', 'cls'}
        
        #t rack multiline strings
        self.multiline_string_ranges = []

    def _setup_colors(self):
        #define color scheme for elements
        self.colors = {
            'keyword': '#3d75ec',        #blue
            'builtin': '#6f42c1',        #purple
            'string': '#00d200',         #green
            'docstring': '#228B22',      #dark green
            'comment': '#959595',        #gray
            'number': '#442288',         #dark prple
            'function': '#005cc5',       #dark blue
            'class': '#d42baf',          #pink
            'decorator': '#e0701f',      #orange
            'operator': '#000000',       #black
            'error': '#FF0000',          #red
            'current_line': '#e6f3ff',   #light blue
            'highlight': '#ffff00'       #yellow
        }

    def _configure_tags(self):
        #configure text widget tags with colors
        for tag_name, color in self.colors.items():
            self.text_widget.tag_configure(tag_name, foreground=color)
        self.text_widget.tag_configure('current_line', background=self.colors['current_line'])

    def _setup_font(self):
        #font and tab sizing
        default_font = tkfont.Font(font=self.text_widget['font'])
        self.text_widget.configure(
            font=default_font,
            tabs=(default_font.measure('    '), 'center')
        )

    def highlight_syntax(self, event=None):
        #apply Python syntax highlighting to the text, clear existing tags except current_line and highlight
        for tag in self.text_widget.tag_names():
            if tag not in ('current_line', 'highlight'):
                self.text_widget.tag_remove(tag, '1.0', 'end')
        
        #get visible text region for performance
        first_line = int(self.text_widget.index('@0,0').split('.')[0])
        last_line = int(self.text_widget.index(f'@0,{self.text_widget.winfo_height()}').split('.')[0]) + 2
        visible_text = self.text_widget.get(f'{first_line}.0', f'{last_line}.end')
        
        try:
            #tokenize the visible content
            tokens = tokenize.generate_tokens(io.StringIO(visible_text).readline)
            self._process_tokens(tokens, first_line)
        except (tokenize.TokenError, IndentationError):
            pass  #skip highlighting on syntax errors

    def _process_tokens(self, tokens, start_line):
        #process tokens and apply appropriate highlighting
        self.multiline_string_ranges = []
        
        for tok in tokens:
            toknum, tokval, (srow, scol), (erow, ecol), _ = tok
            start = f"{srow + start_line - 1}.{scol}"
            end = f"{erow + start_line - 1}.{ecol}"
            
            #handle diff token types
            if toknum == tokenize.NAME:
                self._highlight_name(tokval, start, end)
            elif toknum == tokenize.STRING:
                self._highlight_string(tokval, start, end, srow, erow)
            elif toknum == tokenize.NUMBER:
                self.text_widget.tag_add('number', start, end)
            elif toknum == tokenize.COMMENT:
                self.text_widget.tag_add('comment', start, end)
            elif toknum == tokenize.OP:
                self._highlight_operator(tokval, start, end)

    def _highlight_name(self, name, start, end):
        #highlight Python names 
        if keyword.iskeyword(name):
            self.text_widget.tag_add('keyword', start, end)
        elif name in self.builtins:
            self.text_widget.tag_add('builtin', start, end)
        elif name.startswith('__') and name.endswith('__'):
            self.text_widget.tag_add('builtin', start, end)

    def _highlight_string(self, string, start, end, srow, erow):
        #handle string highlighting 
        if srow != erow:  # Multiline string (docstring)
            self.text_widget.tag_add('docstring', start, end)
            self.multiline_string_ranges.append((start, end))
        elif string.startswith(('"""', "'''")) or string.endswith(('"""', "'''")):
            self.text_widget.tag_add('docstring', start, end)
        else:
            self.text_widget.tag_add('string', start, end)

    def _highlight_operator(self, operator, start, end):
        #operators and decorators
        if operator == '@':
            # Find the end of the decorator name
            line = self.text_widget.get(start, f"{start.split('.')[0]}.end")
            match = re.search(r'@(\w+)', line)
            if match:
                decorator_end = f"{start.split('.')[0]}.{match.end()}"
                self.text_widget.tag_add('decorator', start, decorator_end)
        else:
            self.text_widget.tag_add('operator', start, end)

    def highlight_line(self, line_num):
        #highlight a specific line for errors or debugging
        self.text_widget.tag_remove('error', '1.0', 'end')
        if line_num > 0:
            self.text_widget.tag_add('error', f'{line_num}.0', f'{line_num}.end')

    def highlight_range(self, start_pos, end_pos):
        #highlight a specific range of text
        self.text_widget.tag_add('highlight', start_pos, end_pos)

    def clear_highlight(self):
        self.text_widget.tag_remove('highlight', '1.0', 'end')