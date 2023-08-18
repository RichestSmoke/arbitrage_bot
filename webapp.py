
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from main import finally_dict
import time


# finally_dict = {
#     'KOKUSDT': {
#         'Spred': 1.36,
#         'buy_exchange': {'exchange': 'kucoin', 'price': 0.01234},
#         'sell_exchange': {'exchange': 'baybit', 'price': 0.01251}
#     },
#     'VSYSUSDT': {
#         'Spred': 1.46,
#         'buy_exchange': {'exchange': 'kucoin', 'price': 0.001319},
#         'sell_exchange': {'exchange': 'mexc', 'price': 0.0013385}
#     },
#     # Добавьте остальные данные в словарь finaly_dict
# }

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app)


@app.route("/")
def index():
    return render_template("index.html", data=finally_dict)

@socketio.on("connect")
def handle_connect():
    emit("data_update", finally_dict, broadcast=True)
    socketio.start_background_task(update_finally_dict)

def update_finally_dict():
    while True:
        socketio.emit("data_update", finally_dict)
        time.sleep(4)

if __name__ == "__main__":
    socketio.run(app, '127.0.0.1', 5000, debug=True)
