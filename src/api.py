from flask import Response
from flask import redirect, request
from flask import session, Markup
from flask import Flask, render_template
from flask import flash
from src.in_memory_storage import InMemoryStorage
from src.in_memory_storage import StorageItem

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

    # - get the word form request.form['secretWord'] aka word space
    secret_word = request.form['secretWord']
    # - upload on the database
    image_file = request.files['image']
    image_bytes = image_file.stream.read()
    image_content_type = image_file.content_type
    database.add(StorageItem(image_bytes=image_bytes, image_content_type=image_content_type, secret_word=secret_word))
    # - write the uploaded word on the website
    flash("Uploaded word " + repr(secret_word))
    # - redirect back to the main page
    return redirect('/')  # redirect back to the main page


@app.route('/game', methods=['GET'])
def game():  
    if 'secret_item_id' in session:
        if database.has_index(session['secret_item_id']):
            return render_template('game.html')
        flash("No words uploaded yet! Please upload at least one word to start guessing")
        return redirect("/")
    if database.is_empty():
        flash("No words uploaded yet! Please upload at least one word to start guessing")
        return redirect("/")
    word_id = database.get_random_item_index()
    session['secret_item_id'] = word_id
    return render_template('game.html')


@app.route('/make_a_guess', methods=['POST'])
def make_a_guess():
    if 'secret_item_id' not in session:  # this should never happen
        flash("You can't guess words without starting the game first!")
        return redirect('/game')

    word_id = session['secret_item_id']
    secret_word = database.get_item_by_index(word_id)

    if request.form['guessed_word'] == secret_word.secret_word:
        flash(Markup("You guessed right! Good job! The secret word was <b>%s</b>" % secret_word.secret_word))
        del session['secret_item_id']
        return redirect('/')

    flash("You didn't guess right! Try again!")
    return redirect('/game')

@app.route('/image', methods=['GET'])
def get_image():
    item_id = int(request.args['item_id'])
    item = database.get_item_by_index(item_id)
    return Response(item.image_bytes, mimetype=item.image_content_type)
