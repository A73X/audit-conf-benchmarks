import mmap

class RegExport:
    def __init__(self):
        self.name = 'RegExport'
        self.parsable_files = ['HKLM.txt', 'HKU.txt', 'HKCU.txt', 'HKCC.txt', 'HKCR.txt']
        self.encoding = 'utf-16-le'
        self.new_line = b'\r\x00\n\x00'

    def parse(self, file, regkeys):
        regkeys_dict_v, regkeys_dict_b = self.regkeys_dicts(regkeys)
        found_values = {}
        with open(file, "r", encoding=self.encoding, errors='ignore') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as s:
                line_start = 0
                
                while line_start < len(s):
                    line_end = self.find_end_of_line(s, line_start)
                    
                    # Extract line bytes
                    line_bytes = s[line_start:line_end].lower()
                    
                    # Check if any regkey is in this line
                    for regkey in regkeys_dict_b.keys():
                        regkeys_to_delete = []
                        if regkeys_dict_b[regkey] in line_bytes:
                            # Decode line only when we find a match
                            line_content = line_bytes.decode(self.encoding, errors='ignore')
                            regkey_d = regkeys_dict_b[regkey].decode(self.encoding, errors='ignore')
                            # Check if exact line
                            if f'[{regkey_d}]' == line_content:
                                value = self.extract_value(regkeys_dict_v[regkey], s, line_start, line_end)
                                # If value is found
                                if value:
                                    found_values[regkey] = value
                                    regkeys_to_delete.append(regkey)
                    
                    # Remove found regkey value
                    for found_regkey in regkeys_to_delete:
                        del regkeys_dict_b[found_regkey]
                        del regkeys_dict_v[found_regkey]

                    if not regkeys_dict_b:
                        break
                    else:
                        line_start = self.move_to_next_line(s, line_end)
        return found_values
    
    def find_end_of_line(self, s, line_start):
        # Find end of current line
        line_end = s.find(self.new_line, line_start)
        if line_end == -1:
            line_end = len(s)  # Last line without newline
        return line_end
    
    def move_to_next_line(self, s, line_end):
        # Move to next line
        if line_end == len(s):
            return len(s) # Break while loop
        line_start = line_end + len(self.new_line)
        return line_start
    
    def regkeys_dicts(self, regkeys):
        regkeys_dict_v = {}
        regkeys_dict_b = {}
        
        for regkey in regkeys:
            regkey = self.format_regkey(regkey)
            regkeys_dict_v[regkey] = regkey.split(':')[-1].lower()
            regkeys_dict_b[regkey] = regkey.split(':')[0].encode(self.encoding).lower()
        return regkeys_dict_v, regkeys_dict_b
    
    def format_regkey(self, regkey):
        if 'HKLM' in regkey:
            regkey = regkey.replace('HKLM', 'HKEY_LOCAL_MACHINE')
        elif 'HKU' in regkey:
            regkey = regkey.replace('HKU', 'HKEY_USERS')
        elif 'HKCU' in regkey:
            regkey = regkey.replace('HKCU', 'HKEY_CURRENT_USER')
        elif 'HKCC' in regkey:
            regkey = regkey.replace('HKCC', 'HKEY_CURRENT_CONFIG')
        elif 'HKCR' in regkey:
            regkey = regkey.replace('HKCR', 'HKEY_CLASSES_ROOT')

        return regkey
    
    def extract_value(self, param, s, line_start, line_end):
        while line_start < len(s):
            # Start on new line
            line_start = line_end + len(self.new_line)
            
            line_end = self.find_end_of_line(s, line_start)
            # Extract line bytes
            line_bytes = s[line_start:line_end].lower()
            line_content = line_bytes.decode(self.encoding, errors='ignore')
            if line_content:
                if param in line_content:
                    return line_content.split('=')[-1].split(':')[-1]
                else:
                    line_start = self.move_to_next_line(s, line_end)
            else: # End of registry key block
                break
        return None
