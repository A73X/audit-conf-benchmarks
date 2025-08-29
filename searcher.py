import os, mmap, re, chardet

class Searcher:
    def __init__(self, workdir, not_unique_param):
        self.workdir = workdir
        self.workdir_files = []
        self.not_unique_param = not_unique_param
        self.file_size_exclusion = 1000000000 # 1 GB
        self.list_all_files()

    def list_all_files(self):
        file_paths = []
        for root, dirs, files in os.walk(self.workdir):
            for file in files:
                file_paths.append(os.path.join(root, file))
        self.workdir_files = file_paths
    
    def detect_encoding(self, file_path):
        """Auto-detect file encoding with BOM detection"""
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
        """Case sensitive"""
        file_paths = []

        for file in self.workdir_files:
            try:
                fsize = os.path.getsize(file)
                if (fsize == 0) or (fsize > self.file_size_exclusion):
                    continue
                encoding = self.detect_encoding(file)
                with open(file, "r", encoding=encoding, errors='ignore') as f:
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as s:
                        if s.find(keyword.encode(encoding)) != -1:
                            file_paths.append(file)
            except Exception as e:
                # Print or log errors like permission issues
                print(f"Skipping {file}: {e}")
        return file_paths
    
    def search_keyword_insensitive(self, keyword):
        """Case insensitive"""
        file_paths = []
        
        for file in self.workdir_files:
            try:
                fsize = os.path.getsize(file)
                if (fsize == 0) or (fsize > self.file_size_exclusion):
                    continue
                encoding = self.detect_encoding(file)
                keyword_bytes = keyword.encode(encoding)
                with open(file, "r", encoding=encoding, errors='ignore') as f:
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as s:
                        if self.__case_insensitive_find(s, keyword_bytes) != -1:
                            file_paths.append(file)
            except Exception as e:
                # Print or log errors like permission issues
                print(f"Skipping {file}: {e}")
        return file_paths
    

    def __case_insensitive_find(self, data, keyword):
        # Converts to lowercase
        data_lower = bytes(data).lower()
        keyword_lower = keyword.lower()
        return data_lower.find(keyword_lower)
    
    def regkey_to_keyword(self, regkey):
        if regkey.startswith(('HKLM', 'HKU', 'HKEY_LOCAL_MACHINE', 'HKEY_USERS')):
            keyword = regkey.split(":", 1)[-1].strip()
            # Detect if duplicate
            if keyword in self.not_unique_param:
                keyword = regkey.split("\\")[-1].split(":")[0].strip()
                if keyword == "Parameters":
                    keyword = regkey.split("\\")[-2].strip()
        else:
            if ":" in regkey:
                keyword = regkey.split(":")[-1].strip()
            else:
                keyword = regkey.split("\\")[-1].strip()
        return keyword