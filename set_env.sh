#!/bin/bash

# Bunları değiştir:
# "run" dosyasının bulunduğu adresi yaz
PROJECT_DIR="/home/ali/git/okubir/okubir_python"
# mysql username/password'ünü yaz
MYSQL_URL="mysql://root:5@localhost/okubir_python?charset=utf8"

if [ "$1" = "test" ]
then
    export APP_CONFIG="okubir.config.TestConfig"
    export UPLOAD_PATH="$PROJECT_DIR/okubir_python/tests/uploads"
    export DATABASE_URL='sqlite:///:memory:'
    echo "Test config is set"
elif [ "$1" = "dev" ]
then
    export APP_CONFIG="okubir.config.DevelopmentConfig"
    export DATABASE_URL=$MYSQL_URL
    export UPLOAD_PATH="$PROJECT_DIR/okubir/static/uploads"
    echo "Development config is set"
elif [ "$1" = "pro" ]
then
    export APP_CONFIG="okubir.config.ProductionConfig"
    export DATABASE_URL=$MYSQL_URL
    export UPLOAD_PATH="$PROJECT_DIR/okubir/static/uploads"
    echo "Production config is set" 
else
    echo "Wrong argument given"
fi
