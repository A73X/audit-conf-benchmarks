from helper import Helper
import re

class Comparator:
    def __init__(self):
        self.checks_l = []
        self.checks_values_d = {}
        self.default_values_d = {}
        self.values_d = {}
        self.compliance_l = []
        self.use_defaults = False
        self.helper = Helper()

    def set_checks_l(self, checks_l):
        self.checks_l = checks_l

    def set_checks_values_d(self, checks_values_d):
        self.checks_values_d = checks_values_d

    def set_default_values_d(self, default_values_d):
        self.default_values_d = default_values_d

    def set_use_defaults(self, use_defaults):
        self.use_defaults = use_defaults

    def set_values_d(self, values_d):
        self.values_d = values_d

    def eval_compliance(self):
        # Init compliance and reason list
        compliance_l = []
        reason_l = []
        
        # Compliance for each check
        for check_list in self.checks_l:
            compliance_keys_l = []
            reasons_keys_l = []
            # Compare each key
            for key in check_list:
                if key not in self.checks_values_d:
                    compliance = "check manually"
                    reason = f"{key} : No value expected"
                elif key not in self.values_d:
                    if self.use_defaults and self.default_values_d.get(key) is not None:
                        compliance, reason = self.__comparator_with_default(key)
                    else:
                        compliance = "check manually"
                        reason = f"{key} : No value found"
                else:
                    found_values = self.values_d[key]
                    if isinstance(found_values, list):
                        if len(found_values) == 1 or all(v == found_values[0] for v in found_values):
                            found_value = found_values[0]
                            compliance, reason = self.__comparator(key, found_value)
                        else:
                            compliance = "check manually"
                            reason = f"{key} : Different values found"
                    else:
                        # If found_values is not a list, treat it as a single value.
                        compliance, reason = self.__comparator(key, found_value)

                # Store compliance and reason for key
                compliance_keys_l.append(compliance)
                reasons_keys_l.append(reason)
            
            # Get compliance for check
            compliance_l.append(self.__get_compliance_for_check(compliance_keys_l))
            reason_l.append(reasons_keys_l)

            # Logging
            self.helper.log_info(f"Checked compliance for {len(compliance_l)}/{len(self.checks_l)}", end="\r", flush=True)
        
        # Logging
        print()
        return compliance_l, reason_l


    def __normalize(self, v, other):
        """Normalize Enabled/Disabled strings to int when the other side is numeric, and vice versa."""
        _map = {"enabled": 1, "disabled": 0}
        if isinstance(v, str) and isinstance(other, int) and v.lower() in _map:
            return _map[v.lower()]
        if isinstance(v, int) and isinstance(other, str) and other.lower() in _map:
            return _map.get(str(v), v)  # 1→"enabled" side already handled by swapped call
        return v

    def __comparator(self, key, found_value):
        # Check expected value
        expected_value = self.checks_values_d[key]
        if expected_value is None:
            compliance = "check manually"
            reason = "Expected value not found"
            return compliance, reason
        elif not isinstance(expected_value, dict):
            compliance = "check manually"
            reason = f"Unexpected format for {key} : {expected_value}"
            return compliance, reason
        elif expected_value["condition_type"] == "unknown":
            compliance = "check manually"
            reason = "Operator not found"
            return compliance, reason

        # Check operator
        operator = expected_value["parsed_value"]["operator"]
        if operator == "==":
            value = expected_value["parsed_value"]["value"]
            # Unwrap single-item list
            if isinstance(value, list) and len(value) == 1:
                value = value[0]
            # Normalize Enabled/Disabled ↔ 1/0 between the two sides
            value = self.__normalize(value, found_value)
            found_value = self.__normalize(found_value, value)
            # Normalise lists: lowercase + sort for case-insensitive order-independent comparison
            if isinstance(value, list) and isinstance(found_value, list):
                value = sorted(i.lower() for i in value)
                found_value = sorted(i.lower() for i in found_value)
            if value == found_value:
                compliance = "compliant"
                reason = f"{found_value} == {value}"
            else:
                compliance = "non-compliant"
                reason = f"{found_value} != {value}"
        elif operator == "in":
            value = expected_value["parsed_value"]["value"]
            # Normalize Enabled/Disabled ↔ 1/0 so "Enabled" in [1, 2] works
            found_value = self.__normalize(found_value, value[0] if value else found_value)
            if found_value in value:
                compliance = "compliant"
                reason = f"{found_value} in {value}"
            else:
                compliance = "non-compliant"
                reason = f"{found_value} not in {value}"
        elif operator == ">=":
            value = expected_value["parsed_value"]["value"]
            try:
                if found_value >= value:
                    compliance = "compliant"
                    reason = f"{found_value} >= {value}"
                else:
                    compliance = "non-compliant"
                    reason = f"{found_value} < {value}"
            except (TypeError, ValueError):
                compliance = "check manually"
                reason = f"Type error in comparison >= ({found_value} and {value})"
        elif operator == "<=":
            value = expected_value["parsed_value"]["value"]
            try:
                if found_value <= value:
                    compliance = "compliant"
                    reason = f"{found_value} <= {value}"
                else:
                    compliance = "non-compliant"
                    reason = f"{found_value} > {value}"
            except (TypeError, ValueError):
                compliance = "check manually"
                reason = f"Type error in comparison <= ({found_value} and {value})"
        elif operator == "!=":
            value = expected_value["parsed_value"]["value"]
            try:
                if found_value != value:
                    compliance = "compliant"
                    reason = f"{found_value} is different from {value}"
                else:
                    compliance = "non-compliant"
                    reason = f"{found_value} is not different from {value}"
            except (TypeError, ValueError):
                compliance = "check manually"
                reason = f"Type error in comparison != ({found_value} and {value})"
        # Complex condition
        elif operator == "compound":
            # List of conditions to be evaluated.
            conditions = expected_value["parsed_value"]["conditions"]
            results = []
            reasons = []
            for condition in conditions:
                op = condition['operator']
                value = condition['value']
                try:
                    if op == '<=':
                        if found_value <= value:
                            results.append(True)
                            reasons.append(f"{found_value} <= {value}")
                        else:
                            results.append(False)
                            reasons.append(f"{found_value} > {value}")
                    elif op == '!=':
                        if found_value != value:
                            results.append(True)
                            reasons.append(f"{found_value} is different from {value}")
                        else:
                            results.append(False)
                            reasons.append(f"{found_value} is not different from {value}")
                    elif op == '>=':
                        if found_value >= value:
                            results.append(True)
                            reasons.append(f"{found_value} >= {value}")
                        else:
                            results.append(False)
                            reasons.append(f"{found_value} < {value}")
                    else:
                        results.append(False)
                        reasons.append(f"Unsupported operator : {op}")
                except (TypeError, ValueError):
                    results.append(False)
                    reasons.append(f"Type error in comparison {op} ({found_value} and {value})")

            if all(results):
                compliance = "compliant"
                reason = ", ".join(reasons)
            elif not all(results) and any("Unsupported operator" in r for r in reasons):
                compliance = "check manually"
                reason = ", ".join(reasons)
            else:
                compliance = "non-compliant"
                reason = ", ".join(reasons)
        else:
            compliance = "check manually"
            reason = f"Unsupported operator : {operator}"
        
        # Return compliance and reson for key
        reason = f"{key} : {reason}"
        return compliance, reason
    
    def __comparator_with_default(self, key):
        default_value = self.default_values_d[key]

        # "NOT_CONFIGURED" means the key is absent on the machine.
        # Check whether the expected value explicitly allows key absence.
        if default_value == "NOT_CONFIGURED":
            expected = self.checks_values_d.get(key)
            if isinstance(expected, dict) and isinstance(expected.get("parsed_value"), dict):
                parsed = expected["parsed_value"]
                # The value expression "X or that the key does not exist" was already
                # normalised to operator == by the extractor, so key absence is compliant.
                if parsed.get("operator") == "==":
                    return "compliant", f"[default] {key} : key not found, default is NOT_CONFIGURED (key absent) == {parsed.get('value')}"
            return "non-compliant", f"[default] {key} : key not found, default is NOT_CONFIGURED (key absent)"

        compliance, reason = self.__comparator(key, default_value)
        return compliance, f"[default] {reason}"

    def __get_compliance_for_check(self, compliance_keys_l):
        compliance = "compliant"
        for c in compliance_keys_l:
            if c == "non-compliant":
                compliance = "non-compliant"
                break
            elif c == "check manually":
                compliance = "check manually"
                break
            elif c == "compliant":
                continue
            # Garbage in compliance list
            else:
                compliance = "check manually"
                break
        return compliance