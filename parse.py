import re
import sys

path = None
if len(sys.argv) < 2:
    print(f'Usage: {sys.argv[0]} <strings_file>')
    exit()
path = sys.argv[1]

def bits_to_type(bits):
    types = {8: 'uint8_t', 16: 'uint16_t', 32: 'uint32_t', 64: 'uint64_t'}
    if bits not in types:
        return None
    return types[bits]

def parse_struct(struct_name, struct_type, data):
    members = data.split(';')
    if struct_type == 's':
        print(f'struct {struct_name}\n{{')
    else:
        print(f'union {struct_name}\n{{')
    bit_offset = 0
    padding_count = 0
    for m in members:
        if len(m) <= 1:
            continue
        s = re.findall(r'(\w+):\(\d+,\d+\)(?:=x.(\w+):)?,(\d+),(\d+)', m)
        if len(s) == 0:
            continue
        s = s[0]
        name = s[0]
        type_name = s[1]
        offset = int(s[2])
        bits = int(s[3])
        #name, offset, bits = s[0]

        if bit_offset != offset:
            # add padding
            if (offset - bit_offset) % 8 != 0:
                raise Exception('not divisible by 8')
            padding = (offset - bit_offset) // 8
            print(f'\tchar pad{padding_count}[{padding}];')
            padding_count += 1
            # update bit_offset
            bit_offset = offset

        if len(type_name) == 0:
            if bits % 8 != 0:
                raise Exception('not divisible by 8')
            type = bits_to_type(bits)
            bytes = bits // 8
            if type == None:
                print(f'\tchar {name}[{bytes}];')
            else:
                print(f'\t{type} {name};')
        else:
            print(f'\t{type_name} {name};')
        if struct_type == 's':
            bit_offset += bits
        #print(name, offset, bits)
    print('};\n')

def parse_enum(enum_name, data):
    values = data.split(',')
    n = 0
    print('typedef enum\n{')
    for v in values:
        pair = v.split(':')
        if len(pair) != 2:
            continue
        key = pair[0]
        value = int(pair[1])
        if len(values) - 1 == n + 1:
            print(f'\t{key} = {value}')
        else:
            print(f'\t{key} = {value},')
        n += 1
    print(f'}} {enum_name};\n')
    
print('#include <stdint.h>\n')

type_names = {}
with open(path, 'r') as f:
    lines = f.readlines()
    for line in lines:
        try:    
            query = r'(\w+):t\(\d+,\d+\)=([use])(?:\d+)?'
            s = re.findall(query, line)
            if len(s) == 0:
                continue
            type_name = s[0][0]

            if len(type_name) == 0:
                continue

            if type_name in type_names:
                continue
            
            type = s[0][1]
            pos = re.search(query, line).end()
            data = line[pos:]
            if type == 's' or type == 'u':
                parse_struct(type_name, type, data)
            elif type == 'e':
                parse_enum(type_name, data)
            else:
                raise Exception('expected struct, union or enum')
            type_names[type_name] = True
        except:
            pass
