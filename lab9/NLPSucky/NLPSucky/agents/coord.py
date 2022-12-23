from ast import literal_eval

def to_coord(word):
    try:
        t = literal_eval(word)
        if type(t) == tuple:
            return t
        return None
    except:
        return None
    
def is_coord(word):
    return to_coord(word) != None
