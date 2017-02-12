from flask import Flask
from flask import render_template,request,Response,make_response
from play_cloudant import play_cloudant
app = Flask(__name__)
play = play_cloudant()


@app.route('/', methods=['GET', 'POST'])
def welcome():
    return render_template('welcome.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        data = file.read().decode("utf-8")
        success = play.upload(data,file.filename)
        return render_template('upload.html', get=False,success=success)
    else:
        return render_template('upload.html', get=True)


@app.route('/download', methods=['GET', 'POST'])
def download():
    if request.method == 'GET':
        return render_template('download.html')
    else:
        filename = request.form['filename']
        version_number = request.form['version_number']
        data = play.download(filename,version_number)
        print(data)
        if data:
            response = make_response(data)
            response.headers["Content-Disposition"] = "attachment; filename="+filename
            return response
        else:
            return render_template('download.html',msg="Please enter the existing file name")


@app.route('/list')
def list_files():
    files = play.list()
    return render_template('list.html', list=files)


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'GET':
        return render_template('delete.html')
    else:
        filename = request.form['filename']
        version_number = request.form['version_number']
        data = play.delete(filename,version_number)
        if data:
            return render_template('delete.html',msg="File is deleted from cloudant")
        else:
            return render_template('delete.html',msg="Please enter the existing file name to delete it")

if __name__ == '__main__':
    app.run()