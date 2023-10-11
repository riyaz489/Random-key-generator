from flask import Flask, jsonify
from queries import free_booked_key, book_available_keys

app = Flask(__name__)


@app.get("/sequence/<numbers>")
def get_sequence(numbers):
    try:
        n = int(numbers)
    except:
        return 'input  is invalid, try with integer'
    res = book_available_keys(n)
    return jsonify({
        'keys': res
    })


@app.delete('/sequence/<seq>')
def delete_sequence(seq: str):
    try:
        n = int(seq)
    except:
        return 'try with number'
    res = free_booked_key(n)
    return jsonify({
        'keys deleted': str(res)
    })



if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.

    app.run()