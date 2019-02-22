from src.models.models import Sermon_Series, Authors
import flask as fl
from src.forms.index import Settings
from src.models.db import session

def main():
    fm = Settings()
    if fl.request.method == 'GET':
        return fl.render_template('settings.html', form=fm)

    else:
        # process form
        if fm.validate_on_submit():
            ss_name = fl.request.form['add_ss_name']
            auth_name = fl.request.form['add_author_name']
            organisation_name = fl.request.form['org_name']

            # any with same name?
            if ss_name != None or ss_name == '':
                same_name = Sermon_Series.query.filter(Sermon_Series.name == ss_name).all()

                if len(same_name) == 0:
                    res = Sermon_Series(name=ss_name)
                    session.add(res)
                else:
                    fl.flash("Sermon series name already taken!")

            if auth_name != None or auth_name == '':
                same_name = Authors.query.filter(Authors.name == auth_name).all()

                if len(same_name) == 0:
                    res = Authors(name=auth_name)
                    session.add(res)
                else:
                    fl.flash("Author name already taken!")

            # commit
            try:
                session.commit()
                session.flush()
                fl.flash("Success")
            except IOError:
                fl.flash("Failed to submit to database")

            return fl.redirect(fl.url_for('settings'))
        else:
            fl.flash("Failed")
            return fl.redirect(fl.url_for('settings'))
