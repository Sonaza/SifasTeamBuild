from IdolDatabase.KiraraClient import KiraraIdol

class CardNonExtant(): pass
class CardMissing(): pass

def is_valid_card(value):     return isinstance(value, KiraraIdol)
def is_missing_card(value):   return isinstance(value, CardMissing)
def is_nonextant_card(value): return value == None or isinstance(value, CardNonExtant)
