SOURCE_DIR=source
PAGES= \
${SOURCE_DIR}/Города_России_А.html \
${SOURCE_DIR}/Города_России_Б.html \
${SOURCE_DIR}/Города_России_В.html \
${SOURCE_DIR}/Города_России_Г.html \
${SOURCE_DIR}/Города_России_Д.html \
${SOURCE_DIR}/Города_России_Е.html \
${SOURCE_DIR}/Города_России_Ж.html \
${SOURCE_DIR}/Города_России_З.html \
${SOURCE_DIR}/Города_России_И.html \
${SOURCE_DIR}/Города_России_К.html \
${SOURCE_DIR}/Города_России_Л.html \
${SOURCE_DIR}/Города_России_М.html \
${SOURCE_DIR}/Города_России_Н.html \
${SOURCE_DIR}/Города_России_О.html \
${SOURCE_DIR}/Города_России_П.html \
${SOURCE_DIR}/Города_России_Р.html \
${SOURCE_DIR}/Города_России_С.html \
${SOURCE_DIR}/Города_России_Т.html \
${SOURCE_DIR}/Города_России_У.html \
${SOURCE_DIR}/Города_России_Ф.html \
${SOURCE_DIR}/Города_России_Х.html \
${SOURCE_DIR}/Города_России_Ц.html \
${SOURCE_DIR}/Города_России_Ч.html \
${SOURCE_DIR}/Города_России_Ш.html \
${SOURCE_DIR}/Города_России_Щ.html \
${SOURCE_DIR}/Города_России_Э.html \
${SOURCE_DIR}/Города_России_Ю.html \
${SOURCE_DIR}/Города_России_Я.html \


XSL_TEMPLATE=xsl/extract.xsl
EXTRACTED_CITIES=${SOURCE_DIR}/cities_extracted

DB_DIR=db

default: all
all: download extract makedb

$(PAGES):
	wget \
	"http://ru.wikipedia.org/w/index.php?title=`basename $@ | basename $@ .html`&printable=yes" \
	-O "$@";

mkdirs:
	mkdir -p ${DB_DIR}
	mkdir -p ${SOURCE_DIR}

download: mkdirs $(PAGES)

$(EXTRACTED_CITIES):
	rm -f "${EXTRACTED_CITIES}"
	( for PAGE in ${PAGES}; do \
		tidy -w 9000 -q --show-warnings no -asxml -utf8 "$$PAGE" | \
		xsltproc --encoding "UTF-8" --html --novalid "${XSL_TEMPLATE}" - >> "${EXTRACTED_CITIES}"; \
	done; )
	
extract: $(EXTRACTED_CITIES)

makedb:
	PYTHONPATH=.. python makedb.py "${EXTRACTED_CITIES}"

remake:
	rm -f $(EXTRACTED_CITIES)
	rm -f "${DB_DIR}"/*
	$(MAKE) extract makedb

clean:
	rm -f ${PAGES}
	rm -f "${EXTRACTED_CITIES}"
	rm -f "${DB_DIR}"/*
	rm -f *.pyc
