from flask import Flask, render_template, request, jsonify # type: ignore
from flask_cors import CORS # type: ignore
from models import init_db, Rule, evaluate_rule

app = Flask(__name__)
CORS(app)
init_db()
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/create_rule', methods=['POST'])
def create_rule_api():
    try:
        rule_string = request.json.get('rule')
        if not rule_string:
            return jsonify({"error": "Rule string is missing"}), 400
        rule = Rule(rule_string=rule_string)
        rule.save()
        return jsonify({"message": "Rule created", "id": rule.id, "rule": rule.rule_string})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule_api():
    try:
        rule_id = request.json.get('rule_id')
        data = request.json.get('data')
        if not rule_id:
            return jsonify({"error": "Rule ID is missing"}), 400
        if not data:
            return jsonify({"error": "Data for evaluation is missing"}), 400
        result = evaluate_rule(rule_id, data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
    

