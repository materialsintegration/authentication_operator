#!/bin/sh
# Zabbixマニュアルビルドスクリプト for Jenkins

export PATH=/usr/local/bin:$PATH
directories=(./)
pdffilenames=(MIAuthLibraryManual.pdf)
targetdirs=()
count=0
logfile="`pwd`/build.log"
if [ -e $logfile ]; then
    rm $logfile
fi
touch $logfile
for dir in ${directories[@]}
do
    cd $dir
    make clean
    # make reStracturedText to PDF via tex documents
    echo "-------------------- build latex files ----------" >> $logfile
    echo "make latex" >> $logfile 2>&1
    make latex >> $logfile 2>&1
    echo "-------------------- 1st compile dvi file -----------" >> $logfile
    pushd build/latex
    echo "platex --shell-escape --interaction=nonstopmode sphinx.tex" >> $logfile 2>&1
    platex --shell-escape --interaction=nonstopmode sphinx.tex >> $logfile 2>&1
    echo "-------------------- 2nd compile dvi file -----------" >> $logfile
    echo "platex --shell-escape --interaction=nonstopmode sphinx.tex" >> $logfile 2>&1
    platex --shell-escape --interaction=nonstopmode sphinx.tex >> $logfile 2>&1
    echo "-------------------- convert pdf file -----------" >> $logfile
    echo "dvipdfmx sphinx.dvi" >> $logfile 2>&1
    dvipdfmx sphinx.dvi >> $logfile 2>&1
    if [ -e "sphinx.pdf" ]; then
        # とりあえず成果物確認用ページへコピーする。
        # 本来はちゃんとした公開ページへコピーすること。
        echo "copy sphinx.pdf to ${pdffilenames[$count]}" >> $logfile
        #cp phasefield.pdf /var/www/html/docroot/$dir/phasefield.pdf
        cp sphinx.pdf ${pdffilenames[$count]}
        #let count++
    fi
    popd
    echo "-------------------- generate web pages ---------" >> $logfile
    echo "make html" >> $logfile 2>&1
    make html >> $logfile 2>&1
    pushd build
    #echo "copy html directory from here to ${targetdirs[$count]}" >> $logfile
    #cp -rp html /var/lib/mi-docroot/static/${targetdirs[$count]}/html >> $logfile
    popd
    let count++
    cd ../
done

# copy to public space for documents

