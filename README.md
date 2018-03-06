This command-line tool reads django settings, then connects to configured postgresql server as superuser, and tries to create the database and user with password, according to the django settings.

## Installation

```
pip install pginit
```

## Usage

You can either set `DJANGO_SETTINGS_MODULE` environment variable, or specify settings module path in the first command-line argument.

```bash
pginit path.to.settings
```
