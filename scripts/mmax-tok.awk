# Tokenise texts according to the (not very sophisticated) default tokenisation
# scheme in MMAX.
#
# Christian Hardmeier
# 13 March 2018

BEGIN {
	FS = " ";
}

match($0, /<seg [^>]+>(.*)<\/seg>/, m) {
	n = split(m[1], a, / /);
	out = "";
	for(i = 1; i <= n; i++) {
		w = a[i];
		prefix = suffix = "";
		while(match(w, /^([("])(.*)$/, m)) {
			prefix = append(prefix, m[1])
			w = m[2];
		}
		while(match(w, /^(.*)([,;")!?:.])$/, m)) {
			suffix = append(m[2], suffix);
			w = m[1];
		}
		out = append(out, append(prefix, append(w, suffix)));
	}
	print out;
}

function append(a, b) {
	if(a == "" || b == "")
		return a b;
	else
		return a " " b;
}
