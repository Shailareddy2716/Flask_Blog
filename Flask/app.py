import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

# Initialize the Flask application
app = Flask(__name__)

# Secret key for flash messages
app.config['SECRET_KEY'] = 'DV_230'


# Function to establish a database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Return rows as dictionary-like objects
    return conn


# Function to retrieve a post by ID
def get_post(post_id):
    with get_db_connection() as conn:
        post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    if post is None:
        abort(404)  # Return a 404 error if the post is not found
    return post


@app.route('/')
def index():
    # Fetch all posts
    with get_db_connection() as conn:
        posts = conn.execute('SELECT * FROM posts ORDER BY created DESC').fetchall()
    # Render the homepage and pass the posts to the template
    return render_template('index.html', posts=posts)


@app.route('/<int:post_id>')
def post(post_id):
    # Retrieve and render a specific post
    post = get_post(post_id)
    return render_template('post.html', post=post)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content'].strip()

        if not title:
            flash('Title is required!', 'danger')
        elif not content:
            flash('Content is required!', 'danger')
        else:
            # Insert new post into the database
            with get_db_connection() as conn:
                conn.execute(
                    'INSERT INTO posts (title, content, created) VALUES (?, ?, datetime("now"))',
                    (title, content),
                )
            flash('Post created successfully!', 'success')
            return redirect(url_for('index'))

    # Render the form for creating a new post
    return render_template('create.html')


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    # Get the post to be edited by its ID
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content'].strip()

        if not title:
            flash('Title is required!', 'danger')
        elif not content:
            flash('Content is required!', 'danger')
        else:
            # Update the post in the database
            with get_db_connection() as conn:
                conn.execute(
                    'UPDATE posts SET title = ?, content = ? WHERE id = ?',
                    (title, content, id),
                )
            flash('Post updated successfully!', 'success')
            return redirect(url_for('index'))

    # Render the edit form
    return render_template('edit.html', post=post)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    with get_db_connection() as conn:
        conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    flash(f'"{post["title"]}" was successfully deleted!', 'success')
    return redirect(url_for('index'))


# Run the app
if __name__ == '__main__':
    app.run(debug=True)