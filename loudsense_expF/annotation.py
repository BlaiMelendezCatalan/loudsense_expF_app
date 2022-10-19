import os
import numpy as np
import sqlite3
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from loudsense_expF.auth import login_required
from loudsense_expF.db import get_db
from loudsense_expF.constants import AUDIBLE, BARELY, INAUDIBLE, RANDOM_SEED


np.random.seed(RANDOM_SEED)

bp = Blueprint('annotation', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    db.row_factory = sqlite3.Row

    user_id = session.get('user_id')
    row = db.execute(
        f'SELECT u.group_id FROM user u where u.id = {user_id}'
    ).fetchone()
    group_id = row['group_id']

    media_dir = os.path.dirname(__file__)
    media_dir = os.path.join(media_dir, 'static', 'media')
    all_wav_names = os.listdir(media_dir)
    np.random.shuffle(all_wav_names)

    rows = db.execute(
        'SELECT a.wav_name FROM annotation a JOIN user u ON a.annotator_id '
        '= u.id ORDER BY created DESC'
    ).fetchall()
    db.close()

    done_wav_names = []
    for row in rows:
        done_wav_names.append(row['wav_name'])

    wav_name = None
    for name in all_wav_names:
        if group_id != 'all' and f'___group_{group_id}' not in name:
            continue
        if name not in done_wav_names:
            wav_name = name
            break

    if wav_name is None:
        return render_template('annotation/done.html')

    return render_template('annotation/index.html', wav_name=wav_name)

@bp.route('/<string:wav_name>/<string:class_>/update_db')
@login_required
def update_db(wav_name, class_):
    db = get_db()
    user_id = session.get('user_id')
    
    query = ("INSERT INTO annotation (annotator_id, wav_name, class) "
             f"VALUES ({user_id}, '{wav_name}', '{class_}')")
    try:
        db.execute(query)
        db.commit()
    except db.IntegrityError:
        error = f"You already annotated this audio."
    else:
        return redirect(url_for('annotation.index'))

    flash(error)

    return redirect(url_for('annotation.index'))