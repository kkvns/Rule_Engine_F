import sqlite3

def init_db():
    conn = sqlite3.connect('rules.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_string TEXT)''')
    conn.commit()
    conn.close()

class Rule:
    def __init__(self, rule_string):
        self.rule_string = rule_string
        self.id = None  # Initialize id as None before saving

    def save(self):
        conn = sqlite3.connect('rules.db')
        c = conn.cursor()
        c.execute('INSERT INTO rules (rule_string) VALUES (?)', (self.rule_string,))
        self.id = c.lastrowid  # Get the auto-generated id
        conn.commit()
        conn.close()

    @staticmethod
    def get_rule_by_id(rule_id):
        conn = sqlite3.connect('rules.db')
        c = conn.cursor()
        c.execute('SELECT * FROM rules WHERE id = ?', (rule_id,))
        rule = c.fetchone()
        conn.close()
        if rule:
            return Rule(rule[1])
        return None

def apply_condition(data_value, operator, value):
    try:
        # Convert the values to the same type before comparison
        if isinstance(data_value, str) and value.isdigit():
            value = int(value)
        elif isinstance(data_value, int):
            value = int(value)
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

def evaluate_rule(rule_id, data):
    rule = Rule.get_rule_by_id(rule_id)
    if rule:
        try:
            # Replace logical operators and equality operators for Python compatibility
            rule_string = rule.rule_string.replace('AND', 'and').replace('OR', 'or').replace('=', '==')
            result = eval(rule_string, {}, data)
            return {'result': result}
        except Exception as e:
            return {'error': str(e)}
    return {'error': 'Rule not found'}
