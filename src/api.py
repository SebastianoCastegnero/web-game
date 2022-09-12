from flask import redirect, request
from flask import session, Markup
from flask import Flask, render_template
from flask import flash
from src.in_memory_storage import InMemoryStorage

database = InMemoryStorage()


app = Flask(__name__)
# This key guarantees security of the sessions, and must be kept secret.
# When creating a serious service, you should never commit a secret key in plain text
# to the codebase. We will cut the corner here just to make sessions work,
# but you should know this is insecure.
app.secret_key = "f3cfe9ed8fae309f02079dbf"  # random string

APP_VERSION = '0.0.1'


@app.context_processor
def inject_app_version():
    return dict(app_version=APP_VERSION)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/guess')
def guess():
    return render_template('guess.html')


@app.route('/upload_image')
def upload_image():
    return render_template('upload_image.html')


@app.route('/words')
def words():
    return render_template('words.html')


# browsers send POST request when submitting a form
@app.route('/upload_word', methods=['POST'])
def upload_word():
    # request.form is a special variable in Flask that will contain the form data
    # note the "name" attribute of the <input> we have in HTML
    secret_word = request.form['secretWord']
    database.add_word(secret_word)
    flash("Uploaded word " + repr(secret_word))
    return redirect('/')  # redirect back to the main page


@app.route('/game', methods=['GET'])
def game():
    if 'secret_word_id' in session:
        if database.get_word_by_index(session['secret_word_id']) is not None:
            return render_template('game.html')

    word_id = database.get_random_word_index()
    if word_id is None:
        flash("No words uploaded yet! Please upload at least one word to start guessing")
        return redirect("/")

    session['secret_word_id'] = word_id

    return render_template('game.html')


@app.route('/make_a_guess', methods=['POST'])
def make_a_guess():
    if 'secret_word_id' not in session:  # this should never happen
        flash("You can't guess words without starting the game first!")
        return redirect('/game')

    secret_word = database.get_word_by_index(session['secret_word_id'])

    if request.form['guessed_word'] == secret_word:
        flash(Markup("You guessed right! Good job! The secret word was <b>%s</b>" % secret_word))
        del session['secret_word_id']
        return redirect('/')

    flash("You didn't guess right! Try again!")
    return redirect('/game')