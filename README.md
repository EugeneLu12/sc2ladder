# sc2ladder
website for StarCraft II ladders


## Development

```
poetry shell
poetry install
python manage.py migrate
python manage.py update_db
python manage.py createsuperuser // optional
python manage.py runserver
```

Run `poetry run task style` to format files before making a PR.

## Deploying

When changing dependencies run `poetry run task requirements` since heroku doesn't
support pyproject.toml files yet.

In general heroku should automatically deploy from master, but if for some
reason that bugs out or you want to deploy a change that's not on GitHub's
master branch then: for first time setup you'll have to install the Heroku
CLI and do `heroku git:remote -a sc2ladder`. After that simply run
`git push heroku master`.


## Debugging

Useful commands: `heroku logs --tail`, `heroku ps`, and `heroku logs --dyno [dyno from heroku ps] --tail
`
