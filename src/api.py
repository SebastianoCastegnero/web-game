from flask import redirect, request
from flask import session, Markup
from flask import Flask, render_template
from flask import flash
from cosmos_storage import CosmosStorage
from src.database.in_memory_storage import InMemoryStorage
from src.database.storage_item import StorageItem
from src.database.blob_storage import BlobStorage

database = InMemoryStorage()
blobStorage = BlobStorage()
cosmosdb = CosmosStorage.from_env()

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

@app.route('/upload_word', methods=['POST'])
def upload_word():
    secret_word = request.form['secretWord']
    image_file = request.files['image']
    image_bytes = image_file.stream.read()
    image_content_type = image_file.content_type
    imageurl = blobStorage.upload_image(image_bytes=image_bytes, content_type=image_content_type)
    cosmosdb.add(StorageItem(image_url=imageurl, secret_word=secret_word))
    flash("Uploaded word " + repr(secret_word))
    return redirect('/')


@app.route('/game', methods=['GET'])
def game():  
    if 'secret_item_id' in session:
        if cosmosdb.has_index(session['secret_item_id']):
            return render_template('game.html')
        flash("No words uploaded yet! Please upload at least one word to start guessing")
        return redirect("/")
    if cosmosdb.is_empty():
        flash("No words uploaded yet! Please upload at least one word to start guessing")
        return redirect("/")
    word_id = cosmosdb.get_random_item_index()
    session['secret_item_id'] = word_id
    return render_template('game.html')


@app.route('/make_a_guess', methods=['POST'])
def make_a_guess():
    if 'secret_item_id' not in session:  # this should never happen
        flash("You can't guess words without starting the game first!")
        return redirect('/game')

    word_id = session['secret_item_id']
    secret_word = cosmosdb.get_item_by_index(word_id)

    if request.form['guessed_word'] == secret_word.secret_word:
        flash(Markup("You guessed right! Good job! The secret word was <b>%s</b>" % secret_word.secret_word))
        del session['secret_item_id']
        return redirect('/')

    flash("You didn't guess right! Try again!")
    return redirect('/game')

@app.route('/image', methods=['GET'])
def get_image():
    item_id = request.args['item_id']
    item = cosmosdb.get_item_by_index(item_id)
    return redirect(item.image_url, code=302)
