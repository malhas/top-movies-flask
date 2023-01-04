from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

TMDB_APIKEY = "1ec959d25bbe0be78fb50ec275c11845"
TMDB_SEARCH_URL = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_APIKEY}&query="

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer)
    description = db.Column(db.String(500))
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(250))
    img_url = db.Column(db.String(250))

    def __init__(self, title, year, description, img_url):
        self.title = title
        self.year = year
        self.description = description
        self.img_url = img_url

        super(Movie, self).__init__()


class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField("Your Review", validators=[DataRequired()])
    submit = SubmitField("Done")


class AddMovie(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    add = SubmitField("Add Movie")


@app.route("/")
def home():
    db.create_all()
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)


@app.route("/delete", methods=["GET", "POST"])
def delete():
    movie_id = request.args.get("id")
    print(movie_id)
    movie = Movie.query.get(movie_id)
    print(movie)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddMovie()
    if form.validate_on_submit():
        response = requests.get(TMDB_SEARCH_URL + form.title.data).json()
        return render_template("select.html", movies=response["results"])
    return render_template("add.html", form=form)


@app.route("/add_details", methods=["GET", "POST"])
def add_details():
    movie_id = request.args.get("id")
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_APIKEY}").json()
    movie = Movie(
        title=response["original_title"],
        year=int(response["release_date"].split("-")[0]),
        description=response["overview"],
        img_url=f"https://image.tmdb.org/t/p/w500/{response['poster_path']}")
    db.session.add(movie)
    db.session.commit()
    return redirect(url_for("edit", id=movie.id))


if __name__ == '__main__':
    app.run(debug=True)
