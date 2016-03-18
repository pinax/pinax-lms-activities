Pinax LMS Activities
========================
.. image:: http://slack.pinaxproject.com/badge.svg
   :target: http://slack.pinaxproject.com/

.. image:: https://img.shields.io/travis/pinax/pinax-lms-activities.svg
    :target: https://travis-ci.org/pinax/pinax-lms-activities

.. image:: https://img.shields.io/coveralls/pinax/pinax-lms.svg
    :target: https://coveralls.io/r/pinax/pinax-lms-activities

.. image:: https://img.shields.io/pypi/dm/pinax-lms.svg
    :target:  https://pypi.python.org/pypi/pinax-lms-activities/

.. image:: https://img.shields.io/pypi/v/pinax-lms.svg
    :target:  https://pypi.python.org/pypi/pinax-lms-activities/

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target:  https://pypi.python.org/pypi/pinax-lms-activities/


Pinax
------

Pinax is an open-source platform built on the Django Web Framework. It is an ecosystem of reusable Django apps, themes, and starter project templates.
This collection can be found at http://pinaxproject.com.


pinax-lms-activities
---------------------

``pinax-lms-activities`` provides a framework and base learning activities for Pinax LMS. It is a framework for building interactive activities like quizzes, etc. to use in courses for example.


Running the Tests
------------------------------------

::

    $ pip install detox
    $ detox


Documentation
--------------

The ``pinax-lms-activities`` documentation is currently under construction. If you would like to help us write documentation, please join our Slack team and let us know! The Pinax documentation is available at http://pinaxproject.com/pinax/.

Contribute
----------------

See this blog post http://blog.pinaxproject.com/2016/02/26/recap-february-pinax-hangout/ including a video, or our How to Contribute (http://pinaxproject.com/pinax/how_to_contribute/) section for an overview on how contributing to Pinax works. For concrete contribution ideas, please see our Ways to Contribute/What We Need Help With (http://pinaxproject.com/pinax/ways_to_contribute/) section.

In case of any questions we recommend you join our Pinax Slack team (http://slack.pinaxproject.com) and ping us there instead of creating an issue on GitHub. Creating issues on GitHub is of course also valid but we are usually able to help you faster if you ping us in Slack.

We also highly recommend reading our Open Source and Self-Care blog post (http://blog.pinaxproject.com/2016/01/19/open-source-and-self-care/).


Code of Conduct
-----------------

In order to foster a kind, inclusive, and harassment-free community, the Pinax Project has a code of conduct, which can be found here  http://pinaxproject.com/pinax/code_of_conduct/. We ask you to treat everyone as a smart human programmer that shares an interest in Python, Django, and Pinax with you.


Pinax Project Blog and Twitter
-------------------------------

For updates and news regarding the Pinax Project, please follow us on Twitter at @pinaxproject and check out our blog http://blog.pinaxproject.com.


Overview
--------

At the moment, pinax-lms-activities provides both a collection of abstract base classes for building learning activities and a core app for managing retrieval of activities and per user activity state.

The abstract activities subclass each other. For example a TwoChoiceQuiz is a type of quiz where a question is asked and the student has to pick between one of two possible answers provided (the correct answer and a distractor). TwoChoiceQuiz is abstract because it doesn't provide the actual questions, a subclass needs to do that. TwoChoiceQuiz itself subclasses Quiz which subclasses Activity. Activity is the top-level base class for all activities.

When developing a concrete activity there are a number of different facets to consider:

(a) what’s the question / answer mechanic (e.g. two-choice quiz)
(b) what’s the algorithm for choosing what to ask / generating questions (random? based on what user has seen? or what they found difficult? or based on their "level"?)
(c) what are the exit criteria for a session ending (do they just get asked 10 questions, is it based on X correct in a row or is it completely open ended)
(d) what data needs to be stored about a session for scoring / analytics and/or feeding back into (b)

Currently the abstract base activities are really just addressing (a) and the individual concrete activities have to do (b) and (c). There really isn’t much (d) at all yet.

But we want to get there on all these facets.
