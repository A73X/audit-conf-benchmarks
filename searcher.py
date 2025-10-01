from helper import Helper
import os, mmap, re, chardet, threading

class Searcher:
    def __init__(self, workdir, nb_threads):
        self.workdir = workdir
        self.workdir_files_l = []
        self.__not_unique_key_l = []
        self.file_size_exclusion = 1000000000 # 1 GB
        self.nb_threads = nb_threads
        self.helper = Helper()
        self.keyword_to_key_mapping = {
            "Enforce password history": "PasswordHistorySize",
            "Maximum password age": "MaximumPasswordAge",
            "Minimum password age": "MinimumPasswordAge",
            "Minimum password length": "MinimumPasswordLength",
            "Password must meet complexity requirements": "PasswordComplexity",
            "Store passwords using reversible encryption": "ClearTextPassword",
            "Account lockout duration": "LockoutDuration",
            "Account lockout threshold": "LockoutBadCount",
            "Reset account lockout counter after": "ResetLockoutCounter",
            "Guest account status": "EnableGuestAccount",
            "Rename administrator account": "NewAdministratorName",
            "Rename guest account": "NewGuestName",
            "Allow anonymous SID/Name translation": "LSAAnonymousNameLookup",
            "Force logoff when logon hours expire": "ForceLogoffWhenHourExpire",
            "Allow log on locally": "SeInteractiveLogonRight",
            "Deny log on locally": "SeDenyInteractiveLogonRight",
            "Allow log on through Remote Desktop Services": "SeRemoteInteractiveLogonRight",
            "Deny log on through Remote Desktop Services": "SeDenyRemoteInteractiveLogonRight",
            "Log on as a batch job": "SeBatchLogonRight",
            "Deny log on as a batch job": "SeDenyBatchLogonRight",
            "Log on as a service": "SeServiceLogonRight",
            "Deny log on as a service": "SeDenyServiceLogonRight",
            "Take ownership of files or other objects": "SeTakeOwnershipPrivilege",
            "Shut down the system": "SeShutdownPrivilege",
            "Force shutdown from a remote system": "SeRemoteShutdownPrivilege",
            "Debug programs": "SeDebugPrivilege",
            "Manage auditing and security log": "SeSecurityPrivilege",
            "Change the system time": "SeSystemtimePrivilege",
            "Change the time zone": "SeTimeZonePrivilege",
            "Back up files and directories": "SeBackupPrivilege",
            "Restore files and directories": "SeRestorePrivilege",
            "Impersonate a client after authentication": "SeImpersonatePrivilege",
            "Replace a process level token": "SeAssignPrimaryTokenPrivilege",
            "Increase scheduling priority": "SeIncreaseBasePriorityPrivilege",
            "Load and unload device drivers": "SeLoadDriverPrivilege",
            "Lock pages in memory": "SeLockMemoryPrivilege",
            "Create symbolic links": "SeCreateSymbolicLinkPrivilege",
            "Take ownership of files or objects": "SeTakeOwnershipPrivilege"
        }

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
    
    def __case_insensitive_find(self, data, keyword):
        # Converts to lowercase
        data_lower = bytes(data).lower()
        keyword_lower = keyword.lower()
        return data_lower.find(keyword_lower)
    
    def __regkey_to_keyword(self, regkey):
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
                    keyword = keyword.split("Audit ", 1)[-1]
                keyword = self.__convert_keyword_secpol_compliant(keyword)
        return keyword
    
    def __convert_keyword_secpol_compliant(self, keyword):
        if keyword in self.keyword_to_key_mapping.keys():
            return self.keyword_to_key_mapping[keyword]
        else:
            return keyword
    
    def search_insensitive(self, checks_l):
        # Flatten and convert regkeys -> keywords
        keywords_d = {regkey: self.__regkey_to_keyword(regkey) for check in checks_l for regkey in check}
        
        regkeys_per_file_d = {}
        lock = threading.Lock()

        # Split files for work
        chunks_files_l = self.__split_files_l(self.workdir_files_l)
        
        # Init threads
        threads = []
        for chunk in chunks_files_l:
            t = threading.Thread(target=self.__search_insensitive_thread, args=(lock, chunk, keywords_d, regkeys_per_file_d,))
            threads.append(t)

        # Start each thread
        for t in threads:
            t.start()

        # Wait for all threads to finish
        for t in threads:
            t.join()

        # Logging
        print()
        return regkeys_per_file_d
    
    def __split_files_l(self, files_l):
        # Calculate base chunk size and remainder
        total_length = len(files_l)
        base_chunk_size, remainder = divmod(total_length, self.nb_threads)

        chunks = []
        for i in range(self.nb_threads):
            # Calculate start index
            # First 'remainder' chunks get an extra element
            start_offset = min(i, remainder)
            start_index = i * base_chunk_size + start_offset

            # Calculate end index
            end_offset = min(i + 1, remainder)
            end_index = (i + 1) * base_chunk_size + end_offset

            # Extract the chunk
            chunk = files_l[start_index:end_index]
            chunks.append(chunk)

        return chunks
    
    def __search_insensitive_thread(self, lock, chunk, keywords_d, regkeys_per_file_d):
        local_regkeys_d = {}
        
        for file in chunk:
            try:
                fsize = os.path.getsize(file)
                if (fsize == 0) or (fsize > self.file_size_exclusion):
                    continue
                encoding = self.__detect_encoding(file)
                with open(file, "r", encoding=encoding, errors='ignore') as f:
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                        content = bytes(mm).lower()
                        for regkey, keyword in keywords_d.items():
                            self.helper.log_loading(f"Searching for potential values in files for parsing")
                            if content.find(keyword.encode(encoding).lower()) != -1:
                                local_regkeys_d.setdefault(file, []).append(regkey)
            except Exception as e:
                # Print or log errors like permission issues
                print(f"Skipping {file}: {e}")
        
        # Update dict when lock is acquired
        with lock:
            for file, regkeys in local_regkeys_d.items():
                regkeys_per_file_d.setdefault(file, []).extend(regkeys)