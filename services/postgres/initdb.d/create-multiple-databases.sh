#!/bin/bash

set -e
set -u


function create_users_and_databases() {
	local database=$1
	local user=$1
	local password=$2
	local admin_user=$3
	echo "Creating user and database '$database'"
	psql -v ON_ERROR_STOP=0 --username "$admin_user" <<-EOSQL
	    CREATE USER $user;
	    CREATE DATABASE $database;
		ALTER USER $user WITH PASSWORD '$password';
	    GRANT ALL PRIVILEGES ON DATABASE $database TO $user;
EOSQL
}

echo "POSGRES USER '$POSTGRES_USER'"

if [ -n "$POSTGRES_DATABASES" ]; then
	echo "Multiple database creation requested: $POSTGRES_DATABASES"
	databases=(${POSTGRES_DATABASES//,/ })
	passwords=(${POSTGRES_PASSWORDS//,/ })

	for i in "${!databases[@]}"; do
		create_users_and_databases ${databases[i]} ${passwords[i]} $POSTGRES_USER
	done
	echo "Multiple databases created"
fi