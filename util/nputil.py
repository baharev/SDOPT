
# TODO Do we need this function at all? str would give [1 2] 
# which is probably even nicer
def pretty_str_numpy_array(arr):
    #  array([1, 2], dtype=int32)) -> '1, 2'
    str_arr = str(arr)
    beg = str_arr.find('[')+1
    end = str_arr.rfind(']')
    return str_arr[beg:end]