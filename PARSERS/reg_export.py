import mmap

class RegExport:
    def __init__(self):
        self.name = 'RegExport'
        self.parsable_files_l = ['HKLM.txt', 'HKU.txt', 'HKCU.txt', 'HKCC.txt', 'HKCR.txt']
        self.encoding = 'utf-16-le'
        self.new_line = b'\r\x00\n\x00'

    def parse(self, file, regkeys_l):
        formatted_regkeys_keys_d, formatted_regkeys_bytes_d, formatted_regkeys_og_regkeys_d = self.__prepare_dicts_for_parsing(regkeys_l)
        found_values_d = {}
        found_proofs_d = {}
        with open(file, "r", encoding=self.encoding, errors='ignore') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                line_start = 0
                
                while line_start < len(mm):
                    line_end = self.__find_end_of_line(mm, line_start)
                    
                    # Extract line bytes
                    line_bytes = mm[line_start:line_end].lower()
                    
                    # Check if any regkey is in this line
                    for regkey_f in formatted_regkeys_bytes_d.keys():
                        regkeys_to_delete_l = []
                        regkey_b = formatted_regkeys_bytes_d[regkey_f]

                        if regkey_b in line_bytes:
                            # Decode line only when we find a match
                            line_content = line_bytes.decode(self.encoding, errors='ignore')
                            subkey = formatted_regkeys_bytes_d[regkey_f].decode(self.encoding, errors='ignore')
                            # Check if exact subkey in line
                            if f'{subkey}]' in line_content:
                                key = formatted_regkeys_keys_d[regkey_f]
                                value = self.__extract_value(key, mm, line_start, line_end)
                                # If value is found
                                if value is not None:
                                    regkey_og = formatted_regkeys_og_regkeys_d[regkey_f] # Original key
                                    found_values_d[regkey_og] = value
                                    found_proofs_d[regkey_og] = file
                                    regkeys_to_delete_l.append(regkey_f)
                    
                    # Remove found regkey value
                    for found_regkey in regkeys_to_delete_l:
                        del formatted_regkeys_keys_d[found_regkey]
                        del formatted_regkeys_bytes_d[found_regkey]
                        del formatted_regkeys_og_regkeys_d[found_regkey]

                    if not formatted_regkeys_bytes_d:
                        break
                    else:
                        line_start = self.__move_to_next_line(mm, line_end)
        return found_values_d, found_proofs_d
    
    def __find_end_of_line(self, mm, line_start):
        # Find end of current line
        line_end = mm.find(self.new_line, line_start)
        if line_end == -1:
            line_end = len(mm)  # Last line without newline
        return line_end
    
    def __move_to_next_line(self, mm, line_end):
        # Move to next line
        if line_end == len(mm):
            return len(mm) # Break while loop
        line_start = line_end + len(self.new_line)
        return line_start
    
    def __prepare_dicts_for_parsing(self, regkeys_l):
        formatted_regkeys_keys_d = {}
        formatted_regkeys_bytes_d = {}
        formatted_regkeys_og_regkeys_d = {}
        
        for regkey in regkeys_l:
            formatted_regkey = self.__format_regkey(regkey)
            formatted_regkeys_keys_d[formatted_regkey] = formatted_regkey.split(':')[-1].lower()
            formatted_regkeys_bytes_d[formatted_regkey] = formatted_regkey.split(':')[0].encode(self.encoding).lower()
            formatted_regkeys_og_regkeys_d[formatted_regkey] = regkey
        return formatted_regkeys_keys_d, formatted_regkeys_bytes_d, formatted_regkeys_og_regkeys_d
    
    def __format_regkey(self, regkey):
        if 'HKLM' in regkey:
            regkey = regkey.replace('HKLM', 'HKEY_LOCAL_MACHINE')
        elif 'HKU' in regkey:
            regkey = regkey.replace('HKU', 'HKEY_USERS').split('\\', 2)[-1]
        elif 'HKCU' in regkey:
            regkey = regkey.replace('HKCU', 'HKEY_CURRENT_USER')
        elif 'HKCC' in regkey:
            regkey = regkey.replace('HKCC', 'HKEY_CURRENT_CONFIG')
        elif 'HKCR' in regkey:
            regkey = regkey.replace('HKCR', 'HKEY_CLASSES_ROOT')

        return regkey
    
    def __extract_value(self, key, mm, line_start, line_end):
        while line_start < len(mm):
            # Start on new line
            line_start = line_end + len(self.new_line)
            
            line_end = self.__find_end_of_line(mm, line_start)
            # Extract line bytes
            line_bytes = mm[line_start:line_end].lower()
            line_content = line_bytes.decode(self.encoding, errors='ignore')
            if line_content:
                if key in line_content:
                    # Check if multiline value
                    if line_content.endswith(('\\')):
                        raw_value = line_content.split('=')[-1][:-1] # Remove trailing \
                        line_start = line_end + len(self.new_line)
                        raw_value += self.__extract_multiline_value(mm, line_start)
                        value = self.__convert_value(raw_value)
                        return value
                    else:
                        raw_value = line_content.split('=')[-1]
                        value = self.__convert_value(raw_value)
                        return value
                else:
                    line_start = self.__move_to_next_line(mm, line_end)
            else: # End of keys block
                break
        return None # Didn't find any value
    
    def __extract_multiline_value(self, mm, line_start):
        value = ""
        while line_start < len(mm):
            line_end = self.__find_end_of_line(mm, line_start)
            # Extract line bytes
            line_bytes = mm[line_start:line_end].lower()
            line_content = line_bytes.decode(self.encoding, errors='ignore').strip()
            # Detect new key
            if not line_content.startswith(('"')):
                # Detect end of value with \ char
                if line_content[-1] == '\\':
                    value += line_content[:-1]
                    line_start = self.__move_to_next_line(mm, line_end)
                else:
                    value += line_content
                    return value
    
    def __convert_value(self, raw_value):
        # Get value type
        if raw_value.startswith(('"')):
            reg_type = "string"
        else:
            reg_type = raw_value.split(':', 1)[0]
        
        value = raw_value.split(':', 1)[-1]
        
        # Convert value
        if reg_type == "string":
            return raw_value[1:-1] # Remove quotes
        elif reg_type == "dword": # 32-bit unsigned int
            return int(value, 16)
        elif reg_type == "qword": # 64-bit unsigned int
            return int(value, 16)
        elif reg_type == "hex": # Raw binary data
            # Parse hex bytes: "01,02,03" -> bytes([0x01, 0x02, 0x03])
            hex_bytes = [int(b, 16) for b in value.split(',') if b.strip()]
            return bytes(hex_bytes)
        elif reg_type.startswith("hex(") and reg_type.endswith(")"):
            # Extract the type number: hex(7) -> 7
            type_num = int(reg_type[4:-1])
            hex_bytes = [int(b, 16) for b in value.split(',') if b.strip()]
            
            if type_num == 0:  # REG_NONE
                return "None"
            elif type_num == 1:  # REG_SZ (string in hex format)
                return bytes(hex_bytes).decode('utf-16le').rstrip('\x00')
            elif type_num == 2:  # REG_EXPAND_SZ (expandable string)
                return bytes(hex_bytes).decode('utf-16le').rstrip('\x00')
            elif type_num == 3:  # REG_BINARY
                return bytes(hex_bytes)
            elif type_num == 4:  # REG_DWORD (little-endian)
                return int.from_bytes(bytes(hex_bytes), 'little')
            elif type_num == 5:  # REG_DWORD_BIG_ENDIAN
                return int.from_bytes(bytes(hex_bytes), 'big')
            elif type_num == 7:  # REG_MULTI_SZ (string array)
                decoded = bytes(hex_bytes).decode('utf-16le')
                # Split on null chars, remove empty strings and final double-null
                strings = [s for s in decoded.split('\x00') if s]
                return strings
            elif type_num == 11:  # REG_QWORD (64-bit little-endian)
                return int.from_bytes(bytes(hex_bytes), 'little')
            else:
                # Unknown type, return raw bytes
                return bytes(hex_bytes)
        else:
            # Unknown format, return as-is
            return raw_value