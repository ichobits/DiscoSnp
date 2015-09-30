#!/bin/bash
#*****************************************************************************
#   VCF_Creator: mapping and VCF creation feature in DiscoSnp++
#   Copyright (C) 2015  INRIA
#   Author: C.Riou
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#*****************************************************************************

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
remove=0
PATH_VCF_creator=""
samfile=""
vcffile=""
genome=""
PATH_BWA=""
discoSNPs=""
bwa_threads=""
l=10
n=""
s=0
igv=0
function help {
echo " ##############################"
echo "   Run VCF_creator pipeline     "
echo " ##############################"
echo "Usage : ./run_VCF_creator.sh OPT"
echo -e "##MODE 1: WITHOUT REFERENCE GENOME. Create a vcf file without alignment:" 
echo -e "\t\t./run_VCF_creator.sh -p <disco_file> -o <output> [-l <seed_size>] [-n <mismatch_number>] [-s <bwa_errors_in_seed>] [-w]"
echo -e "##MODE 2: ALIGNING AGAINST A REFERENCE GENOME:"
echo -e "\t\t./run_VCF_creator.sh -G <ref> -p <disco_file> -o <output> [-B <path_bwa>] [-l <seed_size>] [-n <mismatch_number>] [-s <bwa_errors_in_seed>] [-w] "
echo -e "##MODE 3: USING A HOME MADE ALIGNMENT. Samfile from bwa already exists: "
echo -e "\t\t./run_VCF_creator.sh -f <sam_file> -n <mismatch_number> -o <output> [-l <seed_size>] [-s <bwa_errors_in_seed>] [-w]"
echo
echo -e "\t-h: print this message"
echo -e "\t-p: discosnp++ output file (foo_coherent.fa)"
echo -e "\t\t Mandatory unless MODE 3"
echo -e "\t-o: output <file> (VCF format)"
echo -e "\t\t Mandatory"

#echo -e "\t-c : path where VCF_creator is"
echo -e "\t-G: reference genome (Fasta format)"
echo -e "\t\t Optional unless MODE 2: you want the mapping positions of the predicted variants in the VCF file and you do not provide a third-party sam file. E.G.: -B and -G options must be used together"
echo -e "\t-B: bwa path. i.e. /home/me/my_programs/bwa-0.7.12/ (note that bwa must be pre-compiled)"
echo -e "\t\t Optional unless MODE 2 if bwa is not in the binary path. E.G.: -B and -G options must be used together"

echo -e "\t-I : Creation of output specific to IGV (Integrative Genomics Viewer)"
echo -e "\t\t Optional"

echo -e "\t-f: <file>.sam: skip the alignment phases to create the vcf file"
echo -e "\t\t Optional unless MODE 3: you want the mapping positions of the predicted variants in the VCF file without remapping on a reference genome. -f option must be used together with -n"

echo -e "\t-s: bwa option: seed distance"
echo -e "\t\t Optional, default 0"
echo -e "\t-l: bwa option: length of the seed for alignment"
echo -e "\t\t Optional, default 10"
echo -e "\t-n: bwa option: maximal bwa mapping distance"
echo -e "\t\t Optional in MODE 1 AND 2, default 3 - warning, bwa mapping running time highly depends on this parameter."
echo -e "\t\t Mandatory in MODE 3. "

echo -e "\t-t: bwa option: Number of threads (default=unlimited) "
echo -e "\t-w: remove waste tmp files (index files) "
echo -e "\t\t Optional"
}

#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------

while getopts "hB:c:G:p:l:n:s:wIf:o:t:" opt; do
case $opt in
       
       t)
       bwa_threads="-t ",$OPTARG
       ;;
       
	w)
	remove=1
	;;

	h)
	help
	exit 1
	;;

	B)
	echo -e "\t##BWA directory: $OPTARG" >&2
	PATH_BWA=$OPTARG
	;;

	# c)
#        echo -e "\t##VCF_creator directory: $OPTARG" >&2
#        PATH_VCF_creator=$OPTARG
#        ;;

	G)
	echo -e "\t##use genome : $OPTARG" >&2
	genome=$OPTARG
	;;

	p)
	echo -e "\t##use disco SNPS : $OPTARG" >&2
	discoSNPs=$OPTARG
	;;

	s)
	echo -e "\t##use distance with the seed : $OPTARG" >&2
	s=$OPTARG
	;;

	n)
	echo -e "\t##use number of mismatches : $OPTARG" >&2
	n=$OPTARG
	;;

	l)
	echo -e "\t##use seed length : $OPTARG" >&2
	l=$OPTARG
	;;

	f)
	echo -e "\t##use directly samfile : $OPTARG" >&2
	samfile=$OPTARG
	;;
	
	I)
	echo -e "\t##Will create a vcf file for IGV : Sorting VCF by mapping positions and removing unmapped variants"
	igv=1
	;;
		
	o)
	echo -e "\t##output : $OPTARG" >&2
	vcffile=$OPTARG
	;;
	
	\?)
	echo -e "##Invalid option: -$OPTARG" >&2
	exit 1
	;;

	:)
	echo "##Option -$OPTARG requires an argument." >&2
	exit 1
	;;
esac
done

#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
###Tests
if [ -z "$vcffile" ];then
        if [ ! -z "$samfile" ];then
                echo -e "..To skip the alignment phase ..."
                echo -e "\t./run_VCF_creator.sh -f <sam_file> -n <mismatch_number> -o <output> [-l <seed_size>] [-s <bwa_errors_in_seed>] [-w]"
                exit 1
        else
	        help
	        exit 1
	fi
fi

