def searchvow(word:str) ->set:
    """ выводит гланые"""
    vowels = set('aeiou')
    found = vowels.intersection(set(word))
    return found

def searchlet(word:str,letters:str = 'aeuoi') ->set:
    return set(letters).intersection(set(word))

    


        
        
