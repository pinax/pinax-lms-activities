from setuptools import find_packages, setup

VERSION = "0.18.0"
LONG_DESCRIPTION = """
.. image:: http://pinaxproject.com/pinax-design/patches/pinax-lms-activities.svg
    :target: https://pypi.python.org/pypi/pinax-lms-activities/
===================
Pinax Announcements
===================
.. image:: https://img.shields.io/pypi/v/pinax-lms-activities.svg
    :target: https://pypi.python.org/pypi/pinax-lms-activities/
\
.. image:: https://img.shields.io/circleci/project/github/pinax/pinax-lms-activities.svg
    :target: https://circleci.com/gh/pinax/pinax-lms-activities
.. image:: https://img.shields.io/codecov/c/github/pinax/pinax-lms-activities.svg
    :target: https://codecov.io/gh/pinax/pinax-lms-activities
.. image:: https://img.shields.io/github/contributors/pinax/pinax-lms-activities.svg
    :target: https://github.com/pinax/pinax-lms-activities/graphs/contributors
.. image:: https://img.shields.io/github/issues-pr/pinax/pinax-lms-activities.svg
    :target: https://github.com/pinax/pinax-lms-activities/pulls
.. image:: https://img.shields.io/github/issues-pr-closed/pinax/pinax-lms-activities.svg
    :target: https://github.com/pinax/pinax-lms-activities/pulls?q=is%3Apr+is%3Aclosed
\
.. image:: http://slack.pinaxproject.com/badge.svg
    :target: http://slack.pinaxproject.com/
.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://opensource.org/licenses/MIT/
\
``pinax-lms-activities`` is a well tested, documented, and proven solution
for any site wanting announcements for it's users.
Announcements have title and content, with options for filtering their display:
* ``site_wide`` - True or False
* ``members_only`` - True or False
* ``publish_start`` - date/time or none
* ``publish_end`` - date/time or none
``pinax-announcements`` has three options for dismissing an announcement:
* ``DISMISSAL_NO`` - always visible
* ``DISMISSAL_SESSION`` - dismiss for the session
* ``DISMISSAL_PERMANENT`` - dismiss forever
Supported Django and Python Versions
------------------------------------
+-----------------+-----+-----+-----+-----+
| Django / Python | 2.7 | 3.4 | 3.5 | 3.6 |
+=================+=====+=====+=====+=====+
|  1.11           |  *  |  *  |  *  |  *  |
+-----------------+-----+-----+-----+-----+
|  2.0            |     |  *  |  *  |  *  |
+-----------------+-----+-----+-----+-----+
"""


setup(
    author="Pinax Developers",
    author_email="team@pinaxproject.com",
    description="framework and base learning activities for Pinax LMS",
    name="pinax-lms-activities",
    long_description=LONG_DESCRIPTION,
    version=VERSION,
    url="https://github.com/pinax/pinax-lms-activities/",
    license="MIT",
    packages=find_packages(),
    package_data={
        "pinax.lms.activities": [
            "templates/pinax/lms/activities/*"
        ]
    },
    test_suite="runtests.runtests",
    install_requires=[
        "django>=1.11",
        "django-appconf>=1.0.1",
        "pinax-eventlog>=1.1.1",
        "jsonfield>=1.0.3"
    ],
    tests_require=[
        "django-test-plus>=1.0.22",
        "pinax-templates>=1.0.4",
        "mock>=2.0.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False
)
