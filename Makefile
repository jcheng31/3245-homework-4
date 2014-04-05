index:
	python src/index.py -i patsnap-corpus -d run/dictionary.txt

search:
	python src/search.py -d run/dictionary.txt -p run/postings.txt \
		-q queries/q1.xml -o run/output.txt

search2:
	python src/search.py -d run/dictionary.txt -p run/postings.txt \
		-q queries/q2.xml -o run/output.txt

search3:
	python src/search.py -d run/dictionary.txt -p run/postings.txt \
		-q queries/q3.xml -o run/output.txt

matric_no := a0082877m-a0080860h-a0092104u

submission:
	rm -rf $(matric_no) $(matric_no).zip
	mkdir $(matric_no)
	rsync -r src/ $(matric_no)/ --exclude=*.pyc
	zip -r $(matric_no).zip $(matric_no)
	rm -rf $(matric_no)
