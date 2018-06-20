import  os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = './upload'
NUM_SLICES = 155
ALLOWED_EXTENSIONS = set(['nii', 'nii.gz', 'gz'])
app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path="")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "super secret key"

def clean_jpeg_dir():
    '''
    Clean the upload directory everytime this server  is run
    :return: None
    '''
    os.system('rm -rf ./upload/*')


def check_extension(filename):
    '''
    Check if the uploaded file  has a legal extension

    :param filename: filename of the upload
    :return: Boolean
    '''
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/demo', methods=['GET', 'POST'])
def demo():
    '''
    A demo page, which renders the quadview page. This is to preserve sanity when
    repeatedly running server. No need to upload files again and again to see if the
    rendering works. Just click on demo button.

    :return:
    '''
    return render_template('uploader.html')

@app.route('/uploads/')
def uploaded_file():
    '''
    Endpoint called  after a successful upload. Renders the quadview page.
    Currently just returns a randomass string. It should render the uploader.html
    template, just like the demo endpoint.

    :return:
    '''
    return "Successful Upload!"


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    '''
    Home endpoint. Supports both GET and POST. If a GET request is encountered (someone asked for
    the webpage), the index.html page is rendered. If a POST request with 4 files are sent, the
    files are validated, and then saved to the directory.

    :return:
    '''
    if request.method == 'GET':
        return render_template('index.html')

    elif request.method == 'POST':
        # check of the post request has the file  part
        if 't1' not in request.files or 't2' not in request.files or \
                't2flair' not in request.files or 't1ce' not in request.files:
            flash('No file part!')
            return redirect(request.url)

        flash(request.files.keys())
        # get all the files
        t1_file = request.files['t1']
        t2_file = request.files['t2']
        t2flair_file = request.files['t2flair']
        t1ce_file = request.files['t1ce']

        if t1_file.filename == '' or \
                t2_file.filename == '' or \
                t1ce_file.filename == '' or \
                t2flair_file.filename == '':
            flash('No selected file!')
            return redirect(request.url)

        if (t1_file and check_extension(t1_file.filename)) and \
                t2_file and check_extension(t2_file.filename) and \
                t1ce_file and check_extension(t1ce_file.filename) and \
                t2flair_file and check_extension(t2flair_file.filename):
            # clean directories before uploading
            logger.debug('Cleaning data directory..')
            clean_jpeg_dir()
            logger.debug('Data directory empty')
            t1_filename = secure_filename(t1_file.filename)
            t1_file.save(os.path.join(app.config['UPLOAD_FOLDER'], t1_filename))

            t2_filename = secure_filename(t2_file.filename)
            t2_file.save(os.path.join(app.config['UPLOAD_FOLDER'], t2_filename))

            t1ce_filename = secure_filename(t1ce_file.filename)
            t1ce_file.save(os.path.join(app.config['UPLOAD_FOLDER'], t1ce_filename))

            t2flair_filename = secure_filename(t2flair_file.filename)
            t2flair_file.save(os.path.join(app.config['UPLOAD_FOLDER'], t2flair_filename))

            return redirect(url_for('uploaded_file'))

    return render_template('index.html')

if __name__ == '__main__':
    logger.debug('Cleaning data directory..')
    clean_jpeg_dir()
    logger.debug('Data directory empty')
    import platform

    # to make the code portable even on cedar,you need to add conditions here
    node_name = platform.node()
    if node_name == 'XPS15':
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', port=80)