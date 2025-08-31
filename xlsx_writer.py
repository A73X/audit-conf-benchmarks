import openpyxl

class XlsxWriter:
    def __init__(self, benchmark_xlsx):
        self.benchmark_xlsx = benchmark_xlsx
    
    def write(self, checks, values, proofs):
        benchmark_sheet=0 # first sheet
        value_column=14 # column (N)
        proof_column=15 # column (O)
        row=5 # Start at second row to account for headers

        # Load the workbook
        workbook = openpyxl.load_workbook(self.benchmark_xlsx)
        # Select the benchmark sheet explicitly
        sheet = workbook.worksheets[benchmark_sheet]

        # Iterate through checks
        for regkeys in checks:
            sheet.cell(row=row, column=value_column).value = self.__format_value(regkeys, values)
            sheet.cell(row=row, column=proof_column).value = self.__format_value(regkeys, proofs)
            row+=1

        # Save the changes
        workbook.save(self.benchmark_xlsx)
        workbook.close()
    
    def __format_value(self, regkeys, values):
        cell_value = ""
        for regkey in regkeys:
            if regkey in values.keys():
                for value in values[regkey]:
                    if cell_value: # Format new line
                        cell_value += "\n"
                    cell_value += f"{regkey} : {value}"
            else:
                if cell_value: # Format new line
                    cell_value += "\n"
                cell_value += f"{regkey} : NOT FOUND"
        return cell_value
    
    def __format_proof(self, regkeys, proofs):
        cell_value = ""
        for regkey in regkeys:
            if regkey in proofs.keys():
                for proof in proofs[regkey]:
                    if cell_value: # Format new line
                        cell_value += "\n"
                    cell_value += f"{regkey} : {proof}"
            else:
                if cell_value: # Format new line
                    cell_value += "\n"
                cell_value += f"{regkey} : NOT FOUND"
        return cell_value