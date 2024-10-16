import numpy as np
from amps.functions import *


class Question:

    def __init__(self, qt=None, file=None, id=None):
        '''
        Parameters 
            file - path for file containing problem template
            qt - question template (string)
            id - identifier for problem
        '''
        
        self.file = file
        self.qt = qt
        self.id = id
        
        self.type = 'MC'
        self.margin = '0'
        
        # Create items to store information from template
        self.var_script = ''
        self.conditions = []
        
        self.text_raw = ''
        self.text_canvas_new = ''
        self.text_canvas_old = ''
        
        self.answer_options = []
        
        self.versions = []
        
        # Check if a template has been provided. 
        if qt is None and file is None:
            print('No problem template has been provided.')
            return
        
        # If template has been provided as a file, load it. 
        if qt is None:
            with open(file) as f:
                self.qt = f.read()

        # Parse the template and text
        self.parse_template()
        self.parse_text()


    def parse_template(self):
        
        mode = None
        
        # Split question template
        lines = self.qt.split('\n')
        
        for line in lines:
            #line = line.strip()
            
            #-----------------------------------------------------
            # Skip blank lines unless processing the question text
            #-----------------------------------------------------
            if line == '' and mode != '#---TEXT---#':
                pass

            #-----------------------------------------------
            # Determine the mode
            #-----------------------------------------------
            elif line[:4] == '#---':
                mode = line
            
            #-----------------------------------------------
            # config
            #-----------------------------------------------
            elif mode == '#---CONFIG---#':
                line = line.strip(' ')
                line = line.replace('= ', '=')
                line = line.replace(' =', '=')
                #print(len(line))
                param, value = line.split('=')
                if param == 'type':
                    self.type = value
                elif param == 'margin':
                    self.margin = value
                elif param == 'id':
                    self.id = value
            
            #-----------------------------------------------
            # VARIABLES
            #-----------------------------------------------
            elif mode == '#---VARIABLES---#':
                self.var_script += line + '\n'
            
            #-----------------------------------------------
            # Distractors
            #-----------------------------------------------
            elif mode == '#---DISTRACTORS---#':
                self.var_script += line + '\n'
                
            #-----------------------------------------------
            #  CONDITIONS
            #-----------------------------------------------
            elif mode == '#---CONDITIONS---#':
                self.conditions.append(line)
                
            #-----------------------------------------------
            #  TEXT
            #-----------------------------------------------
            elif mode == '#---TEXT---#':
                self.text_raw += line + '\n'

            #-----------------------------------------------
            # ANSWER_OPTIONS
            #-----------------------------------------------
            elif mode == '#---ANSWER_OPTIONS---#':
                self.answer_options.append(line)
                

    def parse_text(self):

        sections = []
        
        cur_sec = {'mode':'text', 'prev':None, 'next':None, 'lines':[], 'blanks':0}
        
        mode = 'text'
        
        lines = self.text_raw.split('\n')
        for line in lines:
            prev_mode = mode
            
            #---------------------------------------
            # Determine new mode
            #---------------------------------------
            stripped = line.strip(' ')
            if stripped == '':
                mode = 'blank'
            elif stripped == 'TABLE' or mode == 'table':    
                mode = 'table'
            elif stripped[0] == '*':
                mode = 'list'
            elif stripped[0] == '$' and stripped[-1] == '$':
                mode = 'eqn'
            else:
                mode = 'text'
            
            
            if mode == 'blank':
                cur_sec['blanks'] += 1
            
            else:
                # Append content if mode has not changed
                # Also start a new component for equations. 
                if prev_mode == mode and mode != 'eqn':
                    cur_sec['lines'].append(line)
                
                # If mode has changed, start a new component. 
                else:
                    cur_sec['next'] = mode
                    old_mode = cur_sec['mode']
                    sections.append(cur_sec)
                    cur_sec = {'mode':mode, 'prev':old_mode, 'next':None, 'lines':[line], 'blanks':0}
            
            if stripped == 'END TABLE':
                mode = None
       
        sections.append(cur_sec)
        
    
        for s in sections:
            temp = s.copy()
            temp['lines'] = len(temp['lines'])
            #print(temp)

        text_new = ''
        text_old = ''
        text_jup = ''
        for s in sections:
            text_new += self.process_section(s, 'new')
            text_old += self.process_section(s, 'old')
            text_jup += self.process_section(s, 'jup')
        
        self.text_canvas_new = text_new
        self.text_canvas_old = text_old
        self.text_jupyter = text_jup
        
        

    def process_section(self, s, output='new'):
        text = ''
        
        N = s['blanks']
        
        if s['mode'] == 'text':
            # Start new paragraph, if needed
            if s['prev'] != 'text':
                text += '<p style="margin: 0px 0px 12px 0px;">'
                
            # Glue lines together. 
            for line in s['lines']:
                text += line.strip(' ') + ' '
            
            # Close paragraph
            K = 0 if (N <= 1 or s['next'] is None) else N
            text += '\n' + '<br/>' * K + '</p>\n'
            
        
        elif s['mode'] == 'list':
            # Start list
            text += '<ul>\n'
            
            # Add list items
            for line in s['lines']:
                line = line[1:].strip(' ')
                text += f'    <li>{line}</li>\n'
            
            # End list
            text += '</ul>\n'
            text += blank_lines(N-1)
            
        elif s['mode'] == 'eqn':
            K = 0 if (N <= 1 or s['next'] is None) else N
            bp = '<br/>' * K
            
            for line in s['lines']:  # There should always be only one line in an EQN section. 
                if line[:2] == '$$':
                    text += f'<p style="text-align: center; margin: 0px 0px 12px 0px;">{line}{bp}</p>\n'
                elif line[:4] == '    ':
                    text += f'<p style="padding-left:40px; margin: 0px 0px 12px 0px;">{line}{bp}</p>\n'
                else:
                    text += f'<p margin: 0px 0px 12px 0px;>{line}{bp}</p>\n'
        
        elif s['mode'] == 'table':
            
            table_contents = []
            table_config = {}
            
            for line in s['lines'][1:-2]:
                cells = line.split('|')[1:-1]
                cells = [c.strip(' ') for c in cells]
                table_contents.append(cells)
            params = s['lines'][-2].split(';')
            for p_set in params:
                p,v = p_set.split(':')
                p = p.strip(' ')
                v = v.strip(' ')
                if v not in ['C', 'L', 'R']:
                    v = eval(v)
                table_config[p.lower()] = v
            
            text += TABLE(table_contents, table_config)
            text += blank_lines(N-1)


        return text
        

    #------------------------------------------------------------
    # generate function creates versions from template
    #------------------------------------------------------------
    def generate(self, n=1, seed=None, attempts=1000, prevent_duplicates=True):
        '''
        Description: Creates versions from template
        
        Paramters:
        n                  : Number of versions to generate.
        attempts           : Total number of attempts allowed to generate each question
        prevent_duplicates : ??????????????????
        seed               : Seed for RNG
        '''
        
        from IPython.core.display import HTML, display
        
        self.versions = []
        
        generation_attempts = 0
        duplicates_encountered = 0
        
        if seed is not None:
            np.random.seed(seed)
        
        
        # Loop for the desired number of questions
        for i in range(n):
            
            # Attempt to generated a problem
            for k in range(attempts):
                
                generation_attempts += 1
                version = self.generate_one()
                
                # Check to see if conditions were met.
                # If not, restart loop and try again. 
                if version is None:
                    continue
                
                
                # Check to see if the question is a duplicate
                # If so, restart loop and try again. 
                if prevent_duplicates:
                    dup = False
                    for v in self.versions:
                        if version['text_new'] == v['text_new']:
                            duplicates_encountered += 1
                            dup = True 
                            break
                    if dup: continue
                
                break  # if here, a version was found
            
            # Add version to list
            self.versions.append(version)
                
        
        display(HTML('<b>Generating Versions</b>'))
        print(f'{generation_attempts} attempts were required to generate {n} versions. {duplicates_encountered} duplicate versions were generated and discarded.\n')
        

    def generate_one(self, testing_level=0, verbose=False):
        from IPython.core.display import HTML, display
        
        # Prepare Scope
        scope = {}
        exec('from amps.functions import *', scope)
        
        
        # Execute Variables
        exec(self.var_script, scope)
        del scope['__builtins__']       # Just for tidiness
        
        # Get rid of precision/rounding issues.
        for k, v in scope.items():
            if isinstance(v, float):
                scope[k] = round(v, 12)
        
        # Check conditions
        for cond in self.conditions:
            valid = eval(cond, scope)
            if not valid:
                if verbose: print(f'  Unsatisfied Condition: "{cond}"')
                return None
        
        
        # Insert variables into text and answer options. 
        version_dict = {
            'text_new' : insert_vars(self.text_canvas_new, scope),
            'text_old' : insert_vars(self.text_canvas_old, scope),
            'text_jup' : insert_vars(self.text_jupyter, scope),
            'answer_options' : [insert_vars(ao, scope) for ao in self.answer_options]
        }
        
        return version_dict


    def display_versions(self, size=3, limit=None, compact_answers=False, colab=False):
        from IPython.display import HTML, display, Markdown, Latex, Javascript
        
        # This is a hack used to fix display in Colab
        if colab:
            display(Latex(""))
        
        if len(self.versions) == 0:
            print('No versions have been generated. Please call the generate() method.')
            return
        
        if limit is None: limit = len(self.versions) 
        limit = min(limit, len(self.versions))
        
        display(HTML('<b>Displaying Versions</b><br /><br />'))
        
        for i in range(limit):
            text = self.versions[i]['text_jup']
            answer_options = self.versions[i]['answer_options']
            
            display(HTML(f'<hr><b>Version {i+1}</b>'))
            display(Markdown(f'<font size="{size}">{text}</font>'))
            print()
            
            # Display Multiple Choice Answers
            if self.type == 'MC':
                if compact_answers:
                    print(answer_options)
                else:
                    letters = list('abcdefghijklmnopqrstuvwzyz')
                    for i, ao in enumerate(answer_options):
                        x = letters[i]
                        #print(f'[{x}] {ao}' if i==0 else f'({x}) {ao}')
                        display(Markdown(f'`[{x}]` {ao}' if i==0 else f'`({x})` {ao}'))
            
            if self.type == 'MA':
                if compact_answers:
                    print(answer_options)
                else:
                    for i, ao in enumerate(answer_options):
                        #print(f'[{x}] {ao}' if i==0 else f'({x}) {ao}')
                        ao_mod = ao
                        if ao_mod[:3] == '[ ]': ao_mod = '`[ ]`' + ao_mod[3:]
                        elif ao_mod[:3] == '[X]': ao_mod = '`[X]`' + ao_mod[3:]
                            
                        display(Markdown(f'{ao_mod}'))
            
                        
            # Display Numerical Answers
            elif self.type == 'NUM':
                print(f'ANSWER: {answer_options[0]} +- {self.margin}')
            print()    
        
        display(HTML('<hr>'))
        
        # This is a hack used to fix display in Colab
        if colab: 
            from amps.autorender import katex_autorender_min
            display(Javascript(katex_autorender_min))
            
    def generate_qti(self, path='', quiz_version='new', print_versions=0, 
                     make_file=True, generate_zip=False):
        import os
        
        if len(self.versions) == 0:
            print('No versions have been generated. Please call the generate() method.')
            return
        
        qti_text = f'Quiz title: {self.id}\n'
        qti_text += 'Quiz description: Generated by Vario.\n\n'
        
        for i, v in enumerate(self.versions):
            
            if quiz_version == 'new':
                version_text = self.versions[i]['text_new']
            elif quiz_version == 'old':
                version_text = self.versions[i]['text_old']
            else:
                print('Quiz version not recognized.')
                return
            
            #if quiz_version == 'new':
                #version_text = version_text.replace('</p>', '<br/><br/></p>\n')
                #version_text = version_text.replace('</table>', '</table><p>&nbsp;</p>')
                        
            num_len = len(str(i+1))
            spaces = ' ' * (num_len + 2)
                        
            version_text = version_text.replace('\n', f'\n{spaces}')
            
            qti_text += f'Title: Version {i+1}\n'
            qti_text += f'Points: 1\n'
            qti_text += f'{i+1}. {version_text}\n'
            
            answer_options = self.versions[i]['answer_options']
            
            # Add Multiple Choice Answer Options
            if self.type == 'MC':
                letters = list('abcdefghijklmnopqrstuvwzyz')
                for j, ao in enumerate(answer_options):
                    x = letters[j]
                    if x == 'a': x = '*a'
                    qti_text += f'{x}) {ao}\n' 

            # Add Multiple Answer Options
            if self.type == 'MA':
                for j, ao in enumerate(answer_options):
                    ao_mod = ao.replace('[X]', '[*]')
                    qti_text += f'{ao_mod}\n' 
            
                                            
            # Add Numerical Answer
            elif self.type == 'NUM':
                ans = answer_options[0]
                qti_text += f'=   {ans} +- {self.margin}'
        
            qti_text += '\n\n'
            
            if i+1 == print_versions:    
                print(qti_text)
        
        if make_file:
            if path != '':
                if path[-1] != '/':
                    path = path + '/'
            
                if not os.path.exists(path):
                    os.mkdir(path)
                
            with open(f'{path}{self.id}.txt', 'w') as file:
                file.write(qti_text)
            
        if generate_zip:
            import subprocess
            cmd = f'text2qti "{path}{self.id}.txt"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
            if result.returncode != 0:
                print(result.returncode)
                print()
                print(result.stdout)
                print()
                print(result.stderr)
            else:
                print('QTI zip generated successfully!')
        



