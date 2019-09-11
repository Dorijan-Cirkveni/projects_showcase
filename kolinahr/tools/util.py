def signum(a, b):
    '''
    Returns 1 if value of object a is greater than that of object b.
    Returns 0 if objects are equivalent in value.
    Returns -1 if value of object a is lesser than that of object b.
    '''
    return int(a > b) - int(a < b)

class Comparable:
    '''
    An abstract class that can be inherited to make a class comparable and sortable.
    For proper functionality, function diff must be overridden.
    '''
    def diff(self, other):
        """
        Calculates the difference in value between two objects and returns a number.
        If the returned number is
        - positive, the value of object a is greater than that of object b.
        - 0, objects are equivalent in value.
        - negative, value of object a is lesser than that of object b.
        Used in comparison operations.
        Override this function."""
        return 0

    def __eq__(self, other):
        return self.diff(other) == 0

    def __ne__(self, other):
        return self.diff(other) != 0

    def __lt__(self, other):
        return self.diff(other) < 0

    def __le__(self, other):
        return self.diff(other) <= 0

    def __gt__(self, other):
        return self.diff(other) > 0

    def __ge__(self, other):
        return self.diff(other) >= 0