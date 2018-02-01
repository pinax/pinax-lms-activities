![](http://pinaxproject.com/pinax-design/patches/pinax-lms-activities.svg)

# Pinax LMS Activities

[![](https://img.shields.io/pypi/v/pinax-lms-activities.svg)](https://pypi.python.org/pypi/pinax-lms-activities/)

[![CircleCi](https://img.shields.io/circleci/project/github/pinax/pinax-lms-activities.svg)](https://circleci.com/gh/pinax/pinax-lms-activities)
[![Codecov](https://img.shields.io/codecov/c/github/pinax/pinax-lms-activities.svg)](https://codecov.io/gh/pinax/pinax-lms-activities)
[![](https://img.shields.io/github/contributors/pinax/pinax-lms-activities.svg)](https://github.com/pinax/pinax-lms-activities/graphs/contributors)
[![](https://img.shields.io/github/issues-pr/pinax/pinax-lms-activities.svg)](https://github.com/pinax/pinax-lms-activities/pulls)
[![](https://img.shields.io/github/issues-pr-closed/pinax/pinax-lms-activities.svg)](https://github.com/pinax/pinax-lms-activities/pulls?q=is%3Apr+is%3Aclosed)

[![](http://slack.pinaxproject.com/badge.svg)](http://slack.pinaxproject.com/)
[![](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)


## Table of Contents

* [About Pinax](#about-pinax)
* [Overview](#overview)
  * [Supported Django and Python versions](#supported-django-and-python-versions)
* [Documentation](#documentation)
  * [Installation](#installation)
* [Change Log](#change-log)
* [Contribute](#contribute)
* [Code of Conduct](#code-of-conduct)
* [Connect with Pinax](#connect-with-pinax)
* [License](#license)


## About Pinax

Pinax is an open-source platform built on the Django Web Framework. It is an
ecosystem of reusable Django apps, themes, and starter project templates. This
collection can be found at http://pinaxproject.com.


## pinax-lms-activities

`pinax-lms-activities` provides a framework and base learning activities for
Pinax LMS. It is a framework for building interactive activities like quizzes,
etc. to use in courses for example.


### Overview

At the moment, pinax-lms-activities provides both a collection of abstract base
classes for building learning activities and a core app for managing retrieval
of activities and per user activity state.

The abstract activities subclass each other. For example a TwoChoiceQuiz is a
type of quiz where a question is asked and the student has to pick between one
of two possible answers provided (the correct answer and a distractor).
TwoChoiceQuiz is abstract because it doesn't provide the actual questions, a
subclass needs to do that. TwoChoiceQuiz itself subclasses Quiz which
subclasses Activity. Activity is the top-level base class for all activities.

When developing a concrete activity there are a number of different facets to
consider:

* (a) what’s the question / answer mechanic (e.g. two-choice quiz)
* (b) what’s the algorithm for choosing what to ask / generating questions
  (random? based on what user has seen? or what they found difficult? or based
  on their "level"?)
* (c) what are the exit criteria for a session ending (do they just get asked
  10 questions, is it based on X correct in a row or is it completely open
  ended)
* (d) what data needs to be stored about a session for scoring / analytics
  and/or feeding back into (b)

Currently the abstract base activities are really just addressing (a) and the
individual concrete activities have to do (b) and (c). There really isn’t
much (d) at all yet.

_But we want to get there on all these facets._


#### Supported Django and Python versions

Django \ Python | 2.7 | 3.4 | 3.5 | 3.6
--------------- | --- | --- | --- | ---
1.11 |  *  |  *  |  *  |  *
2.0  |     |  *  |  *  |  *


## Documentation

### Installation

To install pinax-lms-activities:

```shell
    $ pip install pinax-lms-activities
```

Add `pinax.lms-activities` to your `INSTALLED_APPS` setting:

```python
    INSTALLED_APPS = [
        # other apps
        "pinax.lms-activities",
    ]
```

Lastly add `pinax.lms.activities.urls` to your project urlpatterns:

```python
    urlpatterns = [
        # other urls
        url(r"^activities/", include("pinax.lms.activities.urls")),
    ]
```

## Change Log

### 0.18.0

### 0.1

* initial release


## Contribute

For an overview on how contributing to Pinax works read this [blog post](http://blog.pinaxproject.com/2016/02/26/recap-february-pinax-hangout/)
and watch the included video, or read our [How to Contribute](http://pinaxproject.com/pinax/how_to_contribute/) section.
For concrete contribution ideas, please see our
[Ways to Contribute/What We Need Help With](http://pinaxproject.com/pinax/ways_to_contribute/) section.

In case of any questions we recommend you join our [Pinax Slack team](http://slack.pinaxproject.com)
and ping us there instead of creating an issue on GitHub. Creating issues on GitHub is of course
also valid but we are usually able to help you faster if you ping us in Slack.

We also highly recommend reading our blog post on [Open Source and Self-Care](http://blog.pinaxproject.com/2016/01/19/open-source-and-self-care/).


## Code of Conduct

In order to foster a kind, inclusive, and harassment-free community, the Pinax Project
has a [code of conduct](http://pinaxproject.com/pinax/code_of_conduct/).
We ask you to treat everyone as a smart human programmer that shares an interest in Python, Django, and Pinax with you.


## Connect with Pinax

For updates and news regarding the Pinax Project, please follow us on Twitter [@pinaxproject](https://twitter.com/pinaxproject)
and check out our [Pinax Project blog](http://blog.pinaxproject.com).


## License

Copyright (c) 2012-2018 James Tauber and contributors under the [MIT license](https://opensource.org/licenses/MIT).

