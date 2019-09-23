def argTest(types, args):
    correct = True
    for a in range(len(types)):
        if not isinstance(args[a], types[a]):
            correct = False
    if correct:
        return True
    else:
        return False
