# NO ADDITIONAL IMPORTS!
import doctest
from text_tokenize import tokenize_sentences


class Trie:
    def __init__(self, key_type):
        self.value = None
        self.children = dict()
        self.key_type = key_type


    def __setitem__(self, key, value):
        """
        Add a key with the given value to the trie, or reassign the associated
        value if it is already present in the trie.  Assume that key is an
        immutable ordered sequence.  Raise a TypeError if the given key is of
        the wrong type.
        """        
        key_type = type(key)
        
        if self.key_type != key_type:  # If the key type is not the same, return a Type Error.
            raise TypeError
        
        if len(key) == 0:  # When we are done with the key, set the value as told.
            self.value = value
            return
        
        if key[:1] in self.children:  # We index like this to take into account tuples; if the next letter is in the children already, continue along that branch.
            self.children[key[:1]][key[1:]] =  value
        else:
            new_trie = Trie(key_type)  # Create a new branch if the child does not exist and continue.
            self.children[key[:1]] = new_trie
            new_trie[key[1:]] = value
        
        
        
    def __getitem__(self, key):
        """
        Return the value for the specified prefix.  If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        >>> t = Trie(tuple)
        >>> t[2, ] = 'cat'
        >>> t[1, 0, 1, 80] = 'tomato'
        >>> t[2, ]
        'cat'
        >>> t[1, 0, 1, 80]
        'tomato'
        """
        key_type = type(key)
        
        if self.key_type != key_type:  # If the key type is not the same, return a Type Error.
            raise TypeError
            
        if len(key) == 0:
            if self.value == None:
                raise KeyError  # If we get to the end of the key, and the value is None, return a KeyError.
            return self.value
        else:
            next_trie = self.children[key[:1]]  # We go to the next trie, and recurse.
            return next_trie[key[1:]]
        
        

    def __delitem__(self, key):
        """
        Delete the given key from the trie if it exists. If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        >>> t = Trie(str)
        >>> t['bat'] = True
        >>> t['bar'] = True
        >>> t['bark'] = True
        >>> del t['bar']
        >>> t['bar']
        Traceback (most recent call last):
            ...
        KeyError
        """
        self[key]  # This checks to see if we will get a key or type error.
        self[key] =  None # We set the key's value to None, as if we were deleting it.

    def __contains__(self, key):
        """
        Is key a key in the trie? return True or False.
        >>> t = Trie(tuple)
        >>> t[2, ] = 'cat'
        >>> t[1, 0, 1, 80] = 'tomato'
        >>> (2, ) in t
        True
        >>> (1,) in t
        False
        """
        try:
            self[key]
        except KeyError:
            return False
        else:
            return True

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this trie and
        its children.  Must be a generator!
        """
        
        def recursive_step(trie, key):  # Make a recursive function that goes through the children for us.
            if trie.value:  # If the current node has a value, yield the current node and its value.
                yield (key, trie.value)
                
            for child in trie.children:  # Do the same for all the children.
                yield from recursive_step(trie.children[child], key + child)
                
        if self.key_type == tuple:  # Get the correct initial key for the very first node.
            key = ()
        else:
            key = ""
        return recursive_step(self, key)


def make_word_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    words in the text, and whose values are the number of times the associated
    word appears in the text
    >>> t = make_word_trie("Hello, my name is Isuf. I am from London and study at MIT in the USA")
    >>> t['hello']
    1
    >>> 'my' in t
    True
    """
    sentences = tokenize_sentences(text)
    word_freq = {}
    for i in range(len(sentences)):
        words_in_sentence = sentences[i].split(" ")
        for word in words_in_sentence:  # We get each word that hasn't been put in the dictionary and initialize it's value to 1. 
            if word not in word_freq:
                word_freq[word] = 1
            else:
                word_freq[word] += 1
                
    word_trie = Trie(str)  # We create a Trie that has a str type.
    for word in word_freq:
        word_trie[word] = word_freq[word]  # We set each word as a key with its frequency as its value.

    return word_trie

