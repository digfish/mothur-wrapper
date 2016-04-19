This is one utility that I had need since the first time I started playing with [mothur](http://www.mothur.org). It allows to restore the last configuration of parameters used in the last mothur session in case mothur breaks down. It parses the log file written by mothur by default in search of every parameter passed in the commands and stores in a .mothur-wrapper.ini file stored in the same dir where you execute it.

If you are using a mothur batch script you can use placeholders inside the script with a parameter like `$fasta` and the wrapper will fill it with the values stored in the ini file. This way, you can split one big mothur batch script into smaller ones (useful, for example, in the case you use some time-consuming command like `dist.seqs` or `filter.seqs`) and resume the work invoking the next batch script in the series as the argument to mothur-wrapper in the next step after the termination of the last one.
If you just not want to remember the complete path of the file used as the reference for alignment, you can put drop a `.mothur-wrapper.ini` in your home directory with just these lines:
```
[config]
reference=/home/myusername/mothur_db/silva.bacteria.fasta
taxonomy=/home/myusername/mothur_db/silva.bacteria.ncbi.tax
```
and if you use the following mothur batch script:
```
classify.seqs(fasta=current, count=current,reference=$reference,taxonomy=$taxonomy,processors=$num_cpus)
```
it will replace the placeholders `$taxonomy`,`$reference` and `$num_cpus` with the values stored in the .ini in this way:
```
classify.seqs(fasta=current, count=current,reference=/home/myusername/mothur_db/silva.bacteria.fasta,taxonomy=/home/myusername/mothur_db/silva.bacteria.ncbi.tax,processors=4)
```
the `$num_cpus` is filled by default with the number of CPU cores you have so you don't need to explicit assign a value to it.

As I said there are two modes of operation, on the image the `mothur` binary has:
* Interactive mode: just type `mothur-wrapper.py` and voilà
* Batch mode: `mothur-wrapper.py [your-mothur-batch-script-here]`

In either of the modes, you can pass arguments in the command line like in the example:
`mothur-wrapper.py --fasta example1.fasta --reference reference.fasta` and these argument values will override the ones you have in your `.mothur-wrapper.ini` .

Just a piece of warning: the `mothur-wrapper.py` will write a new `.mothur-wrapper.ini`in the same directory where you execute it. It will always try first time to read the .ini file in your home root dir if you have one there. 

In order to properly work, the `mothur` binary must already reside in a directory that it's already setted in your `$PATH`.

Last changes:
-------

* Implemented interactive mode: if mothur-wrapper was invoked without a batch script, mothur is invoked in interactive mode just as the usual mothur works. All the settings filled from the console or the config file are passed to mothur directly.
* Mothur-wrapper is implemented in python: for interactive mode you'll need to install the `pexpect` module: 
	```pip install pexpect```
