#Utils module
import types

''' HTTP Status codes to help readability 
    http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
'''
class StatusCode: 
  bad = 400
  unauth = 401
  forbidden = 403
  not_found = 404
  
  internal_error = 500


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