def insert_vars(text, scope):
    a = 0
    b = 0
    temp = text
    new_text = ''
        
    while len(temp) > 0:
        
        a = temp.find('[[')
        while temp[a+2] == '[':
            a += 1
        
        b = temp.find(']]', a)
        
        if a == -1 or b == -1:
            new_text += temp 
            break
        
        var_string = temp[a+2:b]      
        new_text += temp[:a]
        new_text += DISPLAY(var_string, scope)            
        
        temp = temp[b+2:]

    return new_text


def DISPLAY(x, scope):
       
    tokens = x.split(':')
    
    var_name = tokens[0]
    value = eval(var_name, scope)
    
    
    # If only a value is supplied, find it and move on
    if len(tokens) == 1:
        return str(value)
    
    # Get params (they exist, if we get to this point)
    param_string = tokens[1]
    params = param_string.split(',')
    
    prec = params[0].strip()
    fmt = 'U' if len(params) == 1 else params[1].strip()

    if prec != '':
        # If var_name contains operations (x*10) then format method will break.
        # We will create a temp variable to handle this situation. 
        if var_name not in scope.keys():
            scope['__TEMP_VAR__'] = value
            var_name = '__TEMP_VAR__'
        
        f_string = '{' + f'{var_name}:.{prec}f' + '}'
        
        val_string = f_string.format(**scope)
        value = round(value, int(prec))
    
    
    # Check to see if number is a leading coefficient
    if fmt in ['Ca', 'C0']:
        if value == 1: return ''                        #  1 --> ''
        if value == -1: return '- '                     # -1 -->  -
        if value >= 0: return str(value)                #  x -->  x    
        if value < 0: return  ' - ' + str(abs(value))   # -x --> -x
    
    # Check to see if number is a leading coefficient
    if fmt in ['Cb', 'C1']:
        if value == 1: return '+ '                      #  1 -->  +
        if value == -1: return '- '                     # -1 -->  -
        if value >= 0: return '+ ' + str(value)         #  x --> +x    
        if value < 0: return  '- ' + str(abs(value))    # -x --> -x
        
    # Check to see if number is a leading coefficient
    if fmt in ['Cc', 'C2']:
        if value >= 0: return '+ ' + str(value)         #  x --> +x    
        if value < 0: return  '- ' + str(abs(value))    # -x --> -x
    
    
    return val_string


def blank_lines(n):
    if n <= 0: return ''
    if n == 1: return '<p>&nbsp;</p>' + '\n'
    return '<p>&nbsp;' + '<br />'*n + '</p>' + '\n'