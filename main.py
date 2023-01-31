from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,IntegerField,FloatField
from wtforms.validators import DataRequired,InputRequired,Length
import requests


API_MOVIE = "MOVIE DB FREE API"
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///some website'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'YOUR SECRET KEY'
Bootstrap(app)
db = SQLAlchemy(app)

class AddForm(FlaskForm):
    title = StringField(label='Movie Title',validators=[InputRequired(),Length(min=2,max=16)])
    submit = SubmitField(label='Submit')



with app.app_context():
    class Movie(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(250), unique=True, nullable=False)
        year = db.Column(db.String(250), nullable=False)
        description = db.Column(db.String(250), nullable=False)
        rating = db.Column(db.String(250), nullable=False)
        ranking = db.Column(db.String(250), nullable=False)
        review = db.Column(db.String(250), nullable=False)
        img_url = db.Column(db.String(250), nullable=False)

        def __repr__(self):
            return '<books %r>' % self.title,self.year,self.rating,self.description,self.ranking,self.review,self.img_url

with app.app_context():
    new_movie = Movie(
        title="Phone Booth",
        year=2002,
        description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
        rating=7.3,
        ranking=10,
        review="My favourite character was the caller.",
        img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    )
    # db.drop_all()
    # db.create_all()
    # db.session.add(new_movie)
    # db.session.commit()

class Form(FlaskForm):
    rating = FloatField(label='Rating',validators=[InputRequired()])
    review = StringField(label='Review',validators=[InputRequired(),Length(min=3,max=16)])
    submit = SubmitField(label='Done')


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range (len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html",movies=all_movies)

@app.route("/edit",methods=["POST","GET"])
def edit():
    form = Form()
    id = request.args.get('id')
    print(f"edit_movie = {id}")
    movie_to_update = Movie.query.get(id)
    if form.validate_on_submit():
        new_rating = form.rating.data
        new_review = form.review.data
        movie_to_update.rating = new_rating
        movie_to_update.review = new_review
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html",form=form)

@app.route("/delete",methods=["POST","GET"])
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))
@app.route("/add",methods=["POST","GET"])
def add():
    add_form= AddForm()
    query = {
            "api_key":API_MOVIE,
            "query": add_form.title.data
        }
    if add_form.validate_on_submit():
        response = requests.get(url="https://api.themoviedb.org/3/search/movie",params=query)
        movie_data = response.json()['results']
        print(movie_data)
        return render_template('select.html',moviess=movie_data)
    return render_template('add.html',form=add_form)
@app.route("/find")
def find():
        selected_movie_id = request.args.get("id")
        print(f"selected_movie:{selected_movie_id}")
        if selected_movie_id != None:
            parameters2 = {
                "api_key": API_MOVIE
                }
            response2 = requests.get(url=f"https://api.themoviedb.org/3/movie/{selected_movie_id}", params=parameters2).json()
            movie_title = response2['title']
            img_url = f"https://image.tmdb.org/t/p/original/{response2['poster_path']}"
            year = response2['release_date']
            description = response2['overview']
            with app.app_context():
                new_movie3 = Movie(
                    id=selected_movie_id,
                    title=movie_title,
                    year=year,
                    description=description,
                    rating=0,
                    ranking=1,
                    review="None",
                    img_url=img_url
                )
                db.session.add(new_movie3)
                db.session.commit()
        return redirect(url_for('edit',id=selected_movie_id))
if __name__ == '__main__':
    app.run(debug=True)
