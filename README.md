Last changes:
--------------

* Implemented interactive mode: if mothur-wrapper was invoked without a batch script, mothur is invoked in interactive mode just as the usual mothur works. All the settings filled from the console or the config file are passed to mothur directly.
* Mothur-wrapper is implemented in python: for interactive mode you'll need to install the `pexpect` module: 
	```pip install pexpect```

This is one utility that I had need since the first time I started playing with mothur. It allows to restore the last configuration of parameters used in the last mothur session in case mothur breaks down. It parses the log file produced by mothur by default in search of every parameter passed in the commands and stores in a .mothur-wrapper.ini file stored in the same dir where you execute it.

If you are using a mothur batch script you can use placeholders inside the script with the $parameter like $fasta and the wrapper will fill in the values stored in the ini file. Allows you to break down one mothur batch script into smaller ones (useful, for example, in the case you use some command like dist.seqs or filter.seqs) and resume the work invoking the batch script as argument to mothur-wrapper in the next step after the execution.

