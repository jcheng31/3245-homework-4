index:
	python src/index.py -i patsnap-corpus -d run/dictionary.txt \
		-p run/postings.txt

search:
	python src/search.py -d run/dictionary.txt -p run/postings.txt \
		-q queries/q1.xml -o run/results.txt

search2:
	python src/search.py -d run/dictionary.txt -p run/postings.txt \
		-q queries/q2.xml -o run/results.txt

search3:
	python src/search.py -d run/dictionary.txt -p run/postings.txt \
		-q queries/q3.xml -o run/results.txt

search5:
	python src/search.py -d run/dictionary.txt -p run/postings.txt \
		-q queries/q5.xml -o run/results.txt

learn:
	python src/learn.py -d run/dictionary.txt

matric_no := a0082877m-a0080860h-a0092104u

submission:
	rm -rf $(matric_no) $(matric_no).zip
	mkdir $(matric_no)
	rsync -r src/ $(matric_no)/ --exclude=*.pyc
	zip -r $(matric_no).zip $(matric_no)
	rm -rf $(matric_no)

mark_fast:
	time python src/search.py -d run/dictionary.txt -p run/postings.txt \
		-q benchmark/q1.xml -o run/br1.txt
	time python src/search.py -d run/dictionary.txt -p run/postings.txt \
		-q benchmark/q1.xml -o run/br2.txt
	time python src/search.py -d run/dictionary.txt -p run/postings.txt \
		-q benchmark/q1.xml -o run/br3.txt
	time python src/search.py -d run/dictionary.txt -p run/postings.txt \
		-q benchmark/q1.xml -o run/br4.txt
	echo Query 1 > run/benchmark.txt
	benchmark/eval.pl run/br1.txt benchmark/q1-qrels.txt >> run/benchmark.txt
	echo Query 2 >> run/benchmark.txt
	benchmark/eval.pl run/br2.txt benchmark/q2-qrels.txt >> run/benchmark.txt
	echo Query 3 >> run/benchmark.txt
	benchmark/eval.pl run/br3.txt benchmark/q3-qrels.txt >> run/benchmark.txt
	echo Query 4 >> run/benchmark.txt
	benchmark/eval.pl run/br4.txt benchmark/q4-qrels.txt >> run/benchmark.txt
	cat run/benchmark.txt

mark:
	time python src/index.py -i patsnap-corpus -d run/dictionary.txt \
		-p run/postings.txt
	time python src/search.py -d run/dictionary.txt -p run/postings.txt \
		-q benchmark/q1.xml -o run/br1.txt
	time python src/search.py -d run/dictionary.txt -p run/postings.txt \
		-q benchmark/q1.xml -o run/br2.txt
	time python src/search.py -d run/dictionary.txt -p run/postings.txt \
		-q benchmark/q1.xml -o run/br3.txt
	time python src/search.py -d run/dictionary.txt -p run/postings.txt \
		-q benchmark/q1.xml -o run/br4.txt
	echo Query 1 > run/benchmark.txt
	benchmark/eval.pl run/br1.txt benchmark/q1-qrels.txt >> run/benchmark.txt
	echo Query 2 >> run/benchmark.txt
	benchmark/eval.pl run/br2.txt benchmark/q2-qrels.txt >> run/benchmark.txt
	echo Query 3 >> run/benchmark.txt
	benchmark/eval.pl run/br3.txt benchmark/q3-qrels.txt >> run/benchmark.txt
	echo Query 4 >> run/benchmark.txt
	benchmark/eval.pl run/br4.txt benchmark/q4-qrels.txt >> run/benchmark.txt
	cat run/benchmark.txt
