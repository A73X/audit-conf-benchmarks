import re

class Comparator:
    def __init__(self):
        self.checks_l = []
        self.checks_values_d = {}
        self.values_d = {}
        self.compliance_l = []

    def set_checks_l(self, checks_l):
        self.checks_l = checks_l

    def set_checks_values_d(self, checks_values_d):
        self.checks_values_d = checks_values_d
    
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
        return compliance_l, reason_l


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
            if value == found_value:
                compliance = "compliant"
                reason = f"{found_value} == {value}"
            else:
                compliance = "non-compliant"
                reason = f"{found_value} != {value}"
        elif operator == "in":
            value = expected_value["parsed_value"]["value"]
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