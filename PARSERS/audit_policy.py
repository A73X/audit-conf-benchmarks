import csv, mmap

class AuditPolicy:
    def __init__(self):
        self.name = 'AuditPolicy'
        self.parsable_files_l = ['.csv']

    def __extract_keys(self, regkeys_l):
        keyword_uipath_d = {}
        for key in regkeys_l:
            if key.startswith(("Computer Configuration")):
                keyword = key.split("\\")[-1]
                if keyword.startswith(("Audit ")):
                    keyword = keyword.split("Audit ", 1)[-1]
                keyword_uipath_d[keyword] = key
        return keyword_uipath_d

            
    def parse(self, file, regkeys_l):
        values_d = {}
        proofs_d = {}
        keyword_uipath_d = self.__extract_keys(regkeys_l)
        with open(file, "r", errors='ignore', newline='') as f:
            reader = csv.reader(f)
            header = next(reader)  # Ignore header line
            for row in reader:
                if len(row) > 4:
                    subcategory = row[2]
                    inclusion_setting = row[4]
                    if subcategory in keyword_uipath_d.keys():
                        values_d[keyword_uipath_d[subcategory]] = inclusion_setting
                        proofs_d[keyword_uipath_d[subcategory]] = file
        return values_d, proofs_d