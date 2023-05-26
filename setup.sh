#!/bin/bash

# create directories
WORKDIR=$(pwd)
mkdir fbrowse_data
mkdir private
mkdir tmp
cd bin
mkdir blast

# check conda
CONDADIR=$(dirname "$(which conda)")
CONDADIR=$(dirname "$CONDADIR")
CONDA="$CONDADIR/etc/profile.d/conda.sh"
if ! [ -f "$CONDA" ]; then
		echo "Conda not found. Install anaconda and run setup.sh again."
		exit
fi
echo "Found Conda installation in $CONDADIR"

# Create conda environment
source $CONDA
conda config --add channels bioconda
conda config --add channels conda-forge
conda create -y -n cgcms-gapmind
conda activate cgcms-gapmind

# Install sqlite, hmmer and diamond
conda install -c anaconda sqlite
conda install -y -c bioconda hmmer diamond
ln -s $(which hmmsearch) hmmsearch
ln -s $(which hmmfetch) hmmfetch
ln -s $(which diamond) diamond

# Install NCBI BLAST (not BLAST+ !)
conda install -y blast-legacy=2.2.19
cd blast
ln -s $(which formatdb) formatdb
ln -s $(which blastall) blastall
ln -s $(which fastacmd) fastacmd
cd ../..

# Install Perl libraries
conda install -y -c bioconda perl-findbin perl-dbi perl-getopt-long perl-list-util perl-dbd-sqlite perl-lwp-simple perl-xml-libxml perl-json perl-cgi

# Retrieve reference data
cd tmp
mkdir path.aa
cd path.aa
wget https://papers.genomics.lbl.gov/tmp/path.aa/curated.faa
wget https://papers.genomics.lbl.gov/tmp/path.aa/curated.db
wget https://papers.genomics.lbl.gov/tmp/path.aa/steps.db
cd ..
mkdir path.carbon
cd path.carbon
wget https://papers.genomics.lbl.gov/tmp/path.carbon/curated.faa
wget https://papers.genomics.lbl.gov/tmp/path.carbon/curated.db
wget https://papers.genomics.lbl.gov/tmp/path.carbon/steps.db
cd ../..

# Prepare reference data
perl bin/extractHmms.pl tmp/path.aa/steps.db tmp/path.aa
perl bin/extractHmms.pl tmp/path.carbon/steps.db tmp/path.carbon
bin/diamond makedb --in tmp/path.aa/curated.faa --db tmp/path.aa/curated.faa.udb
bin/diamond makedb --in tmp/path.carbon/curated.faa --db tmp/path.carbon/curated.faa.udb

conda deactivate

