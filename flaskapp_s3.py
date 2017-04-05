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
            return render_template('s3/welcome.html')
        else:
            return render_template('login.html',msg="Please check the user name and password")


@app.route('/s3/uploads', methods=['GET', 'POST'])
def uploads3():
    if request.method == 'POST':
        f = request.files['file']
        success = play_s3.upload(f)
        return render_template('s3/uploads.html', get=False,success=success)
    else:
        return render_template('s3/uploads.html', get=True)


@app.route('/s3/lists')
def list_filess3():
    files = play_s3.list()
    return render_template('s3/lists.html', list=files)


@app.route('/s3/deletes', methods=['GET', 'POST'])
def deletes3():
    if request.method == 'GET':
        return render_template('s3/deletes.html')
    else:
        filename = request.form['filename']
        data = play_s3.delete(filename)
        if data:
            return render_template('s3/deletes.html',msg="File is deleted from s3")
        else:
            return render_template('s3deletes.html',msg="Please enter the existing file name to delete it")


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))