def make_phrase_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    sentences in the text (as tuples of individual words) and whose values are
    the number of times the associated sentence appears in the text.
    >>> t = make_phrase_trie("Hello. There is a cat in my house. I'm not sure why. There is a cat in my house.")
    >>> t[('hello',)]
    1
    >>> ('there', 'is', 'a', 'cat', 'in', 'my', 'house') in t
    True
    """
    sentences = tokenize_sentences(text)
    sentence_freq = {}
    for sentence in sentences:
        if sentence not in sentence_freq:
            sentence_freq[sentence] = 1
        else:
            sentence_freq[sentence] += 1
    sentence_trie = Trie(tuple)
    for sentence in sentence_freq:
        sentence_trie[tuple(sentence.split(" "))] = sentence_freq[sentence]  # We do a similar thing to above except we use sentences and use tuples.
        
    return sentence_trie

def autocomplete(trie, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is of an inappropriate type for the
    trie.
    >>> t = Trie(str)
    >>> t['read'] = 7
    >>> t['red'] = 3
    >>> t['reads'] = 9
    >>> t['hello'] = 2
    >>> t['help'] = 10
    >>> autocomplete(t, 're', 1)
    ['reads']
    >>> autocomplete(t, 're')
    ['reads', 'read', 'red']
    >>> autocomplete(t, 'e')
    []
    """
    if trie.key_type != type(prefix):  # If the types are not correct, raise a TypeError.
        raise TypeError
        
    pointer = 0
    next_trie = trie
    
    while pointer < len(prefix):  # We go along the prefix, and make sure that the children still exist.
        try:
            next_trie = next_trie.children[prefix[pointer:pointer + 1]]  # Indexing like this takes into account tuples and strings.
            pointer += 1
        except KeyError:  # If the prefix is not in the trie, return an empty list.
            return []

    sorted_list = sorted(next_trie, key = lambda p: p[1], reverse = True)  # We sort all the nodes and values by value is descending order.
    
    sorted_words = [prefix + rest for rest, freq in sorted_list]  # Create a list of the prefix plus the rest of the word based on the list above.
    
    if max_count == None:
        return sorted_words  # Return all the sorted words if max_count is None.
    else:
        return sorted_words[:max_count]  # If max_count is not none, return the sorted words up to the max count.
    

def letter_insert(word):
    """
    Return a list of all possible words when inserting each letter from the
    alphabet into each place in the word.
    """
    output = []
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    for letter in alphabet:
        for i in range(len(word)):
            new_word = word[:i] + letter + word[i:]
            if new_word not in output:
                output.append(new_word)
    return output

def letter_delete(word):
    """
    Return a list of possble words from a given word when deleting each letter
    from that word.
    """
    output = []
    for i in range(len(word)):
        output.append(word[:i] + word[i + 1:])
    return output

def replace_letter(word):
    """
    Return a list of all possible words when replacing a letter from that word
    with any letter from the alphabet.
    """
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    output = []
    for letter in alphabet:
        for i in range(len(word)):
            new_word = word[:i] + letter + word[i + 1:]
            if new_word not in output:
                output.append(new_word)
    return output

def letter_swap(word):
    """
    Return a list of words from a given word where every 2 adjacent letters
    are swapped.
    """
    word = list(word)
    
    output = []
    
    for i in range(len(word) - 1):
        mutated_word = ""
        output.append(mutated_word.join(word[:i] + [word[i + 1]] + [word[i]] + word[i + 2:]))
    return output
    
    
    
