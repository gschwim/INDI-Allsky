from flask import Flask, send_file
import io

app = Flask(__name__)

@app.route('/live', methods=['GET'])
def serveImage():
    file = '/dev/shm/color.png'

    image = open(file, 'rb')
    image = io.BytesIO(image.read())

    return send_file(image, mimetype='image/png')

if __name__ == '__main__':

    app.run(host='0.0.0.0')