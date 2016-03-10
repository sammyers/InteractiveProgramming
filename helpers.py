def vector_add(*args):
	i = sum([arg[0] for arg in args])
	j = sum([arg[1] for arg in args])
	k = sum([arg[2] for arg in args])
	return (i, j, k)

def vector_multiply(scalar, vector):
	return tuple([scalar * component for component in vector])
