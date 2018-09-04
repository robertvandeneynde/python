#!/usr/bin/env python3
import os
import stat

def is_user_writable(filename):
  return bool(os.stat(filename).st_mode & stat.S_IWUSR)

class OutFile:
    """
    with OutFile("compiled.txt") as f: f.write('stuff')
    # compiled.txt is read only, you can repeat this process
    
    print_created can be set to True to print the name of the file create 
    or be set to 'green' to print the filename in color.
    """
    def __init__(self, filename, supargs='', *, print_created=False):
        self.filename = filename
        self.supargs = supargs
        self.print_created = print_created
    
    def unlock(self):
        if os.path.isfile(self.filename):
            if is_user_writable(self.filename):
                raise ValueError('{} exists and is writable'.format(self.filename))
            os.chmod(self.filename, 0o644)
    
    def lock(self):
        os.chmod(self.filename, 0o444)
    
    def __enter__(self):
        self.unlock()
        self.f = open(self.filename, ''.join({'w'} | set(self.supargs)))
        self.f.__enter__()
        return self.f
    
    def __exit__(self, type, value, traceback):
        self.lock()
        self.f.__exit__(type, value, traceback)
        if self.print_created == True:
            print("Created '" + self.filename + "'")
        elif self.print_created == 'green':
            print('\033[32m' + "Created '" + self.filename + "'" + '\033[0m')

def OutFilePrint(filename, supargs=''):
    return OutFile(filename, supargs, print_created=True)

def OutFileGreen(filename, supargs=''):
    return OutFile(filename, supargs, print_created='green')
