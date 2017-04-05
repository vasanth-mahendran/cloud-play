import csv
import os
import time
from io import StringIO
from random import randint

import redis
from flask import render_template,request
from sqlalchemy.sql import or_, and_

import application
from application.models import Feeds, RainFeeds
from application.modules.play_s3 import play_s3

application.app.debug = True
redis_store = redis.StrictRedis(host='myredissec.rzx2zy.ng.0001.usw2.cache.amazonaws.com', port=6379, db=0)
application.db.create_all()
application.db.session.commit()
s3 = play_s3()


@application.app.route('/', methods=['GET', 'POST'])
@application.app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('rds/welcome.html')


@application.app.route('/import', methods=['GET', 'POST'])
def import_data():
    try:
        start_time = time.time()
        import_d = s3.download('UNPrecip.csv')
        f = StringIO(import_d)
        reader = csv.reader(f)
        application.db.session.bulk_save_objects([
                                         RainFeeds(row[0], row[1], row[2], row[3], row[4], row[5])
                                         for row in reader
                                    ])
        count_10k = RainFeeds.query.filter(or_(RainFeeds.L > 10000, RainFeeds.M > 10000, RainFeeds.P > 10000)).count()
        count_rem_canada = RainFeeds.query.filter(RainFeeds.A != 'CANADA').count()
        print(count_rem_canada)
        print(count_10k)
        RainFeeds.query.filter_by(A='CANADA').delete()
        RainFeeds.query.filter(RainFeeds.L > 10000).update(dict(L=-1))
        RainFeeds.query.filter(RainFeeds.M > 10000).update(dict(M=-1))
        RainFeeds.query.filter(RainFeeds.P > 10000).update(dict(P=-1))
        application.db.session.commit()
        application.db.session.close()
        time_taken = round(((time.time() - start_time) / 60), 2)
    except:
        print('-------error-------')
        application.db.session.rollback()
        raise
    stat = {'import': True, 'sql': True, 'time': time_taken, 'delete_rem': count_rem_canada, 'update_no': int(count_10k)}
    return render_template('rds/statistics.html', stat=stat)


@application.app.route('/query', methods=['GET', 'POST'])
def query():
    time_taken = 0
    try:
        if request.method == 'GET':
            return render_template('rds/query.html')
        else:
            start_time = time.time()
            country = request.form['country']
            where1 = request.form['where1']
            where2 = request.form['where2']
            key1, op1, value1 = where1.split(',', 3)
            key2, op2, value2 = where2.split(',', 3)
            list_and = []
            if op1 == 'E':
                list_and.append(getattr(RainFeeds, key1) == value1)
            elif op1 == 'L':
                list_and.append(getattr(RainFeeds, key1) < value1)
            if op2 == 'E':
                list_and.append(getattr(RainFeeds, key2) == value2)
            elif op2 == 'L':
                list_and.append(getattr(RainFeeds, key2) < value2)
            for x in range(1, 251):
                data = RainFeeds.query.filter(and_(or_(RainFeeds.A == country, RainFeeds.B == country), *list_and)).all()
            print(data)
            application.db.session.close()
            time_taken = round(((time.time() - start_time) / 60), 2)
    except:
        print('-------error-------')
        application.db.session.rollback()
        raise
    return render_template('rds/statistics.html',stat={'sql': True, 'query': True, 'count_no': len(data), 'time': time_taken})


@application.app.route('/match', methods=['GET', 'POST'])
def match():
    time_taken = 0
    try:
        start_time = time.time()
        all = RainFeeds.query.filter(RainFeeds.A==RainFeeds.B).limit(5).all()
        time_taken = round(((time.time() - start_time) / 60), 2)
        application.db.session.close()
    except:
        print('-------error-------')
        application.db.session.rollback()
        raise
    return render_template('rds/statistics.html',stat={'match': True, 'sql': True, 'time': time_taken, 'matches': all})


@application.app.route('/random', methods=['GET', 'POST'])
def random():
    time_taken = 0
    try:
        start_time = time.time()
        for x in range(1, 5001):
            randomi = randint(1, 5000)
            data = Feeds.query.filter_by(ID=randomi).first()
            redis_store.set(randomi,data)
        time_taken = round(((time.time() - start_time) / 60), 2)
        application.db.session.close()
    except:
        print('-------error-------')
        application.db.session.rollback()
        raise
    return render_template('rds/statistics.html',stat={'random': True, 'sql': True, 'time': time_taken})


@application.app.route('/specific', methods=['GET', 'POST'])
def specific():
    time_taken = 0
    try:
        start_time = time.time()
        for x in range(1, 5001):
            data = Feeds.query.filter_by(ID=x).first()
            redis_store.set(x, data)
        time_taken = round(((time.time() - start_time) / 60), 2)
        application.db.session.close()
    except:
        print('-------error-------')
        application.db.session.rollback()
        raise
    return render_template('rds/statistics.html',stat={'random': True, 'sql': True, 'time': time_taken})


@application.app.route('/specific/cache', methods=['GET', 'POST'])
def specific_cache():
    time_taken = 0
    try:
        start_time = time.time()
        for x in range(1, 5001):
            data = redis_store.get(x)
            if data is None:
                data = Feeds.query.filter_by(ID=x).first()
                redis_store.set(x, data)
        time_taken = round(((time.time() - start_time) / 60), 2)
        application.db.session.close()
    except:
        print('-------error-------')
        application.db.session.rollback()
        raise
    return render_template('rds/statistics.html',stat={'random': True, 'sql': True, 'time': time_taken})


@application.app.route('/random/cache', methods=['GET', 'POST'])
def random_cache():
    time_taken = 0
    try:
        start_time = time.time()
        for x in range(1, 5001):
            randomi = randint(1, 5000)
            data = redis_store.get(randomi)
            if data is None:
                data = Feeds.query.filter_by(ID=randomi).first()
                redis_store.set(randomi, data)
        time_taken = round(((time.time() - start_time) / 60), 2)
        application.db.session.close()
    except:
        print('-------error-------')
        application.db.session.rollback()
        raise
    return render_template('rds/statistics.html',stat={'random': True, 'sql': True, 'time': time_taken})

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    application.app.run(host='0.0.0.0', port=int(port))