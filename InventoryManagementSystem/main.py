from flask import Flask, render_template, request
import qrcode
from io import BytesIO
from base64 import b64encode

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def generateQR():
    memory = BytesIO()
    data = request.form.get('serial_no')
    
    # Check if the input is a 5-digit number
    if data.isdigit() and len(data) == 5:
        img = qrcode.make(data)
        img.save(memory)
        memory.seek(0)

        base64_img = "data:image/png;base64," + b64encode(memory.getvalue()).decode('ascii')
        return render_template('index.html', data=base64_img)
    else:
        error_msg = "Please enter a 5-digit number."
        return render_template('index.html', error=error_msg)

if __name__ == '__main__':
    app.run(debug=True)