=========
Socialize
=========

Socialize is a Django app to create social networks with social authentication.

Quick start
-----------

1. Add "socialize" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'socialize',
    )

2. Include the socialize URLconf in your project urls.py like this::

    url(r'^socialize/', include('socialize.urls')),

3. Run `python manage.py syncdb` to create the socialize models.

4. Visit http://127.0.0.1:8000/ to view a sample with social authentications