from app import create_app, db

app = create_app('development')

with app.app_context():
    from app.analytics.api import calculate_attrition_rates
    from app.models import AttritionAlert

    results = calculate_attrition_rates('department')
    # Convert results list to dict keyed by group with latest period's attrition
    latest = {}
    for r in results:
        grp = r['group']
        latest[grp] = r['attrition_rate']

    # Sort groups by attrition desc
    sorted_groups = sorted(latest.items(), key=lambda x: x[1], reverse=True)

    created = 0
    for grp, rate in sorted_groups[:3]:
        # create alert regardless of threshold
        alert = AttritionAlert(alert_type='attrition_hotspot', group_name=grp, value=rate)
        db.session.add(alert)
        created += 1
    db.session.commit()
    print('Created demo alerts:', created)
    print('Total alerts now:', AttritionAlert.query.count())
