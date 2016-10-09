from flask import Flask, render_template, url_for, request, redirect
from flask_pymongo import PyMongo
from redis import Redis
from flask_sse import sse
import pygal
import json
from pygal.style import LightSolarizedStyle
from bson import json_util
import codecs
from urllib2 import urlopen  # python 2 syntax
#from urllib.request import urlopen # python 3 syntax


app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'flmdb'
app.config['MONGO_URI'] = 'mongodb://addmin:addmin@ds013414.mlab.com:13414/flmdb'

mongo = PyMongo(app)
redis = Redis(host='redis', port=6379)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/moviesa', methods=['POST'])
def moviesa():
    redis.lpush('moviestore', request.form['title'])
    return redirect(url_for('find'))

@app.route('/finder')
def find(state='IA', city='Ames'):
    """
Date must be in YYYYMMDD
"""
    api_key = '1759214509c0c83c'
    date=redis.rpop('moviestore')
    url = 'http://api.wunderground.com/api/{key}/history_{date}/q/{state}/{city}.json'
    new_url = url.format(key=api_key,
                         date=date,
                         state=state,
                         city=city)
    result = urlopen(new_url).read().decode('utf-8')
    parsed = json.loads(result)
    history = parsed['history']['observations']
    imp_temps = [float(i['tempi']) for i in history]
    times = ['%s:%s' % (i['utcdate']['hour'], i['utcdate']['min']) for i in history]
    user = mongo.db.users
    user.insert({'name' : date, 'xs' : times, 'ys' : imp_temps})
    return redirect(url_for('draw', date=date))
    
@app.route('/day/<date>')
def draw(date):
        title = 'Temps for Ames, IA on %s' % (date)
        bar_chart = pygal.Bar(width=1200, height=600,
                              explicit_size=True, title=title,
                              style=LightSolarizedStyle,
                              disable_xml_declaration=True)
        user = mongo.db.users
        moviee = user.find_one({'name' : date})
        bar_chart.x_labels = moviee['xs']
        bar_chart.add('Temps in F', moviee['ys'])
        return render_template('index.html',
                               bar_chart=bar_chart,
                               date=request.args.get('date'))

if __name__ == '__main__':
        app.run(host='0.0.0.0', debug=True)
