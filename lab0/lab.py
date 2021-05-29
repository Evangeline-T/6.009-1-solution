# No Imports Allowed!


def backwards(sound):
    new_sound = {'rate': 0, 'left': 0, 'right': 0}  #Create new sound
    new_sound['rate'] = sound['rate']               #Copy the rate from original sound
    new_left = sound['left'][:]                     #Create a copy of the value lists
    new_left.reverse()                              #Reverse the list
    new_right = sound['right'][:]                   #Repeat
    new_right.reverse()                             #Repeat
    new_sound['left'] = new_left                    #Assign the reversed sound the reversed samples
    new_sound['right'] = new_right
    return new_sound                                #Return new sound
      
        
def mix(sound1, sound2, p):
    if sound1['rate'] != sound2['rate']:            #Check if the rates are the same
        return None
    new_mix = {'rate': 0, 'left': 0, 'right': 0}    #Create the mixed sound
    new_mix['rate'] = sound1['rate']                #Create copies of all the samples I will need
    new_sound1_right = sound1['right'][:]
    new_sound1_left = sound1['left'][:]
    new_sound2_right = sound2['right'][:]
    new_sound2_left = sound2['left'][:]
    
    if len(new_sound1_right) < len(new_sound2_right):#Reduce the size of the samples so that the sounds are the appropriate length in time
        new_sound2_right = new_sound2_right[:len(new_sound1_right)]
        
    elif len(new_sound2_right) < len(new_sound1_right):
        new_sound1_right = new_sound1_right[:len(new_sound2_right)]
        
    if len(new_sound1_left) < len(new_sound2_left):
        new_sound2_left = new_sound2_left[:len(new_sound1_left)]
        
    elif len(new_sound2_left) < len(new_sound1_left):
        new_sound1_left = new_sound1_left[:len(new_sound2_left)]
    
    new_sound1_rightp = [i*p for i in new_sound1_right]#Multiply the samples with the corresponding scale in the list
    new_sound1_leftp = [i*p for i in new_sound1_left]
    new_sound2_rightp = [i*(1-p) for i in new_sound2_right]
    new_sound2_leftp = [i*(1-p) for i in new_sound2_left]
    
    mix_right = []                                      #Add the changed samples to a list for right or left, while adding the rights and lefts together
    for i in range(0, len(new_sound1_rightp)): 
        mix_right.append(new_sound1_rightp[i] + new_sound2_rightp[i])
        
    mix_left = [] 
    for i in range(0, len(new_sound1_leftp)): 
        mix_left.append(new_sound1_leftp[i] + new_sound2_leftp[i]) 
        
    new_mix['left'] = mix_left                          #Put the new left and right in the mixed sound
    new_mix['right'] = mix_right
    
    return new_mix                                      #Return the sound
    


def echo(sound, num_echos, delay, scale):
    echo_sound = {'rate': sound['rate'], 'left': [], 'right': [] }      #Create new sound
    sample_delay = round(delay * sound['rate'])                         #Create the appropriate sample delay
    left = sound['left'][:]                                             #Make copies of the left and right samples twice
    right = sound['right'][:]
    echo_left = left[:]
    echo_right = right[:]
    start_position = 0                                                  #A counter to place the delay
    for i in range(num_echos):
        new_scale = scale**(i+1)                                        #The appropriate scale for the iteration
        start_position += sample_delay                                  #The appropriate start position 
        if start_position > len(left)-1:                                #If the delay is longer than the sound, place 0s after the sample is over
            num_zeros = start_position - len(left)
            for zeros in range(num_zeros):
                left.append(0)
        
        for num, j in zip(echo_left, range(start_position, start_position + len(left))): #Iterate through the sample and scaled sample and add at the appropriate positions
            new_num = num*new_scale
            if j > len(left) - 1:
                left.append(new_num)
            else:
                left[j] += new_num
                
    start_position = 0                                                  #Repeat
    for i in range(num_echos):
        new_scale = scale**(i+1)
        start_position += sample_delay
        if start_position > len(right)-1:
            num_zeros = start_position - len(right)
            for zeros in range(num_zeros):
                right.append(0)
        
        for num, j in zip(echo_right, range(start_position, start_position + len(right))):
            new_num = num*new_scale
            if j > len(right) - 1:
                right.append(new_num)
            else:
                right[j] += new_num
                
    echo_sound['left'] = left
    echo_sound['right'] = right
    
    return echo_sound
    

def pan(sound):
    pan_sound = {'rate': sound['rate'], 'left': [], 'right':[]}          #Create empty sound
    N = len(sound['right'])                                              #Find N
    right_sound_modified = sound['right'][:]                             #Create copies of the right and left samples
    left_sound_modified = sound['left'][:]
    for i in range(0, N):
        right_sound_modified[i] = right_sound_modified[i] * i/(N-1)      #Modify the samples appropriately
        left_sound_modified[i] = left_sound_modified[i] * (1 - i/(N-1))
    pan_sound['right'] = right_sound_modified                            #Input the modified samples into the new sound
    pan_sound['left'] = left_sound_modified
    return pan_sound

def remove_vocals(sound):
    no_vocals = {'rate': sound['rate'], 'left': [], 'right': []}         #Create new empty sound
    left = sound['left'][:]                                              #Create copies of left and right
    right = sound['right'][:]
    left_right = []
    for i in range(len(left)):
        left_right.append(left[i] - right[i])                            #Create the modified sample by subtracting
    no_vocals['left'] = left_right                                       #Input the new sound into the empty sounds left and right
    no_vocals['right'] = left_right
    return no_vocals

# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds

import io
import wave
import struct

def load_wav(filename):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, 'r')
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    left = []
    right = []
    for i in range(count):
        frame = f.readframes(1)
        if chan == 2:
            left.append(struct.unpack('<h', frame[:2])[0])
            right.append(struct.unpack('<h', frame[2:])[0])
        else:
            datum = struct.unpack('<h', frame)[0]
            left.append(datum)
            right.append(datum)

    left = [i/(2**15) for i in left]
    right = [i/(2**15) for i in right]

    return {'rate': sr, 'left': left, 'right': right}


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, 'w')
    outfile.setparams((2, 2, sound['rate'], 0, 'NONE', 'not compressed'))

    out = []
    for l, r in zip(sound['left'], sound['right']):
        l = int(max(-1, min(1, l)) * (2**15-1))
        r = int(max(-1, min(1, r)) * (2**15-1))
        out.append(l)
        out.append(r)

    outfile.writeframes(b''.join(struct.pack('<h', frame) for frame in out))
    outfile.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)
    hello = load_wav('sounds/hello.wav')
    
    mystery = load_wav('sounds/mystery.wav')
    write_wav(backwards(mystery), 'mystery_reversed.wav')
    
    synth = load_wav('sounds/synth.wav')
    water = load_wav('sounds/water.wav')
    
    write_wav(mix(synth, water, 0.2), 'synth_water_mix.wav')
    
    chord = load_wav('sounds/chord.wav')
    write_wav(echo(chord, 5, 0.3, 0.6), 'chord.wav')
    
    car = load_wav('sounds/car.wav')
    write_wav(pan(car), 'car.wav')
    
    coffee = load_wav('sounds/coffee.wav')
    write_wav(remove_vocals(coffee), 'coffee.wav')
    
    # write_wav(backwards(hello), 'hello_reversed.wav')
    