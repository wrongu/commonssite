# run migrators
from commonssite.migrators import *
from os.path import expanduser 

if __name__ == '__main__':
	HvacMigrator.migrate(expanduser('~/code/hvac/log-snapshots/0206.csv'))
