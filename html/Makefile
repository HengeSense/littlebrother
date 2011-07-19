CSSOBJS=css/goggles.user.min.css \
	css/ui/common.min.css \
	css/ui/index.min.css \
	css/ui/profile.min.css \
	css/ui/pack.min.css \
	
	
JSOBJS=js/ui/common.min.js \
	js/ui/index.min.js \
	js/ui/profile.min.js \
	js/ui/pack.min.js \
	js/ui/query.min.js \
	js/jquery.littlebrother.proto.min.js \
	

default: $(CSSOBJS) $(JSOBJS)

%.min.css : %.css
	yui-compressor $< > $@
	
%.min.js : %.js
	yui-compressor $< > $@

clean:
	rm -f $(CSSOBJS)
	rm -f $(JSOBJS)
	