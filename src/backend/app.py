# src/backend/app.py

from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage for forms
forms = {}

@app.route('/forms', methods=['POST'])
def create_form():
    form_id = len(forms) + 1
    form_data = request.json
    forms[form_id] = form_data
    return jsonify({"id": form_id, "form": form_data}), 201

@app.route('/forms/<int:form_id>', methods=['GET'])
def read_form(form_id):
    form_data = forms.get(form_id)
    if form_data:
        return jsonify({"id": form_id, "form": form_data}), 200
    else:
        return jsonify({"error": "Form not found"}), 404

@app.route('/forms/<int:form_id>', methods=['PUT'])
def update_form(form_id):
    form_data = request.json
    if form_id in forms:
        forms[form_id] = form_data
        return jsonify({"id": form_id, "form": form_data}), 200
    else:
        return jsonify({"error": "Form not found"}), 404

@app.route('/forms/<int:form_id>', methods=['DELETE'])
def delete_form(form_id):
    if form_id in forms:
        del forms[form_id]
        return jsonify({"message": "Form deleted"}), 200
    else:
        return jsonify({"error": "Form not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)