#Utils module
import types

#Compare excercise numbers in format 1.2.3.XXX
def exercise_cmp(x,y):
  for v in [x,y]:
    if not (type(v) is types.StringType or type(v) is types.UnicodeType):
      return -1 
 
  xs = x.split('.')
  ys = y.split('.')
  for a,b in zip(xs,ys):
    c = cmp(int(a), int(b)) if a.isdigit() and b.isdigit() else cmp(a,b)
    if c != 0: return c
  
  return len(xs)-len(ys)




