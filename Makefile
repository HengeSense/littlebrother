PYTHON=`which python`
PYTHONPATH=$$PYTHONPATH:./littlebrother/
PEP8_ARGS=--ignore W191,W291,E501,E201,E202,E203,E251
SRC= \
	littlebrother/ident/metaphone_ru.py \
	littlebrother/ident/names.py \
	littlebrother/ident/orgs.py \
	\
	littlebrother/rank/distance.py \
	littlebrother/rank/weight.py \
	littlebrother/rank/average.py \
	littlebrother/rank/median.py \
	\
	littlebrother/html/lxmlp.py \
	\
	littlebrother/db/db.py \
	littlebrother/db/sqldb.py \
	\
	littlebrother/api/utils.py \
	littlebrother/api/jsonfront.py \
	littlebrother/api/query.py \
	\
	littlebrother/crawling/gather.py \
	\
	littlebrother/web/application.py \

PEP8_SRC=${SRC} \
	littlebrother/ident/config.py \
	littlebrother/db/config.py \
	littlebrother/db/prepare.py \
	littlebrother/crawling/config.py \
	littlebrother/api/config.py \
	littlebrother/web/wsgi_fapws3.py \
	littlebrother/web/config.py \


default: all
all: pep8 tests

tests:
	@( for FILE in ${SRC}; do \
		echo "Running tests for $$FILE"; \
		PYTHONPATH=${PYTHONPATH} ${PYTHON} $$FILE; \
	done; )

pep8:
	@( for FILE in ${PEP8_SRC}; do \
		echo "Running pep8 check for $$FILE"; \
		pep8 ${PEP8_ARGS} $$FILE; \
	done; )

clean:
	@( for FILE in `find . -name *.pyc`; do \
		rm -f $$FILE; \
	done; )
