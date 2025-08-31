import openpyxl, re

class CheckExtractor:
    def __init__(self):
        self.checks_l = []
        self.checks_values_d = {}
        self.not_unique_key_l = []
        self.__processed_keys_l = []
        self.__regkey_pattern = re.compile(r'^(HKLM|HKU|HKEY_LOCAL_MACHINE|HKEY_USERS)\\.*', re.MULTILINE)
        self.__ui_path_pattern = re.compile(r'^(.*\\.*)+$')

    def extract_checks_from_xlsx(self, benchmark_xlsx):
        benchmark_sheet=0 # first sheet
        audit_column=9 # column (I)
        remediation_column=10 # column (J)
        
        # Load the workbook
        workbook = openpyxl.load_workbook(benchmark_xlsx, read_only=True)

        # Select the benchmark sheet
        sheet = workbook.worksheets[benchmark_sheet]

        row=5 # Start at second row to account for headers
        cell_value = "Random to get in loop" # Should not be empty
        # Loops until it finds an empty cell
        while cell_value :
            # Get the cell value at audit column
            cell_value = sheet.cell(row=row, column=audit_column).value
            # Check if string (empty cell are NoneType)
            if isinstance(cell_value, str):
                regkeys_l = self.__get_regkeys_in_audit_cell(cell_value)
                if not regkeys_l:
                    # Get the cell value at remediation column
                    cell_value = sheet.cell(row=row, column=remediation_column).value
                    ui_paths_l = self.__get_ui_paths_in_remediation_cell(cell_value)
                    self.checks_l.append(ui_paths_l)
                    self.__get_values_in_remediation_cell(cell_value, ui_paths_l)
                else:
                    self.checks_l.append(regkeys_l)
                    self.__get_values_in_audit_cell(cell_value, regkeys_l)
            row+=1
        workbook.close()

    def __get_regkeys_in_audit_cell(self, cell_value):
        regkeys_l = []

        cell_value_lines = cell_value.split('\n')
        no_match = True
        # Get all params
        for line in cell_value_lines:
            if self.__regkey_pattern.match(line):
                regkey = re.search(r'^(?:HKLM|HKU|HKEY_LOCAL_MACHINE|HKEY_USERS)\\.*', line).group()
                regkeys_l.append(regkey)
                # Check duplicated key
                self.__check_duplicate_key(regkey)
                no_match = False
        # Check if no match found
        if no_match:
            return None
        # Return reg keys
        return regkeys_l

    def __get_ui_paths_in_remediation_cell(self, cell_value):
        ui_paths_l = []

        cell_value_lines = cell_value.split('\n')
        no_match = True
        for line in cell_value_lines:
            if self.__ui_path_pattern.match(line):
                ui_path = line.split(':', 1)[-1].strip()
                ui_paths_l.append(ui_path)
                # Check duplicated key
                self.__check_duplicate_key(ui_path)
                no_match = False
                break
        # Check if no match found
        if no_match:
            return None
        # Return checks
        return ui_paths_l
    
    def __get_values_in_audit_cell(self, cell_value, regkeys_l):
        cell_value_lines = cell_value.split('\n')
        line_values = ""
        
        # Get value line
        for line in cell_value_lines:
            if 'value of' in line:
                line_values = line.split('value of', 1)[-1]
                break
        # For each registry key get value
        for regkey in regkeys_l:
            key = regkey.split(':', 1)[-1]
            # Check if specific value for key
            if (key in line_values) and (key != line_values):
                # Get value for key
                for part in line_values.split(' and '):
                    if key in part:
                        # Get value with splits
                        value = part.strip().split(' (')[0].split('value of ')[-1]
                        break
            else:
                value = line_values.strip()[:-1]
            # Add regkey and value to dict
            self.checks_values_d[regkey] = value

    def __get_values_in_remediation_cell(self, cell_value, ui_paths_l):
        cell_value_lines = cell_value.split('\n')
        line_values = ""
        
        # Get value line
        for line in cell_value_lines:
            if 'UI path to' in line:
                line_values = line.split('UI path to', 1)[-1].split(':', 1)[0]
                break
        value = line_values.strip()
        # Add UI path and value to dict
        self.checks_values_d[ui_paths_l[0]] = value

    def __check_duplicate_key(self, regkey):
        # Regkey
        if regkey.startswith(('HKLM', 'HKU', 'HKEY_LOCAL_MACHINE', 'HKEY_USERS')):
            key = regkey.split(':', 1)[-1]
        # UI path
        else:
            # Extract last part of the UI path
            if ":" in regkey:
                key = regkey.split(":")[-1].strip()
            else:
                key = regkey.split("\\")[-1].strip()
        # Update list of keys that are not unique
        if key in self.__processed_keys_l:
            if key not in self.not_unique_key_l:
                self.not_unique_key_l.append(key)
        else:
            self.__processed_keys_l.append(key)