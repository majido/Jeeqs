#Utils module
import types

#Compare strings. The string with longer length always wins otherwise the contents are compared
def str_cmp (a,b):
  for v in [a,b]:
    if not (type(v) is types.StringType or type(v) is types.UnicodeType):
      return -1 
  if len(a) != len(b):
    return len(a)-len(b)
  else:
    return cmp(a,b)
  #standard implementation
  #minl = min(len(a),len(b))
  #c = cmp(a[:minl],b[:minl])
  #return c if c != 0 else len(a) - len(b)

#Compare excercise numbers in format 1.2.3.XXX
def exercise_cmp(x,y):
  xs = x.split('.')
  ys = y.split('.')
  for a,b in zip(xs,ys):
    c = cmp(int(a), int(b)) if a.isdigit() and b.isdigit() else cmp(a,b)
    if c != 0: return c
  
  return len(xs)-len(ys)




