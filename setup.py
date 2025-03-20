"""Setup script for the django-socialize app."""

import os

from setuptools import setup, Command

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


class DjangoTestCommand(Command):
    """Custom command to run Django tests."""

    description = 'Run Django tests.'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run the test suite."""
        import django
        from django.conf import settings
        from django.core.management import execute_from_command_line

        # Configure Django settings for testing
        settings.configure(
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'socialize',
            ],
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
        )
        django.setup()

        # Run tests
        execute_from_command_line(['manage.py', 'test', 'tests'])


setup(
    name='django-socialize',
    version='0.6.0',
    packages=['socialize'],
    include_package_data=True,
    license='LGPLv3 License',
    description='A Django app to create social networks with social authentication.',
    long_description=README,
    long_description_content_type='text/x-rst',
    url='https://williamlagos.github.io/',
    author='William Oliveira de Lagos',
    author_email='william.lagos@icloud.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    cmdclass={'test': DjangoTestCommand},
)
