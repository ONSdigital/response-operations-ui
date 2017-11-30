from response_operations_ui import app


@app.route('/', methods=['GET'])
def test_route():
    return 'Home'
