import PIL.Image
import flask,PIL,os
app=flask.Flask(__name__)
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/encode', methods=['POST'])
def encode():
    image= flask.request.files['Image']
    message= flask.request.form['Text']

    if not image or not message:
        return 'Please provide both an image and a message.'
    
    input_path=os.path.join(app.config['UPLOAD_FOLDER'],'original.png')
    output_path=os.path.join(app.config['UPLOAD_FOLDER'],'encoded.png')
    image.save(input_path)
    hide_data_in_image(input_path, message, output_path)
    
    encoded_file_url = flask.url_for('static', filename='encoded.png')
    return flask.render_template('index.html', encoded_file_url=encoded_file_url)

@app.route('/decode', methods=['POST'])
def decode():
    encoded_image = flask.request.files['EncodedImage']

    if not encoded_image:
        return "Please upload an encoded image."

    input_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded_input.png')
    encoded_image.save(input_path)

    decoded_text = extract_data_from_image(input_path)
    return flask.render_template('index.html', decoded_text=decoded_text)

def hide_data_in_image(input_image_path, secret_message, output_image_path):
    image=PIL.Image.open(input_image_path)
    image= image.convert('RGB')
    binary_message= ''.join(format(ord(i), '08b') for i in secret_message) + '1111111111111110'
    pixels=list(image.getdata())

    new_pixels=[]
    data_index=0

    for pixel in pixels:
        r,g,b=pixel
        if data_index < len(binary_message):
            r = (r & ~1) | int(binary_message[data_index])
            data_index += 1
        if data_index < len(binary_message):
            g = (g & ~1) | int(binary_message[data_index])
            data_index += 1
        if data_index < len(binary_message):
            b = (b & ~1) | int(binary_message[data_index])
            data_index += 1
        new_pixels.append((r, g, b))

    image.putdata(new_pixels)
    image.save(output_image_path)


def extract_data_from_image(image_path):
    image = PIL.Image.open(image_path)
    image = image.convert('RGB')
    pixels = list(image.getdata())

    binary_data = ""
    for pixel in pixels:
        for value in pixel[:3]:
            binary_data += str(value & 1)

    chars = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    decoded_message = ""
    for c in chars:
        if c == '11111110':
            break
        decoded_message += chr(int(c, 2))

    return decoded_message.rstrip('\x00ÿ')


if __name__ == '__main__':
    app.run(debug=True)