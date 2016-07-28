#!/usr/bin/env python
import os
import unittest

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from okubir import app, db


migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

@manager.command
def test():
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
	manager.run()
