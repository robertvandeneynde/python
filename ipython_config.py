c = get_config()

#------------------------------------------------------------------------------
# PromptManager configuration
#------------------------------------------------------------------------------

# This is the primary interface for producing IPython's prompts.

# using in_template: https://stackoverflow.com/questions/22150661/ipython-customize-prompt-to-display-cell-run-time
# https://github.com/ipython/ipython/blob/master/IPython/terminal/prompts.py
# https://ipython.readthedocs.io/en/latest/config/details.html#custom-prompts
from datetime import datetime, timedelta
from IPython.terminal.prompts import Prompts, Token, ClassicPrompts

class SpaceContinuationPrompts(Prompts):
    """ Doesn't print "...:" but only spaces """
    def continuation_prompt_tokens(self, *a, **b):
        try:
            token, = Prompts.continuation_prompt_tokens(self, *a, **b)
        except:
            raise AssertionError('continuation_prompt is supposed to be of len 1')
        return [
            (token[0], ' ' * len(token[1]))
        ]

# Todo, find out why this class does the same as the one before
class NoContinuationPrompts(Prompts):
    """ Doesn't print "...:" """
    def continuation_prompt_tokens(self, *a, **b):
        return [
            (Token.Prompt, '')
        ]

class DateTimePrompts(Prompts):
    """
    Prints current time at every N prompts and other variations in order to measure the time you spent in ipython.
    """
    
    def set_format(self, format):
        self.format = format
    
    def set_n(self, n):
        self.n = n
        
    def set_minutes(self, m): # m:float
        self.minutes = minutes
    
    def set_interval(self, interval):
        self.interval = interval
        
    def set_no_modulo(self, no_modulo):
        self.no_modulo = no_modulo
        
    def set_no_timebased(self, no_timebased):
        self.no_timebased = no_timebased
    
    def in_prompt_tokens(self, cli=None):
        assert cli is None  # IPython 6 to 7
        from datetime import datetime, timedelta
        
        if not hasattr(self, 'memory'):
            self.memory = {}
            self.memory_to = {}
            self.printed = {}
        
        printed = self.printed

        fmt = getattr(self, 'format', '%H:%M')
        interval = getattr(self, 'interval', False)
        N = getattr(self, 'n', 10)
        minutes = getattr(self, 'minutes', 5)
        no_timebased = getattr(self, 'no_timebased', False)
        no_modulo = getattr(self, 'no_modulo', True)
        
        n = self.shell.execution_count
        
        if n not in self.memory:
            self.memory_to[n] = self.memory[n] = datetime.now()
        else:
            self.memory_to[n] = datetime.now()
        
        try:
            difference = self.memory_to[n] - self.last_printed
        except AttributeError:
            difference = None
        
        datestr1 = self.memory[n].strftime(fmt)
        datestr2 = datestr1 if not interval else self.memory_to[n].strftime(fmt)
        
        if n not in printed:
            printed[n] = (
                n == 1
                or n % N == 0 and not no_modulo
                or difference and abs(difference) > timedelta(minutes=minutes) and not no_timebased
            )
        
        # print('[', 'last_printed', getattr(self, 'last_printed', None), 'difference', difference, 'printed', printed, ']')
        
        if printed[n]:
            self.last_printed = self.memory[n]
        
        return [
            (Token.Comment, '# ' + (datestr1 if datestr1 == datestr2 else '{} - {}'.format(datestr1, datestr2)) + ' ' + '\n')
        ] * printed[n] + Prompts.in_prompt_tokens(self)  # Ipython 6 to 7 (no cli)
    
c.TerminalInteractiveShell.prompts_class = type('MyPrompt', (DateTimePrompts, SpaceContinuationPrompts), {})

################################
# Defaults options uncommented #
################################

# Whether to display a banner upon starting IPython.
c.TerminalIPythonApp.display_banner = False  # default True

# Set to confirm when you try to exit IPython with an EOF (Control-D in Unix,
# Control-Z/Enter in Windows). By typing 'exit' or 'quit', you can force a
# direct exit without any confirmation.
c.TerminalInteractiveShell.confirm_exit = False  # default True

# Make IPython automatically call any callable object even if you didn't type
# explicit parentheses. autocall = 0 (disable), 1 (smart), 2 (full)
c.TerminalInteractiveShell.autocall = 1

# Show rewritten input, e.g. for autocall.
c.TerminalInteractiveShell.show_rewritten_input = False
