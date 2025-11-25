from helper import Helper

class Secpol:
    def __init__(self):
        self.name = 'Secpol'
        self.parsable_files_l = ['.inf']
        self.helper = Helper()
        self.key_to_keyword_mapping = {
            "AllowAdministratorLockout": "Allow Administrator account lockout",
            "PasswordHistorySize": "Enforce password history",
            "MaximumPasswordAge": "Maximum password age",
            "MinimumPasswordAge": "Minimum password age",
            "MinimumPasswordLength": "Minimum password length",
            "PasswordComplexity": "Password must meet complexity requirements",
            "ClearTextPassword": "Store passwords using reversible encryption",
            "LockoutDuration": "Account lockout duration",
            "LockoutBadCount": "Account lockout threshold",
            "ResetLockoutCount": "Reset account lockout counter after",
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
            "SeCreateSymbolicLinkPrivilege": "Create symbolic links",
            "SeNetworkLogonRight": "Access this computer from the network",
            "SeTcbPrivilege": "Act as part of the operating system",
            "SeIncreaseQuotaPrivilege": "Adjust memory quotas for a process",
            "SeCreatePagefilePrivilege": "Create a pagefile",
            "SeCreateTokenPrivilege": "Create a token object",
            "SeTrustedCredManAccessPrivilege": "Access Credential Manager as a trusted caller",
            "SeCreateGlobalPrivilege": "Create global objects",
            "SeCreatePermanentPrivilege": "Create permanent shared objects",
            "SeDenyNetworkLogonRight": "Deny access to this computer from the network",
            "SeEnableDelegationPrivilege": "Enable computer and user accounts to be trusted for delegation",
            "SeAuditPrivilege": "Generate security audits",
            "SeLockMemoryPrivilege": "Lock pages in memory",
            "SeRelabelPrivilege": "Modify an object label",
            "SeSystemEnvironmentPrivilege": "Modify firmware environment values",
            "SeManageVolumePrivilege": "Perform volume maintenance tasks",
            "SeProfileSingleProcessPrivilege": "Profile single process",
            "SeSystemProfilePrivilege": "Profile system performance"
        }

        self.sid_to_name = {
            # https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dtyp/81d92bba-d22b-4a8c-908a-554ab29148ab
            # Universal well-known SIDs
            "S-1-0-0": "Null SID",
            "S-1-1-0": "Everyone",
            "S-1-2-0": "Local",
            "S-1-2-1": "Console Logon",
            "S-1-3-0": "Creator Owner",
            "S-1-3-1": "Creator Group",
            
            # NT Authority
            "S-1-5-1": "Dialup",
            "S-1-5-2": "Network",
            "S-1-5-3": "Batch",
            "S-1-5-4": "Interactive",
            "S-1-5-6": "Service",
            "S-1-5-7": "Anonymous",
            "S-1-5-8": "Proxy",
            "S-1-5-9": "Enterprise Controllers",
            "S-1-5-10": "Self",
            "S-1-5-11": "Authenticated Users",
            "S-1-5-12": "Restricted Code",
            "S-1-5-13": "Terminal Server Users",
            "S-1-5-18": "Local System",
            "S-1-5-19": "Local Service",
            "S-1-5-20": "Network Service",
            "S-1-5-113": "Local account",
        
            # Built-in domain alias (Local groups)
            "S-1-5-32-544": "Administrators",
            "S-1-5-32-545": "Users",
            "S-1-5-32-546": "Guests",
            "S-1-5-32-547": "Power Users",
            "S-1-5-32-548": "Account Operators",
            "S-1-5-32-549": "Server Operators",
            "S-1-5-32-550": "Print Operators",
            "S-1-5-32-551": "Backup Operators",
            "S-1-5-32-552": "Replicators",
            "S-1-5-32-553": "RAS Servers",
            "S-1-5-32-554": "Pre-Windows 2000 Compatible Access",
            "S-1-5-32-555": "Remote Desktop Users",
            "S-1-5-32-556": "Network Configuration Operators",
            "S-1-5-32-557": "Incoming Forest Trust Builders",
            "S-1-5-32-558": "Performance Monitor Users",
            "S-1-5-32-559": "Performance Log Users",
            "S-1-5-32-560": "Authorization Access Group",
            "S-1-5-32-561": "Terminal Server License Servers",
            "S-1-5-32-562": "Distributed COM Users",
            "S-1-5-32-568": "IUsers",
            "S-1-5-32-569": "Cryptographic Operators",
            "S-1-5-32-571": "Event Log Readers",
            "S-1-5-32-573": "Certificate Service DCOM Access",
            "S-1-5-32-574": "RDS Remote Access Servers",
            "S-1-5-32-575": "RDS Endpoint Servers",
            "S-1-5-32-576": "RDS Management Servers",
            "S-1-5-32-577": "Hyper-V Administrators",
            "S-1-5-32-579": "Access Control Assistance Operators",
            "S-1-5-32-580": "Remote Management Users",
            "S-1-5-32-581": "Default Account",
            "S-1-5-32-582": "Storage Replica Administrators",
            "S-1-5-32-583": "Device Owners",
            "S-1-5-32-584": "User Mode Drivers",
            "S-1-5-32-585": "Certificate Service DCOM Access",
            "S-1-5-90-0": "Window Manager\\Window Manager Group",
        
            # Mandatory Integrity Levels
            "S-1-16-0": "Untrusted",
            "S-1-16-4096": "Low",
            "S-1-16-8192": "Medium",
            "S-1-16-8448": "Medium-Plus",
            "S-1-16-12288": "High",
            "S-1-16-16384": "System",
            "S-1-16-20480": "Protected Process",

            # NT SERVICE Names
            "S-1-5-80-2970612574-78537857-698502321-558674196-1451644582": "NT SERVICE\\DPS",
            "S-1-5-80-3139157870-2983391045-3678747466-658725712-1809340420": "NT SERVICE\\WdiServiceHost",

            # NT VIRTUAL MACHINE
            "S-1-5-83-0": "NT VIRTUAL MACHINE\\Virtual Machines"
        }

    def __sid_value(self, value):
        value = value.replace("*","")
        if value in self.sid_to_name.keys():
            return self.sid_to_name[value]
        else:
            return value
    
    def __convert_enabled_disabled(self, value):
        if value == 0:
            return "Disabled"
        elif value == 1:
            return "Enabled"
        else:
            return value
        
    def __interprete_value(self, key, value):
        keys_l = ["PasswordComplexity", "ClearTextPassword", "RequireLogonToChangePassword", 
                  "ForceLogoffWhenHourExpire", "EnableAdminAccount", "EnableGuestAccount", 
                  "AllowAdministratorLockout", "LSAAnonymousNameLookup"]
        
        if any(k in key for k in keys_l):
            return self.__convert_enabled_disabled(value)
        
        if isinstance(value, str) and "*S-" in value:
            sid_value_l = value.split(",")
            interpreted_value_l = [self.__sid_value(sid.strip()) for sid in sid_value_l]
            if len(interpreted_value_l) == 1:
                return interpreted_value_l[0]
            else:
                return interpreted_value_l
        
        #  Return as-is
        return value

    def __extract_keys(self, regkeys_l):
        keyword_uipath_d = {}
        for key in regkeys_l:
            if key.startswith(("Computer Configuration")):
                keyword = key.split("\\")[-1].strip()
                # Check if subkey or key
                if ':' in keyword:
                    keyword = keyword.split(":",1)[-1].strip()
                keyword_uipath_d[keyword] = key
            elif key.startswith(("HKLM")):
                newkey = key.replace("HKLM", "MACHINE").replace(":", "\\").lower()
                keyword_uipath_d[newkey] = key
        return keyword_uipath_d

    def parse(self, file, regkeys_l):
        values_d = {}
        proofs_d = {}
        keyword_uipath_d = self.__extract_keys(regkeys_l)

        with open(file, "r", encoding='utf-16-le', errors='ignore') as f:
            lines = f.readlines()

        current_section = None
        for line in lines:
            # Logging
            len_uipath = len(keyword_uipath_d.keys())
            len_values = len(values_d.keys())
            self.helper.log_loading(f"Found {len_values}/{len_uipath} potential values in {file} with {self.name} parser")

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

            # Convert to int
            if val.isdigit():
                val = int(val)

            if current_section in ["System Access", "Privilege Rights"]:
                # For these sections, the simple key is searched for in the mapping.
                if (key in self.key_to_keyword_mapping.keys()) and (self.key_to_keyword_mapping[key] in keyword_uipath_d.keys()):
                    values_d[keyword_uipath_d[self.key_to_keyword_mapping[key]]] = self.__interprete_value(key, val)
                    proofs_d[keyword_uipath_d[self.key_to_keyword_mapping[key]]] = file
            elif current_section == "Registry Values":
                key = key.lower()
                val_type = int(val.split(',', 1)[0])
                val = val.split(',', 1)[-1].replace('"', '')
                # String
                if (val_type == 1) and val.isdigit():
                    val = int(val)
                # Int
                elif val_type == 4:
                    val = int(val)
                # Empty list
                elif (val_type == 7) and not val:
                    val = []
                # List
                elif val_type == 7:
                    val = val.split(',')

                if (key in keyword_uipath_d.keys()):
                    values_d[keyword_uipath_d[key]] = self.__interprete_value(key, val)
                    proofs_d[keyword_uipath_d[key]] = file

        # Logging
        print()
        return values_d, proofs_d