import openpyxl
import re

class CheckExtractor:
    def __init__(self):
        self.checks = []
        self.checks_values = {}
        self.not_unique_param = []
        self.__processed_params = []

    def extract_checks_from_xlsx(self, benchmark_xlsx):
        benchmark_sheet=0 # first sheet
        audit_column=9 # column (I)
        remediation_column=10 # column (J)
        
        # Load the workbook
        workbook = openpyxl.load_workbook(benchmark_xlsx)

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
                reg_keys = self.get_regkeys_in_audit_cell(cell_value)
                if reg_keys == 404:
                    # Get the cell value at remediation column
                    cell_value = sheet.cell(row=row, column=remediation_column).value
                    checks = self.get_check_in_remediation_cell(cell_value)
                    self.checks.append(checks)
                    self.get_values_in_remediation_cell(cell_value, checks)
                else:
                    self.checks.append(reg_keys)
                    self.get_values_in_audit_cell(cell_value, reg_keys)
            row+=1
        workbook.close()

    def get_regkeys_in_audit_cell(self, cell_value):
        pattern = re.compile(r'^(HKLM|HKU|HKEY_LOCAL_MACHINE|HKEY_USERS)\\.*', re.MULTILINE) # Registry key pattern
        reg_keys=[]

        cell_value_lines = cell_value.split('\n')
        no_match = True
        # Get all params
        for line in cell_value_lines:
            if pattern.match(line):
                #if (param == "Start") or (param == "Disabled") or (param == "Enabled") or (param == "<numeric value>") or (param == "Machine"):
                #    param=keys_param[0].split('\\')[-1]
                reg_key = re.search(r'^(?:HKLM|HKU|HKEY_LOCAL_MACHINE|HKEY_USERS)\\.*', line).group()
                reg_keys.append(reg_key)
                # Check duplicated param
                self.check_duplicate_param(reg_key.split(':', 1)[-1])
                no_match = False
        # Check if no match found
        if no_match:
            return 404
        # Return reg keys
        return reg_keys

    def get_check_in_remediation_cell(self, cell_value):
        pattern = re.compile(r'^(.*\\.*)+$') # key pattern
        checks = []

        cell_value_lines = cell_value.split('\n')
        no_match = True
        for line in cell_value_lines:
            if pattern.match(line):
                check = line.split('\\')[-1]
                checks.append(check)
                # Check duplicated param
                self.check_duplicate_param(check)
                no_match = False
                break
        # Check if no match found
        if no_match:
            return 404
        # Return checks
        return checks
    
    def get_values_in_audit_cell(self, cell_value, reg_keys):
        cell_value_lines = cell_value.split('\n')
        line_values = ""
        
        # Get value line
        for line in cell_value_lines:
            if 'value of' in line:
                line_values = line.split('value of', 1)[-1]
                break
        # For each registry key get value
        for reg_key in reg_keys:
            param = reg_key.split(':', 1)[-1]
            # Check if specific value for param
            if (param in line_values) and (param != line_values):
                # Get value for param
                for part in line_values.split(' and '):
                    if param in part:
                        # Get value with splits
                        value = part.strip().split(' (')[0].split('value of ')[-1]
                        break
            else:
                value = line_values.strip()[:-1]
            # Add regkey and value to dict
            self.checks_values[reg_key] = value

    def get_values_in_remediation_cell(self, cell_value, checks):
        cell_value_lines = cell_value.split('\n')
        line_values = ""
        
        # Get value line
        for line in cell_value_lines:
            if 'UI path to' in line:
                line_values = line.split('UI path to', 1)[-1].split(':', 1)[0]
                break
        value = line_values.strip()
        # Add check and value to dict
        self.checks_values[checks[0]] = value

    def check_duplicate_param(self, param):
        if param in self.__processed_params:
            if param not in self.not_unique_param:
                self.not_unique_param.append(param)
        self.__processed_params.append(param)