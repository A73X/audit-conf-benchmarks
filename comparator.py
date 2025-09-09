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

    def compare_and_print(self):
        for check_list in self.checks_l:
            for key in check_list:
                if key not in self.checks_values_d:
                    status = "No value expected"
                elif key not in self.values_d:
                    status = "No values found"
                else:
                    found_values = self.values_d[key]
                    if isinstance(found_values, list):
                        if len(found_values) == 1 or all(v == found_values[0] for v in found_values):
                            found_value = found_values[0]
                            status = self.comparator(key, found_value)
                        else:
                            status = "N/A"
                    else:
                        # If found_values is not a list, treat it as a single value.
                        status = self.comparator(key, found_value)

                if "non-compliant" in status:
                    print()
                    print(f"KEY : {key} - STATUS : {status}")
                    print(f"'{type(found_value)}' : '{type(self.checks_values_d[key]['parsed_value']['value'])}'")


    def comparator(self, key, found_value):
        expected_value = self.checks_values_d[key]
        if expected_value is None:
            return "Expected value not found"
        elif not isinstance(expected_value, dict):
            return f"Unexpected format for {key} : {expected_value}"
        elif expected_value["condition_type"] == "unknown":
            return "operator not found"
        operator = expected_value["parsed_value"]["operator"]

        if operator == "==":
            value = expected_value["parsed_value"]["value"]
            if value == found_value:
                return f"compliant : {found_value} == {value}"
            else:
                return f"non-compliant : {found_value} != {value}"
        elif operator == "in":
            value = expected_value["parsed_value"]["value"]
            if found_value in value:
                return f"compliant : {found_value} in {value}"
            else:
                return f"non-compliant : {found_value} is not in {value}"
        elif operator == ">=":
            value = expected_value["parsed_value"]["value"]
            try:
                if found_value >= value:
                    return f"compliant : {found_value} >= {value}"
                else:
                    return f"non-compliant : {found_value} < {value}"
            except (TypeError, ValueError):
                return f"Type error in comparison >= ({found_value} and {value})"
        elif operator == "<=":
            value = expected_value["parsed_value"]["value"]
            try:
                if found_value <= value:
                    return f"compliant : {found_value} <= {value}"
                else:
                    return f"non-compliant : {found_value} > {value}"
            except (TypeError, ValueError):
                return f"Type error in comparison <= ({found_value} and {value})"
        elif operator == "!=":
            value = expected_value["parsed_value"]["value"]
            try:
                if found_value != value:
                    return f"compliant : {found_value} != {value}"
                else:
                    return f"non-compliant : {found_value} == {value}"
            except (TypeError, ValueError):
                return f"Type error in comparison != ({found_value} and {value})"
            
        elif operator == "compound":
            # List of conditions to be evaluated.
            conditions = expected_value["parsed_value"]["conditions"]
            results = []
            for condition in conditions:
                op = condition['operator']
                value = condition['value']
                if op == '<=':
                    results.append(found_value <= value)
                elif op == '!=':
                    results.append(found_value != value)
                elif op == '>=':
                    results.append(found_value >= value)
                else:
                    results.append(False)

            if all(results):
                return "compliant"
            else:
                return "non-compliant"
        else:
            return f"Unsupported operator : {operator}"