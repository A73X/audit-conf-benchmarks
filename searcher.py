import os, mmap, re, chardet

class Searcher:
    def __init__(self, workdir):
        self.workdir = workdir
        self.workdir_files_l = []
        self.__not_unique_key_l = []
        self.file_size_exclusion = 1000000000 # 1 GB

    def set_not_unique_key_l(self, not_unique_key_l):
        self.__not_unique_key_l = not_unique_key_l

    def list_all_files(self, workdir):
        file_paths_l = []
        for root, dirs, files in os.walk(workdir):
            for file in files:
                file_paths_l.append(os.path.join(root, file))
        self.workdir_files_l = file_paths_l
    
    def __detect_encoding(self, file_path):
        with open(file_path, 'rb') as f:
            raw_data = f.read(4)  # Read first 4 bytes to check BOM
            
            # Check for BOM markers
            if raw_data.startswith(b'\xff\xfe\x00\x00'):
                return 'utf-32-le'
            elif raw_data.startswith(b'\x00\x00\xfe\xff'):
                return 'utf-32-be'
            elif raw_data.startswith(b'\xff\xfe'):
                return 'utf-16-le'
            elif raw_data.startswith(b'\xfe\xff'):
                return 'utf-16-be'
            elif raw_data.startswith(b'\xef\xbb\xbf'):
                return 'utf-8-sig'
            
            # Fallback to chardet for files without BOM
            f.seek(0)
            raw_data = f.read(8192) # Read first 8KB for detection
            result = chardet.detect(raw_data)
            return result['encoding'] if result['confidence'] > 0.7 else 'utf-8'
    
    def search_keyword_sensitive(self, keyword):
        file_paths_l = []

        for file in self.workdir_files_l:
            try:
                fsize = os.path.getsize(file)
                if (fsize == 0) or (fsize > self.file_size_exclusion):
                    continue
                encoding = self.__detect_encoding(file)
                with open(file, "r", encoding=encoding, errors='ignore') as f:
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                        if mm.find(keyword.encode(encoding)) != -1:
                            file_paths_l.append(file)
            except Exception as e:
                # Print or log errors like permission issues
                print(f"Skipping {file}: {e}")
        return file_paths_l
    
    def search_keyword_insensitive(self, keyword):
        file_paths_l = []
        
        for file in self.workdir_files_l:
            try:
                fsize = os.path.getsize(file)
                if (fsize == 0) or (fsize > self.file_size_exclusion):
                    continue
                encoding = self.__detect_encoding(file)
                with open(file, "r", encoding=encoding, errors='ignore') as f:
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                        if self.__case_insensitive_find(mm, keyword.encode(encoding)) != -1:
                            file_paths_l.append(file)
            except Exception as e:
                # Print or log errors like permission issues
                print(f"Skipping {file}: {e}")
        return file_paths_l
    
    def __case_insensitive_find(self, data, keyword):
        # Converts to lowercase
        data_lower = bytes(data).lower()
        keyword_lower = keyword.lower()
        return data_lower.find(keyword_lower)
    
    def regkey_to_keyword(self, regkey):
        # Regkey
        if regkey.startswith(('HKLM', 'HKU', 'HKEY_LOCAL_MACHINE', 'HKEY_USERS')):
            keyword = regkey.split(":", 1)[-1].strip()
            # Detect if duplicated key
            if keyword in self.__not_unique_key_l:
                # Get subkey
                keyword = regkey.split("\\")[-1].split(":")[0].strip()
                if keyword == "Parameters":
                    # Get subkey
                    keyword = regkey.split("\\")[-2].strip()
        # UI path
        else:
            # Extract last part of the UI path
            if ":" in regkey:
                keyword = regkey.split(":")[-1].strip()
            else:
                keyword = regkey.split("\\")[-1].strip()
                if keyword.startswith(("Audit ")):
                    keyword = keyword.split("Audit ",1)[-1]
        return keyword