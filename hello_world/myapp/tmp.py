from flask import Flask, render_template, request, redirect, url_for
from models import db, Driver, Team, Circuit, Race, RaceDriver
from datetime import date, datetime, time
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///f1races.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('list_races'))


@app.route('/races')
def list_races():
    stmt = text("SELECT * FROM races")
    result = db.session.execute(stmt)
    
    races = []
    for row in result:
        row_data = dict(row._mapping)
        # Convert start and end time to datetime objects manually
        row_data['start_time'] = datetime.fromisoformat(row_data['start_time'])
        row_data['end_time'] = datetime.fromisoformat(row_data['end_time'])
        races.append(Race(**row_data))

    return render_template('races.html', races=races)

@app.route('/races/add', methods=['GET', 'POST'])
def add_race():
    if request.method == 'POST':
        print(">>> FORM DATA:", request.form)  # Add this line
        race = Race(
            title=request.form['title'],
            start_time=datetime.fromisoformat(request.form['start_time']),
            end_time=datetime.fromisoformat(request.form['end_time']),
            team_id=int(request.form['team']),
            circuit_id=int(request.form['circuit'])
        )

        db.session.add(race)
        db.session.commit()

        driver_link = RaceDriver(
            race_id=race.race_id,
            driver_id=int(request.form['driver'])
        )
        db.session.add(driver_link)
        db.session.commit()

        return redirect(url_for('list_races'))

    teams = Team.query.all()
    circuits = Circuit.query.all()
    drivers = Driver.query.all()
    return render_template('add_race.html', teams=teams, circuits=circuits, drivers=drivers)

@app.route('/races/delete/<int:id>')
def delete_race(id):
    race = Race.query.get(id)
    if race:
        db.session.delete(race)
        db.session.commit()
    return redirect(url_for('list_races'))

@app.route('/races/edit/<int:id>', methods=['GET', 'POST'])
def edit_race(id):
    race = Race.query.get_or_404(id)
    driver_link = RaceDriver.query.filter_by(race_id=id).first()

    if request.method == 'POST':
        race.title = request.form['title']
        race.start_time = datetime.fromisoformat(request.form['start_time'])
        race.end_time = datetime.fromisoformat(request.form['end_time'])
        race.team_id = int(request.form['team'])
        race.circuit_id = int(request.form['circuit'])

        if driver_link:
            driver_link.driver_id = int(request.form['driver'])
        else:
            new_driver = RaceDriver(
                race_id=race.race_id,
                driver_id=int(request.form['driver'])
            )
            db.session.add(new_driver)

        db.session.commit()
        return redirect(url_for('list_races'))

    teams = Team.query.all()
    circuits = Circuit.query.all()
    drivers = Driver.query.all()
    return render_template('edit_race.html', race=race, driver_link=driver_link,
                           teams=teams, circuits=circuits, drivers=drivers)

@app.route('/report', methods=['GET', 'POST'])
def report():
    teams     = Team.query.all()
    circuits  = Circuit.query.all()
    results   = []
    stats     = {}
    error     = None
    no_results = False

    if request.method == 'POST':
        try:
            # parse form inputs
            team_id    = int(request.form['team'])
            circuit_id = int(request.form['circuit'])
            d1 = date.fromisoformat(request.form['start'])
            d2 = date.fromisoformat(request.form['end'])
            start_date = datetime.combine(d1, time.min)
            end_date   = datetime.combine(d2, time.max)

            # fetch filtered races
            stmt = text("""
                SELECT * FROM races
                 WHERE team_id    = :team_id
                   AND circuit_id = :circuit_id
                   AND start_time >= :start_date
                   AND end_time   <= :end_date
            """)
            rows = db.session.execute(stmt, {
                'team_id':    team_id,
                'circuit_id': circuit_id,
                'start_date': start_date,
                'end_date':   end_date
            })

            # build objects + compute stats
            total_duration = 0
            parsed = []
            for row in rows:
                data = dict(row._mapping)
                data['start_time'] = datetime.fromisoformat(data['start_time'])
                data['end_time']   = datetime.fromisoformat(data['end_time'])
                race = Race(**data)
                parsed.append(race)
                total_duration += (race.end_time - race.start_time).total_seconds() / 60

            if not parsed:
                no_results = True
            else:
                count = len(parsed)
                stats = {
                    'num_races':    count,
                    'avg_duration': round(total_duration / count, 2)
                }
                results = parsed

        except Exception as e:
            error = str(e)

    return render_template('report.html',
                           teams=teams,
                           circuits=circuits,
                           results=results,
                           stats=stats,
                           error=error,
                           no_results=no_results)
