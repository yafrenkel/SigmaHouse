from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

clients = []
clients_dic = {}


@app.route('/smart', methods=['GET'])
def smart():
    serial_number = request.args.get('serial_number')
    user_name = request.args.get('user_name')
    ip_address = request.args.get('ip_address')

    if not serial_number or not user_name:
        return jsonify({'error': 'Missing serial_number or user_name'}), 400

    test_message = "Hello dude!"
    # Create a custom message
    message = f"Hello {user_name}, your device {serial_number} is registered!"

    # Add client to the list
    clients.append({'serial_number': serial_number, 'ip_address':  ip_address, 'user_name': user_name, 'message': message})

    clients_dic[ip_address] = {'serial_number': serial_number, 'ip_address':  ip_address, 'user_name': user_name}

    return jsonify({'message': message})

#http://192.168.1.4/smart?serial_number=111111&user_name=Lilia&ip_address=11221212
#http://iot.gurus.com/smart?serial_number=jes_house_address&user_name=JEssica&ip_address=Jes_IP

@app.route('/test')
def test():
    for key,value in clients_dic.items():
        print(clients_dic[key])
        print(value['serial_number'])
        print(value['ip_address'])

    return ''


@app.route('/')
def index():
    clients_list = list(clients_dic.values())
    # Render a simple HTML page with the list of clients
    html = """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>Client List</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            margin: 20px;
          }
          table {
            width: 100%;
            border-collapse: collapse;
          }
          th, td {
            padding: 8px 12px;
            border: 1px solid #ccc;
          }
          th.gray {
            background-color: #f2f2f2;
          }
          .blue {
            color: blue;
          }
          th.pink {
            background-color: #f2f2f2;
          }
        </style>
      </head>
      <body>
        <h1 class="blue">Registered Smart Houses</h1>
        <table>
          <thead>
            <tr>
              <th>Serial Number</th>
              <th>IP Address</th>
              <th>User Name</th>
              <th>Message</th>
            </tr>
          </thead>
          <tbody>
            {% for client in clients %}
            <tr>
              <td>{{ client.serial_number }}</td>
              <td>{{ client.ip_address }}</td>
              <td>{{ client.user_name }}</td>
              <td>{{ client.message }}</td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </body>
    </html>
    """
    return render_template_string(html, clients=clients_list)


if __name__ == '__main__':
    app.run(
        host="0.0.0.0", port=80, debug=True, use_reloader=False  # noqa: S201, S104
    )
