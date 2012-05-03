"""
Helps with running test cases over a challenge's solution

"""

import traceback
import new
import sys
import StringIO
import os
import string

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

from models import *
import lib.markdown as markdown

def compile_and_run(program, output):
    """
    Compiles and runs the given program and returns an output dict containing the result of compilation and execution under key 'result'
    Also a program module containing the compiled program is returned when compilation and execution is successful
    """

    # the python compiler doesn't like network line endings
    program = program.replace('\r\n', '\n')

    # add a couple newlines at the end of the program. this makes
    # single-line expressions such as 'class Foo: pass' evaluate happily.
    program += '\n\n'

    # log and compile the program up front
    try:
        compiled = compile(program, '<sudmitted>', 'exec')
    except:
        output['result'] += 'Compile error:  \n' + format_exc() 
        raise
    # create a dedicated module to be used as this program's __main__
    program_module = new.module('__main__')
    #TODO(majid) Does this properly sandbox the builtins. I can call print!
    program_module.__builtins__ = {}
    #print program_module.__dict__ 
    
    # swap in our custom module for __main__. run the program, swap the custom module out.
    old_main = sys.modules.get('__main__')
    try:
        sys.modules['__main__'] = program_module
        program_module.__name__ = '__main__'

        # run!
        try:
            stdout_buffer = StringIO.StringIO()
            stderr_buffer = StringIO.StringIO()
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            try:
                sys.stdout = stdout_buffer
                sys.stderr = stderr_buffer
                exec compiled in program_module.__dict__
                
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                
                # Write the buffer to response
                output['result'] += stdout_buffer.getvalue()
                output['result'] += stderr_buffer.getvalue()

        except:
            output['result'] += 'Execution error: \n' + format_exc()
            raise

        return program_module

    finally:
        sys.modules['__main__'] = old_main

def format_exc():
  etype, value, tb = sys.exc_info()
  t = ''.join(traceback.format_exception(etype, value, tb)[2:]) #ignore the first frame which is this frame!
  return t #.replace('\n', '  \n').replace(' ', '&nbsp;')



def run_testcases(program, challenge, attempt, robot):
    """
    Runs the challenge's test cases over the given program (persisted as attempt) and persists the results as a feedback
    # TODO remove robot parameter
    """
    output = {'result' : ''}
    success = True

    vote='correct'

    try:
        program_module = compile_and_run(program, output)
    except:
        success = False
        vote = 'incorrect'

    if success:
        test_num = 0
        for test in challenge.testcases:
            test_num = test_num + 1
            result = eval(test.statement, program_module.__dict__)
            if not str(result) == test.expected:
                success = False
                output['result'] += " Failed with the statement:  \n *****  \n" \
                                    + test.statement \
                                    + '  \n Expected result:  \n' \
                                    + test.expected \
                                    + '  \n Actual result:  \n' \
                                    + str(result) \
                                    + '   \n'

        if test_num == 0:
            output['result'] += 'No test cases to run!'
        elif success:
            output['result'] += 'Success! All tests ran successfully!'
        else:
            vote = 'incorrect'

    feedback = Feedback(
            parent=attempt,
            attempt=attempt,
            author=robot,
            attempt_author=attempt.author,
            markdown=output['result'],
            content=markdown.markdown(output['result'], ['codehilite', 'mathjax']),
            vote=vote)
    return feedback

