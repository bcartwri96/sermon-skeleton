from src.models.models import Sermon_Series
import flask as fl
from src.forms.index import AddSermonSeries
from src.models.db import session

def main():
    fm = AddSermonSeries()
    if fl.request.method == 'GET':
        return fl.render_template('settings.html', form=fm)

    else:
        # process form
        if fm.validate_on_submit():
            nm = fl.request.form['name']
            res = Sermon_Series(name=nm)

            # commit
            try:
                session.add(res)
                session.commit()
                fl.flash("Success")
            except IOError:
                fl.flash("Failed to submit to database")

            return fl.redirect(fl.url_for('settings'))
