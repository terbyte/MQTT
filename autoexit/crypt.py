from datetime import datetime, timedelta
from .lst_str_convert import *


def cipher_decipher(key, input_string):
    ''' XOR Cipher Algorithm '''
    key_lenght = len(key)
    converted_string = ""
    for i in range(0, len(input_string)):
        j = i % key_lenght
        xor = ord(input_string[i]) ^ ord(key[j])
        converted_string = converted_string + chr(xor)
    return converted_string


# SAMPLE USAGE
if __name__ == "__main__":
    # cipher/encryption key; provide a fairly secure password/key here
    key = "superSecure"     # make this unique per site

    # message list
    timenow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # timein = (timenow - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S")
    # timeout = timenow.strftime("%Y-%m-%d %H:%M:%S")
    ''' data or list composition
    siteid      :   999                 :    3  : int
    entryid     :   99                  :    2  : int
    vehicleid   :   99                  :    2  : int
    Time-in     :   YYYY-MM-DD hh:mm:ss :   19  : string
    plateno     :   XXXXXXXXXXXXX       :   16  : string
      total no. of data chars           =   42 chars 
      + separators (comma)              =    4 
      OVERALL TOTAL no. of chars        =   46  '''
    a_list = [
        999,         # site ID
        99,         # entry zone ID
        999,         # vehicle type ID
        timenow,     # vehicle time-in
        "1234-67890123456"  # plate no.
    ]
    print("original list    =>", a_list, len(a_list), type(a_list))

    # convert list to string using ISA custom lib 'lst_str_convert.py'
    c_str = list2str(a_list)
    print("List to string   =>", c_str, len(c_str), type(c_str))

    # encrypt the original string
    enc_str = cipher_decipher(key, c_str)
    print("Encrypted string =>", enc_str, len(enc_str), type(enc_str))

    # split enc_str into 3-chunks of length-16
    enc_chunk = split_string(enc_str, 3, 16)
    print("\nSplit encrypted string into chunks...")
    for i in range(len(enc_chunk)):
        print(
            f"  enc_chunk[{i}]   => {enc_chunk[i]} with lengt={len(enc_chunk[i])}")

    # re-assemble enc_chunk back into a single string (enc_assembled_str)
    enc_assembled_str = ""
    for i in range(len(enc_chunk)):
        enc_assembled_str += enc_chunk[i]
    enc_assembled_str = enc_assembled_str.rstrip()  # remove trailing spaces
    print("Re-assembled str =>", enc_assembled_str, len(enc_assembled_str))

    # the encrypted message can be decrypted
    # by using the same 'key' on the encMessage
    dec_str = str(cipher_decipher(key, enc_assembled_str))
    # dec_str = str(cipher_decipher(key, enc_str))
    print("\nDecrypted string =>", dec_str, len(dec_str), type(dec_str))

    # convert back string to list using ISA custom lib 'lst_str_convert.py'
    a_newlist = str2list(dec_str)
    print("String to list   =>", a_newlist, len(a_newlist), type(a_newlist))
