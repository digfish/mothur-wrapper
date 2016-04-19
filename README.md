This is one utility that I had need since the first time I started playing with [mothur](http://www.mothur.org). It allows to restore the last configuration of parameters used in the last mothur session in case mothur breaks down. It parses the log file written by mothur by default in search of every parameter passed in the commands and stores in a .mothur-wrapper.ini file stored in the same dir where you execute it.

If you are using a mothur batch script you can use placeholders inside the script with the $parameter like $fasta and the wrapper will fill in the values stored in the ini file. Allows you to break down one mothur batch script into smaller ones (useful, for example, in the case you use some command like `dist.seqs` or `filter.seqs`) and resume the work invoking the next batch script in the series as argument to mothur-wrapper in the next step after the execution.
Or just not having to remember the complete path of the file used as the reference for alignment, you can put drop a `.mothur-wrapper.ini` in your home directory with just these lines:
```
[config]
reference=/home/myusername/mothur_db/silva.bacteria.fasta
taxonomy=/home/myusername/mothur_db/silva.bacteria.ncbi.tax
```

and if you use the following mothur script:
```
classify.seqs(fasta=current, count=current,reference=$reference,taxonomy=$taxonomy,processors=$num_cpus)
```
it will replace the placeholders `$taxonomy`,`$reference` and `$num_cpus` for:
```
classify.seqs(fasta=current, count=current,reference=/home/myusername/mothur_db/silva.bacteria.fasta,taxonomy=/home/myusername/mothur_db/silva.bacteria.ncbi.tax,processors=4)
```

the `$num_cpus` is filled by default with the number of CPU cores you have and you don't need to explicit assign a value to it.

As I said there are two modes of operation, exactly like the bare mothur binary has:
* Interactive mode: `mothur-wrapper.py`
* Batch mode: `mothur-wrapper.py [your-mothur-batch-script-here]`

In interative mode, you can pass arguments in the command line like in the example:
`mothur-wrapper.py --fasta example1.fasta --reference reference.fasta` and these argument values will override the ones you have in your `.mothur-wrapper.ini` .

Just a piece of notice: the `mothur-wrapper.py` will write a new `.mothur-wrapper.ini`in the same directory where you execute it. It will always first try to read the file with the same name in your home root dir if you have one there. 

In order to properly work, the `mothur` binary must already reside in a directory that it's already setted in your `$PATH`.

Last changes:
-------

* Implemented interactive mode: if mothur-wrapper was invoked without a batch script, mothur is invoked in interactive mode just as the usual mothur works. All the settings filled from the console or the config file are passed to mothur directly.
* Mothur-wrapper is implemented in python: for interactive mode you'll need to install the `pexpect` module: 
	```pip install pexpect```
