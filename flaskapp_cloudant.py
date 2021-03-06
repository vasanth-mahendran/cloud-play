import os

from flask import Flask
from flask import render_template,request, make_response
from application.modules.play_cloudant import play_cloudant

from application.modules.play_s3 import play_s3

app = Flask(__name__)
play = play_cloudant()
play_s3 = play_s3()


@app.route('/', methods=['GET', 'POST'])
def welcome():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        user_name = request.form['username']
        password = request.form['password']
        success = play_s3.login(user_name,password)
        print(success)
        if success:
            return render_template('cloudant/welcome.html')
        else:
            return render_template('login.html',msg="Please check the user name and password")


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        description = request.form['description']
        data = file.read()
        size = file.tell()
        print(size)
        if size>=650000:
            return render_template('cloudant/upload.html', get=False, error="file size exceeds")
        else:
            success = play.upload(data,file.filename,file.content_type,description)
            return render_template('cloudant/upload.html', get=False,success=success)
    else:
        return render_template('cloudant/upload.html', get=True)


@app.route('/download', methods=['GET', 'POST'])
def download():
    if request.method == 'GET':
        filename = request.args.get('filename')
        version_number = request.args.get('version_number')
        print(filename,version_number)
        if(filename and version_number):
            data = play.download(filename, version_number)

            if data:
                response = make_response(data['contents'])
                response.headers['Content-Type'] = data['content_type']
                response.headers["Content-Disposition"] = "attachment; filename=" + filename
                return response
            else:
                return render_template('cloudant/download.html', msg="Please enter the existing file name")
        else:
            return render_template('cloudant/download.html')
    else:
        filename = request.form['filename']
        version_number = request.form['version_number']
        data = play.download(filename,version_number)
        print(data)
        #if(data['content_type']=='image/jpeg'):
            #content = json.loads(data['contents'])
        if data:
            response = make_response(data['contents'])
            response.headers['Content-Type'] = data['content_type']
            response.headers["Content-Disposition"] = "attachment; filename="+filename
            return response
        else:
            return render_template('cloudant/download.html',msg="Please enter the existing file name")


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('cloudant/search.html')
    else:
        keyword = request.form['keyword']
        data = play.search(keyword)
        print(data)
        return render_template('cloudant/search.html', found=data)


@app.route('/list')
def list_files():
    files = play.list()
    return render_template('cloudant/list.html', list=files)


@app.route('/local',methods=['GET', 'POST'])
def list_local_files():
    if request.method == 'GET':
        return render_template('cloudant/view.html')
    else:
        dirpath = request.form['dirpath']
        files = play.localfiles(dirpath)
        print(files)
        return render_template('cloudant/view.html',files=files)


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'GET':
        return render_template('cloudant/delete.html')
    else:
        filename = request.form['filename']
        version_number = request.form['version_number']
        data = play.delete(filename,version_number)
        if data:
            return render_template('cloudant/delete.html',msg="File is deleted from cloudant")
        else:
            return render_template('cloudant/delete.html',msg="Please enter the existing file name to delete it")


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
