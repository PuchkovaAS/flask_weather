import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, flash
import sys
import requests

app = Flask(__name__)
appid = '5493ef258d707a2785561ade2a80bac3'
url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=Metric&appid=' + appid
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////12/SVN_ALL/Weather App/Weather App/task/web/weather.db'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'fdgdfgdfggf786hfg6hfg6h7f'
db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.name


def get_weather(city_name, city_id):
    res = requests.get(url.format(city_name)).json()
    if res['cod'] == '404':
        return None

    tz = datetime.timezone(datetime.timedelta(seconds=res['timezone']))
    # time = int(datetime.datetime.now(tz).timestamp())
    time = datetime.datetime.now(tz).time().hour
    if 6 < time < 12:
        current_time = 'evening-morning'
    elif 12 <= time <= 20:
        current_time = 'day'
    else:
        current_time = 'night'

    dict_with_weather_info = {
        'city': city_name,
        'temp': int(res['main']['temp']),
        'current_time': current_time,
        'state': res['weather'][0]['main'],
        'id': city_id,
    }
    # print(dict_with_weather_info)
    # tz = datetime.timezone(datetime.timedelta(seconds=10800))
    # dt = datetime.datetime.now()
    # print(tz.utcoffset(dt))
    # # print(datetime.timezone(10800, name=None))
    # print(datetime.datetime.utcnow())
    # print(datetime.datetime.now(tz))
    # print(int(datetime.datetime.now(tz).timestamp()))
    return dict_with_weather_info


@app.route('/delete/<city_id>', methods=['GET', 'POST'])
def delete(city_id):
    city = City.query.filter_by(id=city_id).first()
    db.session.delete(city)
    db.session.commit()
    return redirect('/')


@app.route('/', methods=['POST', 'GET'])
def add_city():
    citys = []
    if request.method == 'POST':
        city_name = request.form['city_name']

        if city_name is None or city_name == '':
            flash("The city doesn't exist!")
            return redirect('/')

        all_city_base = [city.name for city in City.query.all()]

        if city_name not in all_city_base:
            weather = get_weather(city_name, 1)
            if weather is None:
                flash("The city doesn't exist!")
                return redirect('/')
            new_city = City(name=city_name)
            db.session.add(new_city)
            db.session.commit()


        else:
            flash("The city has already been added to the list!")
            return redirect('/')
    for city_name, city_id in [[city.name, city.id] for city in City.query.all()]:
                citys.append(get_weather(city_name, city_id))

    return render_template('index.html', citys=citys)


# @app.route('/')
# def index():
#     return render_template('index.html')


# don't change the following way to run flask:
if __name__ == '__main__':
    db.create_all()
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
