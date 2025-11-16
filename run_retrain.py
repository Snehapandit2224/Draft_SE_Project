from app import create_app

app = create_app('development')
with app.app_context():
    from app.ml_models.training import retrain_model
    retrain_model()
    print('RETRAIN_DONE')