def autocorrect(trie, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    >>> t = Trie(str)
    >>> t['read'] = 7
    >>> t['red'] = 3
    >>> t['reads'] = 9
    >>> t['hello'] = 2
    >>> t['help'] = 10
    >>> autocorrect(t, 'rel')
    ['red']
    >>> autocorrect(t, 'red', 3)
    ['red', 'read']
    >>> autocorrect(t, 'he', 1)
    ['help']
    """
    if max_count is None or type(max_count) != int:  # If max count is None or not an integer, we do autocomplete with None, else we do autocomplete with the max_count.
        auto_corrected_words = autocomplete(trie, prefix, None)
    else:
        auto_corrected_words = autocomplete(trie, prefix, max_count)

    all_possible_edits = list(set(letter_insert(prefix) + letter_delete(prefix) + replace_letter(prefix) + letter_swap(prefix)))  # We get all the possible edits.

    valid_edits = []
    
    for edit in all_possible_edits:
        if edit in trie:
            valid_edits.append((edit, trie[edit]))  # Now we get just the edits in the trie.
    sorted_edits = sorted(valid_edits, key = lambda p: p[1], reverse = True)  # Sort the edits based on their frequency.
    
    words = auto_corrected_words
    
    i = 0
    
    while True:
        if max_count is not None:
            if len(words) == max_count:  # Once the number of words we have is equal to max_count, we can break.
                break
            
        edit = sorted_edits[i][0]  # We get each of the valid edits and check if it is words.
        
        if edit not in words:
            words.append(edit)
            
        if edit == sorted_edits[-1][0]:  # If we are on the last word, we can break.
            break
        
        i += 1
        
    return words
        
        
        
def word_filter(trie, pattern):
    """
    Return list of (word, freq) for all words in trie that match pattern.
    pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    >>> t = Trie(str)    
    >>> t['read'] = 7
    >>> t['red'] = 3
    >>> t['reads'] = 9
    >>> t['hello'] = 2
    >>> t['help'] = 10
    >>> word_filter(t, "r*d")
    [('red', 3), ('read', 7)]
    >>> word_filter(t, "??")
    []
    >>> word_filter(t, "he?*")
    [('hello', 2), ('help', 10)]
    """
    def word_filter_recursive(trie, pattern, key = ''):
        output = []
        if not pattern:  # If we are at the end of the pattern, we can return the key, value.
            if trie.value:
                return [(key, trie.value)]
            
        elif pattern[0] == "*":
            output.extend(word_filter_recursive(trie, pattern[1:], key))  # If we have a *, we add a sequence of size 0 and the sequences with the children.
            for child in trie.children:
                output.extend(word_filter_recursive(trie.children[child], pattern, key + child))
                
        elif pattern[0] == '?':  # If we have a ?, we just add the child and carry on.
            for child in trie.children:
                output.extend(word_filter_recursive(trie.children[child], pattern[1:], key + child))
                
        else:
            for child in trie.children:
                if child == pattern[0]:  # If we have a letter, we check that they match and move on with those.
                    output.extend(word_filter_recursive(trie.children[child], pattern[1:], key + child))
                    
        return output
    
    patterned_words = set(word_filter_recursive(trie, pattern))  # Create a set to remove duplicates.
    
    return list(patterned_words)  # Turn into list.

# you can include test cases of your own in the block below.
if __name__ == '__main__':
    doctest.testmod()
    
    # with open("alice.txt", encoding="utf-8") as f:
    #     alice = f.read()

    # alice_sentence = make_phrase_trie(alice)
    # # print(autocomplete(alice_sentence, (), 6))
    # alice_words = make_word_trie(alice)
    # # print(autocorrect(alice_words, 'hear', 12))
    # # print(len(autocomplete(alice_sentence, ())))
    # # print(s um(alice_sentence[i] for i in autocomplete(alice_sentence, ())))
    
    # with open("meta.txt", encoding="utf-8") as f:
    #     meta = f.read()
    
    # meta_words = make_word_trie(meta)
    # # print(autocomplete(meta_words, 'gre', 6))
    # # print(word_filter(meta_words, 'c*h'))
    
    # with open("tale.txt", encoding="utf-8") as f:
    #     tale = f.read()
    
    # tale_words = make_word_trie(tale)
    # # print(word_filter(tale_words, 'r?c*t'))
    
    # with open("pride.txt", encoding="utf-8") as f:
    #     pride = f.read()
    
    # pride_words = make_word_trie(pride)
    # # print(autocorrect(pride_words, 'hear'))
    
    # with open("dracula.txt", encoding="utf-8") as f:
    #     dracula = f.read()
        
    # dracula_words = make_word_trie(dracula)
    # # print(len(autocomplete(dracula_words, "")))
    # # print(sum(dracula_words[i] for i in autocomplete(dracula_words, "")))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    