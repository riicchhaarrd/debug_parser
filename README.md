# debug_parser
# Usage
### 1. Gather strings from the executable.
`strings binary.exe > strings.txt`

### 2. Parse and convert them back to structs, unions and enums.
`python3 parse.py strings.txt types.h`
