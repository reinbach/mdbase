======
mdbase
======

ZeroMQ MajorDomo Titanic Patterm implementation

Objectives
==========

What would it take to make use of this pattern as the central base for a service orientated architecture.

Various services able to auto register with the base and clients able to call these various services.

Logging and system status added to the base to get some insight into what is happening and how things are performing.

Aiming to support mainly Python 3.x with the hope of being backward compatible to Python 2.6


Installation
============

Basic installation;

      git clone https://github.com/reinbach/mdbase.git
      cd mdbase/
      python setup.py install


To run the tests;

      python run_tests.py


To check coverage of tests;

      pip install coverage
      coverage run --source=mdbase run_tests.py
      coverage report
