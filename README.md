# z01

Code powering 01z.co

## Development

This is a standard Django app, install and run with:

```sh
# setup venv
python3 -m venv .venv
source .venv/bin/activate

# setup env variables
cp .envrc.example .envrc
source .envrc

# install dependencies
pip install -r requirements.txt

# run dev server
python manage.py runserver
```

## License

MIT
