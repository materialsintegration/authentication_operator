#!/bin/sh
# Zabbixマニュアルビルドスクリプト for Jenkins

export PATH=/usr/local/bin:$PATH
directories=(workflow suggest)
pdffilenames=(WorkflowUserManual.pdf SuggetAdminManual.pdf)
targetdirs=(suggest_v1/user suggest_v1/admin)
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
    pushd _build/latex
    echo "uplatex --shell-escape --interaction=nonstopmode UserManual.tex" >> $logfile 2>&1
    uplatex --shell-escape --interaction=nonstopmode UserManual.tex >> $logfile 2>&1
    echo "-------------------- 2nd compile dvi file -----------" >> $logfile
    echo "uplatex --shell-escape --interaction=nonstopmode UserManual.tex" >> $logfile 2>&1
    uplatex --shell-escape --interaction=nonstopmode UserManual.tex >> $logfile 2>&1
    echo "-------------------- convert pdf file -----------" >> $logfile
    echo "dvipdfmx UserManual.dvi" >> $logfile 2>&1
    dvipdfmx UserManual.dvi >> $logfile 2>&1
    if [ -e "UserManual.pdf" ]; then
        # とりあえず成果物確認用ページへコピーする。
        # 本来はちゃんとした公開ページへコピーすること。
        echo "copy UserManual to ${pdffilenames[$count]}" >> $logfile
        #cp phasefield.pdf /var/www/html/docroot/$dir/phasefield.pdf
        #let count++
    fi
    popd
    echo "-------------------- generate web pages ---------" >> $logfile
    echo "make html" >> $logfile 2>&1
    make html >> $logfile 2>&1
    pushd _build
    echo "copy html directory from here to ${targetdirs[$count]}" >> $logfile
    cp -rp html /var/lib/mi-docroot/static/${targetdirs[$count]}/html >> $logfile
    popd
    let count++
    cd ../
done

# copy to public space for documents

