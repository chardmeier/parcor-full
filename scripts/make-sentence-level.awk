# Create an MMAX sentence level by reading a tokenised input file and generating
# a sentence markable for each input line.
#
# Christian Hardmeier
# 13 March 2018

BEGIN {
	FS = " ";
	print "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>";
	print "<!DOCTYPE markables SYSTEM \"markables.dtd\">";
	print "<markables xmlns=\"www.eml.org/NameSpaces/sentence\">";
	orderid = 0;
	word = 1;
}

{
	if(NF == 1)
		span = sprintf("word_%d", word);
	else
		span = sprintf("word_%d..word_%d", word, word + NF - 1);

	printf "<markable mmax_level=\"sentence\" orderid=\"%d\" id=\"markable_%d\" span=\"%s\" />\n", orderid, orderid, span;
	word += NF;
	orderid++;
}

END {
	print "</markables>";
}
