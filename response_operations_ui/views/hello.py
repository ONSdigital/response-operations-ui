from flask import render_template

from response_operations_ui import app


@app.route('/', methods=['GET'])
def test_route():
    return render_template('test.html')
