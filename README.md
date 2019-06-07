# sc2ladder
website for StarCraft II ladders


## Development

First create a `.env` file with `BLIZZARD_CLIENT_ID` and `BLIZZARD_CLIENT_SECRET`
set to the appropriate values (`pipenv` will automatically load these env variables when you do `pipenv shell`)

```
pipenv shell
python manage.py migrate
python manage.py createsuperuser // optional
python manage.py runserver
```

## Deploying

For first time setup you'll have to install the Heroku CLI and do
`heroku git:remote -a sc2ladder`. After that simply run `git push heroku master`.


## Debugging

Useful commands: `heroku logs --tail`, `heroku ps`, and `heroku logs --dyno [dyno from heroku ps] --tail
`