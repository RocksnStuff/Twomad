import atexit

def all_done():
    print ('all_done()')

atexit.register(all_done)