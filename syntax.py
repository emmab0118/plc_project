import tokenize
import io
import keyword

class SyntaxHighlighter:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.colors = {
            'keyword': 'blue',
            'string': 'green',
            'comment': 'red',
            'number': 'purple',
            'builtin': 'orange',
            'default': 'black'
        }
        self._configure_tags()

    def _configure_tags(self):
        #configure text tags for syntax highlighting 
        for tag_name, color in self.colors.items():
            self.text_widget.tag_configure(tag_name, foreground=color)

    def highlight_syntax(self, event=None):
        #remove tags and applies syntax highlighting to the code
        for tag in self.text_widget.tag_names():
            self.text_widget.tag_remove(tag, "1.0", "end")
        
        #get all content
        text = self.text_widget.get("1.0", "end-1c")
        
        try:
            #tokenize the content
            tokens = tokenize.generate_tokens(io.StringIO(text).readline)
            
            for toknum, tokval, (srow, scol), (erow, ecol), _ in tokens:
                #convert row/col to tkinter positions
                start_pos = f"{srow}.{scol}"
                end_pos = f"{erow}.{ecol}"
                
                #apply appropriate tag based on token type
                if toknum == tokenize.NAME:
                    if keyword.iskeyword(tokval):
                        self.text_widget.tag_add('keyword', start_pos, end_pos)
                    elif tokval in dir(__builtins__):
                        self.text_widget.tag_add('builtin', start_pos, end_pos)
                elif toknum == tokenize.STRING:
                    self.text_widget.tag_add('string', start_pos, end_pos)
                elif toknum == tokenize.NUMBER:
                    self.text_widget.tag_add('number', start_pos, end_pos)
                elif toknum == tokenize.COMMENT:
                    self.text_widget.tag_add('comment', start_pos, end_pos)
                    
        except (tokenize.TokenError, IndentationError, AttributeError):
            #skip highlighting when error
            pass