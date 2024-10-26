import re

class Node:
    def __init__(self, node_type, left=None, right=None, value=None):
        self.node_type = node_type  # "operator" or "operand"
        self.left = left  # Left child
        self.right = right  # Right child
        self.value = value  # Could be a condition like "age > 30"

    # Serialize Node into a dictionary
    def to_dict(self):
        return {
            "type": self.node_type,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None,
            "value": self.value
        }

# Parsing the rule string into an AST (handles AND/OR, parentheses)
def create_rule(rule_string):
    rule_string = rule_string.strip()

    # Handle parentheses recursively by balancing them
    if rule_string.startswith("(") and rule_string.endswith(")"):
        return create_rule(rule_string[1:-1])

    # Find the main AND/OR outside any parentheses
    split_index = find_main_operator(rule_string)

    if split_index != -1:
        operator = rule_string[split_index:split_index + 3].strip()
        left_part = rule_string[:split_index].strip()
        right_part = rule_string[split_index + 3:].strip()

        return Node(
            "operator", 
            left=create_rule(left_part), 
            right=create_rule(right_part), 
            value=operator
        )
    
    # Handle simple condition case (no AND/OR)
    return parse_condition(rule_string)

# Helper function to find the main AND/OR operator outside parentheses
def find_main_operator(rule_string):
    paren_count = 0
    for i, char in enumerate(rule_string):
        if char == '(':
            paren_count += 1
        elif char == ')':
            paren_count -= 1
        elif paren_count == 0:
            # Check if we have AND or OR outside of parentheses
            if rule_string[i:i + 3] == 'AND' or rule_string[i:i + 2] == 'OR':
                return i
    return -1

# Parse a condition like "age > 30"
def parse_condition(condition):
    match = re.match(r"(\w+)\s*([><=!]+)\s*(.+)", condition)
    if match:
        key = match.group(1)
        operator = match.group(2)
        value = match.group(3).strip().replace("'", "")
        return Node("operand", value=(key, operator, value))
    else:
        raise ValueError(f"Invalid condition format: {condition}")

# Evaluating the rule against the data
def evaluate_rule(rule_string, data):
    ast = create_rule(rule_string)
    return evaluate_ast(ast, data)

# Recursive function to evaluate AST against data
def evaluate_ast(node, data):
    if node.node_type == "operand":
        key, operator, value = node.value
        return apply_condition(data.get(key), operator, value)
    
    elif node.node_type == "operator":
        left_result = evaluate_ast(node.left, data)
        right_result = evaluate_ast(node.right, data)

        if node.value == "AND":
            return left_result and right_result
        elif node.value == "OR":
            return left_result or right_result

def apply_condition(data_value, operator, value):
    # Try to cast data_value and value to appropriate types before comparing
    try:
        if isinstance(data_value, str):
            # Attempt to cast string data value to an integer or float if needed
            if data_value.isdigit():
                data_value = int(data_value)
            else:
                try:
                    data_value = float(data_value)
                except ValueError:
                    pass  # Leave as string

        # Try to cast the 'value' (from rule) into int or float as well
        if value.isdigit():
            value = int(value)
        else:
            try:
                value = float(value)
            except ValueError:
                pass  # Leave as string

        # Apply the condition based on the operator
        if operator == ">":
            return data_value > value
        elif operator == "<":
            return data_value < value
        elif operator == "==":
            return data_value == value
        elif operator == "!=":
            return data_value != value
        else:
            raise ValueError(f"Unknown operator: {operator}")

    except Exception as e:
        raise ValueError(f"Error evaluating condition: {e}")
