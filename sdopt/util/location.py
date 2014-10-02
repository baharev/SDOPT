import inspect

def location():
    callerframerecord = inspect.stack()[1]  # 0 this line, 1 caller
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    return 'File \"%s\", line %d, in %s' % (info.filename, info.lineno, info.function)
