
def list2str(a_list):
    ''' convert a list into a comma separated string '''
    c_list = [str(i) for i in a_list]   # convert list items into string
    a_str = ",".join(c_list)  # list to string via "join"
    return a_str


def str2list(a_str):
    ''' convert a comma separated string into a list '''
    # uses list comprehension to differentiate int and str
    a_list = [int(e) if e.isdigit() else e for e in a_str.split(',')]
    return a_list


def split_string(a_str, chunk_cnt=1, chunk_len=48):
    ''' Split a string into fixed length chunks of string 
    using list comprehension '''
    smax_len = chunk_len * chunk_cnt    # set max size of a string
    a_str = "{0:<{1}.{1}}".format(a_str, smax_len)  # pad or truncate string
    # split string into chunks
    chunks = [a_str[i:i+chunk_len] for i in range(0, len(a_str), chunk_len)]
    return chunks


# SAMPLE USAGE
if __name__ == "__main__":
    a_list = [
        99,         # site ID
        99,         # entry zone ID
        99,         # vehicle type ID
        "2021-04-16 04:13:00",     # vehicle time-in
        "1234-5678901234"  # plate no.
    ]
    print("Original list:", a_list, len(a_list))
    # conversion
    c_str = list2str(a_list)
    print("List to str  :", c_str, len(c_str))
    c_list = str2list(c_str)
    print("String to lst:", c_list, len(c_list))

    mblock = split_string(c_str, 3, 16)
    mb_len = len(mblock)
    print("Split string into chunks...")
    for i in range(mb_len):
        print(f"  chunk[{i}] => {mblock[i]} with lengt={len(mblock[i])}")
