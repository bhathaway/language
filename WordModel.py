from collections import defaultdict
import re

phonemes = set(['aa', 'ae', 'ah', 'ao', 'aw', 'ay', 'b', 'ch', 'd', 'dh', 'eh',
  'er', 'ey', 'f', 'g', 'hh', 'ih', 'iy', 'jh', 'k', 'l', 'm', 'n', 'ng', 'ow',
  'oy', 'p', 'r', 's', 'sh', 't', 'th', 'uh', 'uw', 'v', 'w', 'y', 'z', 'zh' ])

# These are consonants that could be followed by another to represent a
# different phoneme. This set is used in the parser below
ambiguous_prefixes = set(['d', 'n', 's', 't', 'z'])

vowels = set(['aa', 'ae', 'ah', 'ao', 'aw', 'ay', 'eh', 'er', 'ey', 'ih',
  'iy', 'ow', 'oy', 'uh', 'uw' ])


# Ouch. Turns out I might not even need this silly thing.
class Phoneme:
    def __init__(self, s):
        self.representation = str()
        self.emphasis = 0
        for c in s:
            if c.isalpha():
                self.representation += c
            elif c.isdigit():
                if c != '0' and c != '1' and c != '2':
                    raise ValueError('Invalid emphasis')
                else:
                    self.emphasis = int(c)
                    break

        self.representation = self.representation.lower()
                    
        if self.representation in phonemes:
            if self.representation in vowels:
                self.is_vowel = True
            else:
                self.is_vowel = False
        else:
            raise ValueError('%s is not a recognized phoneme' % s)

    def __repr__(self):
        result = None
        if self.emphasis == 0:
            result = self.representation.lower()
        elif self.emphasis == 1:
            result = self.representation.lower() + '\'\''
        else:
            result = self.representation.lower() + '\''
        return result

    def isVowel(self):
        return self.is_vowel

    def isConsonant(self):
        return not self.is_vowel

    def emphasis(self):
        return self.emphasis


def createDictionary(file):
    result = defaultdict(list)
    f = open(file)

    for line in f:
        tokens = line.rstrip('\n').split(' ')
        key = tokens[0]
        if not key[0].isalpha():
            continue
        key = key.lower().split('(')[0]
        # The space at the end is to assist in matching
        value = str.join(' ', tokens[1:]).lower().lstrip(' ') + ' '
        result[key].append(value)

    return result

# To make this function more friendly to the specific task of matching
# pronunciations, I'll add some special substitions. :v is vowel, :c is
# consonant. How do I deal with the whole emphasis thing? Let's keep it simple.
# (:v0 :v1 :v2) Look for these first, since they overlap with :v. The
# parentheses should allow these to be used in combination with other regular
# expression elements.
# :v (any vowel) = ([aeiou].[012])
# :v0            = ([aeiou].0)
# :v1            = ([aeiou].1)
# :v2            = ([aeiou].2)
# :c             = ([^ aeiou]+)
# Here's another idea. To avoid all the spacing, prefer no spacing and do a 
# greedy parsing of the phonemes. In case greedy would be bad, use ' in the
# string to stop the greedy algorthim. It should only rarely be needed. One
# slight problem is that the [] will probably not be useful anymore. Oh, well.
# It's a small price to pay. Here's another addition, allow spacing, too, for
# the copy paste happy person. The best way to do this is to "absorb" all
# consecutive spaces into one space. In fact, that can be done at the very
# end
def getMatches(dictionary, expression):
    # First business. Space out the phonemes.
    result = ''
    parsing_special = False
    previous_char = ''
    previous_vowel = ''
    for c in expression:
        if previous_vowel != '':
            if c == '0' or c == '1' or c == '2':
                result += previous_vowel + c + ' '
                previous_vowel = ''
                continue
            else:
                result += previous_vowel + '[012] '
                previous_vowel = ''

        if previous_char != '':
            if c.isalpha() and previous_char + c in vowels:
                previous_vowel = previous_char + c
                previous_char = ''
                continue
            if c.isalpha() and previous_char + c in phonemes:
                result += previous_char + c + ' '
                previous_char = ''
                continue
            else:
                result += previous_char + ' '
                previous_char = ''

        if parsing_special:
            result += c
            parsing_special = False
        elif c == ':':
            result += c
            parsing_special = True
        elif c == ';':
            # This allows one to use the raw representation of phonemes.
            # In other words, this tells the parser to assume the characters
            # aren't phonemes
            parsing_special = True
        elif c in ambiguous_prefixes:
            # Guaranteed previous_char is empty here.
            # Wait for next character to decide
            previous_char = c
        elif c in phonemes:
            result += c + ' '
        elif c.isalpha():
            previous_char = c
        elif c != '\'':
            result += c

    if previous_vowel != '':
        result += previous_vowel + '[012] '
    elif previous_char != '':
        result += previous_char + ' '

    expression = result
    expression = expression.replace(':v0', '([aeiou].0 )')
    expression = expression.replace(':v1', '([aeiou].1 )')
    expression = expression.replace(':v2', '([aeiou].2 )')
    expression = expression.replace(':v', '([aeiou].[012] )')
    expression = expression.replace(':c', '([^ aeiou]+ )')
    # Implicitly match the whole string
    expression += '$'
    expression = re.sub(r'\s+', ' ', expression)
    print ('Final expression: %s' % expression)
    result = []
    expr = re.compile(expression)
    for k in dictionary:
        v = dictionary[k]
        for i in v:
            if expr.match(i):
                result.append(k)
                break
    return result

