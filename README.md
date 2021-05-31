
Create and manage tournament fixtures (knockout).

The project uses django framework for backend and admin panel and Jquery Brackets to display the fixture.

## Setup

#### Create virtual env
```shell
python -m virtualenv env
```
```shell
.\env\Scripts\activate

or

.\env\Scripts\activate.ps1
```

#### Install packages from requirements.txt
```
(env) pip install -r requirement.txt
```

#### Setup database
```
(env)  python manage.py makemigrations
```

```
(env)  python manage.py migrate
```

#### Create superuser to access admin panel
```
(env)  python manage.py createsuperuser
```

### Run application

```
(env)  python manage.py runserver
```