# if [ -z "$PATH_VCF_creator" ];then
#        PATH_VCF_creator=$DIR"/tools"
# fi
PATH_VCF_creator=$DIR"/tools"
if [ ! -e  $PATH_VCF_creator/VCF_creator.py ]; then
	echo "...Unable to find VCF_creator..."
	exit 1
fi


#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
####Use the pipeline of aligement
if [ -z "$samfile" ];then
        if [ ! -z  "$vcffile" ] && [ -z "$genome" ] && [ -z "$discoSNPs" ]; then
	        help
	        exit 1
	fi
	#Ghost mode
        if [ -z "$genome" ]; then
                echo -e "...Ghost mode..."
                echo -e "...Creation of a vcf without alignment..."
                if [ -z "$discoSNPs" ] && [ -z "$vcffile" ];then
                       echo -e "...To create a vcf without alignment ..."
                       echo -e "...You must provide an output <file>.vcf : option -o..."
                       echo -e "...And the file disco : option -p..."
                       exit 1 
                else
                        n=3
                        
                        python $PATH_VCF_creator/VCF_creator.py -s $discoSNPs -o $vcffile #-n $n
		        echo -e "... Creation of the vcf file : done ...==> $vcffile" 
		        exit 
                fi    
        fi
	if [ -z "$PATH_BWA" ] ;then
		IS_BWA=$(command -v bwa)
	
	
	
		if [ -z "$IS_BWA" ];then
			echo -e "... BWA not found... add bwa to \$PATH or give directly the path (-B)"
			exit 1
		else 
			PATH_BWA=$(dirname $IS_BWA)
		fi
	fi
	
	
	if [ -z "$vcffile" ] ; then
		echo -e "...You must provide an output <file> : option -o (for help -h)..."
                help
		exit 1
	fi
	if [ -z "$genome" ]; then
		echo -e "...You must provide a genome of reference : option -G (for help -h)..."
              help
		exit 1
	fi
	
	if [ -z "$discoSNPs" ];then
		echo "... Error : file disco is missing : option -p (for help -h)..."
              help
		exit 1
	else
		if [ ! -e $PATH_VCF_creator/remove_extensions_disco_file.py ];then
			echo "...Unable to find remove_extensions_disco_file.py..."
			exit 1
		else
			discoSNPsbis=$(basename $discoSNPs .fa)"bis.fasta"
			python $PATH_VCF_creator/remove_extensions_disco_file.py $discoSNPs $discoSNPsbis
			if [ -z "$discoSNPsbis" ];then
				echo "...Error with the script remove_extensions_disco_file.py..."
			fi
		fi
	fi
	if [ -z "$n" ];then
		echo -e "\t##Default value for the number of mismatches allowed in alignment : 3 (to change it -n)"
		n=3
	fi
###BWA 
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
	#BWA files
       #Pierre: user gave a file name we must respect its choice.
#	vcf=$(basename $vcffile .vcf)"_"$(basename $discoSNPs .fa)"_n"$n"_l"$l"_s"$s".vcf" 
	samfile=$(basename $discoSNPs .fa)"BWA_OPT_n"$n"_l"$l"_s"$s".sam"
	saifile=$(basename $vcffile .vcf)"_n"$n"_l"$l"_s"$s".sai"
	indexamb=$genome".amb"
	indexann=$genome".ann"
	indexbwt=$genome".bwt"
	indexpac=$genome".pac"
	indexsa=$genome".sa"
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
	##Indexation of reference genome
	if [ -e $indexamb ] && [ -e $indexann ] && [ -e $indexbwt ] && [ -e $indexpac ] && [ -e $indexsa ]; then
		echo -e "...Indexation : Using the existing index..."
	else
		$PATH_BWA/bwa index $genome
	fi
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
	##Alignment discosnps on the reference genome
	if [ -e $saifile ]; then
		echo -e "...Alignment : Using the existing file : $saifile"
	else
		$PATH_BWA/bwa mem $genome $discoSNPsbis > $samfile
	fi
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
	##Creation of the vcf file
	# if [ -e $vcffile ]; then
#               echo -e "...VCF file for this alignment already exists...==> $vcf"
#        else
		python $PATH_VCF_creator/VCF_creator.py -s $samfile -o $vcffile #-n $n
		echo -e "... Creation of the vcf file : done ...==> $vcffile"
       # fi       
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
	
else
       ####Skip alignment phase to create a vcf file
##Test to execute VCF_creator
        echo -e "...Skipping alignment phase..."
        if [ -z "$n" ];then
                echo -e " ...To do it you must provide the number of mismatch of the alignment..."
                echo -e "\t./run_VCF_creator.sh -f <sam_file> -n <mismatch_number> -o <output> [-l <seed_size>] [-s <bwa_errors_in_seed>] [-w]"
                exit 1
        fi
	if [ -z "$vcffile" ] || [[ "$vcffile" =~ *.vcf ]]; then
		echo -e "...You must provide an output <file>..."
		exit 1
	fi
	if [ -z "$n" ]; then
		echo -e "...You must provide the number of mismatch allowed during the alignment phase.."
		exit 1
	fi
	##Creation of the vcf file
       
	python $PATH_VCF_creator/VCF_creator.py -s $samfile -o $vcffile #-n $n
	echo -e "... Creation of the vcf file : done ...==> $vcffile"
fi

if [ $igv -eq 1 ] ; then 
       $DIR/create_IGV_compatible_VCF.sh $vcffile
fi


if [ $remove -eq 1 ];then
	rm -f $indexamb $indexann $indexbwt $indexpac $indexsa $saifile $discoSNPsbis tmp.vcf
else
	rm -f $saifile tmp.vcf #rm -f $saifile $discoSNPsbis tmp.vcf
fi	


