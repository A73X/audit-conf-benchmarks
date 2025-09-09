class Secpol:
    def __init__(self):
        self.name = 'Secpol'
        self.parsable_files_l = ['.inf']
        self.key_to_keyword_mapping = {
            "PasswordHistorySize": "Enforce password history",
            "MaximumPasswordAge": "Maximum password age",
            "MinimumPasswordAge": "Minimum password age",
            "MinimumPasswordLength": "Minimum password length",
            "PasswordComplexity": "Password must meet complexity requirements",
            "ClearTextPassword": "Store passwords using reversible encryption",
            "LockoutDuration": "Account lockout duration",
            "LockoutBadCount": "Account lockout threshold",
            "ResetLockoutCounter": "Reset account lockout counter after",
            "EnableGuestAccount": "Guest account status",
            "NewAdministratorName": "Rename administrator account",
            "NewGuestName": "Rename guest account",
            "LSAAnonymousNameLookup": "Allow anonymous SID/Name translation",
            "ForceLogoffWhenHourExpire": "Force logoff when logon hours expire",
            "SeInteractiveLogonRight": "Allow log on locally",
            "SeDenyInteractiveLogonRight": "Deny log on locally",
            "SeRemoteInteractiveLogonRight": "Allow log on through Remote Desktop Services",
            "SeDenyRemoteInteractiveLogonRight": "Deny log on through Remote Desktop Services",
            "SeBatchLogonRight": "Log on as a batch job",
            "SeDenyBatchLogonRight": "Deny log on as a batch job",
            "SeServiceLogonRight": "Log on as a service",
            "SeDenyServiceLogonRight": "Deny log on as a service",
            "SeTakeOwnershipPrivilege": "Take ownership of files or other objects",
            "SeShutdownPrivilege": "Shut down the system",
            "SeRemoteShutdownPrivilege": "Force shutdown from a remote system",
            "SeDebugPrivilege": "Debug programs",
            "SeSecurityPrivilege": "Manage auditing and security log",
            "SeSystemtimePrivilege": "Change the system time",
            "SeTimeZonePrivilege": "Change the time zone",
            "SeBackupPrivilege": "Back up files and directories",
            "SeRestorePrivilege": "Restore files and directories",
            "SeImpersonatePrivilege": "Impersonate a client after authentication",
            "SeAssignPrimaryTokenPrivilege": "Replace a process level token",
            "SeIncreaseBasePriorityPrivilege": "Increase scheduling priority",
            "SeLoadDriverPrivilege": "Load and unload device drivers",
            "SeLockMemoryPrivilege": "Lock pages in memory",
            "SeCreateSymbolicLinkPrivilege": "Create symbolic links"
        }

    def __extract_keys(self, regkeys_l):
        keyword_uipath_d = {}
        for key in regkeys_l:
            if key.startswith(("Computer Configuration")):
                keyword = key.split("\\")[-1]
                keyword_uipath_d[keyword] = key
        return keyword_uipath_d

    def parse(self, file, regkeys_l):
        values_d = {}
        proofs_d = {}
        keyword_uipath_d = self.__extract_keys(regkeys_l)

        with open(file, "r", encoding='utf-16-le', errors='ignore') as f:
            lines = f.readlines()

        current_section = None
        for line in lines:
            l = line.strip()
            if not l or l.startswith(';'):
                continue
            if l.startswith('[') and l.endswith(']'):
                current_section = l.strip('[]').strip()
                continue

            if '=' not in l:
                continue  # Ignore lines without ‘=’

            key, val = l.split('=', 1)
            key = key.strip()
            val = val.strip()

            # Cleaning of quotation marks around values
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]

            if current_section in ["System Access", "Privilege Rights"]:
                # For these sections, the simple key is searched for in the mapping.
                if (key in self.key_to_keyword_mapping.keys()) and (self.key_to_keyword_mapping[key] in keyword_uipath_d.keys()):
                    print(f"{key} = {val}")
                    values_d[keyword_uipath_d[self.key_to_keyword_mapping[key]]] = val
                    proofs_d[keyword_uipath_d[self.key_to_keyword_mapping[key]]] = file

        return values_d, proofs_d