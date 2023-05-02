#pattern = r'\w+:t\(\d+,\d+\)=s(?P<size>\d+)'
#pattern = r'\w+:t\(\d+,\d+\)=s(\d+)(\w+)'
import re

def bits_to_type(bits):
    types = {8: 'uint8_t', 16: 'uint16_t', 32: 'uint32_t', 64: 'uint64_t'}
    if bits not in types:
        return None
    return types[bits]

def parse_line(line):
    struct_name = line.split(':')[0]
    s = re.search(r'=s\d+', line)
    if not s:
        return
    after = line[s.end():]
    members = after.split(';')
    print(f'struct {struct_name}\n{{')
    bit_offset = 0
    padding_count = 0
    for m in members:
        if len(m) <= 1:
            continue
        s = re.findall(r'(\w+):\(\d+,\d+\),(\d+),(\d+)', m)
        if len(s) == 0:
            continue
        s = s[0]
        name = s[0]
        offset = int(s[1])
        bits = int(s[2])
        #name, offset, bits = s[0]
        if bits % 8 != 0:
            raise Exception('not divisible by 8')
        type = bits_to_type(bits)
        bytes = bits // 8
        if bit_offset != offset:
            # add padding
            if (offset - bit_offset) % 8 != 0:
                raise Exception('not divisible by 8')
            padding = (offset - bit_offset) // 8
            print(f'\tchar pad{padding_count}[{padding}];')
            padding_count += 1
            # update bit_offset
            bit_offset = offset
        if type == None:
            print(f'\tchar {name}[{bytes}];')
        else:
            print(f'\t{type} {name};')
        bit_offset += bits
        #print(name, offset, bits)
    print('};\n')
    
print('#include <stdint.h>\n')

with open("types.h", 'r') as f:
    lines = f.readlines()
    for line in lines:
        try:
            parse_line(line)
        except:
            pass
